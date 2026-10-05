import pandas as pd

CITY_MAP = {
    "sanaa": "Sanaa", "aden": "Aden", "taiz": "Taiz"
}


def clean_students(df):
    x = df.copy()
    x.columns = [c.strip().lower().replace(" ", "_") for c in x.columns]
    x["student_name"] = x["student_name"].astype(str).str.strip()
    x["major"] = x["major"].astype(str).str.strip()
    x["city"] = x["city"].astype(str).str.strip().str.lower().map(CITY_MAP).fillna(x["city"].astype(str).str.strip())
    x["student_id"] = pd.to_numeric(x["student_id"], errors="coerce").astype("Int64")
    x["age"] = pd.to_numeric(x["age"], errors="coerce")
    before = len(x)
    x = x.drop_duplicates(subset=["student_id"], keep="first")
    duplicates = before - len(x)
    return x, duplicates


def clean_api(df):
    x = df.copy()
    x["student_id"] = pd.to_numeric(x["student_id"], errors="coerce").astype("Int64")
    x["api_name"] = x["api_name"].astype("string").str.strip()
    x["api_course"] = x["api_course"].astype("string").str.strip()
    return x


def clean_web(df):
    x = df.copy()
    x["major"] = x["major"].astype(str).str.strip()
    for column in ["web_title", "web_summary", "web_url"]:
        x[column] = x[column].astype("string").str.strip()
    return x


def clean_mongodb(df):
    x = df.copy()
    if x.empty:
        return pd.DataFrame(columns=["student_id", "email", "phone", "guardian_name"])
    x["student_id"] = pd.to_numeric(x["student_id"], errors="coerce").astype("Int64")
    for column in ["email", "phone", "guardian_name"]:
        if column not in x.columns:
            x[column] = pd.NA
        x[column] = x[column].astype("string").str.strip()
    return x[["student_id", "email", "phone", "guardian_name"]]
