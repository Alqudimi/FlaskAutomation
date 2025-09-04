# دليل الاستخدام
## User Guide

### نظرة عامة / Overview

منصة معالجة الرؤية الحاسوبية هي أداة قوية ومتقدمة لمعالجة وتحليل الصور باستخدام تقنيات الذكاء الاصطناعي. تدعم المنصة اللغتين العربية والإنجليزية وتوفر مجموعة شاملة من أدوات معالجة الصور.

The Computer Vision Processing Platform is a powerful and advanced tool for image processing and analysis using artificial intelligence techniques. The platform supports both Arabic and English languages and provides a comprehensive set of image processing tools.

### بدء الاستخدام / Getting Started

#### الواجهة الرئيسية / Main Interface

عند فتح التطبيق، ستجد:
When you open the application, you will find:

1. **شريط العنوان** / **Title Bar**: يحتوي على اسم التطبيق وأزرار التحكم
2. **منطقة تحميل الصور** / **Image Upload Area**: لرفع الصور المراد معالجتها
3. **لوحة الأدوات** / **Tools Panel**: تحتوي على جميع أدوات المعالجة
4. **منطقة العرض** / **Display Area**: لعرض النتائج والصور المعالجة

#### رفع الصور / Uploading Images

##### الطرق المدعومة / Supported Methods:
1. **السحب والإفلات** / **Drag & Drop**: اسحب الصورة من الحاسوب إلى المنطقة المحددة
2. **زر الرفع** / **Upload Button**: اضغط على "اختر ملف" وحدد الصورة
3. **اللصق** / **Paste**: استخدم Ctrl+V للصق صورة من الحافظة

##### التنسيقات المدعومة / Supported Formats:
- PNG (.png)
- JPEG/JPG (.jpg, .jpeg)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- WebP (.webp)

##### حدود الحجم / Size Limits:
- الحد الأقصى: 16 ميجابايت / Maximum: 16 MB
- الأبعاد المثلى: 1920×1080 بكسل أو أقل / Optimal dimensions: 1920×1080 pixels or less

### الأدوات الأساسية / Basic Tools

#### 1. المرشحات / Filters

##### مرشحات التمويه / Blur Filters:
- **التمويه الغاوسي** / **Gaussian Blur**: للحصول على تمويه ناعم ومتدرج
  - `حجم النواة` / `Kernel Size`: 3, 5, 7, 9, 11
  - `قيمة السيجما` / `Sigma Value`: 0.5 - 5.0

- **التمويه المتوسط** / **Median Blur**: يزيل الضوضاء مع المحافظة على الحواف
  - `حجم النواة` / `Kernel Size`: 3, 5, 7, 9

- **التمويه الثنائي** / **Bilateral Blur**: يحافظ على الحواف أثناء التمويه
  - `القطر` / `Diameter`: 5-20
  - `قيمة السيجما` / `Sigma Color`: 20-150
  - `قيمة السيجما المكانية` / `Sigma Space`: 20-150

##### مرشحات الكشف / Detection Filters:
- **كاني للحواف** / **Canny Edge**: يكتشف حواف الأشياء في الصورة
  - `الحد الأدنى` / `Lower Threshold`: 50-200
  - `الحد الأقصى` / `Upper Threshold`: 100-300

- **سوبل للحواف** / **Sobel Edge**: يكتشف الحواف الرأسية والأفقية
  - `الحجم` / `Size`: 1, 3, 5, 7
  - `الاتجاه` / `Direction`: X, Y, أو كلاهما / Both

- **لابلاسيان** / **Laplacian**: يبرز المناطق ذات التباين العالي
  - `حجم النواة` / `Kernel Size`: 1, 3, 5

##### مرشحات الشكل / Morphological Filters:
- **التآكل** / **Erosion**: يقلل من حجم الكائنات البيضاء
- **التمدد** / **Dilation**: يزيد من حجم الكائنات البيضاء
- **الفتح** / **Opening**: يزيل الضوضاء الصغيرة
- **الإغلاق** / **Closing**: يملأ الفجوات الصغيرة

#### 2. استخراج الميزات / Feature Extraction

##### خوارزميات الاستخراج / Extraction Algorithms:

**SIFT (Scale-Invariant Feature Transform)**:
- مقاوم للتغييرات في الحجم والدوران
- مثالي للصور عالية الجودة
- المعاملات / Parameters:
  - `عدد الميزات` / `Features Count`: 100-1000
  - `عدد الطبقات` / `Octave Layers`: 3-8

**ORB (Oriented FAST and Rotated BRIEF)**:
- سريع وفعال في الاستخدام
- مناسب للتطبيقات الفورية
- المعاملات / Parameters:
  - `عدد الميزات` / `Features Count`: 50-500
  - `عامل التدرج` / `Scale Factor`: 1.2-2.0

**FAST (Features from Accelerated Segment Test)**:
- سريع جداً في الكشف
- مناسب للفيديو والتطبيقات الفورية
- المعاملات / Parameters:
  - `الحد الأدنى` / `Threshold`: 10-50

**HOG (Histogram of Oriented Gradients)**:
- ممتاز لكشف الأشكال والأشخاص
- يحلل اتجاهات التدرجات
- المعاملات / Parameters:
  - `حجم النافذة` / `Window Size`: 64×128, 128×256
  - `حجم الخلية` / `Cell Size`: 8×8, 16×16

#### 3. التحويلات الهندسية / Geometric Transformations

##### التحويلات الأساسية / Basic Transformations:

**الدوران / Rotation**:
- `الزاوية` / `Angle`: -360° إلى +360°
- `نقطة المركز` / `Center Point`: تلقائي أو مخصص
- `عامل التكبير` / `Scale Factor`: 0.1-3.0

**الإزاحة / Translation**:
- `الإزاحة الأفقية` / `Horizontal Shift`: -500 إلى +500 بكسل
- `الإزاحة الرأسية` / `Vertical Shift`: -500 إلى +500 بكسل

**التكبير/التصغير / Scaling**:
- `عامل X` / `X Factor`: 0.1-5.0
- `عامل Y` / `Y Factor`: 0.1-5.0 (اختياري)
- `طريقة الاستيفاء` / `Interpolation`: خطي، مكعبي، أقرب جار

**القص / Cropping**:
- `نقطة البداية X` / `Start X`: 0-عرض الصورة
- `نقطة البداية Y` / `Start Y`: 0-ارتفاع الصورة
- `العرض` / `Width`: 10-عرض الصورة
- `الارتفاع` / `Height`: 10-ارتفاع الصورة

**الانعكاس / Flipping**:
- `أفقي` / `Horizontal`: انعكاس يسار-يمين
- `رأسي` / `Vertical`: انعكاس أعلى-أسفل
- `كلاهما` / `Both`: انعكاس في الاتجاهين

##### التحويلات المتقدمة / Advanced Transformations:

**التحويل الأفيني / Affine Transform**:
- يسمح بالدوران، التكبير، والإزاحة معاً
- يحافظ على الخطوط المستقيمة والمسافات النسبية

**التحويل المنظوري / Perspective Transform**:
- يصحح التشويه المنظوري
- مفيد لصور الوثائق والأسطح المائلة

### الميزات المتقدمة / Advanced Features

#### 1. المعالجة المتعددة / Batch Processing

تسمح بتطبيق عدة عمليات في نفس الوقت:
Allows applying multiple operations simultaneously:

##### معالجة المرشحات المتعددة / Multiple Filters Processing:
```json
{
  "image_id": "image_0",
  "filter_tasks": [
    {
      "task_id": "blur1",
      "filter_type": "gaussian_blur",
      "parameters": {"ksize": 5, "sigma": 1.0}
    },
    {
      "task_id": "edge1",
      "filter_type": "canny_edge",
      "parameters": {"low_threshold": 100, "high_threshold": 200}
    }
  ]
}
```

##### معالجة الميزات المتعددة / Multiple Features Processing:
- استخراج SIFT و ORB في نفس الوقت
- مقارنة نتائج خوارزميات مختلفة
- تحليل إحصائي للنتائج

##### معالجة التحويلات المتعددة / Multiple Transformations Processing:
- تطبيق عدة تحويلات هندسية
- إنشاء مجموعة من الإصدارات المختلفة
- مقارنة النتائج جنباً إلى جنب

#### 2. المعالجة المتسلسلة / Chain Processing

تطبيق العمليات بتسلسل محدد:
Apply operations in a specific sequence:

##### سلسلة المرشحات / Filter Chain:
1. تطبيق مرشح التمويه الغاوسي
2. تطبيق كشف الحواف بكاني
3. تطبيق العمليات الشكلية

##### سلسلة التحويلات / Transformation Chain:
1. دوران الصورة 45 درجة
2. تكبيرها بنسبة 1.5
3. قصها للحجم المطلوب

#### 3. المقارنة والتحليل / Comparison and Analysis

##### مقارنة النتائج / Results Comparison:
- عرض جنب إلى جنب / Side-by-side view
- حساب الاختلافات الإحصائية / Statistical differences
- تحليل جودة النتائج / Quality analysis

##### الإحصائيات المتاحة / Available Statistics:
- متوسط الشدة / Mean Intensity
- الانحراف المعياري / Standard Deviation
- الحد الأدنى والأقصى للقيم / Min/Max Values
- التوزيع الهستوجرامي / Histogram Distribution

### نصائح الاستخدام / Usage Tips

#### للحصول على أفضل النتائج / For Best Results:

1. **جودة الصور** / **Image Quality**:
   - استخدم صوراً عالية الدقة
   - تجنب الصور المضغوطة بقوة
   - تأكد من الإضاءة الجيدة

2. **اختيار المعاملات** / **Parameter Selection**:
   - ابدأ بالقيم الافتراضية
   - جرب قيماً مختلفة تدريجياً
   - احفظ الإعدادات المفضلة

3. **تسلسل العمليات** / **Operation Sequence**:
   - طبق التحسينات الأساسية أولاً
   - استخدم المرشحات قبل استخراج الميزات
   - احفظ نسخة أصلية قبل التعديلات الكبيرة

#### تحسين الأداء / Performance Optimization:

1. **حجم الصور** / **Image Size**:
   - اختصر الصور الكبيرة جداً
   - استخدم أحجاماً مناسبة للمهمة
   - تجنب المعالجة غير الضرورية

2. **استخدام الذاكرة** / **Memory Usage**:
   - أغلق المشاريع غير المستخدمة
   - امسح النتائج المؤقتة
   - راقب استخدام الموارد

### استكشاف الأخطاء / Troubleshooting

#### مشاكل شائعة / Common Issues:

**رسالة "صورة غير موجودة"** / **"Image not found" message**:
- تأكد من رفع الصورة بنجاح
- تحقق من تنسيق الملف
- أعد رفع الصورة إذا لزم الأمر

**بطء في المعالجة** / **Slow processing**:
- قلل من حجم الصورة
- استخدم معاملات أبسط
- تحقق من سرعة الإنترنت

**نتائج غير متوقعة** / **Unexpected results**:
- راجع المعاملات المستخدمة
- جرب إعدادات مختلفة
- تأكد من جودة الصورة الأصلية

### أمثلة عملية / Practical Examples

#### مثال 1: تحسين صورة فوتوغرافية / Example 1: Photo Enhancement
1. ارفع الصورة الأصلية
2. طبق مرشح التمويه الثنائي لتنعيم البشرة
3. استخدم تعديل الألوان لتحسين التباين
4. احفظ النتيجة النهائية

#### مثال 2: استخراج النص من وثيقة / Example 2: Document Text Extraction
1. ارفع صورة الوثيقة
2. طبق التحويل المنظوري لتصحيح الميل
3. استخدم كشف الحواف لتحديد النص
4. طبق العمليات الشكلية لتحسين الوضوح

#### مثال 3: تحليل صورة طبية / Example 3: Medical Image Analysis
1. ارفع الصورة الطبية
2. استخدم مرشحات التحسين لزيادة التباين
3. طبق كشف الحواف لتحديد الهياكل
4. استخرج الميزات لتحليل إضافي

### الدعم والمساعدة / Support and Help

#### موارد إضافية / Additional Resources:
- دليل API للمطورين / API Guide for Developers
- قاموس المصطلحات / Glossary of Terms
- أمثلة ونماذج كود / Code Examples and Samples
- منتدى المجتمع / Community Forum

#### الحصول على المساعدة / Getting Help:
- راجع هذا الدليل أولاً / Check this guide first
- ابحث في الأسئلة الشائعة / Search FAQ
- تواصل مع فريق الدعم / Contact support team
- شارك في المجتمع / Participate in community

---

**ملاحظة**: هذا الدليل يغطي الاستخدام الأساسي والمتقدم للمنصة. للحصول على تفاصيل تقنية أكثر، راجع دليل API أو وثائق المطور.

**Note**: This guide covers basic and advanced usage of the platform. For more technical details, refer to the API guide or developer documentation.