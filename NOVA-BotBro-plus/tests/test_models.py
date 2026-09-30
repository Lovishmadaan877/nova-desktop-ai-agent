from nova.models import Action, Plan, TaskRequest, TaskResult


def test_task_request_validation():
    request = TaskRequest(goal='Open Notepad')
    assert request.confirm_sensitive is False


def test_plan_has_independent_step_arguments():
    a = Action(type='wait', args={'seconds': 1})
    p = Plan(goal='wait', steps=[a])
    assert p.steps[0].args == {'seconds': 1}


def test_task_result_defaults():
    result = TaskResult(task_id=1, status='completed', message='ok', steps_completed=1)
    assert result.verified is False
    assert result.screenshots == []
    assert result.trace == []
