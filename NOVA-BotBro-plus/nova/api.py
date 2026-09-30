from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .models import TaskRequest
from . import db
from .orchestrator import Orchestrator
app=FastAPI(title='NOVA — Autonomous Windows Desktop Agent',version='2.0.0'); db.init_db()
HTML='''<!doctype html><html><head><meta charset="utf-8"><title>NOVA</title><style>body{font-family:system-ui,Arial;max-width:1000px;margin:40px auto;padding:0 20px}textarea{width:100%;height:110px;padding:12px;font-size:16px;box-sizing:border-box}button{padding:12px 20px;font-size:16px}pre{background:#f5f5f5;padding:15px;white-space:pre-wrap;overflow:auto}.card{border:1px solid #ddd;border-radius:10px;padding:18px;margin-top:20px}</style></head><body><h1>NOVA</h1><p>Observe → Plan → Act → Verify → Recover</p><div class="card"><textarea id="goal" placeholder="Try: Open Paint and draw a lion sketch"></textarea><br><br><label><input id="confirm" type="checkbox"> Confirm sensitive actions</label><br><br><button onclick="runTask()">Run task</button></div><div class="card"><pre id="out">Ready.</pre></div><script>async function runTask(){let goal=document.getElementById('goal').value.trim();if(!goal)return;document.getElementById('out').textContent='NOVA is observing and planning...';let r=await fetch('/tasks',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({goal,confirm_sensitive:document.getElementById('confirm').checked})});document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2)}</script></body></html>'''
@app.get('/',response_class=HTMLResponse)
def home():return HTML
@app.get('/health')
def health():return {'status':'ok','agent':'NOVA','version':'2.0.0'}
@app.get('/tasks')
def tasks():return db.recent_tasks()
@app.post('/tasks')
def create(req:TaskRequest):
    i=db.create_task(req.goal); return Orchestrator().run(req.goal,i,req.confirm_sensitive).model_dump()
