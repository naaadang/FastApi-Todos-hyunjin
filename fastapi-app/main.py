from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import json
import os
import time
from prometheus_fastapi_instrumentator import Instrumentator
# InfluxDB 관련 라이브러리 임포트
from influxdb_client import InfluxDBClient, Point # Point 추가
from influxdb_client.client.write_api import SYNCHRONOUS # SYNCHRONOUS 추가
app = FastAPI()
# Prometheus 메트릭스 엔드포인트 (/metrics)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# To-Do 항목을 위한 데이터 모델
class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    deadline: str
    performance: int

TODO_FILE = "todo.json"

# InfluxDB 설정 (환경 변수 사용 권장)
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://influxdb:8086") # docker-compose 서비스 이름으로 설정
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "my-super-secret-token") # docker-compose에서 설정한 토큰
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "my-org") # docker-compose에서 설정한 조직
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "my-bucket") # docker-compose에서 설정한 버킷

# InfluxDB 클라이언트 초기화
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


# InfluxDB로 메트릭 전송하는 미들웨어 추가
@app.middleware("http")
async def log_request_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # InfluxDB로 데이터 전송
    if influx_write_api:
        try:
            point = Point("fastapi_app_metrics") \
                .tag("endpoint", request.url.path) \
                .tag("method", request.method) \
                .field("response_time_seconds", process_time) \
                .field("status_code", response.status_code)

            influx_write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
            # print(f"Sent metric to InfluxDB: {request.url.path}, time: {process_time:.4f}s, status: {response.status_code}") # 디버깅용
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
    todos.append(todo.dict())
    save_todos(todos)
    return JSONResponse(content=todo.dict())

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo.update(updated_todo.dict())
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
    with open("templates/index.html", "r", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content=content)
