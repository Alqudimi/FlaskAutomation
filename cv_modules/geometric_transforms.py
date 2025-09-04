import cv2
import numpy as np
from enum import Enum

class GeometricTransformationType(Enum):
    TRANSLATION = "translation"
    ROTATION = "rotation"
    SCALING = "scaling"
    SHEAR = "shear"
    AFFINE = "affine"
    PERSPECTIVE = "perspective"
    FLIP = "flip"
    CROP = "crop"
    RESIZE = "resize"
    WARP_POLAR = "warp_polar"
    COLOR_ADJUSTMENT = "color_adjustment"

class ColorChannel(Enum):
    RED = 2
    GREEN = 1
    BLUE = 0
    ALL = -1

class GeometricTransformation:
    
    def __init__(self, image: np.ndarray):
        if image is None:
            raise ValueError("الصورة المدخلة لا يمكن أن تكون None")
        
        if not isinstance(image, np.ndarray):
            raise TypeError(f"نوع الصورة يجب أن يكون numpy.ndarray، لكن تم إدخال: {type(image)}")
        
        if image.size == 0:
            raise ValueError("الصورة المدخلة فارغة")
        
        self.original_image = image.copy()
        self.current_image = image.copy()
        self.transformation_history = []
        
    def reset(self):
        self.current_image = self.original_image.copy()
        self.transformation_history.clear()
        
    def get_current_image(self):
        return self.current_image.copy()
    
    def get_original_image(self):
        return self.original_image.copy()
    
    def get_history(self):
        return self.transformation_history.copy()
    
    def _validate_points(self, points, expected_count, name):
        if points is None:
            raise ValueError(f"النقاط {name} لا يمكن أن تكون None")
        
        if not isinstance(points, np.ndarray):
            raise TypeError(f"نقاط {name} يجب أن تكون numpy.ndarray")
        
        if points.shape[0] != expected_count:
            raise ValueError(f"عدد نقاط {name} يجب أن يكون {expected_count}")
        
        if points.shape[1] != 2:
            raise ValueError(f"كل نقطة في {name} يجب أن تحتوي على إحداثيين (x, y)")
    
    def _validate_parameters(self, **kwargs):
        for param_name, param_value in kwargs.items():
            if param_value is None:
                raise ValueError(f"معامل {param_name} لا يمكن أن يكون None")

    def adjust_color_channel(self, channel: ColorChannel, value: int):
        try:
            if not isinstance(channel, ColorChannel):
                raise ValueError("القناة اللونية يجب أن تكون من نوع ColorChannel")
            
            if value < -255 or value > 255:
                raise ValueError("قيمة الضبط يجب أن تكون بين -255 و 255")
            
            if channel == ColorChannel.ALL:
                adjusted_image = self.current_image.astype(np.int16) + value
                adjusted_image = np.clip(adjusted_image, 0, 255).astype(np.uint8)
            else:
                channel_idx = channel.value
                adjusted_image = self.current_image.copy()
                adjusted_image[:, :, channel_idx] = np.clip(
                    adjusted_image[:, :, channel_idx].astype(np.int16) + value, 0, 255
                ).astype(np.uint8)
            
            self.current_image = adjusted_image
            self.transformation_history.append({
                'type': GeometricTransformationType.COLOR_ADJUSTMENT,
                'parameters': {'channel': channel, 'value': value}
            })
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في ضبط القناة اللونية: {str(e)}")

    def set_color_channel(self, channel: ColorChannel, value: int):
        try:
            if not isinstance(channel, ColorChannel):
                raise ValueError("القناة اللونية يجب أن تكون من نوع ColorChannel")
            
            if value < 0 or value > 255:
                raise ValueError("قيمة القناة يجب أن تكون بين 0 و 255")
            
            if channel == ColorChannel.ALL:
                adjusted_image = np.full_like(self.current_image, value)
            else:
                channel_idx = channel.value
                adjusted_image = self.current_image.copy()
                adjusted_image[:, :, channel_idx] = value
            
            self.current_image = adjusted_image
            self.transformation_history.append({
                'type': GeometricTransformationType.COLOR_ADJUSTMENT,
                'parameters': {'channel': channel, 'set_value': value}
            })
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في تعيين القناة اللونية: {str(e)}")

    def multiply_color_channel(self, channel: ColorChannel, factor: float):
        try:
            if not isinstance(channel, ColorChannel):
                raise ValueError("القناة اللونية يجب أن تكون من نوع ColorChannel")
            
            if factor <= 0:
                raise ValueError("معامل الضرب يجب أن يكون قيمة موجبة")
            
            if channel == ColorChannel.ALL:
                adjusted_image = (self.current_image.astype(np.float32) * factor)
                adjusted_image = np.clip(adjusted_image, 0, 255).astype(np.uint8)
            else:
                channel_idx = channel.value
                adjusted_image = self.current_image.copy()
                adjusted_image[:, :, channel_idx] = np.clip(
                    adjusted_image[:, :, channel_idx].astype(np.float32) * factor, 0, 255
                ).astype(np.uint8)
            
            self.current_image = adjusted_image
            self.transformation_history.append({
                'type': GeometricTransformationType.COLOR_ADJUSTMENT,
                'parameters': {'channel': channel, 'multiply_factor': factor}
            })
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في ضرب القناة اللونية: {str(e)}")

    def translate(self, tx, ty, border_mode=cv2.BORDER_CONSTANT, border_value=(0, 0, 0)):
        try:
            self._validate_parameters(tx=tx, ty=ty)
            
            rows, cols = self.current_image.shape[:2]
            translation_matrix = np.float32([[1, 0, tx], [0, 1, ty]])
            
            transformed_image = cv2.warpAffine(
                self.current_image, translation_matrix, (cols, rows),
                borderMode=border_mode, borderValue=border_value
            )
            
            self.current_image = transformed_image
            self.transformation_history.append({
                'type': GeometricTransformationType.TRANSLATION,
                'parameters': {'tx': tx, 'ty': ty, 'border_mode': border_mode, 'border_value': border_value},
                'matrix': translation_matrix
            })
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في تحويل الإزاحة: {str(e)}")
    
    def rotate(self, angle, center=None, scale=1.0, border_mode=cv2.BORDER_CONSTANT, border_value=(0, 0, 0)):
        try:
            self._validate_parameters(angle=angle, scale=scale)
            
            rows, cols = self.current_image.shape[:2]
            
            if center is None:
                center = (cols / 2, rows / 2)
            
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)
            
            cos_angle = np.abs(rotation_matrix[0, 0])
            sin_angle = np.abs(rotation_matrix[0, 1])
            new_cols = int((rows * sin_angle) + (cols * cos_angle))
            new_rows = int((rows * cos_angle) + (cols * sin_angle))
            
            rotation_matrix[0, 2] += (new_cols / 2) - center[0]
            rotation_matrix[1, 2] += (new_rows / 2) - center[1]
            
            transformed_image = cv2.warpAffine(
                self.current_image, rotation_matrix, (new_cols, new_rows),
                borderMode=border_mode, borderValue=border_value
            )
            
            self.current_image = transformed_image
            self.transformation_history.append({
                'type': GeometricTransformationType.ROTATION,
                'parameters': {'angle': angle, 'center': center, 'scale': scale, 
                              'border_mode': border_mode, 'border_value': border_value},
                'matrix': rotation_matrix
            })
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في تدوير الصورة: {str(e)}")
    
    def scale(self, fx, fy=None, interpolation=cv2.INTER_LINEAR):
        try:
            self._validate_parameters(fx=fx)
            
            if fy is None:
                fy = fx
            
            if fx <= 0 or fy <= 0:
                raise ValueError("عوامل التحجيم يجب أن تكون قيم موجبة")
            
            rows, cols = self.current_image.shape[:2]
            new_cols = int(cols * fx)
            new_rows = int(rows * fy)
            
            transformed_image = cv2.resize(
                self.current_image, (new_cols, new_rows), 
                interpolation=interpolation
            )
            
            self.current_image = transformed_image
            self.transformation_history.append({
                'type': GeometricTransformationType.SCALING,
                'parameters': {'fx': fx, 'fy': fy, 'interpolation': interpolation}
            })
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في تحجيم الصورة: {str(e)}")
    
    def affine_transform(self, src_points, dst_points, border_mode=cv2.BORDER_CONSTANT, border_value=(0, 0, 0)):
        try:
            self._validate_points(src_points, 3, "المصدر")
            self._validate_points(dst_points, 3, "الوجهة")
            
            rows, cols = self.current_image.shape[:2]
            affine_matrix = cv2.getAffineTransform(src_points.astype(np.float32), dst_points.astype(np.float32))
            
            transformed_image = cv2.warpAffine(
                self.current_image, affine_matrix, (cols, rows),
                borderMode=border_mode, borderValue=border_value
            )
            
            self.current_image = transformed_image
            self.transformation_history.append({
                'type': GeometricTransformationType.AFFINE,
                'parameters': {'src_points': src_points, 'dst_points': dst_points,
                              'border_mode': border_mode, 'border_value': border_value},
                'matrix': affine_matrix
            })
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في التحويل الأفيني: {str(e)}")
    
    def perspective_transform(self, src_points, dst_points, border_mode=cv2.BORDER_CONSTANT, border_value=(0, 0, 0)):
        try:
            self._validate_points(src_points, 4, "المصدر")
            self._validate_points(dst_points, 4, "الوجهة")
            
            rows, cols = self.current_image.shape[:2]
            perspective_matrix = cv2.getPerspectiveTransform(
                src_points.astype(np.float32), dst_points.astype(np.float32)
            )
            
            transformed_image = cv2.warpPerspective(
                self.current_image, perspective_matrix, (cols, rows),
                borderMode=border_mode, borderValue=border_value
            )
            
            self.current_image = transformed_image
            self.transformation_history.append({
                'type': GeometricTransformationType.PERSPECTIVE,
                'parameters': {'src_points': src_points, 'dst_points': dst_points,
                              'border_mode': border_mode, 'border_value': border_value},
                'matrix': perspective_matrix
            })
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في تحويل المنظور: {str(e)}")
    
    def flip(self, flip_code):
        try:
            if flip_code not in [0, 1, -1]:
                raise ValueError("كود القلب يجب أن يكون 0، 1، أو -1")
            
            transformed_image = cv2.flip(self.current_image, flip_code)
            self.current_image = transformed_image
            
            self.transformation_history.append({
                'type': GeometricTransformationType.FLIP,
                'parameters': {'flip_code': flip_code}
            })
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في قلب الصورة: {str(e)}")
    
    def crop(self, x, y, width, height):
        try:
            self._validate_parameters(x=x, y=y, width=width, height=height)
            
            rows, cols = self.current_image.shape[:2]
            
            if x < 0 or y < 0 or width <= 0 or height <= 0:
                raise ValueError("معاملات القص يجب أن تكون قيم موجبة")
            
            if x + width > cols or y + height > rows:
                raise ValueError("منطقة القص خارج حدود الصورة")
            
            cropped_image = self.current_image[y:y+height, x:x+width]
            self.current_image = cropped_image
            
            self.transformation_history.append({
                'type': GeometricTransformationType.CROP,
                'parameters': {'x': x, 'y': y, 'width': width, 'height': height}
            })
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في قص الصورة: {str(e)}")
    
    def resize(self, width, height, interpolation=cv2.INTER_LINEAR):
        try:
            self._validate_parameters(width=width, height=height)
            
            if width <= 0 or height <= 0:
                raise ValueError("أبعاد الصورة الجديدة يجب أن تكون قيم موجبة")
            
            resized_image = cv2.resize(self.current_image, (width, height), interpolation=interpolation)
            self.current_image = resized_image
            
            self.transformation_history.append({
                'type': GeometricTransformationType.RESIZE,
                'parameters': {'width': width, 'height': height, 'interpolation': interpolation}
            })
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في تغيير حجم الصورة: {str(e)}")

    def apply_transformation(self, transformation_type: GeometricTransformationType, **kwargs):
        """
        تطبيق التحويل الهندسي المحدد
        
        Parameters:
        -----------
        transformation_type : GeometricTransformationType
            نوع التحويل المطلوب
        **kwargs
            معاملات التحويل
            
        Returns:
        --------
        self : GeometricTransformation
        """
        try:
            transformation_methods = {
                GeometricTransformationType.TRANSLATION: self.translate,
                GeometricTransformationType.ROTATION: self.rotate,
                GeometricTransformationType.SCALING: self.scale,
                GeometricTransformationType.AFFINE: self.affine_transform,
                GeometricTransformationType.PERSPECTIVE: self.perspective_transform,
                GeometricTransformationType.FLIP: self.flip,
                GeometricTransformationType.CROP: self.crop,
                GeometricTransformationType.RESIZE: self.resize,
                GeometricTransformationType.COLOR_ADJUSTMENT: self.adjust_color_channel
            }
            
            if transformation_type not in transformation_methods:
                raise ValueError(f"نوع التحويل {transformation_type} غير مدعوم")
            
            return transformation_methods[transformation_type](**kwargs)
            
        except Exception as e:
            raise RuntimeError(f"فشل في تطبيق التحويل: {str(e)}")
