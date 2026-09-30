import sqlite3
from datetime import datetime
from .config import DB_PATH
def connect():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
    c=connect(); c.execute('CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT,goal TEXT,status TEXT,message TEXT,created_at TEXT,finished_at TEXT)'); c.execute('CREATE TABLE IF NOT EXISTS memory(id INTEGER PRIMARY KEY AUTOINCREMENT,task_id INTEGER,key TEXT,value TEXT,created_at TEXT)'); c.commit(); c.close()
def create_task(goal):
    c=connect(); cur=c.execute('INSERT INTO tasks(goal,status,created_at) VALUES(?,?,?)',(goal,'running',datetime.now().isoformat())); c.commit(); i=cur.lastrowid; c.close(); return i
def finish_task(i,status,message):
    c=connect(); c.execute('UPDATE tasks SET status=?,message=?,finished_at=? WHERE id=?',(status,message,datetime.now().isoformat(),i)); c.commit(); c.close()
def save_memory(task_id,key,value):
    c=connect(); c.execute('INSERT INTO memory(task_id,key,value,created_at) VALUES(?,?,?,?)',(task_id,key,value,datetime.now().isoformat())); c.commit(); c.close()
def recent_tasks(limit=30):
    c=connect(); rows=[dict(r) for r in c.execute('SELECT * FROM tasks ORDER BY id DESC LIMIT ?',(limit,)).fetchall()]; c.close(); return rows
