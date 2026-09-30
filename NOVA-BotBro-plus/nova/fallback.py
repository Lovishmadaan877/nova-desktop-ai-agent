from .models import Plan,Action
def fallback_plan(goal):
    g=goal.lower()
    if 'paint' in g and 'lion' in g:
        return Plan(goal=goal,steps=[Action(type='launch_app',args={'app':'mspaint.exe'}),Action(type='wait',args={'seconds':2}),Action(type='screenshot'),Action(type='draw_lion'),Action(type='screenshot'),Action(type='finish',args={'message':'Lion sketch completed in Paint.'})])
    if 'calculator' in g and '345' in g and '782' in g:
        return Plan(goal=goal,steps=[Action(type='launch_app',args={'app':'calc.exe'}),Action(type='wait',args={'seconds':2}),Action(type='type',args={'text':'345*782'}),Action(type='press',args={'key':'enter'}),Action(type='screenshot'),Action(type='finish',args={'message':'Calculation completed.'})])
    if 'notepad' in g:
        return Plan(goal=goal,steps=[Action(type='launch_app',args={'app':'notepad.exe'}),Action(type='wait',args={'seconds':1.5}),Action(type='type',args={'text':goal}),Action(type='screenshot'),Action(type='finish',args={'message':'Text entered in Notepad.'})])
    return Plan(goal=goal,steps=[Action(type='screenshot'),Action(type='finish',args={'message':'General planning requires the configured Ollama text model.'})])
