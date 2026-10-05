import pandas as pd


def validate_csv(df):
    issues = []
    required = {"student_id", "age", "student_name", "major", "city"}
    if not required.issubset(df.columns):
        return pd.DataFrame(), pd.DataFrame(), ["Missing required CSV columns"]
    x = df.copy()
    x["student_id"] = pd.to_numeric(x["student_id"], errors="coerce")
    x["age"] = pd.to_numeric(x["age"], errors="coerce")
    invalid = x[x["student_id"].isna() | x["age"].isna() | ~x["age"].between(16, 80)]
    valid = x[~x.index.isin(invalid.index)]
    for idx in invalid.index:
        if pd.isna(x.loc[idx, "student_id"]): issues.append((idx, "Missing student_id"))
        elif pd.isna(x.loc[idx, "age"]): issues.append((idx, "Missing age"))
        elif not 16 <= x.loc[idx, "age"] <= 80: issues.append((idx, "Invalid Age"))
    return valid, invalid, issues


def validate_api(df):
    required = {"student_id", "api_name"}
    if not required.issubset(df.columns):
        return pd.DataFrame(), pd.DataFrame(), ["Missing required API columns"]
    x = df.copy()
    x["student_id"] = pd.to_numeric(x["student_id"], errors="coerce")
    invalid = x[x["student_id"].isna() | x["api_name"].isna() | x["api_name"].str.strip().eq("")]
    valid = x[~x.index.isin(invalid.index)]
    reasons = []
    for idx in invalid.index:
        if pd.isna(x.loc[idx, "student_id"]): reasons.append((idx, "Missing student_id"))
        else: reasons.append((idx, "Missing API name"))
    return valid, invalid, reasons


def validate_database(df):
    x = df.copy()
    x["student_id"] = pd.to_numeric(x["student_id"], errors="coerce")
    x["gpa"] = pd.to_numeric(x["gpa"], errors="coerce")
    x["attendance"] = pd.to_numeric(x["attendance"], errors="coerce")
    x["score"] = pd.to_numeric(x["score"], errors="coerce")
    invalid = x[
        x["student_id"].isna()
        | x["gpa"].isna()
        | ~x["gpa"].between(0, 4)
        | x["attendance"].isna()
        | ~x["attendance"].between(0, 100)
        | (x["credit_hours"].notna() & (pd.to_numeric(x["credit_hours"], errors="coerce") <= 0))
        | (x["score"].notna() & ~x["score"].between(0, 100))
    ]
    valid = x[~x.index.isin(invalid.index)]
    reasons = []
    for idx in invalid.index:
        row = x.loc[idx]
        if pd.isna(row["student_id"]): reason = "Missing student_id"
        elif pd.isna(row["gpa"]) or not 0 <= row["gpa"] <= 4: reason = "Invalid GPA"
        elif pd.isna(row["attendance"]) or not 0 <= row["attendance"] <= 100: reason = "Invalid Attendance"
        elif pd.notna(row["score"]) and not 0 <= row["score"] <= 100: reason = "Invalid Score"
        else: reason = "Invalid Database Record"
        reasons.append((idx, reason))
    return valid, invalid, reasons


def final_quality_check(df):
    checks = {
        "student_id_not_null": int(df["student_id"].notna().all()),
        "student_id_unique": int(df["student_id"].is_unique),
        "age_range": int(df["age"].between(16, 80).all()),
        "gpa_range": int(df["gpa"].between(0, 4).all()),
        "attendance_range": int(df["attendance"].between(0, 100).all()),
        "score_range": int(df["score"].between(0, 100).all()),
    }
    return all(checks.values()), checks


def validate_mongodb(df):
    required = {"student_id", "email", "phone", "guardian_name"}
    if not required.issubset(df.columns):
        return pd.DataFrame(), pd.DataFrame(), [(0, "Missing required MongoDB columns")]
    x = df.copy()
    x["student_id"] = pd.to_numeric(x["student_id"], errors="coerce")
    invalid = x[x["student_id"].isna() | x["email"].isna() | x["email"].astype(str).str.strip().eq("")]
    valid = x[~x.index.isin(invalid.index)]
    reasons = []
    for idx in invalid.index:
        if pd.isna(x.loc[idx, "student_id"]):
            reason = "Missing student_id"
        else:
            reason = "Missing MongoDB email"
        reasons.append((idx, reason))
    return valid, invalid, reasons
