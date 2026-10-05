INSERT INTO student_metrics (student_id, gpa, attendance, status) VALUES
(1001,3.45,92,'Active'),(1002,3.80,95,'Active'),(1003,2.95,78,'Active'),
(1004,3.70,90,'Active'),(1005,NULL,88,'Active'),(1006,2.70,74,'Active'),
(1007,4.50,92,'Active'),(1008,2.40,68,'Active'),(1009,3.60,101,'Active'),
(1010,3.20,85,'Active'),(1011,2.85,80,'Active'),(1012,3.10,82,'Active'),
(1013,3.90,97,'Active'),(1014,3.55,91,'Active'),(1015,2.20,72,'Active')
ON CONFLICT (student_id) DO NOTHING;

INSERT INTO courses (course_id, course_name, credit_hours) VALUES
(1,'Python Programming',3),(2,'Database Systems',3),(3,'Data Engineering',3),
(4,'Machine Learning',3),(5,'Software Engineering',3)
ON CONFLICT (course_id) DO NOTHING;

INSERT INTO enrollments (student_id, course_id, semester, score) VALUES
(1001,1,'2026-S1',91),(1001,2,'2026-S1',88),
(1002,1,'2026-S1',96),(1002,3,'2026-S1',94),
(1003,2,'2026-S1',79),(1003,5,'2026-S1',82),
(1004,1,'2026-S1',93),(1004,4,'2026-S1',90),
(1005,2,'2026-S1',76),(1005,5,'2026-S1',81),
(1006,1,'2026-S1',72),(1006,2,'2026-S1',75),
(1007,3,'2026-S1',98),(1007,4,'2026-S1',95),
(1008,1,'2026-S1',68),(1008,5,'2026-S1',73),
(1009,2,'2026-S1',87),(1009,3,'2026-S1',91),
(1010,1,'2026-S1',84),(1010,5,'2026-S1',86),
(1011,2,'2026-S1',80),(1011,3,'2026-S1',83),
(1012,3,'2026-S1',88),(1012,5,'2026-S1',85),
(1013,4,'2026-S1',97),(1013,5,'2026-S1',95),
(1014,1,'2026-S1',92),(1014,2,'2026-S1',90),
(1015,3,'2026-S1',70),(1015,5,'2026-S1',74)
ON CONFLICT DO NOTHING;
