import os
from sqlite_utils import Database

# Get the absolute path to the memory directory
memory_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(memory_dir, "agent_memory.db")
db = Database(db_path)

if "tasks" not in db.table_names():
    db["tasks"].create({
        "id": int,
        "task": str,
        "result": str
    }, pk="id")

def save_task(task, result):
    db["tasks"].insert({
        "task": task,
        "result": result
    })

def fetch_memory():
    return list(db["tasks"].rows)
