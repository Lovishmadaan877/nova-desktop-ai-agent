from nova.fallback import fallback_plan
def test_lion_plan(): assert any(x.type=='draw_lion' for x in fallback_plan('Open Paint and draw a lion sketch').steps)
def test_notepad_plan(): assert fallback_plan('Open Notepad and write hello').steps[0].type=='launch_app'
