# Project Documentation — Student Data Pipeline

## 1. Purpose

The project is an ETL/Data Integration pipeline that collects student-related data from five different sources:

1. CSV — base student and demographic data.
2. Real REST API — external student profile data.
3. PostgreSQL — relational academic data.
4. MongoDB — document-based contact/profile data.
5. Web Scraping — public metadata about the student's major.

The pipeline extracts, cleans, validates, integrates, transforms and loads the final dataset.

## 2. Architecture

```text
CSV -------------------------┐
Real REST API ---------------+
PostgreSQL ------------------+
MongoDB ---------------------+--> Extract --> Clean --> Validate --> Integrate
Web Scraping ----------------┘                                      |
                                                                    v
                                                               Transform
                                                                    |
                                                                    v
                                                           Final Quality Check
                                                                    |
                                                                    v
                                                           final_dataset.csv
```

## 3. Why five sources?

The goal is to demonstrate multi-source data engineering using different data models and access methods.

### CSV
Stores base identity and demographic attributes.

### REST API
Provides external student profile attributes in JSON format.

### PostgreSQL
Stores structured academic data such as GPA, attendance, courses, scores and semesters. SQL joins and aggregation are used before integration.

### MongoDB
Stores document-based student contact/profile attributes such as email, phone and guardian name. The collection is `student_profiles` and documents are linked using `student_id`.

### Web Scraping
Reads public Wikipedia pages for the student's major and extracts title, summary and URL. This is an enrichment source, not a source of private student information.

## 4. PostgreSQL setup without Docker

This version does **not** require Docker.

Create a PostgreSQL database named:

```text
student_pipeline
```

Then execute:

```text
database/schema.sql
database/seed.sql
```

Default connection:

```text
Host: localhost
Port: 5432
Database: student_pipeline
User: postgres
```

The password is read from `POSTGRES_PASSWORD` in `.env`.

## 5. MongoDB setup without Docker

Start the MongoDB service installed on the local machine.

Default connection:

```text
mongodb://localhost:27017
```

The project uses:

```text
Database: student_pipeline
Collection: student_profiles
```

Seed the collection with:

```bash
python database/seed_mongodb.py
```

The source module is:

```text
app/sources/mongodb_source.py
```

It uses PyMongo and converts MongoDB documents into a Pandas DataFrame.

## 6. Environment variables

Copy `.env.example` to `.env`.

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=student_pipeline
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_PASSWORD

MONGO_URI=mongodb://localhost:27017
MONGO_DB=student_pipeline
MONGO_COLLECTION=student_profiles
```

Never commit `.env`.

## 7. Real API configuration

`config.json` contains the external Student API URL and an ID offset of `1000` so API IDs can match the project's local IDs.

## 8. Main modules

### `main.py`
Orchestrates extraction from all five sources and the complete ETL flow.

### `app/sources/csv_source.py`
Reads the CSV source with Pandas.

### `app/sources/api_source.py`
Calls the real REST API and adapts its JSON schema.

### `app/sources/database_source.py`
Connects to PostgreSQL using `psycopg2` and executes SQL joins.

### `app/sources/mongodb_source.py`
Connects to local MongoDB using PyMongo and reads `student_profiles`.

### `app/sources/web_scraper.py`
Downloads and parses public web pages using Requests and BeautifulSoup.

### `app/transformation/cleaner.py`
Standardizes source schemas, IDs and text values.

### `app/transformation/integration.py`
Combines the five sources. PostgreSQL is aggregated by `student_id`, MongoDB is deduplicated by `student_id`, and web metadata is joined by `major`.

### `app/transformation/transformer.py`
Handles missing values, calculates performance and attendance categories, and records data lineage.

### `app/validation/quality.py`
Applies source-level and final data-quality rules.

## 9. Integration keys

`student_id` connects:

```text
CSV ↔ API ↔ PostgreSQL ↔ MongoDB
```

`major` connects:

```text
Student data ↔ Web Scraping
```

## 10. MongoDB document example

```json
{
  "student_id": 1001,
  "email": "student1001@example.com",
  "phone": "+967700001001",
  "guardian_name": "Ahmed Ali"
}
```

After extraction, the document becomes a row in a Pandas DataFrame and is merged using `student_id`.

## 11. Data quality rules

- Student ID must exist.
- Age must be between 16 and 80.
- GPA must be between 0 and 4.
- Attendance must be between 0 and 100.
- Score must be between 0 and 100 when present.
- MongoDB email must exist.
- Final student IDs must be unique.

## 12. Outputs

- `data/processed/final_dataset.csv`
- `data/rejected/rejected_records.csv`
- `logs/pipeline.log`

## 13. Running the project

```bash
pip install -r requirements.txt
python database/seed_mongodb.py
python main.py
```

PostgreSQL and MongoDB must already be running, and the machine needs internet access for the external API and web scraping.

## 14. Tests

```bash
python -m unittest discover -s tests -v
```

The tests cover source configuration, cleaning, validation, five-source integration and final data quality.

## 15. Security

Never commit:

- database passwords,
- `.env`,
- API keys,
- private student data,
- logs containing sensitive information.
