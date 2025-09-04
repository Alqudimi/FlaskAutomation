import cv2
import numpy as np
import base64
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_image(image_bytes):
    """Load image from bytes"""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        logger.error(f"Error loading image: {str(e)}")
        return None

def save_image(image, filepath):
    """Save image to file"""
    try:
        success = cv2.imwrite(filepath, image)
        return success
    except Exception as e:
        logger.error(f"Error saving image: {str(e)}")
        return False

def image_to_base64(image):
    """Convert OpenCV image to base64 string"""
    try:
        # Encode image to PNG format
        _, buffer = cv2.imencode('.png', image)
        # Convert to base64
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        logger.error(f"Error converting image to base64: {str(e)}")
        return None

def base64_to_image(base64_string):
    """Convert base64 string to OpenCV image"""
    try:
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(base64_string)
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        logger.error(f"Error converting base64 to image: {str(e)}")
        return None

def resize_image(image, max_width=800, max_height=600):
    """Resize image while maintaining aspect ratio"""
    try:
        height, width = image.shape[:2]
        
        # Calculate scaling factor
        scale_w = max_width / width
        scale_h = max_height / height
        scale = min(scale_w, scale_h)
        
        if scale < 1:
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            return resized_image
        
        return image
    except Exception as e:
        logger.error(f"Error resizing image: {str(e)}")
        return image

def validate_image(image):
    """Validate if image is valid"""
    if image is None:
        return False, "Image is None"
    
    if not isinstance(image, np.ndarray):
        return False, "Image is not a numpy array"
    
    if image.size == 0:
        return False, "Image is empty"
    
    if len(image.shape) not in [2, 3]:
        return False, "Image must be 2D or 3D array"
    
    return True, "Valid image"

def convert_color_space(image, conversion_code):
    """Convert image color space"""
    try:
        converted_image = cv2.cvtColor(image, conversion_code)
        return converted_image
    except Exception as e:
        logger.error(f"Error converting color space: {str(e)}")
        return image

def get_image_info(image):
    """Get basic information about image"""
    try:
        info = {
            'shape': image.shape,
            'dtype': str(image.dtype),
            'size': image.size,
            'min_value': float(np.min(image)),
            'max_value': float(np.max(image)),
            'mean_value': float(np.mean(image))
        }
        
        if len(image.shape) == 3:
            info['channels'] = image.shape[2]
            info['width'] = image.shape[1]
            info['height'] = image.shape[0]
        else:
            info['channels'] = 1
            info['width'] = image.shape[1]
            info['height'] = image.shape[0]
        
        return info
    except Exception as e:
        logger.error(f"Error getting image info: {str(e)}")
        return {}
