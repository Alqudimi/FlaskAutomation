import cv2
import numpy as np
from typing import List, Dict, Any, Union, Optional, Tuple
from enum import Enum
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .feature_extraction import AdvancedFeatureExtractor, FeatureType, FeatureResult
from .image_filters import AdvancedImageProcessor, FilterType
from .geometric_transforms import GeometricTransformation, GeometricTransformationType
from .feature_matching import FeatureMatching, MatchingMethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessingType(Enum):
    FEATURE_EXTRACTION = "feature_extraction"
    IMAGE_FILTERING = "image_filtering"
    GEOMETRIC_TRANSFORMATION = "geometric_transformation"
    FEATURE_MATCHING = "feature_matching"

@dataclass
class ProcessingTask:
    """مهمة معالجة واحدة"""
    task_id: str
    processing_type: ProcessingType
    operation_type: str
    parameters: Dict[str, Any]
    priority: int = 1

@dataclass
class BatchResult:
    """نتيجة معالجة مجموعة من المهام"""
    task_id: str
    success: bool
    result_data: Any
    processing_time: float
    error_message: Optional[str] = None

class BatchProcessor:
    """معالج العمليات المتعددة"""
    
    def __init__(self, image: np.ndarray, max_workers: int = 4):
        """
        تهيئة معالج العمليات المتعددة
        
        Parameters:
        -----------
        image : np.ndarray
            الصورة الأساسية للمعالجة
        max_workers : int
            عدد الخيوط للمعالجة المتوازية
        """
        self.original_image = image.copy()
        self.current_image = image.copy()
        self.max_workers = max_workers
        self.processing_history = []
        self.batch_results = {}
        
        # إنشاء معالجات للأنواع المختلفة
        self.feature_extractor = AdvancedFeatureExtractor(image)
        self.image_processor = AdvancedImageProcessor(image)
        self.geometric_transformer = GeometricTransformation(image)
        
    def process_multiple_features(self, feature_tasks: List[Dict[str, Any]]) -> Dict[str, FeatureResult]:
        """
        استخراج عدة أنواع من الميزات بالتوازي
        
        Parameters:
        -----------
        feature_tasks : List[Dict[str, Any]]
            قائمة بمهام استخراج الميزات
            
        Returns:
        --------
        Dict[str, FeatureResult]
            نتائج استخراج الميزات
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {}
            
            for i, task in enumerate(feature_tasks):
                feature_type = task.get('feature_type')
                parameters = task.get('parameters', {})
                task_id = task.get('task_id', f"feature_{i}")
                
                # إنشاء معالج منفصل لكل مهمة
                extractor = AdvancedFeatureExtractor(self.current_image)
                future = executor.submit(
                    self._extract_feature_safe, 
                    extractor, 
                    feature_type, 
                    parameters, 
                    task_id
                )
                future_to_task[future] = task_id
            
            for future in as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    result = future.result()
                    results[task_id] = result
                    logger.info(f"مهمة استخراج الميزات {task_id} اكتملت بنجاح")
                except Exception as e:
                    logger.error(f"خطأ في مهمة {task_id}: {str(e)}")
                    results[task_id] = None
        
        return results
    
    def process_multiple_filters(self, filter_tasks: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """
        تطبيق عدة مرشحات بالتوازي
        
        Parameters:
        -----------
        filter_tasks : List[Dict[str, Any]]
            قائمة بمهام تطبيق المرشحات
            
        Returns:
        --------
        Dict[str, np.ndarray]
            نتائج تطبيق المرشحات
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {}
            
            for i, task in enumerate(filter_tasks):
                filter_type = task.get('filter_type')
                parameters = task.get('parameters', {})
                task_id = task.get('task_id', f"filter_{i}")
                
                # إنشاء معالج منفصل لكل مهمة
                processor = AdvancedImageProcessor(self.current_image)
                future = executor.submit(
                    self._apply_filter_safe, 
                    processor, 
                    filter_type, 
                    parameters, 
                    task_id
                )
                future_to_task[future] = task_id
            
            for future in as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    result = future.result()
                    results[task_id] = result
                    logger.info(f"مهمة تطبيق المرشح {task_id} اكتملت بنجاح")
                except Exception as e:
                    logger.error(f"خطأ في مهمة {task_id}: {str(e)}")
                    results[task_id] = None
        
        return results
    
    def process_multiple_transformations(self, transform_tasks: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """
        تطبيق عدة تحويلات هندسية بالتوازي
        
        Parameters:
        -----------
        transform_tasks : List[Dict[str, Any]]
            قائمة بمهام التحويلات الهندسية
            
        Returns:
        --------
        Dict[str, np.ndarray]
            نتائج التحويلات الهندسية
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {}
            
            for i, task in enumerate(transform_tasks):
                transformation_type = task.get('transformation_type')
                parameters = task.get('parameters', {})
                task_id = task.get('task_id', f"transform_{i}")
                
                # إنشاء معالج منفصل لكل مهمة
                transformer = GeometricTransformation(self.current_image)
                future = executor.submit(
                    self._apply_transformation_safe, 
                    transformer, 
                    transformation_type, 
                    parameters, 
                    task_id
                )
                future_to_task[future] = task_id
            
            for future in as_completed(future_to_task):
                task_id = future_to_task[future]
                try:
                    result = future.result()
                    results[task_id] = result
                    logger.info(f"مهمة التحويل الهندسي {task_id} اكتملت بنجاح")
                except Exception as e:
                    logger.error(f"خطأ في مهمة {task_id}: {str(e)}")
                    results[task_id] = None
        
        return results
    
    def process_filter_chain(self, filter_chain: List[Dict[str, Any]], apply_to_current: bool = True) -> np.ndarray:
        """
        تطبيق سلسلة من المرشحات بالتتابع
        
        Parameters:
        -----------
        filter_chain : List[Dict[str, Any]]
            سلسلة المرشحات المطلوب تطبيقها
        apply_to_current : bool
            هل نطبق على الصورة الحالية أم نحافظ على الأصلية
            
        Returns:
        --------
        np.ndarray
            الصورة بعد تطبيق سلسلة المرشحات
        """
        if apply_to_current:
            processor = AdvancedImageProcessor(self.current_image)
        else:
            processor = AdvancedImageProcessor(self.original_image)
        
        for filter_config in filter_chain:
            filter_type = filter_config.get('filter_type')
            parameters = filter_config.get('parameters', {})
            processor.apply_filter(filter_type, **parameters)
        
        result_image = processor.get_current_image()
        
        if apply_to_current:
            self.current_image = result_image
        
        return result_image
    
    def process_transformation_chain(self, transform_chain: List[Dict[str, Any]], apply_to_current: bool = True) -> np.ndarray:
        """
        تطبيق سلسلة من التحويلات الهندسية بالتتابع
        
        Parameters:
        -----------
        transform_chain : List[Dict[str, Any]]
            سلسلة التحويلات المطلوب تطبيقها
        apply_to_current : bool
            هل نطبق على الصورة الحالية أم نحافظ على الأصلية
            
        Returns:
        --------
        np.ndarray
            الصورة بعد تطبيق سلسلة التحويلات
        """
        if apply_to_current:
            transformer = GeometricTransformation(self.current_image)
        else:
            transformer = GeometricTransformation(self.original_image)
        
        for transform_config in transform_chain:
            transformation_type = transform_config.get('transformation_type')
            parameters = transform_config.get('parameters', {})
            
            if transformation_type == 'color_adjustment':
                transformer.adjust_color_channel(**parameters)
            else:
                transformer.apply_transformation(
                    GeometricTransformationType(transformation_type), 
                    **parameters
                )
        
        result_image = transformer.get_current_image()
        
        if apply_to_current:
            self.current_image = result_image
        
        return result_image
    
    def process_mixed_operations(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        معالجة عمليات مختلطة (ميزات + مرشحات + تحويلات)
        
        Parameters:
        -----------
        operations : List[Dict[str, Any]]
            قائمة العمليات المختلطة
            
        Returns:
        --------
        Dict[str, Any]
            نتائج جميع العمليات
        """
        results = {
            'features': {},
            'filters': {},
            'transformations': {},
            'processing_time': 0
        }
        
        start_time = time.time()
        
        # تصنيف العمليات حسب النوع
        feature_tasks = []
        filter_tasks = []
        transform_tasks = []
        
        for operation in operations:
            op_type = operation.get('operation_type')
            if op_type == 'feature_extraction':
                feature_tasks.append(operation)
            elif op_type == 'image_filtering':
                filter_tasks.append(operation)
            elif op_type == 'geometric_transformation':
                transform_tasks.append(operation)
        
        # معالجة كل نوع بالتوازي
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            if feature_tasks:
                future_features = executor.submit(self.process_multiple_features, feature_tasks)
                futures.append(('features', future_features))
            
            if filter_tasks:
                future_filters = executor.submit(self.process_multiple_filters, filter_tasks)
                futures.append(('filters', future_filters))
            
            if transform_tasks:
                future_transforms = executor.submit(self.process_multiple_transformations, transform_tasks)
                futures.append(('transformations', future_transforms))
            
            # جمع النتائج
            for result_type, future in futures:
                try:
                    result = future.result()
                    results[result_type] = result
                except Exception as e:
                    logger.error(f"خطأ في معالجة {result_type}: {str(e)}")
                    results[result_type] = {}
        
        results['processing_time'] = time.time() - start_time
        return results
    
    def _extract_feature_safe(self, extractor: AdvancedFeatureExtractor, 
                            feature_type: str, parameters: Dict[str, Any], 
                            task_id: str) -> FeatureResult:
        """استخراج الميزات بطريقة آمنة"""
        try:
            return extractor.extract_features(feature_type, **parameters)
        except Exception as e:
            logger.error(f"خطأ في استخراج الميزات {task_id}: {str(e)}")
            raise
    
    def _apply_filter_safe(self, processor: AdvancedImageProcessor, 
                         filter_type: str, parameters: Dict[str, Any], 
                         task_id: str) -> np.ndarray:
        """تطبيق المرشح بطريقة آمنة"""
        try:
            return processor.apply_filter(filter_type, **parameters)
        except Exception as e:
            logger.error(f"خطأ في تطبيق المرشح {task_id}: {str(e)}")
            raise
    
    def _apply_transformation_safe(self, transformer: GeometricTransformation, 
                                 transformation_type: str, parameters: Dict[str, Any], 
                                 task_id: str) -> np.ndarray:
        """تطبيق التحويل الهندسي بطريقة آمنة"""
        try:
            if transformation_type == 'color_adjustment':
                transformer.adjust_color_channel(**parameters)
            else:
                transformer.apply_transformation(
                    GeometricTransformationType(transformation_type), 
                    **parameters
                )
            return transformer.get_current_image()
        except Exception as e:
            logger.error(f"خطأ في تطبيق التحويل {task_id}: {str(e)}")
            raise
    
    def get_processing_history(self) -> List[Dict[str, Any]]:
        """الحصول على تاريخ المعالجة"""
        return self.processing_history.copy()
    
    def reset_to_original(self) -> None:
        """إعادة تعيين الصورة إلى الحالة الأصلية"""
        self.current_image = self.original_image.copy()
        self.processing_history.clear()
        
        # إعادة تعيين المعالجات
        self.feature_extractor = AdvancedFeatureExtractor(self.original_image)
        self.image_processor = AdvancedImageProcessor(self.original_image)
        self.geometric_transformer = GeometricTransformation(self.original_image)
    
    def get_current_image(self) -> np.ndarray:
        """الحصول على الصورة الحالية"""
        return self.current_image.copy()
    
    def update_current_image(self, new_image: np.ndarray) -> None:
        """تحديث الصورة الحالية"""
        self.current_image = new_image.copy()
        
        # تحديث المعالجات
        self.feature_extractor = AdvancedFeatureExtractor(self.current_image)
        self.image_processor = AdvancedImageProcessor(self.current_image)
        self.geometric_transformer = GeometricTransformation(self.current_image)

class ComparisonProcessor:
    """معالج مقارنة النتائج"""
    
    @staticmethod
    def compare_feature_results(results: Dict[str, FeatureResult]) -> Dict[str, Any]:
        """مقارنة نتائج استخراج الميزات"""
        comparison = {
            'total_methods': len(results),
            'keypoint_counts': {},
            'descriptor_shapes': {},
            'processing_methods': list(results.keys()),
            'summary': {}
        }
        
        for method, result in results.items():
            if result and result.keypoints:
                comparison['keypoint_counts'][method] = len(result.keypoints)
            else:
                comparison['keypoint_counts'][method] = 0
                
            if result and result.descriptors is not None:
                comparison['descriptor_shapes'][method] = result.descriptors.shape
            else:
                comparison['descriptor_shapes'][method] = None
        
        # إحصائيات ملخصة
        keypoint_counts = list(comparison['keypoint_counts'].values())
        if keypoint_counts:
            comparison['summary'] = {
                'max_keypoints': max(keypoint_counts),
                'min_keypoints': min(keypoint_counts),
                'avg_keypoints': sum(keypoint_counts) / len(keypoint_counts),
                'best_method': max(comparison['keypoint_counts'], 
                                 key=comparison['keypoint_counts'].get)
            }
        
        return comparison
    
    @staticmethod
    def compare_filter_results(results: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """مقارنة نتائج المرشحات"""
        comparison = {
            'total_filters': len(results),
            'image_properties': {},
            'filter_methods': list(results.keys())
        }
        
        for method, image in results.items():
            if image is not None:
                comparison['image_properties'][method] = {
                    'shape': image.shape,
                    'dtype': str(image.dtype),
                    'mean_intensity': float(np.mean(image)),
                    'std_intensity': float(np.std(image))
                }
        
        return comparison
    
    @staticmethod
    def compare_transformation_results(results: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """مقارنة نتائج التحويلات الهندسية"""
        comparison = {
            'total_transformations': len(results),
            'image_properties': {},
            'transformation_methods': list(results.keys())
        }
        
        for method, image in results.items():
            if image is not None:
                comparison['image_properties'][method] = {
                    'shape': image.shape,
                    'dtype': str(image.dtype),
                    'size_change': image.shape[:2]
                }
        
        return comparison