# Identity Mapping Scraper

This project provides a Scrapy + Airflow + MongoDB + Neo4j pipeline to scrape, clean, and store identity mapping data.

---

## 🚀 Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd identity-mapping
   ```

2. Build and start Docker containers:
   ```bash
   docker compose up -d --build
   ```

3. Access Airflow UI at: [http://localhost:8080](http://localhost:8080)  
   Default login: `airflow / airflow`

---

## 🕷️ Running Scrapy via Airflow

### Run All Spiders
1. Add spider names inside `spiders.txt` (one per line):
   ```
   npi
   otherspider
   spider2
   ```
2. In Airflow UI → **Trigger DAG** (`dynamic_scrapy_spiders`).
3. All spiders will run in sequence. Logs are available in Airflow.

---

### Run a Specific Spider
You can trigger a **single spider** instead of all.

#### Option 1: Pass Config on Trigger
1. In Airflow UI → click **Trigger DAG w/ config** (⚙️).
2. Provide JSON like:
   ```json
   { "spider_name": "npi" }
   ```
3. Only that spider will run.

#### Option 2: Use Airflow Variable
You can set an Airflow **Variable** so you don’t need to pass config each time:
1. In Airflow UI → **Admin → Variables → Create**
   - Key: `SCRAPY_SPIDER`
   - Value: `npi`
2. Save it.
3. Now, when you trigger the DAG normally, it will pick up this variable and run that spider.

---

### Behavior Summary
- If **config JSON** is provided → that spider runs.
- Else if **Airflow Variable `SCRAPY_SPIDER`** exists → that spider runs.
- Else → all spiders from `spiders.txt` run.

---

## 📊 Data Flow
- Scrapy spiders → MongoDB (raw & cleaned) → Neo4j (graph relationships)

## 🔑 Credentials
- **MongoDB** runs at `mongo:27017` inside Docker.
- **Neo4j** runs at `neo4j:7687`. Default user/pass: `neo4j / newpassword`.

---

## 🛠️ Useful Commands

### Restart Environment Fresh
```bash
docker compose down -v   # stop and remove volumes
docker compose up -d --build
```

### Check Logs
```bash
docker compose logs -f airflow-web
```

