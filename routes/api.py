import os
import cv2
import numpy as np
import base64
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from PIL import Image
import io
import logging

from cv_modules.feature_extraction import AdvancedFeatureExtractor, FeatureType
from cv_modules.image_filters import AdvancedImageProcessor, FilterType
from cv_modules.feature_matching import FeatureMatching, MatchingMethod
from cv_modules.geometric_transforms import GeometricTransformation, GeometricTransformationType, ColorChannel
from cv_modules.batch_processor import BatchProcessor, ComparisonProcessor
from utils.image_utils import allowed_file, save_image, load_image, image_to_base64, base64_to_image

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Global variables to store processors
processors = {}
matchers = {}
batch_processors = {}

@api_bp.route('/upload', methods=['POST'])
def upload_image():
    """Upload and process image file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Read image directly from memory
            image_bytes = file.read()
            image = load_image(image_bytes)
            
            if image is None:
                return jsonify({'error': 'Invalid image file'}), 400
            
            # Generate unique ID for this image
            image_id = f"image_{len(processors)}"
            
            # Store processors
            processors[image_id] = {
                'feature_extractor': AdvancedFeatureExtractor(image),
                'image_processor': AdvancedImageProcessor(image),
                'geometric_transformer': GeometricTransformation(image),
                'batch_processor': BatchProcessor(image),
                'original_image': image
            }
            
            # Store batch processor separately for easier access
            batch_processors[image_id] = processors[image_id]['batch_processor']
            
            # Convert image to base64 for response
            image_base64 = image_to_base64(image)
            
            return jsonify({
                'success': True,
                'image_id': image_id,
                'image_data': image_base64,
                'width': image.shape[1],
                'height': image.shape[0],
                'channels': len(image.shape)
            })
        
        return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, or JPEG files.'}), 400
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@api_bp.route('/extract_features', methods=['POST'])
def extract_features():
    """Extract features from image"""
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        feature_type = data.get('feature_type')
        parameters = data.get('parameters', {})
        
        if image_id not in processors:
            return jsonify({'error': 'Image not found'}), 404
        
        extractor = processors[image_id]['feature_extractor']
        result = extractor.extract_features(feature_type, **parameters)
        
        # Convert result image to base64
        result_image_base64 = None
        if result.image is not None:
            result_image_base64 = image_to_base64(result.image)
        
        # Convert descriptors to list if not None
        descriptors_list = None
        if result.descriptors is not None:
            descriptors_list = result.descriptors.flatten().tolist()
        
        # Convert keypoints to serializable format
        keypoints_data = None
        if result.keypoints is not None:
            keypoints_data = [
                {
                    'x': kp.pt[0],
                    'y': kp.pt[1],
                    'size': kp.size,
                    'angle': kp.angle,
                    'response': kp.response,
                    'octave': kp.octave
                }
                for kp in result.keypoints
            ]
        
        return jsonify({
            'success': True,
            'result_image': result_image_base64,
            'keypoints': keypoints_data,
            'descriptors': descriptors_list,
            'features': result.features,
            'metadata': result.metadata
        })
        
    except Exception as e:
        logger.error(f"Feature extraction error: {str(e)}")
        return jsonify({'error': f'Feature extraction failed: {str(e)}'}), 500

@api_bp.route('/apply_filter', methods=['POST'])
def apply_filter():
    """Apply filter to image"""
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        filter_type = data.get('filter_type')
        parameters = data.get('parameters', {})
        
        if image_id not in processors:
            return jsonify({'error': 'Image not found'}), 404
        
        processor = processors[image_id]['image_processor']
        result_image = processor.apply_filter(filter_type, **parameters)
        
        # Convert result image to base64
        result_image_base64 = image_to_base64(result_image)
        
        return jsonify({
            'success': True,
            'result_image': result_image_base64,
            'history': processor.get_history()
        })
        
    except Exception as e:
        logger.error(f"Filter application error: {str(e)}")
        return jsonify({'error': f'Filter application failed: {str(e)}'}), 500

@api_bp.route('/match_features', methods=['POST'])
def match_features():
    """Match features between two images"""
    try:
        data = request.get_json()
        image_id1 = data.get('image_id1')
        image_id2 = data.get('image_id2')
        matching_method = data.get('matching_method', 'FLANN')
        parameters = data.get('parameters', {})
        
        if image_id1 not in processors or image_id2 not in processors:
            return jsonify({'error': 'One or both images not found'}), 404
        
        image1 = processors[image_id1]['original_image']
        image2 = processors[image_id2]['original_image']
        
        matcher = FeatureMatching(image1, image2)
        method = MatchingMethod(matching_method)
        
        # Detect features and match
        matcher.detect_features(method)
        matcher.match_features(**parameters)
        
        # Draw matches
        matches_image = matcher.draw_matches()
        matches_image_base64 = image_to_base64(matches_image)
        
        # Get statistics
        stats = matcher.get_match_statistics()
        
        # Store matcher for potential homography calculation
        matcher_id = f"matcher_{len(matchers)}"
        matchers[matcher_id] = matcher
        
        return jsonify({
            'success': True,
            'matches_image': matches_image_base64,
            'matcher_id': matcher_id,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Feature matching error: {str(e)}")
        return jsonify({'error': f'Feature matching failed: {str(e)}'}), 500

@api_bp.route('/calculate_homography', methods=['POST'])
def calculate_homography():
    """Calculate homography for matched features"""
    try:
        data = request.get_json()
        matcher_id = data.get('matcher_id')
        parameters = data.get('parameters', {})
        
        if matcher_id not in matchers:
            return jsonify({'error': 'Matcher not found'}), 404
        
        matcher = matchers[matcher_id]
        matcher.calculate_homography(**parameters)
        
        # Convert homography matrix to list
        homography_list = None
        if matcher.homography is not None:
            homography_list = matcher.homography.tolist()
        
        return jsonify({
            'success': True,
            'homography': homography_list
        })
        
    except Exception as e:
        logger.error(f"Homography calculation error: {str(e)}")
        return jsonify({'error': f'Homography calculation failed: {str(e)}'}), 500

@api_bp.route('/apply_transformation', methods=['POST'])
def apply_transformation():
    """Apply geometric transformation to image"""
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        transformation_type = data.get('transformation_type')
        parameters = data.get('parameters', {})
        
        if image_id not in processors:
            return jsonify({'error': 'Image not found'}), 404
        
        transformer = processors[image_id]['geometric_transformer']
        
        # Convert string parameters to appropriate enums if needed
        if 'channel' in parameters and isinstance(parameters['channel'], str):
            parameters['channel'] = ColorChannel[parameters['channel'].upper()]
        
        # Apply transformation
        if transformation_type == 'color_adjustment':
            transformer.adjust_color_channel(**parameters)
        else:
            transformer.apply_transformation(
                GeometricTransformationType(transformation_type), 
                **parameters
            )
        
        result_image = transformer.get_current_image()
        result_image_base64 = image_to_base64(result_image)
        
        return jsonify({
            'success': True,
            'result_image': result_image_base64,
            'history': transformer.get_history()
        })
        
    except Exception as e:
        logger.error(f"Transformation error: {str(e)}")
        return jsonify({'error': f'Transformation failed: {str(e)}'}), 500

@api_bp.route('/reset_image', methods=['POST'])
def reset_image():
    """Reset image to original state"""
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        processor_type = data.get('processor_type', 'all')
        
        if image_id not in processors:
            return jsonify({'error': 'Image not found'}), 404
        
        if processor_type == 'all' or processor_type == 'filter':
            processors[image_id]['image_processor'].reset_to_original()
        
        if processor_type == 'all' or processor_type == 'transform':
            processors[image_id]['geometric_transformer'].reset()
        
        if processor_type == 'all' or processor_type == 'features':
            processors[image_id]['feature_extractor'].reset_image()
        
        # Return current image
        current_image = processors[image_id]['original_image']
        image_base64 = image_to_base64(current_image)
        
        return jsonify({
            'success': True,
            'image_data': image_base64
        })
        
    except Exception as e:
        logger.error(f"Reset error: {str(e)}")
        return jsonify({'error': f'Reset failed: {str(e)}'}), 500

@api_bp.route('/download_image', methods=['POST'])
def download_image():
    """Get processed image for download"""
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        processor_type = data.get('processor_type', 'filter')
        
        if image_id not in processors:
            return jsonify({'error': 'Image not found'}), 404
        
        if processor_type == 'filter':
            current_image = processors[image_id]['image_processor'].get_current_image()
        elif processor_type == 'transform':
            current_image = processors[image_id]['geometric_transformer'].get_current_image()
        elif processor_type == 'features':
            current_image = processors[image_id]['feature_extractor'].get_current_image()
        else:
            current_image = processors[image_id]['original_image']
        
        # Convert image to base64
        image_base64 = image_to_base64(current_image)
        
        return jsonify({
            'success': True,
            'image_data': image_base64,
            'filename': f'processed_image_{image_id}.png'
        })
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@api_bp.route('/get_filter_types', methods=['GET'])
def get_filter_types():
    """Get available filter types"""
    filter_types = [filter_type.value for filter_type in FilterType]
    return jsonify({'filter_types': filter_types})

@api_bp.route('/get_feature_types', methods=['GET'])
def get_feature_types():
    """Get available feature extraction types"""
    feature_types = [feature_type.value for feature_type in FeatureType]
    return jsonify({'feature_types': feature_types})

@api_bp.route('/get_transformation_types', methods=['GET'])
def get_transformation_types():
    """Get available transformation types"""
    transformation_types = [trans_type.value for trans_type in GeometricTransformationType]
    return jsonify({'transformation_types': transformation_types})

@api_bp.route('/get_matching_methods', methods=['GET'])
def get_matching_methods():
    """Get available matching methods"""
    matching_methods = [method.value for method in MatchingMethod]
    return jsonify({'matching_methods': matching_methods})

# ===== معالجة العمليات المتعددة =====

@api_bp.route('/process_multiple_features', methods=['POST'])
def process_multiple_features():
    """استخراج ميزات متعددة بالتوازي"""
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        feature_tasks = data.get('feature_tasks', [])
        
        if image_id not in batch_processors:
            return jsonify({'error': 'Image not found'}), 404
        
        if not feature_tasks:
            return jsonify({'error': 'No feature tasks provided'}), 400
        
        batch_processor = batch_processors[image_id]
        results = batch_processor.process_multiple_features(feature_tasks)
        
        # تحويل النتائج إلى تنسيق قابل للإرسال
        serialized_results = {}
        for task_id, result in results.items():
            if result is not None:
                # تحويل الصورة إلى base64
                result_image_base64 = None
                if result.image is not None:
                    result_image_base64 = image_to_base64(result.image)
                
                # تحويل الواصفات إلى قائمة
                descriptors_list = None
                if result.descriptors is not None:
                    descriptors_list = result.descriptors.flatten().tolist()
                
                # تحويل النقاط المميزة
                keypoints_data = None
                if result.keypoints is not None:
                    keypoints_data = [
                        {
                            'x': kp.pt[0],
                            'y': kp.pt[1],
                            'size': kp.size,
                            'angle': kp.angle,
                            'response': kp.response,
                            'octave': kp.octave
                        }
                        for kp in result.keypoints
                    ]
                
                serialized_results[task_id] = {
                    'result_image': result_image_base64,
                    'keypoints': keypoints_data,
                    'descriptors': descriptors_list,
                    'features': result.features,
                    'metadata': result.metadata
                }
            else:
                serialized_results[task_id] = None
        
        # إضافة مقارنة النتائج
        comparison = ComparisonProcessor.compare_feature_results(results)
        
        return jsonify({
            'success': True,
            'results': serialized_results,
            'comparison': comparison,
            'total_tasks': len(feature_tasks)
        })
        
    except Exception as e:
        logger.error(f"Multiple features extraction error: {str(e)}")
        return jsonify({'error': f'Multiple features extraction failed: {str(e)}'}), 500

@api_bp.route('/process_multiple_filters', methods=['POST'])
def process_multiple_filters():
    """تطبيق مرشحات متعددة بالتوازي"""
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        filter_tasks = data.get('filter_tasks', [])
        
        if image_id not in batch_processors:
            return jsonify({'error': 'Image not found'}), 404
        
        if not filter_tasks:
            return jsonify({'error': 'No filter tasks provided'}), 400
        
        batch_processor = batch_processors[image_id]
        results = batch_processor.process_multiple_filters(filter_tasks)
        
        # تحويل النتائج إلى base64
        serialized_results = {}
        for task_id, result_image in results.items():
            if result_image is not None:
                serialized_results[task_id] = image_to_base64(result_image)
            else:
                serialized_results[task_id] = None
        
        # إضافة مقارنة النتائج
        comparison = ComparisonProcessor.compare_filter_results(results)
        
        return jsonify({
            'success': True,
            'results': serialized_results,
            'comparison': comparison,
            'total_tasks': len(filter_tasks)
        })
        
    except Exception as e:
        logger.error(f"Multiple filters error: {str(e)}")
        return jsonify({'error': f'Multiple filters failed: {str(e)}'}), 500

@api_bp.route('/process_multiple_transformations', methods=['POST'])
def process_multiple_transformations():
    """تطبيق تحويلات هندسية متعددة بالتوازي"""
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        transform_tasks = data.get('transform_tasks', [])
        
        if image_id not in batch_processors:
            return jsonify({'error': 'Image not found'}), 404
        
        if not transform_tasks:
            return jsonify({'error': 'No transformation tasks provided'}), 400
        
        batch_processor = batch_processors[image_id]
        results = batch_processor.process_multiple_transformations(transform_tasks)
        
        # تحويل النتائج إلى base64
        serialized_results = {}
        for task_id, result_image in results.items():
            if result_image is not None:
                serialized_results[task_id] = image_to_base64(result_image)
            else:
                serialized_results[task_id] = None
        
        # إضافة مقارنة النتائج
        comparison = ComparisonProcessor.compare_transformation_results(results)
        
        return jsonify({
            'success': True,
            'results': serialized_results,
            'comparison': comparison,
            'total_tasks': len(transform_tasks)
        })
        
    except Exception as e:
        logger.error(f"Multiple transformations error: {str(e)}")
        return jsonify({'error': f'Multiple transformations failed: {str(e)}'}), 500

@api_bp.route('/process_filter_chain', methods=['POST'])
def process_filter_chain():
    """تطبيق سلسلة من المرشحات بالتتابع"""
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        filter_chain = data.get('filter_chain', [])
        apply_to_current = data.get('apply_to_current', True)
        
        if image_id not in batch_processors:
            return jsonify({'error': 'Image not found'}), 404
        
        if not filter_chain:
            return jsonify({'error': 'No filter chain provided'}), 400
        
        batch_processor = batch_processors[image_id]
        result_image = batch_processor.process_filter_chain(filter_chain, apply_to_current)
        
        result_image_base64 = image_to_base64(result_image)
        
        return jsonify({
            'success': True,
            'result_image': result_image_base64,
            'chain_length': len(filter_chain),
            'applied_to_current': apply_to_current
        })
        
    except Exception as e:
        logger.error(f"Filter chain error: {str(e)}")
        return jsonify({'error': f'Filter chain failed: {str(e)}'}), 500

@api_bp.route('/process_transformation_chain', methods=['POST'])
def process_transformation_chain():
    """تطبيق سلسلة من التحويلات الهندسية بالتتابع"""
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        transform_chain = data.get('transform_chain', [])
        apply_to_current = data.get('apply_to_current', True)
        
        if image_id not in batch_processors:
            return jsonify({'error': 'Image not found'}), 404
        
        if not transform_chain:
            return jsonify({'error': 'No transformation chain provided'}), 400
        
        batch_processor = batch_processors[image_id]
        result_image = batch_processor.process_transformation_chain(transform_chain, apply_to_current)
        
        result_image_base64 = image_to_base64(result_image)
        
        return jsonify({
            'success': True,
            'result_image': result_image_base64,
            'chain_length': len(transform_chain),
            'applied_to_current': apply_to_current
        })
        
    except Exception as e:
        logger.error(f"Transformation chain error: {str(e)}")
        return jsonify({'error': f'Transformation chain failed: {str(e)}'}), 500

@api_bp.route('/process_mixed_operations', methods=['POST'])
def process_mixed_operations():
    """معالجة عمليات مختلطة (ميزات + مرشحات + تحويلات)"""
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        operations = data.get('operations', [])
        
        if image_id not in batch_processors:
            return jsonify({'error': 'Image not found'}), 404
        
        if not operations:
            return jsonify({'error': 'No operations provided'}), 400
        
        batch_processor = batch_processors[image_id]
        results = batch_processor.process_mixed_operations(operations)
        
        # تحويل نتائج الميزات
        if 'features' in results:
            serialized_features = {}
            for task_id, result in results['features'].items():
                if result is not None:
                    result_image_base64 = None
                    if result.image is not None:
                        result_image_base64 = image_to_base64(result.image)
                    
                    descriptors_list = None
                    if result.descriptors is not None:
                        descriptors_list = result.descriptors.flatten().tolist()
                    
                    keypoints_data = None
                    if result.keypoints is not None:
                        keypoints_data = [
                            {
                                'x': kp.pt[0],
                                'y': kp.pt[1],
                                'size': kp.size,
                                'angle': kp.angle,
                                'response': kp.response,
                                'octave': kp.octave
                            }
                            for kp in result.keypoints
                        ]
                    
                    serialized_features[task_id] = {
                        'result_image': result_image_base64,
                        'keypoints': keypoints_data,
                        'descriptors': descriptors_list,
                        'features': result.features,
                        'metadata': result.metadata
                    }
                else:
                    serialized_features[task_id] = None
            results['features'] = serialized_features
        
        # تحويل نتائج المرشحات والتحويلات إلى base64
        for result_type in ['filters', 'transformations']:
            if result_type in results:
                serialized_results = {}
                for task_id, result_image in results[result_type].items():
                    if result_image is not None:
                        serialized_results[task_id] = image_to_base64(result_image)
                    else:
                        serialized_results[task_id] = None
                results[result_type] = serialized_results
        
        return jsonify({
            'success': True,
            'results': results,
            'total_operations': len(operations)
        })
        
    except Exception as e:
        logger.error(f"Mixed operations error: {str(e)}")
        return jsonify({'error': f'Mixed operations failed: {str(e)}'}), 500

@api_bp.route('/reset_batch_processor', methods=['POST'])
def reset_batch_processor():
    """إعادة تعيين معالج الدفعات للصورة الأصلية"""
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        
        if image_id not in batch_processors:
            return jsonify({'error': 'Image not found'}), 404
        
        batch_processor = batch_processors[image_id]
        batch_processor.reset_to_original()
        
        # إعادة تعيين المعالجات العادية أيضاً
        if image_id in processors:
            original_image = processors[image_id]['original_image']
            processors[image_id]['feature_extractor'] = AdvancedFeatureExtractor(original_image)
            processors[image_id]['image_processor'] = AdvancedImageProcessor(original_image)
            processors[image_id]['geometric_transformer'] = GeometricTransformation(original_image)
        
        return jsonify({
            'success': True,
            'message': 'Batch processor reset to original image'
        })
        
    except Exception as e:
        logger.error(f"Reset batch processor error: {str(e)}")
        return jsonify({'error': f'Reset failed: {str(e)}'}), 500
