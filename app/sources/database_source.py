import os

import pandas as pd
import psycopg2


def get_database_connection(config):
    """Create a PostgreSQL connection without storing the password in source code."""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", config.get("host", "localhost")),
        port=os.getenv("POSTGRES_PORT", str(config.get("port", 5432))),
        dbname=os.getenv("POSTGRES_DB", config.get("database", "student_pipeline")),
        user=os.getenv("POSTGRES_USER", config.get("user", "postgres")),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def extract_database(config, logger):
    logger.info("PostgreSQL extraction started")
    query = """
        SELECT
            sm.student_id,
            sm.gpa,
            sm.attendance,
            sm.status,
            c.course_name AS course,
            c.credit_hours,
            e.score,
            e.semester
        FROM student_metrics sm
        LEFT JOIN enrollments e ON sm.student_id = e.student_id
        LEFT JOIN courses c ON e.course_id = c.course_id
        ORDER BY sm.student_id
    """
    with get_database_connection(config) as conn:
        df = pd.read_sql_query(query, conn)
    logger.info("PostgreSQL records: %s", len(df))
    return df
