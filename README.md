# Student Data Pipeline — Five-Source ETL & Data Integration

مشروع **Data Engineering / ETL** يجمع بيانات الطلبة من خمسة مصادر مختلفة، ثم ينفذ الاستخراج والتنظيف والتحقق والدمج والتحويل وفحص الجودة النهائي.

## مصادر البيانات

| المصدر | التقنية | الدور |
|---|---|---|
| CSV | Pandas | البيانات الأساسية للطالب |
| Real REST API | Requests + JSON | بيانات ملف الطالب من API خارجي حقيقي |
| PostgreSQL | Psycopg2 + SQL | GPA، الحضور، المقررات والدرجات |
| MongoDB | PyMongo | البريد والهاتف وبيانات ولي الأمر |
| Web Scraping | Requests + BeautifulSoup | وصف عام للتخصص من صفحات عامة |

المسار:

```text
CSV + Real REST API + PostgreSQL + MongoDB + Web Scraping
                         ↓
                      Extract
                         ↓
                       Clean
                         ↓
                     Validate
                         ↓
                     Integrate
                         ↓
                     Transform
                         ↓
                Final Quality Check
                         ↓
                        Load
                         ↓
                 final_dataset.csv
```

> **مهم:** المشروع لا يحتاج Docker. PostgreSQL وMongoDB في هذه النسخة يعملان كخدمات محلية على جهازك.

> **مهم:** الـAPI عنوانه خارجي حقيقي، لذلك يحتاج اتصالًا بالإنترنت. وWeb Scraping يحتاج الإنترنت أيضًا.

## بنية المشروع

```text
student_data_pipeline/
├── app/
│   ├── sources/
│   │   ├── csv_source.py
│   │   ├── api_source.py
│   │   ├── database_source.py
│   │   ├── mongodb_source.py
│   │   └── web_scraper.py
│   ├── transformation/
│   │   ├── cleaner.py
│   │   ├── transformer.py
│   │   └── integration.py
│   ├── validation/
│   │   └── quality.py
│   ├── output/
│   │   └── csv_writer.py
│   └── utils/
│       └── logger.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── rejected/
├── database/
│   ├── schema.sql
│   ├── seed.sql
│   ├── mongodb_seed.json
│   └── seed_mongodb.py
├── docs/
│   └── PROJECT_DOCUMENTATION.md
├── tests/
├── .env.example
├── .gitignore
├── config.json
├── main.py
├── requirements.txt
└── VERIFICATION_REPORT.md
```

## 1. PostgreSQL المحلي

يجب أن يكون PostgreSQL مثبتًا ويعمل على جهازك.

الإعداد الافتراضي:

```text
Host: localhost
Port: 5432
Database: student_pipeline
User: postgres
```

أنشئ قاعدة البيانات `student_pipeline` من pgAdmin أو psql، ثم شغّل:

```text
database/schema.sql
database/seed.sql
```

لإنشاء الجداول وإدخال البيانات التجريبية.

إذا كانت كلمة مرور PostgreSQL مختلفة، أنشئ `.env` من `.env.example` وضع كلمة المرور الصحيحة:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=student_pipeline
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_PASSWORD
```

لا ترفع `.env` إلى GitHub.

## 2. MongoDB المحلي

يجب أن تكون خدمة MongoDB مثبتة وتعمل على جهازك.

الإعداد الافتراضي:

```text
URI: mongodb://localhost:27017
Database: student_pipeline
Collection: student_profiles
```

بعد تشغيل MongoDB، نفذ من مجلد المشروع:

```bash
python database/seed_mongodb.py
```

سيقرأ `database/mongodb_seed.json` ويضيف بيانات ملفات الطلبة إلى مجموعة `student_profiles`.

مصدر MongoDB موجود في:

```text
app/sources/mongodb_source.py
```

ويقرأ الحقول:

- `student_id`
- `email`
- `phone`
- `guardian_name`

ويتم الربط مع بقية المصادر باستخدام `student_id`.

## 3. Real REST API

المشروع يستخدم:

```text
https://api.ajitdev.com/api/student?limit=150
```

الكود يحول:

```text
id     → student_id
name   → api_name
course → api_course
```

وبما أن بيانات المشروع تستخدم IDs تبدأ من `1001`، فإن:

```json
"api_student_id_offset": 1000
```

يحوّل API ID `1` إلى `1001`.

## 3.1 آلية الاحتياط للـAPI (Real API → Mock API)

عند تشغيل الـPipeline يحاول المشروع الاتصال أولًا بالـReal REST API الموجود في `api_url`.

إذا حدث أي من الآتي:
- انقطاع الإنترنت أو فشل الاتصال.
- انتهاء مهلة الاتصال.
- خطأ HTTP.
- استجابة JSON غير صحيحة أو ناقصة.

فسيحوّل التنفيذ تلقائيًا إلى **Mock API**.

ترتيب الاحتياط هو:

```text
Real API
   ↓ فشل الاتصال/الاستجابة
Remote Mock API (إذا تم وضع رابط في mock_api_url)
   ↓ غير متاح
Local Mock API
   ↓
data/mock/api_students.json
```

في النسخة الحالية تم تضمين بيانات Mock محلية حتى يستطيع المشروع العمل حتى عند عدم وجود إنترنت.

الإعدادات في `config.json`:

```json
"mock_api_url": "",
"mock_api_timeout": 10,
"mock_api_data_path": "data/mock/api_students.json"
```

إذا كان لديك رابط Mock API خارجي من خدمة مثل MockAPI، ضعه في `mock_api_url`، وسيحاول المشروع استخدامه قبل الانتقال إلى الملف المحلي.

## 4. Web Scraping

الملف:

```text
app/sources/web_scraper.py
```

يستخدم Requests وBeautifulSoup لاستخراج عنوان الصفحة والفقرة الأولى والرابط من صفحات عامة حسب التخصص.

## 5. التثبيت

أنشئ بيئة افتراضية:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

ثم:

```bash
pip install -r requirements.txt
```

## 6. التشغيل الكامل

### الخطوة 1 — شغّل PostgreSQL

تأكد من أن خدمة PostgreSQL تعمل وأن قاعدة `student_pipeline` موجودة والجداول والبيانات تم إنشاؤها.

### الخطوة 2 — شغّل MongoDB

تأكد من أن خدمة MongoDB تعمل، ثم نفذ مرة واحدة:

```bash
python database/seed_mongodb.py
```

### الخطوة 3 — أنشئ `.env`

انسخ `.env.example` إلى `.env` وعدل كلمة مرور PostgreSQL إذا لزم.

### الخطوة 4 — شغّل الـPipeline

```bash
python main.py
```

الناتج:

```text
data/processed/final_dataset.csv
data/rejected/rejected_records.csv
logs/pipeline.log
```

## 7. الاختبارات

```bash
python -m unittest discover -s tests -v
```

## 8. Data Quality

القواعد الأساسية:

- `student_id` غير فارغ.
- العمر بين 16 و80.
- GPA بين 0 و4.
- Attendance بين 0 و100.
- Score بين 0 و100.
- البريد الإلكتروني في MongoDB غير فارغ.
- معرف الطالب فريد في الناتج النهائي.

## 9. لماذا PostgreSQL وMongoDB معًا؟

PostgreSQL قاعدة بيانات **Relational** مناسبة للبيانات المنظمة والعلاقات بين الطالب والمقرر والتسجيل والدرجات.

MongoDB قاعدة بيانات **Document** مناسبة لبيانات الملف الشخصي التي يمكن أن تتغير بنيتها بسهولة.

وجود الاثنين في نفس الـPipeline يوضح القدرة على دمج مصادر SQL وNoSQL، وهي نقطة مهمة في مشاريع Data Engineering.

## 10. ملاحظات GitHub

لا ترفع:

- `.env`
- كلمات المرور
- مفاتيح API
- بيانات طلاب حقيقية أو حساسة
- ملفات السجلات `*.log`

ملف `.gitignore` يحتوي على `.env` وملفات السجلات.
