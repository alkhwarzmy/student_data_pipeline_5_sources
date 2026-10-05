import json
import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from app.sources.csv_source import extract_csv
from app.sources.api_source import extract_api
from app.sources.database_source import extract_database
from app.sources.mongodb_source import extract_mongodb
from app.sources.web_scraper import extract_web_scraping
from app.transformation.cleaner import clean_students, clean_api, clean_web, clean_mongodb
from app.transformation.integration import integrate_data
from app.transformation.transformer import transform_data
from app.validation.quality import validate_csv, validate_api, validate_database, validate_mongodb, final_quality_check
from app.output.csv_writer import save_csv
from app.utils.logger import get_logger

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")


def load_config():
    return json.loads((ROOT / "config.json").read_text(encoding="utf-8"))


def write_rejections(records, path):
    rows = [{"source": source, "student_id": student_id, "error_reason": reason}
            for source, reason, student_id in records]
    out = pd.DataFrame(rows, columns=["source", "student_id", "error_reason"])
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False, encoding="utf-8-sig")
    return len(out)


def run_pipeline():
    cfg = load_config()
    logger = get_logger(cfg["log_path"])
    start = time.perf_counter()
    logger.info("========== PIPELINE START ==========")

    # 1) Extract
    csv_raw = extract_csv(ROOT / cfg["csv_path"], logger)
    api_raw = extract_api(
        cfg["api_url"],
        cfg["api_timeout"],
        logger,
        cfg.get("api_student_id_offset", 0),
        mock_api_url=cfg.get("mock_api_url"),
        mock_api_timeout=cfg.get("mock_api_timeout"),
        mock_data_path=ROOT / cfg["mock_api_data_path"] if cfg.get("mock_api_data_path") else None,
    )
    db_raw = extract_database(cfg["postgres"], logger)
    mongo_raw = extract_mongodb(cfg["mongodb"], logger)

    # 2) Clean source schemas
    students, duplicate_count = clean_students(csv_raw)
    api = clean_api(api_raw)
    web_raw = extract_web_scraping(students["major"].tolist(), cfg["web_timeout"], logger)
    web = clean_web(web_raw)
    mongo = clean_mongodb(mongo_raw)

    # 3) Validate sources
    students_valid, _, csv_reasons = validate_csv(students)
    api_valid, _, api_reasons = validate_api(api)
    db_valid, _, db_reasons = validate_database(db_raw)
    mongo_valid, _, mongo_reasons = validate_mongodb(mongo)

    rejected = []
    for idx, reason in csv_reasons:
        sid = students.loc[idx, "student_id"] if idx in students.index else None
        rejected.append(("CSV", reason, sid))
    for idx, reason in api_reasons:
        sid = api.loc[idx, "student_id"] if idx in api.index else None
        rejected.append(("API", reason, sid))
    for idx, reason in db_reasons:
        sid = db_raw.loc[idx, "student_id"] if idx in db_raw.index else None
        rejected.append(("POSTGRESQL", reason, sid))

    for idx, reason in mongo_reasons:
        sid = mongo.loc[idx, "student_id"] if idx in mongo.index else None
        rejected.append(("MONGODB", reason, sid))

    # 4) Integrate five sources
    integrated = integrate_data(students_valid, api_valid, db_valid, mongo_valid, web)

    # 5) Transform
    transformed = transform_data(integrated)

    # 6) Final validation
    ok, checks = final_quality_check(transformed)
    if not ok:
        raise ValueError(f"Final data quality checks failed: {checks}")

    # 7) Load
    save_csv(transformed, ROOT / cfg["processed_path"])
    rejected_count = write_rejections(rejected, ROOT / cfg["rejected_path"])

    missing_values = int(transformed.isna().sum().sum())
    elapsed = time.perf_counter() - start
    logger.info("Final dataset created: %s records", len(transformed))
    logger.info(
        "PIPELINE EXECUTION SUMMARY | CSV=%s API=%s POSTGRESQL=%s MONGODB=%s WEB=%s INTEGRATED=%s VALID=%s REJECTED=%s DUPLICATES=%s MISSING_VALUES=%s PROCESSING_TIME=%.3fs",
        len(csv_raw), len(api_raw), len(db_raw), len(mongo_raw), len(web), len(integrated), len(transformed),
        rejected_count, duplicate_count, missing_values, elapsed
    )
    logger.info("=========== PIPELINE END ===========")
    return transformed, rejected_count, checks


if __name__ == "__main__":
    run_pipeline()
