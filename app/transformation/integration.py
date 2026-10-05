import pandas as pd


def integrate_data(students, api, database, mongodb, web):
    # PostgreSQL can contain several course rows per student, so aggregate it first.
    db_agg = (
        database.groupby("student_id", as_index=False)
        .agg(
            gpa=("gpa", "first"),
            attendance=("attendance", "first"),
            status=("status", "first"),
            course=("course", lambda s: " | ".join(sorted(set(s.dropna().astype(str))))),
            score=("score", "mean"),
            semester=("semester", lambda s: " | ".join(sorted(set(s.dropna().astype(str))))),
        )
    )

    mongo_agg = mongodb.drop_duplicates(subset=["student_id"], keep="first")

    merged = students.merge(api, on="student_id", how="inner")
    merged = merged.merge(db_agg, on="student_id", how="inner")
    merged = merged.merge(mongo_agg, on="student_id", how="inner")
    merged = merged.merge(web, on="major", how="left")
    return merged
