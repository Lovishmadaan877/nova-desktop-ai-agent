import json,re,requests
from .config import OLLAMA_URL,TEXT_MODEL
from .models import Plan
from .fallback import fallback_plan
SYSTEM='''You are NOVA, a Windows computer-use agent planner. Convert a goal into a SHORT safe sequence. For UI decisions prefer semantic targets, e.g. {"type":"click","args":{"target":"Save button"}}. The executor grounds targets with a vision model. Allowed actions: launch_app, click, double_click, move, drag, type, press, hotkey, scroll, wait, screenshot, draw_lion, finish. Never generate unrestricted shell commands. Return ONLY JSON: {"goal":"...","steps":[{"type":"...","args":{},"reason":"..."}]}'''
def _json(t):
    t=re.sub(r'^```(?:json)?','',t.strip(),flags=re.I).strip(); t=re.sub(r'```$','',t).strip(); a=t.find('{'); b=t.rfind('}');
    if a<0 or b<0: raise ValueError('No planner JSON')
    return json.loads(t[a:b+1])
def llm_plan(goal):
    r=requests.post(f'{OLLAMA_URL}/api/chat',json={'model':TEXT_MODEL,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':goal}],'stream':False,'format':'json'},timeout=60); r.raise_for_status(); 
    plan = Plan.model_validate(_json(r.json()['message']['content']))
    if not plan.steps:
        raise ValueError('Planner returned an empty plan')
    return plan
def replan(goal,observation,error):
    prompt=f'Goal: {goal}\nObservation: {observation}\nPrevious action error: {error}\nCreate a revised short JSON plan using only allowed actions.'
    r=requests.post(f'{OLLAMA_URL}/api/chat',json={'model':TEXT_MODEL,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}],'stream':False,'format':'json'},timeout=60); r.raise_for_status(); plan = Plan.model_validate(_json(r.json()['message']['content']))
    if not plan.steps:
        raise ValueError('Replanner returned an empty plan')
    return plan
def make_plan(goal):
    try:return llm_plan(goal)
    except Exception:return fallback_plan(goal)
