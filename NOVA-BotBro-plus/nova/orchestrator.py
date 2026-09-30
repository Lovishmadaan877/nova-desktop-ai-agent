import re
import time

from . import db
from .computer import Computer
from .config import MAX_RETRIES, MAX_STEPS, REQUIRE_CONFIRMATION
from .models import TaskResult
from .planner import make_plan, replan
from .vision import Vision

SENSITIVE_WORDS = {
    'delete', 'remove', 'send', 'purchase', 'buy', 'payment',
    'password', 'credential', 'shutdown', 'format', 'install',
}

class Orchestrator:
    def __init__(self):
        self.computer = Computer()
        self.vision = Vision()

    def run(self, goal, task_id, confirm_sensitive=False):
        tokens = set(re.findall(r'[a-z]+', goal.lower()))
        sensitive = bool(tokens & SENSITIVE_WORDS)
        if REQUIRE_CONFIRMATION and sensitive and not confirm_sensitive:
            msg = 'Blocked by safety gate. Explicit confirmation is required for potentially sensitive goals.'
            db.finish_task(task_id, 'blocked', msg)
            return TaskResult(task_id=task_id, status='blocked', message=msg, steps_completed=0,
                              trace=['Safety gate blocked task.'])

        plan = make_plan(goal)
        trace = [f'PLAN: {len(plan.steps)} actions generated.']
        completed = 0
        retries = 0
        i = 0

        while i < len(plan.steps) and completed < MAX_STEPS:
            action = plan.steps[i]
            try:
                trace.append(f'STEP {i + 1}: {action.type} {action.args}')
                self._execute(action)
                completed += 1

                if action.type not in {'wait', 'move'}:
                    p = self.computer.screenshot(f'after_{i + 1}')
                    obs = self.vision.analyze(p)
                    trace.append('OBSERVE: ' + str(obs.get('description', ''))[:300])

                if action.type == 'finish':
                    return self._finish_verified(goal, task_id, completed, trace)

                i += 1
                retries = 0
            except Exception as exc:
                trace.append(f'ERROR: {exc}')
                if retries >= MAX_RETRIES:
                    msg = f'Task stopped after recovery attempts: {exc}'
                    db.finish_task(task_id, 'failed', msg)
                    return TaskResult(task_id=task_id, status='failed', message=msg,
                                      steps_completed=completed, screenshots=self.computer.screenshots, trace=trace)
                retries += 1
                try:
                    p = self.computer.screenshot(f'failure_{i + 1}_{retries}')
                    obs = self.vision.analyze(p)
                    plan = replan(goal, str(obs), str(exc))
                    i = 0
                    trace.append(f'REPLAN: recovery attempt {retries}; revised plan has {len(plan.steps)} actions.')
                except Exception as replanning_error:
                    trace.append(f'REPLAN ERROR: {replanning_error}')
                    i += 1

        msg = 'Task reached the execution limit without a completion signal.'
        db.finish_task(task_id, 'failed', msg)
        return TaskResult(task_id=task_id, status='failed', message=msg,
                          steps_completed=completed, screenshots=self.computer.screenshots, trace=trace)

    def _finish_verified(self, goal, task_id, completed, trace):
        p = self.computer.screenshot('final_verification')
        result = self.vision.verify_goal(p, goal)
        if result is None:
            msg = 'Actions completed, but final visual verification was unavailable; NOVA did not claim success.'
            db.finish_task(task_id, 'unverified', msg)
            trace.append('VERIFY: unavailable; success not claimed.')
            return TaskResult(task_id=task_id, status='unverified', message=msg,
                              steps_completed=completed, verified=False,
                              screenshots=self.computer.screenshots, trace=trace)

        evidence = str(result.get('evidence', ''))[:300]
        if result.get('success') is True:
            msg = f'Task completed and visually verified. {evidence}'.strip()
            db.save_memory(task_id, 'result', msg)
            db.finish_task(task_id, 'completed', msg)
            trace.append('VERIFY: PASS — ' + evidence)
            return TaskResult(task_id=task_id, status='completed', message=msg,
                              steps_completed=completed, verified=True,
                              screenshots=self.computer.screenshots, trace=trace)

        msg = f'Task actions finished, but verification did not confirm the goal. {evidence}'.strip()
        db.finish_task(task_id, 'failed', msg)
        trace.append('VERIFY: FAIL — ' + evidence)
        return TaskResult(task_id=task_id, status='failed', message=msg,
                          steps_completed=completed, verified=False,
                          screenshots=self.computer.screenshots, trace=trace)

    def _execute(self, action):
        t, x = action.type, action.args
        if t == 'launch_app': self.computer.launch_app(x['app'])
        elif t in {'click', 'double_click'}:
            X, Y = self._coords(x); getattr(self.computer, t)(X, Y)
        elif t == 'move':
            X, Y = self._coords(x); self.computer.move(X, Y)
        elif t == 'drag': self.computer.drag(int(x['x1']), int(x['y1']), int(x['x2']), int(x['y2']))
        elif t == 'type': self.computer.type(x['text'])
        elif t == 'press': self.computer.press(x['key'])
        elif t == 'hotkey': self.computer.hotkey(x['keys'])
        elif t == 'scroll': self.computer.scroll(x['amount'])
        elif t == 'wait': time.sleep(float(x.get('seconds', 1)))
        elif t == 'screenshot': self.computer.screenshot('manual')
        elif t == 'draw_lion': self.computer.draw_lion()
        elif t == 'finish': return
        else: raise ValueError(f'Unsupported action: {t}')

    def _coords(self, args):
        if 'x' in args and 'y' in args:
            return int(args['x']), int(args['y'])
        target = args.get('target')
        if not target:
            raise ValueError('Click requires x/y or semantic target')
        p = self.computer.screenshot('ground')
        found = self.vision.find_target(p, target)
        if not found:
            raise ValueError(f'Vision could not ground target: {target}')
        X, Y, confidence = found
        if confidence and confidence < .35:
            raise ValueError(f'Low vision confidence for {target}: {confidence}')
        return X, Y
