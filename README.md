
# Identity Mapping Crawler

This project integrates **Scrapy**, **Airflow**, **MongoDB**, and **Neo4j** to crawl and process NPI (National Provider Identifier) data.  
It supports running locally with Docker Compose and is designed to be portable (Linux, Windows).

---

## 🚀 Features
- Scrapy spiders to crawl NPI data
- Airflow DAGs for orchestration
- MongoDB for storing crawled data
- Neo4j for graph storage and analysis
- Dynamic spider loading via `spiders.txt`

---

## 📦 Prerequisites

### Linux (Ubuntu)
- [Docker](https://docs.docker.com/engine/install/ubuntu/)
- [Docker Compose](https://docs.docker.com/compose/install/)

```bash
sudo apt update && sudo apt install -y docker.io docker-compose
sudo systemctl enable docker --now
```

### Windows (Recommended: WSL2)
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Enable **WSL2 backend**
- Install [Git for Windows](https://git-scm.com/download/win)

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/identity-mapping.git
cd identity-mapping
```

### 2. Configure Environment
Update credentials if needed in `docker-compose.yml` and `scraper/scraper/settings.py`.

Example Mongo & Neo4j configs in `settings.py`:
```python
MONGO_URI = "mongodb://mongo:27017"
MONGO_DATABASE = "identity_db"

NEO4J_URI = "bolt://neo4j:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "newpassword"
```

### 3. Build & Start Services
```bash
docker compose up --build -d
```

### 4. Initialize Airflow
Run this only once after the first startup:
```bash
docker exec -it identity_airflow_web airflow db init
docker exec -it identity_airflow_web airflow users create    --username airflow    --password airflow    --firstname Admin    --lastname User    --role Admin    --email admin@example.com
```

### 5. Access Services
- **Airflow Web UI** → [http://localhost:8080](http://localhost:8080)  
  (username: `airflow`, password: `airflow`)
- **MongoDB** → `localhost:27017`
- **Neo4j Browser** → [http://localhost:7474](http://localhost:7474)  
  (username: `neo4j`, password: `newpassword`)

---

## 🕷️ Running Scrapy via Airflow
1. Add spider names inside `spiders.txt` (one per line):
```
npi
otherspider
spider2
```

2. Go to Airflow UI → Trigger the DAG (`dynamic_scrapy_spiders`).

3. Logs can be checked in Airflow UI.

---

## 🔄 Resetting the Environment
If you want a fresh start:
```bash
docker compose down -v
docker compose up --build -d
```

This removes all data volumes (Mongo, Postgres, Neo4j).

---

## 🤝 Contribution
1. Fork this repo  
2. Create a new branch  
3. Commit changes  
4. Open a Pull Request

---

## 📜 License
MIT License
