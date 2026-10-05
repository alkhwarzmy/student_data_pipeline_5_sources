import pandas as pd

def transform_data(df):
    x = df.copy()
    # Missing-value strategy for numeric fields.
    x["age"] = x["age"].fillna(x["age"].median()).round().astype(int)
    x["gpa"] = x["gpa"].fillna(x["gpa"].median()).round(2)
    x["attendance"] = x["attendance"].fillna(x["attendance"].median()).round(2)
    x["score"] = pd.to_numeric(x["score"], errors="coerce").round(2)

    # MongoDB profile fields are optional after source validation.
    for column in ["email", "phone", "guardian_name"]:
        x[column] = x[column].fillna("Not available")

    # Web scraping is an enrichment source; missing web text should not break the pipeline.
    for column in ["web_title", "web_summary", "web_url"]:
        x[column] = x[column].fillna("Not available")

    def performance(gpa):
        if gpa >= 3.5: return "Excellent"
        if gpa >= 3.0: return "Very Good"
        if gpa >= 2.5: return "Good"
        if gpa >= 2.0: return "Acceptable"
        return "At Risk"

    x["performance_level"] = x["gpa"].apply(performance)
    x["attendance_status"] = x["attendance"].apply(lambda v: "Good" if v >= 75 else "Low")
    x["source"] = "CSV+REAL_API+POSTGRESQL+MONGODB+WEB_SCRAPING"

    columns = [
        "student_id", "student_name", "age", "major", "city",
        "api_name", "api_course", "gpa", "attendance", "status",
        "email", "phone", "guardian_name",
        "course", "score", "semester",
        "web_title", "web_summary", "web_url",
        "performance_level", "attendance_status", "source"
    ]
    return x[columns].sort_values("student_id").reset_index(drop=True)
