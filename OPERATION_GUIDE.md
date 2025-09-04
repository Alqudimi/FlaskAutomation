# دليل التشغيل
## Operation Guide

### بدء التشغيل / Starting the Application

#### التشغيل الأساسي / Basic Operation
```bash
# الطريقة الموصى بها / Recommended method
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app

# للتطوير / For development
python main.py

# مع تسجيل مفصل / With detailed logging
gunicorn --bind 0.0.0.0:5000 --log-level debug main:app
```

#### فحص حالة النظام / System Status Check
```bash
# فحص الذاكرة / Check memory
free -h

# فحص استخدام المعالج / Check CPU usage
top

# فحص المنافذ المستخدمة / Check used ports
netstat -tulpn | grep :5000
```

### إدارة العمليات / Process Management

#### إيقاف وإعادة تشغيل / Stop and Restart
```bash
# إيقاف العملية / Stop process
pkill -f gunicorn

# إعادة التشغيل / Restart
gunicorn --bind 0.0.0.0:5000 main:app

# إعادة التشغيل مع إعادة تحميل الكود / Restart with code reload
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

#### مراقبة العمليات / Process Monitoring
```bash
# عرض العمليات الجارية / Show running processes
ps aux | grep gunicorn

# مراقبة استخدام الموارد / Monitor resource usage
htop
```

### إعدادات الخادم / Server Configuration

#### إعدادات الإنتاج / Production Settings
```bash
# تشغيل مع عدة عمال / Run with multiple workers
gunicorn --workers 4 --bind 0.0.0.0:5000 main:app

# مع حد زمني للطلبات / With request timeout
gunicorn --workers 4 --timeout 120 --bind 0.0.0.0:5000 main:app

# مع إعدادات الذاكرة / With memory settings
gunicorn --workers 4 --max-requests 1000 --max-requests-jitter 100 --bind 0.0.0.0:5000 main:app
```

#### إعدادات التطوير / Development Settings
```bash
# تشغيل مع إعادة التحميل التلقائي / Run with auto-reload
export FLASK_ENV=development
export FLASK_DEBUG=True
python main.py
```

### إدارة قاعدة البيانات / Database Management

#### العمليات الأساسية / Basic Operations
```python
# في Python shell / In Python shell
from app import app, db

with app.app_context():
    # إنشاء الجداول / Create tables
    db.create_all()
    
    # حذف الجداول / Drop tables
    db.drop_all()
    
    # فحص الاتصال / Check connection
    db.engine.execute('SELECT 1')
```

#### النسخ الاحتياطي والاستعادة / Backup and Restore
```bash
# نسخ احتياطي / Backup
pg_dump cv_platform > backup.sql

# استعادة / Restore
psql cv_platform < backup.sql

# نسخ احتياطي مضغوط / Compressed backup
pg_dump -Fc cv_platform > backup.dump
pg_restore -d cv_platform backup.dump
```

### مراقبة الأداء / Performance Monitoring

#### مراقبة السجلات / Log Monitoring
```bash
# عرض السجلات الحية / View live logs
tail -f application.log

# البحث في السجلات / Search logs
grep "ERROR" application.log
grep "$(date '+%Y-%m-%d')" application.log
```

#### مقاييس الأداء / Performance Metrics
```python
# في الكود / In code
import psutil
import logging

# مراقبة استخدام الذاكرة / Monitor memory usage
memory_info = psutil.virtual_memory()
logging.info(f"Memory usage: {memory_info.percent}%")

# مراقبة استخدام المعالج / Monitor CPU usage
cpu_percent = psutil.cpu_percent(interval=1)
logging.info(f"CPU usage: {cpu_percent}%")
```

### إدارة الملفات / File Management

#### إدارة ملفات الصور / Image File Management
```python
# تنظيف الملفات المؤقتة / Clean temporary files
import os
import time

def cleanup_temp_files(directory='/tmp', max_age=3600):
    """حذف الملفات المؤقتة القديمة / Delete old temporary files"""
    current_time = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > max_age:
                os.remove(file_path)
```

#### إدارة مساحة التخزين / Storage Management
```bash
# فحص استخدام المساحة / Check disk usage
df -h

# فحص حجم المجلدات / Check directory sizes
du -sh /*

# تنظيف مساحة القرص / Clean disk space
find /tmp -type f -atime +7 -delete
```

### الأمان والحماية / Security and Protection

#### تدابير الأمان / Security Measures
```bash
# فحص الثغرات الأمنية / Security audit
pip audit

# تحديث الحزم الأمنية / Update security packages
pip install --upgrade pip setuptools

# فحص ملفات النظام / Check system files
find /var/log -name "*.log" -exec grep -l "CRITICAL\|ERROR" {} \;
```

#### النسخ الاحتياطي الآمن / Secure Backup
```bash
# نسخ احتياطي مشفر / Encrypted backup
tar -czf - /path/to/project | gpg --cipher-algo AES256 --compress-algo 1 --symmetric --output backup.tar.gz.gpg

# استعادة من النسخ المشفر / Restore from encrypted backup
gpg --decrypt backup.tar.gz.gpg | tar -xz
```

### استكشاف الأخطاء / Troubleshooting

#### مشاكل الاتصال / Connection Issues
```bash
# فحص المنافذ / Check ports
lsof -i :5000

# فحص الشبكة / Check network
ping localhost
curl -I http://localhost:5000
```

#### مشاكل الذاكرة / Memory Issues
```python
# مراقبة استخدام الذاكرة / Monitor memory usage
import tracemalloc
tracemalloc.start()

# في نهاية العملية / At the end of operation
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
tracemalloc.stop()
```

### الصيانة الدورية / Regular Maintenance

#### المهام اليومية / Daily Tasks
- فحص السجلات للأخطاء / Check logs for errors
- مراقبة استخدام الموارد / Monitor resource usage
- التحقق من عمل جميع الوظائف / Verify all functions work

#### المهام الأسبوعية / Weekly Tasks
- تنظيف الملفات المؤقتة / Clean temporary files
- نسخ احتياطي من قاعدة البيانات / Database backup
- تحديث السجلات الأمنية / Update security logs

#### المهام الشهرية / Monthly Tasks
- تحديث المكتبات / Update libraries
- مراجعة إعدادات الأمان / Review security settings
- تحسين أداء قاعدة البيانات / Optimize database performance

### الطوارئ / Emergency Procedures

#### استعادة سريعة / Quick Recovery
```bash
# استعادة من النسخة الاحتياطية الأخيرة / Restore from latest backup
pg_restore -d cv_platform latest_backup.dump

# إعادة تشغيل جميع الخدمات / Restart all services
systemctl restart postgresql
systemctl restart nginx
gunicorn --bind 0.0.0.0:5000 main:app
```

#### جهات الاتصال / Emergency Contacts
- مسؤول النظام / System Administrator
- فريق الدعم الفني / Technical Support Team
- مطور التطبيق / Application Developer