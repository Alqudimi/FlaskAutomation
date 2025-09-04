# دليل التثبيت والتشغيل
## Installation & Setup Guide

### متطلبات النظام / System Requirements

#### الحد الأدنى / Minimum Requirements:
- Python 3.8 أو أحدث / Python 3.8 or newer
- 4 GB RAM
- 2 GB مساحة حرة على القرص الصلب / 2 GB free disk space
- اتصال إنترنت مستقر / Stable internet connection

#### الموصى به / Recommended:
- Python 3.10+
- 8 GB RAM أو أكثر / 8 GB RAM or more
- 5 GB مساحة حرة / 5 GB free space
- معالج متعدد النوى / Multi-core processor

### الحزم المطلوبة / Required Packages

التطبيق يحتاج إلى الحزم التالية:
The application requires the following packages:

```
flask==3.0.0
opencv-python==4.8.1.78
numpy==1.24.3
pillow==10.0.1
flask-sqlalchemy==3.1.1
gunicorn==21.2.0
psycopg2-binary==2.9.7
werkzeug==3.0.1
email-validator==2.0.0
```

### التثبيت في بيئة Replit / Installation on Replit

#### الخطوة 1: إعداد البيئة / Step 1: Environment Setup
```bash
# تثبيت Python 3.11 / Install Python 3.11
uv python install 3.11

# تثبيت المكتبات المطلوبة / Install required libraries
uv add flask opencv-python numpy pillow flask-sqlalchemy gunicorn psycopg2-binary werkzeug email-validator
```

#### الخطوة 2: إعداد متغيرات البيئة / Step 2: Environment Variables
```bash
# في ملف .env أو في إعدادات Replit Secrets
# In .env file or Replit Secrets settings

SESSION_SECRET=your-secret-key-here
DATABASE_URL=postgresql://username:password@host:port/database
```

### التثبيت المحلي / Local Installation

#### الخطوة 1: استنساخ المشروع / Step 1: Clone Project
```bash
git clone https://github.com/Alqudimi/FlaskAutomation

```

#### الخطوة 2: إنشاء البيئة الافتراضية / Step 2: Create Virtual Environment
```bash
# إنشاء البيئة الافتراضية / Create virtual environment
python -m venv venv

# تفعيل البيئة (Windows) / Activate (Windows)
venv\Scripts\activate

# تفعيل البيئة (Mac/Linux) / Activate (Mac/Linux)
source venv/bin/activate
```

#### الخطوة 3: تثبيت المتطلبات / Step 3: Install Requirements
```bash
pip install -r requirements.txt
```

#### الخطوة 4: إعداد قاعدة البيانات / Step 4: Database Setup
```bash
# إنشاء قاعدة البيانات (PostgreSQL)
# Create database (PostgreSQL)
createdb cv_platform

# تشغيل التطبيق لإنشاء الجداول
# Run application to create tables
python main.py
```

### التحقق من التثبيت / Installation Verification

#### اختبار الوحدات / Test Modules
```bash
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import PIL; print('Pillow installed successfully')"
python -c "import flask; print('Flask:', flask.__version__)"
```

#### اختبار الخادم / Test Server
```bash
# تشغيل الخادم / Start server
gunicorn --bind 0.0.0.0:5000 main:app

# أو باستخدام Flask / Or using Flask
python main.py
```

### استكشاف الأخطاء / Troubleshooting

#### مشاكل شائعة / Common Issues:

1. **خطأ OpenCV / OpenCV Error:**
   ```bash
   # إذا فشل تثبيت opencv-python / If opencv-python fails
   pip install opencv-python-headless
   ```

2. **مشاكل PostgreSQL / PostgreSQL Issues:**
   ```bash
   # تأكد من تثبيت PostgreSQL / Ensure PostgreSQL is installed
   sudo apt-get install postgresql postgresql-contrib
   ```

3. **مشاكل الذاكرة / Memory Issues:**
   - قم بزيادة حجم الذاكرة المخصصة / Increase allocated memory
   - استخدم صور أصغر للاختبار / Use smaller images for testing

### الإعدادات المتقدمة / Advanced Configuration

#### تحسين الأداء / Performance Optimization
```python
# في ملف الإعدادات / In configuration file
OPENCV_CACHE_SIZE = 1000  # حجم ذاكرة التخزين المؤقت
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB حد أقصى لحجم الملف
```

#### الأمان / Security Settings
```python
# إعدادات الأمان / Security settings
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
WTF_CSRF_ENABLED = True
```

### النشر / Deployment

#### النشر على Replit / Deployment on Replit
1. تأكد من تكوين workflow بشكل صحيح / Ensure workflow is configured correctly
2. اضبط المنفذ على 5000 / Set port to 5000
3. فعّل HTTPS / Enable HTTPS

#### النشر على خوادم أخرى / Deployment on Other Servers
```bash
# استخدام Gunicorn مع عدة عمال / Using Gunicorn with multiple workers
gunicorn --workers 4 --bind 0.0.0.0:5000 main:app

# مع إعدادات الإنتاج / With production settings
gunicorn --workers 4 --max-requests 1000 --timeout 30 --bind 0.0.0.0:5000 main:app
```

### الصيانة / Maintenance

#### تحديث المكتبات / Update Libraries
```bash
pip list --outdated  # عرض الحزم القديمة / Show outdated packages
pip install --upgrade package-name  # تحديث حزمة معينة / Update specific package
```

#### النسخ الاحتياطي / Backup
- قم بعمل نسخة احتياطية من قاعدة البيانات بانتظام / Regular database backups
- احفظ نسخة من ملفات الإعدادات / Save configuration files
- وثّق التغييرات المخصصة / Document custom changes

### الدعم / Support

إذا واجهت مشاكل في التثبيت:
If you encounter installation issues:

1. تحقق من متطلبات النظام / Check system requirements
2. راجع سجلات الأخطاء / Review error logs
3. تأكد من إصدارات المكتبات / Verify library versions
4. استخدم البيئة الافتراضية / Use virtual environment