from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import json
import os
import time
from prometheus_fastapi_instrumentator import Instrumentator
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

app = FastAPI()
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# To-Do 항목을 위한 데이터 모델
class TodoItem(BaseModel):
    # id는 서버에서 생성할 것이므로, 클라이언트에서 받지 않도록 Optional로 하거나,
    # 생성 시에는 필요 없는 필드로 만듭니다.
    # 혹은 생성 시에는 None, 업데이트 시에는 int로 다르게 처리할 수 있습니다.
    # 여기서는 생성 시에는 id가 없어도 되도록 Optional[int]로 변경합니다.
    id: int | None = None # id를 선택 사항으로 변경
    title: str
    description: str
    completed: bool
    deadline: str
    performance: int
    category: str = "일반"

TODO_FILE = "todo.json"

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086") # InfluxDB 주소 확인
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "my-super-secret-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "my-org")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "my-bucket")

try:
    influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    print("InfluxDB client initialized successfully.")
except Exception as e:
    print(f"Failed to initialize InfluxDB client: {e}")
    influx_client = None
    influx_write_api = None

def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_todos(todos):
    with open(TODO_FILE, "w", encoding="utf-8") as file:
        json.dump(todos, file, indent=4, ensure_ascii=False)

@app.middleware("http")
async def log_request_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    if influx_write_api:
        try:
            point = Point("fastapi_app_metrics") \
                .tag("endpoint", request.url.path) \
                .tag("method", request.method) \
                .field("response_time_seconds", process_time) \
                .field("status_code", response.status_code)

            influx_write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        except Exception as e:
            print(f"Error sending metric to InfluxDB: {e}")
    else:
        print("InfluxDB write API not initialized, skipping metric submission.")

    return response

@app.get("/todos", response_model=list[TodoItem])
def get_todos():
    return load_todos()

@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    # 서버에서 고유한 ID 생성
    new_id = int(time.time() * 1000)
    # 생성된 ID를 todo 객체에 할당
    todo.id = new_id
    todos.append(todo.dict())
    save_todos(todos)
    return todo # Changed to return the todo object directly

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            todos[i].update(updated_todo.dict())
            save_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todos = load_todos()
    todos = [todo for todo in todos if todo["id"] != todo_id]
    save_todos(todos)
    return {"message": "To-Do item deleted"}

@app.get("/", response_class=HTMLResponse)
def read_root():
    # templates 디렉토리에 index.html이 있다고 가정합니다.
    # 만약 index.html이 main.py와 같은 레벨에 있다면 단순히 "index.html"로 변경하세요.
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if not os.path.exists(template_path):
         # templates 디렉토리가 없을 경우 현재 디렉토리에서 index.html을 찾도록 대체
        template_path = os.path.join(os.path.dirname(__file__), "index.html")
        if not os.path.exists(template_path):
            raise HTTPException(status_code=500, detail="index.html not found.")

    with open(template_path, "r", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content=content)