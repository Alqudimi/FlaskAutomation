// Computer Vision Processing Platform - Main JavaScript Application
class CVApp {
    constructor() {
        this.currentImageId = null;
        this.currentImageId2 = null;
        this.currentMatcherId = null;
        this.processingHistory = [];
        
        this.initializeEventListeners();
        this.initializeParameterHandlers();
        this.loadFilterTypes();
        this.setupToasts();
    }

    // Initialize event listeners
    initializeEventListeners() {
        // Upload area events
        this.setupUploadArea('uploadArea', 'imageInput', (imageData, imageId) => {
            this.handleImageUpload(imageData, imageId, 'originalImage');
            this.currentImageId = imageId;
            document.getElementById('matchFeaturesBtn').disabled = !this.currentImageId2;
        });

        this.setupUploadArea('uploadArea2', 'imageInput2', (imageData, imageId) => {
            this.currentImageId2 = imageId;
            document.getElementById('matchFeaturesBtn').disabled = !this.currentImageId;
        });

        // Processing buttons
        document.getElementById('extractFeaturesBtn').addEventListener('click', () => this.extractFeatures());
        document.getElementById('applyFilterBtn').addEventListener('click', () => this.applyFilter());
        document.getElementById('matchFeaturesBtn').addEventListener('click', () => this.matchFeatures());
        document.getElementById('applyTransformBtn').addEventListener('click', () => this.applyTransformation());

        // Action buttons
        document.getElementById('resetBtn').addEventListener('click', () => this.resetImage());
        document.getElementById('downloadBtn').addEventListener('click', () => this.downloadImage());

        // Parameter change handlers
        document.getElementById('featureType').addEventListener('change', () => this.updateFeatureParameters());
        document.getElementById('filterType').addEventListener('change', () => this.updateFilterParameters());
        document.getElementById('transformationType').addEventListener('change', () => this.updateTransformParameters());

        // Range input updates
        document.getElementById('ratioThreshold').addEventListener('input', (e) => {
            document.getElementById('ratioThresholdValue').textContent = e.target.value;
        });
    }

    // Setup upload area with drag and drop
    setupUploadArea(areaId, inputId, callback) {
        const area = document.getElementById(areaId);
        const input = document.getElementById(inputId);

        area.addEventListener('click', () => input.click());
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });
        area.addEventListener('dragleave', () => area.classList.remove('dragover'));
        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.uploadImage(files[0], callback);
            }
        });

        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.uploadImage(e.target.files[0], callback);
            }
        });
    }

    // Upload image to server
    async uploadImage(file, callback) {
        if (!file || !file.type.startsWith('image/')) {
            this.showError('يرجى اختيار ملف صورة صحيح');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            this.showLoading(true);
            const response = await axios.post('/api/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            if (response.data.success) {
                callback(response.data.image_data, response.data.image_id);
                this.showSuccess('تم تحميل الصورة بنجاح');
                this.addToHistory('تحميل الصورة', `الأبعاد: ${response.data.width}×${response.data.height}`);
            } else {
                this.showError(response.data.error || 'فشل في تحميل الصورة');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showError('خطأ في تحميل الصورة: ' + (error.response?.data?.error || error.message));
        } finally {
            this.showLoading(false);
        }
    }

    // Handle image upload display
    handleImageUpload(imageData, imageId, targetImageId) {
        const imgElement = document.getElementById(targetImageId);
        imgElement.src = imageData;
        imgElement.classList.add('fade-in');
    }

    // Extract features from image
    async extractFeatures() {
        if (!this.currentImageId) {
            this.showError('يرجى تحميل صورة أولاً');
            return;
        }

        const featureType = document.getElementById('featureType').value;
        const parameters = this.getFeatureParameters(featureType);

        try {
            this.showLoading(true);
            const response = await axios.post('/api/extract_features', {
                image_id: this.currentImageId,
                feature_type: featureType,
                parameters: parameters
            });

            if (response.data.success) {
                document.getElementById('processedImage').src = response.data.result_image;
                document.getElementById('processedImage').classList.add('fade-in');
                
                this.displayFeatureResults(response.data);
                this.showSuccess('تم استخراج الميزات بنجاح');
                this.addToHistory('استخراج الميزات', `النوع: ${featureType}`);
            } else {
                this.showError(response.data.error || 'فشل في استخراج الميزات');
            }
        } catch (error) {
            console.error('Feature extraction error:', error);
            this.showError('خطأ في استخراج الميزات: ' + (error.response?.data?.error || error.message));
        } finally {
            this.showLoading(false);
        }
    }

    // Apply filter to image
    async applyFilter() {
        if (!this.currentImageId) {
            this.showError('يرجى تحميل صورة أولاً');
            return;
        }

        const filterType = document.getElementById('filterType').value;
        const parameters = this.getFilterParameters(filterType);

        try {
            this.showLoading(true);
            const response = await axios.post('/api/apply_filter', {
                image_id: this.currentImageId,
                filter_type: filterType,
                parameters: parameters
            });

            if (response.data.success) {
                document.getElementById('processedImage').src = response.data.result_image;
                document.getElementById('processedImage').classList.add('fade-in');
                
                this.displayFilterResults(response.data);
                this.showSuccess('تم تطبيق المرشح بنجاح');
                this.addToHistory('تطبيق مرشح', `النوع: ${filterType}`);
            } else {
                this.showError(response.data.error || 'فشل في تطبيق المرشح');
            }
        } catch (error) {
            console.error('Filter application error:', error);
            this.showError('خطأ في تطبيق المرشح: ' + (error.response?.data?.error || error.message));
        } finally {
            this.showLoading(false);
        }
    }

    // Match features between two images
    async matchFeatures() {
        if (!this.currentImageId || !this.currentImageId2) {
            this.showError('يرجى تحميل صورتين أولاً');
            return;
        }

        const matchingMethod = document.getElementById('matchingMethod').value;
        const parameters = {
            ratio_threshold: parseFloat(document.getElementById('ratioThreshold').value)
        };

        try {
            this.showLoading(true);
            const response = await axios.post('/api/match_features', {
                image_id1: this.currentImageId,
                image_id2: this.currentImageId2,
                matching_method: matchingMethod,
                parameters: parameters
            });

            if (response.data.success) {
                document.getElementById('processedImage').src = response.data.matches_image;
                document.getElementById('processedImage').classList.add('fade-in');
                
                this.currentMatcherId = response.data.matcher_id;
                this.displayMatchingResults(response.data);
                this.showSuccess('تم مطابقة الميزات بنجاح');
                this.addToHistory('مطابقة الميزات', `الطريقة: ${matchingMethod}`);
            } else {
                this.showError(response.data.error || 'فشل في مطابقة الميزات');
            }
        } catch (error) {
            console.error('Feature matching error:', error);
            this.showError('خطأ في مطابقة الميزات: ' + (error.response?.data?.error || error.message));
        } finally {
            this.showLoading(false);
        }
    }

    // Apply geometric transformation
    async applyTransformation() {
        if (!this.currentImageId) {
            this.showError('يرجى تحميل صورة أولاً');
            return;
        }

        const transformationType = document.getElementById('transformationType').value;
        const parameters = this.getTransformParameters(transformationType);

        try {
            this.showLoading(true);
            const response = await axios.post('/api/apply_transformation', {
                image_id: this.currentImageId,
                transformation_type: transformationType,
                parameters: parameters
            });

            if (response.data.success) {
                document.getElementById('processedImage').src = response.data.result_image;
                document.getElementById('processedImage').classList.add('fade-in');
                
                this.displayTransformResults(response.data);
                this.showSuccess('تم تطبيق التحويل بنجاح');
                this.addToHistory('تحويل هندسي', `النوع: ${transformationType}`);
            } else {
                this.showError(response.data.error || 'فشل في تطبيق التحويل');
            }
        } catch (error) {
            console.error('Transformation error:', error);
            this.showError('خطأ في تطبيق التحويل: ' + (error.response?.data?.error || error.message));
        } finally {
            this.showLoading(false);
        }
    }

    // Get feature parameters based on type
    getFeatureParameters(featureType) {
        const parameters = {};
        
        switch (featureType) {
            case 'fast_corners':
                parameters.threshold = parseInt(document.getElementById('fast_threshold')?.value || 10);
                parameters.nonmax_suppression = document.getElementById('fast_nonmax')?.checked || true;
                break;
            case 'hog':
                parameters.nbins = parseInt(document.getElementById('hog_nbins')?.value || 9);
                parameters.win_sigma = parseFloat(document.getElementById('hog_win_sigma')?.value || 4.0);
                break;
            case 'log_dog_blob':
                parameters.min_threshold = parseFloat(document.getElementById('blob_min_threshold')?.value || 10.0);
                parameters.max_threshold = parseFloat(document.getElementById('blob_max_threshold')?.value || 200.0);
                parameters.min_area = parseFloat(document.getElementById('blob_min_area')?.value || 100.0);
                break;
            case 'orb':
                parameters.n_features = parseInt(document.getElementById('orb_features')?.value || 500);
                parameters.scale_factor = parseFloat(document.getElementById('orb_scale')?.value || 1.2);
                break;
            case 'sift':
                parameters.n_features = parseInt(document.getElementById('sift_features')?.value || 0);
                parameters.contrast_threshold = parseFloat(document.getElementById('sift_contrast')?.value || 0.04);
                break;
        }
        
        return parameters;
    }

    // Get filter parameters based on type
    getFilterParameters(filterType) {
        const parameters = {};
        
        switch (filterType) {
            case 'gaussian_blur':
                parameters.ksize = parseInt(document.getElementById('gaussian_ksize')?.value || 5);
                parameters.sigma = parseFloat(document.getElementById('gaussian_sigma')?.value || 0);
                break;
            case 'median_blur':
                parameters.ksize = parseInt(document.getElementById('median_ksize')?.value || 5);
                break;
            case 'bilateral_filter':
                parameters.d = parseInt(document.getElementById('bilateral_d')?.value || 9);
                parameters.sigma_color = parseFloat(document.getElementById('bilateral_sigma_color')?.value || 75);
                parameters.sigma_space = parseFloat(document.getElementById('bilateral_sigma_space')?.value || 75);
                break;
            case 'canny':
                parameters.threshold1 = parseFloat(document.getElementById('canny_threshold1')?.value || 100);
                parameters.threshold2 = parseFloat(document.getElementById('canny_threshold2')?.value || 200);
                break;
            case 'gamma_correction':
                parameters.gamma = parseFloat(document.getElementById('gamma_value')?.value || 1.0);
                break;
            case 'threshold':
                parameters.thresh = parseFloat(document.getElementById('threshold_value')?.value || 127);
                parameters.maxval = parseFloat(document.getElementById('threshold_maxval')?.value || 255);
                break;
        }
        
        return parameters;
    }

    // Get transformation parameters based on type
    getTransformParameters(transformationType) {
        const parameters = {};
        
        switch (transformationType) {
            case 'translation':
                parameters.tx = parseInt(document.getElementById('translate_tx')?.value || 0);
                parameters.ty = parseInt(document.getElementById('translate_ty')?.value || 0);
                break;
            case 'rotation':
                parameters.angle = parseFloat(document.getElementById('rotate_angle')?.value || 0);
                parameters.scale = parseFloat(document.getElementById('rotate_scale')?.value || 1.0);
                break;
            case 'scaling':
                parameters.fx = parseFloat(document.getElementById('scale_fx')?.value || 1.0);
                parameters.fy = parseFloat(document.getElementById('scale_fy')?.value || 1.0);
                break;
            case 'flip':
                parameters.flip_code = parseInt(document.getElementById('flip_code')?.value || 1);
                break;
            case 'resize':
                parameters.width = parseInt(document.getElementById('resize_width')?.value || 800);
                parameters.height = parseInt(document.getElementById('resize_height')?.value || 600);
                break;
            case 'color_adjustment':
                parameters.channel = document.getElementById('color_channel')?.value || 'ALL';
                parameters.value = parseInt(document.getElementById('color_value')?.value || 0);
                break;
        }
        
        return parameters;
    }

    // Initialize parameter handlers
    initializeParameterHandlers() {
        // Update parameters when feature type changes
        this.updateFeatureParameters();
        this.updateFilterParameters();
        this.updateTransformParameters();
    }

    // Update feature parameters UI
    updateFeatureParameters() {
        const featureType = document.getElementById('featureType').value;
        const container = document.getElementById('featureParameters');
        
        let html = '';
        
        switch (featureType) {
            case 'fast_corners':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">العتبة</label>
                        <input type="range" class="form-range" id="fast_threshold" min="1" max="50" value="10">
                        <small class="parameter-value">القيمة: <span id="fast_threshold_val">10</span></small>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="fast_nonmax" checked>
                        <label class="form-check-label">قمع غير الحد الأقصى</label>
                    </div>`;
                break;
            case 'hog':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">عدد الصناديق</label>
                        <input type="range" class="form-range" id="hog_nbins" min="6" max="18" value="9">
                        <small class="parameter-value">القيمة: <span id="hog_nbins_val">9</span></small>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">Win Sigma</label>
                        <input type="range" class="form-range" id="hog_win_sigma" min="1" max="10" step="0.1" value="4.0">
                        <small class="parameter-value">القيمة: <span id="hog_win_sigma_val">4.0</span></small>
                    </div>`;
                break;
            case 'log_dog_blob':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">الحد الأدنى للعتبة</label>
                        <input type="range" class="form-range" id="blob_min_threshold" min="1" max="50" value="10">
                        <small class="parameter-value">القيمة: <span id="blob_min_threshold_val">10</span></small>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">الحد الأقصى للعتبة</label>
                        <input type="range" class="form-range" id="blob_max_threshold" min="100" max="300" value="200">
                        <small class="parameter-value">القيمة: <span id="blob_max_threshold_val">200</span></small>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">أقل مساحة</label>
                        <input type="range" class="form-range" id="blob_min_area" min="50" max="500" value="100">
                        <small class="parameter-value">القيمة: <span id="blob_min_area_val">100</span></small>
                    </div>`;
                break;
            case 'orb':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">عدد الميزات</label>
                        <input type="range" class="form-range" id="orb_features" min="100" max="2000" value="500">
                        <small class="parameter-value">القيمة: <span id="orb_features_val">500</span></small>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">عامل المقياس</label>
                        <input type="range" class="form-range" id="orb_scale" min="1.1" max="2.0" step="0.1" value="1.2">
                        <small class="parameter-value">القيمة: <span id="orb_scale_val">1.2</span></small>
                    </div>`;
                break;
            case 'sift':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">عدد الميزات (0 = جميع)</label>
                        <input type="range" class="form-range" id="sift_features" min="0" max="2000" value="0">
                        <small class="parameter-value">القيمة: <span id="sift_features_val">0</span></small>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">عتبة التباين</label>
                        <input type="range" class="form-range" id="sift_contrast" min="0.01" max="0.1" step="0.01" value="0.04">
                        <small class="parameter-value">القيمة: <span id="sift_contrast_val">0.04</span></small>
                    </div>`;
                break;
        }
        
        container.innerHTML = html;
        
        // Add event listeners for range inputs
        container.querySelectorAll('input[type="range"]').forEach(input => {
            const updateValue = () => {
                const valueSpan = document.getElementById(input.id + '_val');
                if (valueSpan) valueSpan.textContent = input.value;
            };
            
            input.addEventListener('input', updateValue);
            updateValue(); // Set initial value
        });
    }

    // Update filter parameters UI
    updateFilterParameters() {
        const filterType = document.getElementById('filterType').value;
        const container = document.getElementById('filterParameters');
        
        let html = '';
        
        switch (filterType) {
            case 'gaussian_blur':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">حجم النواة</label>
                        <select class="form-select" id="gaussian_ksize">
                            <option value="3">3</option>
                            <option value="5" selected>5</option>
                            <option value="7">7</option>
                            <option value="9">9</option>
                            <option value="11">11</option>
                        </select>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">سيجما</label>
                        <input type="range" class="form-range" id="gaussian_sigma" min="0" max="5" step="0.1" value="0">
                        <small class="parameter-value">القيمة: <span id="gaussian_sigma_val">0</span></small>
                    </div>`;
                break;
            case 'median_blur':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">حجم النواة</label>
                        <select class="form-select" id="median_ksize">
                            <option value="3">3</option>
                            <option value="5" selected>5</option>
                            <option value="7">7</option>
                            <option value="9">9</option>
                        </select>
                    </div>`;
                break;
            case 'bilateral_filter':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">قطر الجوار</label>
                        <input type="range" class="form-range" id="bilateral_d" min="5" max="15" value="9">
                        <small class="parameter-value">القيمة: <span id="bilateral_d_val">9</span></small>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">سيجما اللون</label>
                        <input type="range" class="form-range" id="bilateral_sigma_color" min="25" max="150" value="75">
                        <small class="parameter-value">القيمة: <span id="bilateral_sigma_color_val">75</span></small>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">سيجما المساحة</label>
                        <input type="range" class="form-range" id="bilateral_sigma_space" min="25" max="150" value="75">
                        <small class="parameter-value">القيمة: <span id="bilateral_sigma_space_val">75</span></small>
                    </div>`;
                break;
            case 'canny':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">العتبة الأولى</label>
                        <input type="range" class="form-range" id="canny_threshold1" min="50" max="200" value="100">
                        <small class="parameter-value">القيمة: <span id="canny_threshold1_val">100</span></small>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">العتبة الثانية</label>
                        <input type="range" class="form-range" id="canny_threshold2" min="150" max="300" value="200">
                        <small class="parameter-value">القيمة: <span id="canny_threshold2_val">200</span></small>
                    </div>`;
                break;
            case 'gamma_correction':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">قيمة جاما</label>
                        <input type="range" class="form-range" id="gamma_value" min="0.1" max="3.0" step="0.1" value="1.0">
                        <small class="parameter-value">القيمة: <span id="gamma_value_val">1.0</span></small>
                    </div>`;
                break;
            case 'threshold':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">قيمة العتبة</label>
                        <input type="range" class="form-range" id="threshold_value" min="0" max="255" value="127">
                        <small class="parameter-value">القيمة: <span id="threshold_value_val">127</span></small>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">القيمة القصوى</label>
                        <input type="range" class="form-range" id="threshold_maxval" min="0" max="255" value="255">
                        <small class="parameter-value">القيمة: <span id="threshold_maxval_val">255</span></small>
                    </div>`;
                break;
            default:
                html = '<p class="text-muted">لا توجد معلمات إضافية لهذا المرشح</p>';
        }
        
        container.innerHTML = html;
        
        // Add event listeners for range inputs
        container.querySelectorAll('input[type="range"]').forEach(input => {
            const updateValue = () => {
                const valueSpan = document.getElementById(input.id + '_val');
                if (valueSpan) valueSpan.textContent = input.value;
            };
            
            input.addEventListener('input', updateValue);
            updateValue(); // Set initial value
        });
    }

    // Update transformation parameters UI
    updateTransformParameters() {
        const transformationType = document.getElementById('transformationType').value;
        const container = document.getElementById('transformParameters');
        
        let html = '';
        
        switch (transformationType) {
            case 'translation':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">الإزاحة الأفقية (tx)</label>
                        <input type="range" class="form-range" id="translate_tx" min="-200" max="200" value="0">
                        <small class="parameter-value">القيمة: <span id="translate_tx_val">0</span></small>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">الإزاحة العمودية (ty)</label>
                        <input type="range" class="form-range" id="translate_ty" min="-200" max="200" value="0">
                        <small class="parameter-value">القيمة: <span id="translate_ty_val">0</span></small>
                    </div>`;
                break;
            case 'rotation':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">زاوية التدوير (درجة)</label>
                        <input type="range" class="form-range" id="rotate_angle" min="-180" max="180" value="0">
                        <small class="parameter-value">القيمة: <span id="rotate_angle_val">0</span></small>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">عامل المقياس</label>
                        <input type="range" class="form-range" id="rotate_scale" min="0.1" max="2.0" step="0.1" value="1.0">
                        <small class="parameter-value">القيمة: <span id="rotate_scale_val">1.0</span></small>
                    </div>`;
                break;
            case 'scaling':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">عامل التحجيم الأفقي</label>
                        <input type="range" class="form-range" id="scale_fx" min="0.1" max="3.0" step="0.1" value="1.0">
                        <small class="parameter-value">القيمة: <span id="scale_fx_val">1.0</span></small>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">عامل التحجيم العمودي</label>
                        <input type="range" class="form-range" id="scale_fy" min="0.1" max="3.0" step="0.1" value="1.0">
                        <small class="parameter-value">القيمة: <span id="scale_fy_val">1.0</span></small>
                    </div>`;
                break;
            case 'flip':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">نوع القلب</label>
                        <select class="form-select" id="flip_code">
                            <option value="1">أفقي</option>
                            <option value="0">عمودي</option>
                            <option value="-1">أفقي وعمودي</option>
                        </select>
                    </div>`;
                break;
            case 'resize':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">العرض الجديد</label>
                        <input type="number" class="form-control" id="resize_width" value="800" min="50" max="2000">
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">الارتفاع الجديد</label>
                        <input type="number" class="form-control" id="resize_height" value="600" min="50" max="2000">
                    </div>`;
                break;
            case 'color_adjustment':
                html = `
                    <div class="parameter-group">
                        <label class="form-label">القناة اللونية</label>
                        <select class="form-select" id="color_channel">
                            <option value="ALL">جميع القنوات</option>
                            <option value="RED">الأحمر</option>
                            <option value="GREEN">الأخضر</option>
                            <option value="BLUE">الأزرق</option>
                        </select>
                    </div>
                    <div class="parameter-group">
                        <label class="form-label">قيمة التعديل</label>
                        <input type="range" class="form-range" id="color_value" min="-100" max="100" value="0">
                        <small class="parameter-value">القيمة: <span id="color_value_val">0</span></small>
                    </div>`;
                break;
        }
        
        container.innerHTML = html;
        
        // Add event listeners for range inputs
        container.querySelectorAll('input[type="range"]').forEach(input => {
            const updateValue = () => {
                const valueSpan = document.getElementById(input.id + '_val');
                if (valueSpan) valueSpan.textContent = input.value;
            };
            
            input.addEventListener('input', updateValue);
            updateValue(); // Set initial value
        });
    }

    // Display feature extraction results
    displayFeatureResults(data) {
        const statsContainer = document.getElementById('processingStats');
        const paramsContainer = document.getElementById('parametersUsed');
        
        let statsHtml = '<h6 class="text-primary">إحصاءات استخراج الميزات</h6>';
        if (data.features) {
            Object.entries(data.features).forEach(([key, value]) => {
                statsHtml += `
                    <div class="stat-item">
                        <span class="stat-label">${this.translateKey(key)}</span>
                        <span class="stat-value">${value}</span>
                    </div>`;
            });
        }
        
        let paramsHtml = '<h6 class="text-primary">المعلمات المستخدمة</h6>';
        if (data.metadata && data.metadata.parameters) {
            Object.entries(data.metadata.parameters).forEach(([key, value]) => {
                if (key !== 'self') {
                    paramsHtml += `
                        <div class="stat-item">
                            <span class="stat-label">${this.translateKey(key)}</span>
                            <span class="stat-value">${value}</span>
                        </div>`;
                }
            });
        }
        
        statsContainer.innerHTML = statsHtml;
        paramsContainer.innerHTML = paramsHtml;
    }

    // Display filter results
    displayFilterResults(data) {
        const statsContainer = document.getElementById('processingStats');
        const paramsContainer = document.getElementById('parametersUsed');
        
        let statsHtml = '<h6 class="text-primary">إحصاءات المرشح</h6>';
        statsHtml += `<div class="stat-item">
            <span class="stat-label">عدد العمليات المطبقة</span>
            <span class="stat-value">${data.history ? data.history.length : 0}</span>
        </div>`;
        
        let paramsHtml = '<h6 class="text-primary">سجل المرشحات</h6>';
        if (data.history && data.history.length > 0) {
            data.history.forEach((item, index) => {
                paramsHtml += `<div class="stat-item">
                    <span class="stat-label">المرشح ${index + 1}</span>
                    <span class="stat-value">${item[0]}</span>
                </div>`;
            });
        }
        
        statsContainer.innerHTML = statsHtml;
        paramsContainer.innerHTML = paramsHtml;
    }

    // Display matching results
    displayMatchingResults(data) {
        const statsContainer = document.getElementById('processingStats');
        const paramsContainer = document.getElementById('parametersUsed');
        
        let statsHtml = '<h6 class="text-primary">إحصاءات المطابقة</h6>';
        if (data.statistics) {
            Object.entries(data.statistics).forEach(([key, value]) => {
                statsHtml += `
                    <div class="stat-item">
                        <span class="stat-label">${this.translateKey(key)}</span>
                        <span class="stat-value">${typeof value === 'number' ? value.toFixed(2) : value}</span>
                    </div>`;
            });
        }
        
        let paramsHtml = '<h6 class="text-primary">معلومات المطابقة</h6>';
        paramsHtml += `
            <div class="stat-item">
                <span class="stat-label">معرف المطابقة</span>
                <span class="stat-value">${data.matcher_id}</span>
            </div>`;
        
        statsContainer.innerHTML = statsHtml;
        paramsContainer.innerHTML = paramsHtml;
    }

    // Display transformation results
    displayTransformResults(data) {
        const statsContainer = document.getElementById('processingStats');
        const paramsContainer = document.getElementById('parametersUsed');
        
        let statsHtml = '<h6 class="text-primary">إحصاءات التحويل</h6>';
        statsHtml += `<div class="stat-item">
            <span class="stat-label">عدد التحويلات المطبقة</span>
            <span class="stat-value">${data.history ? data.history.length : 0}</span>
        </div>`;
        
        let paramsHtml = '<h6 class="text-primary">سجل التحويلات</h6>';
        if (data.history && data.history.length > 0) {
            data.history.forEach((item, index) => {
                paramsHtml += `<div class="stat-item">
                    <span class="stat-label">التحويل ${index + 1}</span>
                    <span class="stat-value">${this.translateKey(item.type)}</span>
                </div>`;
            });
        }
        
        statsContainer.innerHTML = statsHtml;
        paramsContainer.innerHTML = paramsHtml;
    }

    // Reset image to original state
    async resetImage() {
        if (!this.currentImageId) {
            this.showError('لا توجد صورة للإعادة تعيين');
            return;
        }

        try {
            const response = await axios.post('/api/reset_image', {
                image_id: this.currentImageId,
                processor_type: 'all'
            });

            if (response.data.success) {
                document.getElementById('processedImage').src = response.data.image_data;
                document.getElementById('originalImage').src = response.data.image_data;
                
                // Clear results display
                document.getElementById('processingStats').innerHTML = '<p class="text-muted">لا توجد إحصاءات متاحة</p>';
                document.getElementById('parametersUsed').innerHTML = '<p class="text-muted">لا توجد معلمات متاحة</p>';
                
                this.showSuccess('تم إعادة تعيين الصورة بنجاح');
                this.addToHistory('إعادة تعيين', 'إعادة الصورة للحالة الأصلية');
            } else {
                this.showError(response.data.error || 'فشل في إعادة التعيين');
            }
        } catch (error) {
            console.error('Reset error:', error);
            this.showError('خطأ في إعادة التعيين: ' + (error.response?.data?.error || error.message));
        }
    }

    // Download processed image
    async downloadImage() {
        if (!this.currentImageId) {
            this.showError('لا توجد صورة للتحميل');
            return;
        }

        try {
            const response = await axios.post('/api/download_image', {
                image_id: this.currentImageId,
                processor_type: 'filter'
            });

            if (response.data.success) {
                // Create download link
                const link = document.createElement('a');
                link.href = response.data.image_data;
                link.download = response.data.filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                this.showSuccess('تم تحميل الصورة بنجاح');
            } else {
                this.showError(response.data.error || 'فشل في تحميل الصورة');
            }
        } catch (error) {
            console.error('Download error:', error);
            this.showError('خطأ في التحميل: ' + (error.response?.data?.error || error.message));
        }
    }

    // Load filter types from API
    async loadFilterTypes() {
        try {
            const response = await axios.get('/api/get_filter_types');
            // Filter types are already set in HTML, this could be used for dynamic loading
        } catch (error) {
            console.error('Error loading filter types:', error);
        }
    }

    // Setup toast notifications
    setupToasts() {
        this.successToast = new bootstrap.Toast(document.getElementById('successToast'));
        this.errorToast = new bootstrap.Toast(document.getElementById('errorToast'));
    }

    // Show success message
    showSuccess(message) {
        document.getElementById('successMessage').textContent = message;
        this.successToast.show();
    }

    // Show error message
    showError(message) {
        document.getElementById('errorMessage').textContent = message;
        this.errorToast.show();
    }

    // Show/hide loading spinner
    showLoading(show) {
        const spinner = document.getElementById('loadingSpinner');
        const processedImage = document.getElementById('processedImage');
        
        if (show) {
            spinner.classList.remove('d-none');
            processedImage.classList.add('processing');
        } else {
            spinner.classList.add('d-none');
            processedImage.classList.remove('processing');
        }
    }

    // Add operation to history
    addToHistory(operation, details) {
        const historyContainer = document.getElementById('processingHistory');
        const timestamp = new Date().toLocaleTimeString('ar-SA');
        
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item slide-in';
        historyItem.innerHTML = `
            <div class="operation">${operation}</div>
            <div class="details">${details}</div>
            <div class="timestamp">${timestamp}</div>
        `;
        
        // Add to beginning of history
        if (historyContainer.children.length === 1 && historyContainer.children[0].tagName === 'P') {
            historyContainer.innerHTML = '';
        }
        
        historyContainer.insertBefore(historyItem, historyContainer.firstChild);
        
        // Keep only last 10 items
        while (historyContainer.children.length > 10) {
            historyContainer.removeChild(historyContainer.lastChild);
        }
        
        this.processingHistory.unshift({ operation, details, timestamp });
        if (this.processingHistory.length > 10) {
            this.processingHistory = this.processingHistory.slice(0, 10);
        }
    }

    // Translate keys for display
    translateKey(key) {
        const translations = {
            'keypoints_count': 'عدد النقاط المميزة',
            'corners_detected': 'الزوايا المكتشفة',
            'feature_vector_length': 'طول متجه الميزات',
            'descriptor_shape': 'شكل الواصف',
            'blobs_count': 'عدد البقع',
            'descriptors_shape': 'شكل الواصفات',
            'total_matches': 'إجمالي المطابقات',
            'min_distance': 'أقل مسافة',
            'max_distance': 'أكبر مسافة',
            'avg_distance': 'متوسط المسافة',
            'matching_method': 'طريقة المطابقة',
            'keypoints_image1': 'نقاط الصورة الأولى',
            'keypoints_image2': 'نقاط الصورة الثانية',
            'threshold': 'العتبة',
            'nonmax_suppression': 'قمع غير الحد الأقصى',
            'nbins': 'عدد الصناديق',
            'win_sigma': 'سيجما النافذة',
            'n_features': 'عدد الميزات',
            'scale_factor': 'عامل المقياس',
            'contrast_threshold': 'عتبة التباين',
            'ksize': 'حجم النواة',
            'sigma': 'سيجما',
            'tx': 'الإزاحة الأفقية',
            'ty': 'الإزاحة العمودية',
            'angle': 'الزاوية',
            'fx': 'عامل التحجيم الأفقي',
            'fy': 'عامل التحجيم العمودي'
        };
        
        return translations[key] || key;
    }

    // ===== Batch Processing Functions =====

    initializeBatchProcessing() {
        this.tasks = [];
        this.taskCounter = 0;
        
        // Event listeners for batch processing
        document.getElementById('batchOperationType').addEventListener('change', () => this.updateTaskBuilder());
        document.getElementById('addTaskBtn').addEventListener('click', () => this.addNewTask());
        document.getElementById('processBatchBtn').addEventListener('click', () => this.processBatch());
        document.getElementById('clearTasksBtn').addEventListener('click', () => this.clearAllTasks());
        
        this.updateTaskBuilder();
    }

    updateTaskBuilder() {
        const operationType = document.getElementById('batchOperationType').value;
        const taskList = document.getElementById('taskList');
        
        // Clear existing tasks when changing operation type
        this.clearAllTasks();
        
        // Update task builder based on operation type
        switch(operationType) {
            case 'multiple_features':
            case 'multiple_filters':
            case 'multiple_transformations':
                document.getElementById('addTaskBtn').style.display = 'block';
                break;
            case 'filter_chain':
            case 'transformation_chain':
                document.getElementById('addTaskBtn').style.display = 'block';
                break;
            case 'mixed_operations':
                document.getElementById('addTaskBtn').style.display = 'block';
                break;
        }
    }

    addNewTask() {
        const operationType = document.getElementById('batchOperationType').value;
        const taskId = `task_${this.taskCounter++}`;
        
        let taskData = {};
        
        switch(operationType) {
            case 'multiple_features':
                taskData = this.createFeatureTask(taskId);
                break;
            case 'multiple_filters':
                taskData = this.createFilterTask(taskId);
                break;
            case 'multiple_transformations':
                taskData = this.createTransformationTask(taskId);
                break;
            case 'filter_chain':
                taskData = this.createFilterTask(taskId);
                break;
            case 'transformation_chain':
                taskData = this.createTransformationTask(taskId);
                break;
            case 'mixed_operations':
                taskData = this.createMixedTask(taskId);
                break;
        }
        
        this.tasks.push(taskData);
        this.renderTaskList();
    }

    createFeatureTask(taskId) {
        return {
            task_id: taskId,
            feature_type: 'sift',
            parameters: {},
            type: 'feature'
        };
    }

    createFilterTask(taskId) {
        return {
            task_id: taskId,
            filter_type: 'gaussian_blur',
            parameters: { ksize: 5 },
            type: 'filter'
        };
    }

    createTransformationTask(taskId) {
        return {
            task_id: taskId,
            transformation_type: 'rotation',
            parameters: { angle: 45 },
            type: 'transformation'
        };
    }

    createMixedTask(taskId) {
        return {
            task_id: taskId,
            operation_type: 'feature_extraction',
            feature_type: 'sift',
            parameters: {},
            type: 'mixed'
        };
    }

    renderTaskList() {
        const taskList = document.getElementById('taskList');
        
        if (this.tasks.length === 0) {
            taskList.innerHTML = '<p class="text-muted small">لا توجد مهام مضافة</p>';
            return;
        }
        
        taskList.innerHTML = this.tasks.map((task, index) => `
            <div class="task-item border rounded p-2 mb-2">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${this.getTaskDisplayName(task)}</strong>
                        <small class="text-muted d-block">${this.getTaskParametersText(task)}</small>
                    </div>
                    <div>
                        <button class="btn btn-outline-primary btn-sm me-1" onclick="cvApp.editTask(${index})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="cvApp.removeTask(${index})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    getTaskDisplayName(task) {
        const operationType = document.getElementById('batchOperationType').value;
        
        switch(operationType) {
            case 'multiple_features':
                return `استخراج ${this.getArabicFeatureName(task.feature_type)}`;
            case 'multiple_filters':
                return `مرشح ${this.getArabicFilterName(task.filter_type)}`;
            case 'multiple_transformations':
                return `تحويل ${this.getArabicTransformName(task.transformation_type)}`;
            case 'filter_chain':
                return `مرشح ${this.getArabicFilterName(task.filter_type)}`;
            case 'transformation_chain':
                return `تحويل ${this.getArabicTransformName(task.transformation_type)}`;
            case 'mixed_operations':
                return `عملية ${task.operation_type}`;
            default:
                return 'مهمة';
        }
    }

    getArabicFeatureName(type) {
        const names = {
            'fast_corners': 'زوايا FAST',
            'hog': 'HOG',
            'log_dog_blob': 'LoG/DoG Blob',
            'orb': 'ORB',
            'sift': 'SIFT'
        };
        return names[type] || type;
    }

    getArabicFilterName(type) {
        const names = {
            'gaussian_blur': 'تمويه غاوسي',
            'median_blur': 'تمويه متوسط',
            'bilateral_filter': 'مرشح ثنائي',
            'sobel': 'سوبل',
            'canny': 'كاني',
            'laplacian': 'لابلاسيان'
        };
        return names[type] || type;
    }

    getArabicTransformName(type) {
        const names = {
            'translation': 'إزاحة',
            'rotation': 'دوران',
            'scaling': 'تحجيم',
            'flip': 'قلب',
            'crop': 'قص',
            'resize': 'تغيير الحجم'
        };
        return names[type] || type;
    }

    getTaskParametersText(task) {
        const params = Object.entries(task.parameters)
            .map(([key, value]) => `${key}: ${value}`)
            .join(', ');
        return params || 'بدون معلمات';
    }

    editTask(index) {
        // Simple prompt-based editing for now
        const task = this.tasks[index];
        const operationType = document.getElementById('batchOperationType').value;
        
        if (operationType.includes('features')) {
            const newType = prompt('نوع الميزة الجديد:', task.feature_type);
            if (newType) task.feature_type = newType;
        } else if (operationType.includes('filters')) {
            const newType = prompt('نوع المرشح الجديد:', task.filter_type);
            if (newType) task.filter_type = newType;
        } else if (operationType.includes('transformations')) {
            const newType = prompt('نوع التحويل الجديد:', task.transformation_type);
            if (newType) task.transformation_type = newType;
        }
        
        this.renderTaskList();
    }

    removeTask(index) {
        this.tasks.splice(index, 1);
        this.renderTaskList();
    }

    clearAllTasks() {
        this.tasks = [];
        this.renderTaskList();
    }

    async processBatch() {
        if (!this.currentImageId) {
            this.showError('يرجى تحميل صورة أولاً');
            return;
        }

        if (this.tasks.length === 0) {
            this.showError('يرجى إضافة مهام للمعالجة');
            return;
        }

        const operationType = document.getElementById('batchOperationType').value;
        const applyToCurrent = document.getElementById('applyToImage').value === 'current';
        
        try {
            this.showBatchProgress(true);
            this.showLoading(true);
            
            let endpoint = '';
            let requestData = {
                image_id: this.currentImageId,
                apply_to_current: applyToCurrent
            };

            switch(operationType) {
                case 'multiple_features':
                    endpoint = '/api/process_multiple_features';
                    requestData.feature_tasks = this.tasks;
                    break;
                case 'multiple_filters':
                    endpoint = '/api/process_multiple_filters';
                    requestData.filter_tasks = this.tasks;
                    break;
                case 'multiple_transformations':
                    endpoint = '/api/process_multiple_transformations';
                    requestData.transform_tasks = this.tasks;
                    break;
                case 'filter_chain':
                    endpoint = '/api/process_filter_chain';
                    requestData.filter_chain = this.tasks;
                    break;
                case 'transformation_chain':
                    endpoint = '/api/process_transformation_chain';
                    requestData.transform_chain = this.tasks;
                    break;
                case 'mixed_operations':
                    endpoint = '/api/process_mixed_operations';
                    requestData.operations = this.tasks;
                    break;
            }

            const response = await axios.post(endpoint, requestData);
            
            if (response.data.success) {
                this.displayBatchResults(response.data, operationType);
                this.showSuccess('تمت المعالجة المتعددة بنجاح');
                this.addToHistory('معالجة متعددة', `${operationType}: ${this.tasks.length} مهام`);
            } else {
                this.showError(response.data.error || 'فشلت المعالجة المتعددة');
            }
            
        } catch (error) {
            console.error('Batch processing error:', error);
            this.showError('خطأ في المعالجة المتعددة: ' + (error.response?.data?.error || error.message));
        } finally {
            this.showLoading(false);
            this.showBatchProgress(false);
        }
    }

    displayBatchResults(data, operationType) {
        const multipleResultsCard = document.getElementById('multipleResultsCard');
        const multipleResultsGrid = document.getElementById('multipleResultsGrid');
        const comparisonStats = document.getElementById('comparisonStats');
        
        multipleResultsCard.classList.remove('d-none');
        
        if (operationType.includes('chain')) {
            // Single result for chain operations
            multipleResultsGrid.innerHTML = `
                <div class="col-12">
                    <div class="text-center">
                        <h6>النتيجة النهائية</h6>
                        <img src="data:image/png;base64,${data.result_image}" class="img-fluid rounded" style="max-height: 300px;">
                        <p class="text-muted mt-2">تم تطبيق ${data.chain_length} عمليات</p>
                    </div>
                </div>
            `;
        } else {
            // Multiple results display
            const results = data.results || {};
            const resultKeys = Object.keys(results);
            
            multipleResultsGrid.innerHTML = resultKeys.map(taskId => {
                const result = results[taskId];
                if (!result) return '';
                
                const imageData = result.result_image || result;
                return `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card">
                            <div class="card-body text-center">
                                <h6 class="card-title">${taskId}</h6>
                                <img src="data:image/png;base64,${imageData}" class="img-fluid rounded mb-2" style="max-height: 200px;">
                                ${this.generateResultInfo(result, operationType)}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        // Display comparison statistics
        if (data.comparison) {
            comparisonStats.innerHTML = this.generateComparisonDisplay(data.comparison, operationType);
        }
        
        // Update processing stats
        this.updateProcessingStats({
            'عدد المهام': data.total_tasks || data.total_operations || Object.keys(data.results || {}).length,
            'وقت المعالجة': data.processing_time ? `${data.processing_time.toFixed(2)} ثانية` : 'غير متاح',
            'نوع العملية': operationType
        });
    }

    generateResultInfo(result, operationType) {
        if (typeof result === 'string') return '';
        
        if (operationType.includes('features') && result.keypoints) {
            return `<small class="text-muted">النقاط: ${result.keypoints.length}</small>`;
        } else if (operationType.includes('filters') || operationType.includes('transformations')) {
            return '<small class="text-muted">تم التطبيق بنجاح</small>';
        }
        return '';
    }

    generateComparisonDisplay(comparison, operationType) {
        let html = '<h6 class="text-primary">مقارنة النتائج</h6>';
        
        if (operationType.includes('features') && comparison.summary) {
            html += `
                <div class="row">
                    <div class="col-md-3">
                        <div class="text-center">
                            <strong>${comparison.summary.max_keypoints}</strong>
                            <small class="d-block text-muted">أكبر عدد نقاط</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <strong>${comparison.summary.min_keypoints}</strong>
                            <small class="d-block text-muted">أقل عدد نقاط</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <strong>${Math.round(comparison.summary.avg_keypoints)}</strong>
                            <small class="d-block text-muted">متوسط النقاط</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <strong>${comparison.summary.best_method}</strong>
                            <small class="d-block text-muted">أفضل طريقة</small>
                        </div>
                    </div>
                </div>
            `;
        } else {
            html += `
                <div class="text-center">
                    <strong>${comparison.total_methods || comparison.total_filters || comparison.total_transformations}</strong>
                    <small class="d-block text-muted">إجمالي العمليات</small>
                </div>
            `;
        }
        
        return html;
    }

    showBatchProgress(show) {
        const progressDiv = document.getElementById('batchProgress');
        if (show) {
            progressDiv.classList.remove('d-none');
            this.updateBatchProgress(0, 'بدء المعالجة...');
        } else {
            progressDiv.classList.add('d-none');
        }
    }

    updateBatchProgress(percentage, text) {
        const progressBar = document.querySelector('#batchProgress .progress-bar');
        const progressText = document.getElementById('batchProgressText');
        
        progressBar.style.width = `${percentage}%`;
        progressText.textContent = text;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cvApp = new CVApp();
    window.cvApp.initializeBatchProcessing();
});
