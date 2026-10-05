# Student Data Pipeline

خط أنابيب بيانات تعليمي يجمع بيانات الطلبة من خمسة مصادر، ثم ينظفها ويتحقق منها ويدمجها ويحوّلها إلى مجموعة بيانات موحدة بصيغة CSV.

## نظرة عامة

| المصدر | التقنية | البيانات |
|---|---|---|
| CSV | Pandas | البيانات الأساسية للطالب |
| REST API | Requests وJSON | اسم الطالب والمقرر |
| PostgreSQL | Psycopg2 وSQL | المعدل والحضور والمقررات والدرجات |
| MongoDB | PyMongo | البريد والهاتف وبيانات ولي الأمر |
| Web scraping | Requests وBeautifulSoup | معلومات عامة عن التخصص |

يمر التنفيذ بالمراحل التالية:

```text
Extract → Clean → Validate → Integrate → Transform → Quality check → Load
```

تعتمد مطابقة السجلات بين المصادر على `student_id`. المشروع معدّ للتشغيل محليًا، ولا يتطلب Docker.

## بنية المشروع

```text
├── app/
│   ├── sources/          # موصلات مصادر البيانات الخمسة
│   ├── transformation/   # التنظيف والدمج والتحويل
│   ├── validation/       # التحقق من جودة البيانات
│   ├── output/           # كتابة ملفات النتائج
│   └── utils/            # التسجيل والأدوات المساعدة
├── data/
│   ├── mock/             # بيانات API محلية بديلة
│   ├── raw/              # ملفات الإدخال
│   ├── processed/        # مجموعة البيانات النهائية
│   └── rejected/         # السجلات المرفوضة وأسبابها
├── database/             # مخطط وبيانات PostgreSQL وMongoDB
├── docs/                 # توثيق المشروع
├── tests/                # الاختبارات
├── config.json           # إعدادات المسارات والاتصالات
├── main.py               # نقطة تشغيل خط الأنابيب
└── requirements.txt      # اعتماديات Python
```

## المتطلبات

- Python و`pip`.
- PostgreSQL يعمل محليًا، مع قاعدة بيانات باسم `student_pipeline`.
- MongoDB يعمل محليًا على `mongodb://localhost:27017`.
- اتصال بالإنترنت لجلب بيانات REST API ومعلومات التخصص. عند تعذّر REST API، يستخدم المشروع بيانات Mock محلية؛ وتعذّر جلب صفحات الويب لا يوقف بقية خط الأنابيب.

## الإعداد

### 1. تثبيت الاعتماديات

من مجلد المشروع، أنشئ بيئة افتراضية وفعّلها:

```bash
python -m venv .venv
```

على Windows:

```powershell
.venv\Scripts\Activate.ps1
```

على macOS أو Linux:

```bash
source .venv/bin/activate
```

ثم ثبّت الحزم:

```bash
pip install -r requirements.txt
```

### 2. إعداد PostgreSQL

أنشئ قاعدة بيانات باسم `student_pipeline` باستخدام pgAdmin أو `psql`. بعد ذلك نفّذ الملفين التاليين على القاعدة، بهذا الترتيب:

```text
database/schema.sql
database/seed.sql
```

ينشئ `schema.sql` الجداول، ويضيف `seed.sql` بيانات تجريبية. إذا كان اسم المستخدم أو كلمة المرور مختلفًا عن الإعداد المحلي، انسخ `.env.example` إلى `.env` وعدّل قيم PostgreSQL. يستخدم التطبيق متغيرات البيئة التالية للاتصال:

```dotenv
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=student_pipeline
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_PASSWORD
```

### 3. إعداد MongoDB

تأكد من تشغيل خدمة MongoDB. يقرأ التطبيق عنوان الاتصال واسم قاعدة البيانات والمجموعة من `config.json`، والقيم الافتراضية هي:

```text
URI: mongodb://localhost:27017
Database: student_pipeline
Collection: student_profiles
```

لتحميل بيانات العينة إلى MongoDB، نفّذ:

```bash
python database/seed_mongodb.py
```

**تنبيه:** هذا السكربت يحذف جميع المستندات الموجودة في مجموعة `student_profiles` قبل تحميل بيانات العينة. لا تشغّله على مجموعة تحتوي بيانات تريد الاحتفاظ بها.

## إعداد المصادر

### REST API

عنوان الخدمة الافتراضي موجود في `config.json`. يضيف التطبيق قيمة `api_student_id_offset` إلى المعرّف القادم من API لمطابقته مع معرّفات المشروع؛ القيمة الافتراضية هي `1000`، لذلك يصبح المعرّف `1` هو `1001`.

إذا تعذر الاتصال بالخدمة الحقيقية أو كانت استجابتها غير صالحة، يحاول التطبيق استخدام `mock_api_url` إن تم ضبطه، ثم ينتقل إلى الملف المحلي `data/mock/api_students.json`. يمكن ضبط خيارات الاحتياط في `config.json`:

```json
{
  "mock_api_url": "",
  "mock_api_timeout": 10,
  "mock_api_data_path": "data/mock/api_students.json"
}
```

تتوقع محوّلات API حقول `id` و`name`، ويمكنها استخدام `course` عند توفره.

### Web scraping

يجلب التطبيق عنوان الصفحة وفقرتها الأولى من صفحات عامة مرتبطة بالتخصص. إذا لم يتوفر اتصال بالإنترنت أو فشل طلب صفحة، يسجل التحذير ويتابع بمعطيات ويب فارغة لذلك التخصص.

## التشغيل

بعد إعداد PostgreSQL وMongoDB وتحميل بيانات MongoDB التجريبية، شغّل من جذر المشروع:

```bash
python main.py
```

ينشئ التشغيل الملفات التالية:

| الملف | المحتوى |
|---|---|
| `data/processed/final_dataset.csv` | مجموعة البيانات النهائية بعد الدمج والتحويل |
| `data/rejected/rejected_records.csv` | السجلات المرفوضة ومصدرها وسبب الرفض |
| `logs/pipeline.log` | سجل مراحل التنفيذ والملخص |

يتوقف التنفيذ مع خطأ إذا لم تنجح فحوص الجودة النهائية.

## الاختبارات

شغّل الاختبارات من جذر المشروع:

```bash
python -m unittest discover -s tests -v
```

بعض الاختبارات وحداتية ولا تحتاج اتصالًا بقواعد البيانات. اختبار النتيجة النهائية يعتمد على وجود ملف ناتج من تشغيل خط الأنابيب.

## قواعد جودة البيانات

- يجب أن يكون `student_id` موجودًا وفريدًا في الناتج النهائي.
- العمر بين 16 و80.
- المعدل التراكمي `GPA` بين 0 و4.
- الحضور بين 0 و100.
- الدرجة بين 0 و100.
- يجب أن يتوفر بريد إلكتروني غير فارغ في سجلات MongoDB.
- تُسجل السجلات غير الصالحة في ملف المرفوضات مع سبب الرفض.

## الأمان والبيانات

- لا ترفع ملف `.env` أو كلمات المرور أو مفاتيح الوصول إلى GitHub.
- استخدم بيانات تجريبية فقط، ولا تضع بيانات طلبة حقيقية أو حساسة في المستودع.
- يتجاهل `.gitignore` ملف `.env` وملفات السجل.

## التوثيق

للتفاصيل الإضافية، راجع [توثيق المشروع](docs/PROJECT_DOCUMENTATION.md) و[تقرير التحقق](VERIFICATION_REPORT.md).
