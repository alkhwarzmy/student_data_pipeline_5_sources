CREATE TABLE IF NOT EXISTS student_metrics (
    student_id INTEGER PRIMARY KEY,
    gpa NUMERIC(3,2),
    attendance NUMERIC(5,2),
    status VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY,
    course_name VARCHAR(120) NOT NULL,
    credit_hours INTEGER NOT NULL CHECK (credit_hours > 0)
);

CREATE TABLE IF NOT EXISTS enrollments (
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL REFERENCES courses(course_id),
    semester VARCHAR(30) NOT NULL,
    score NUMERIC(5,2),
    PRIMARY KEY (student_id, course_id, semester)
);

CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
