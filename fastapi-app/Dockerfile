# Python 3.9 베이스 이미지 사용
FROM python:3.9-alpine

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY . .

# 의존성 설치
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt influxdb-client uvicorn fastapi prometheus_fastapi_instrumentator

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
