
# 📝 FastAPI Todo App with Full DevOps Pipeline

> **FastAPI 기반 REST API 서비스 + 부하 테스트 + 모니터링 + 정적 분석 + CI/CD 자동화**를 포함한 DevOps 데모 프로젝트

🔗 GitHub Repository: [FastApi-Todos-hyunjin](https://github.com/naaadang/FastApi-Todos-hyunjin)

---

## ✅ 주요 기능

- ✔️ FastAPI 기반 TODO API (CRUD)
- 🧪 Pytest 기반 단위 테스트
- 🔁 JMeter로 성능 테스트 자동 실행
- 🔍 SonarQube를 통한 정적 코드 분석
- 📦 Docker 기반 컨테이너화 및 `docker-compose` 통합 실행
- 🔄 GitHub Actions 기반 CI 파이프라인
- 📊 Prometheus + Grafana 기반 모니터링 환경 구성
- 📡 Node Exporter & cAdvisor를 통한 시스템/컨테이너 메트릭 수집

---

## 🗂 디렉토리 구조

```plaintext
.
├── fastapi-app/
│   ├── main.py                  # FastAPI 엔트리포인트
│   ├── todo.json                # 기본 TODO 데이터
│   ├── templates/index.html     # HTML 렌더링
│   ├── tests/test_main.py       # 단위 테스트
│   ├── sonar-project.properties # SonarQube 설정
│   ├── requirements.txt
│   └── Dockerfile
│
├── jmeter/
│   ├── fastapi_test_plan.jmx    # JMeter 테스트 계획
│   └── Dockerfile               # JMeter 실행 컨테이너
│
├── prometheus/
│   └── prometheus.yml           # Prometheus 설정 파일
│
├── docker-compose.yml           # 전체 서비스 구성
└── .gitignore
````

---

## 🚀 빠른 시작

### 1. 전체 DevOps 환경 실행

```bash
docker-compose up --build
```

서비스 포트:

* FastAPI App: [http://localhost:5001](http://localhost:5001)
* Swagger UI: [http://localhost:5001/docs](http://localhost:5001/docs)
* Prometheus: [http://localhost:9090](http://localhost:9090)
* Grafana: [http://localhost:3000](http://localhost:3000) (ID: `admin`, PW: `admin`)
* SonarQube: [http://localhost:9000](http://localhost:9000)
* Node Exporter: [http://localhost:9100](http://localhost:9100)

### 2. 개별 실행 (FastAPI만 실행)

```bash
cd fastapi-app
uvicorn main:app --reload --port 5001
```




---

## 🛠 기술 스택

| 범주    | 스택                                 |
| ----- | ---------------------------------- |
| 백엔드   | FastAPI, Uvicorn, Pydantic         |
| 테스트   | Pytest, JMeter                     |
| 분석    | SonarQube                          |
| 모니터링  | Prometheus, Grafana, Node Exporter |
| 컨테이너화 | Docker, Docker Compose             |
| 자동화   | GitHub Actions                     |

---
