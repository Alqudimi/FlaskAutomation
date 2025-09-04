import cv2
import numpy as np
from enum import Enum
from typing import Tuple, List, Dict, Any, Optional, Union

class MatchingMethod(Enum):
    """طرق مطابقة الميزات المتاحة"""
    FLANN = "FLANN"
    BF_SIFT_RATIO = "BF_SIFT_RATIO"
    BF_ORB_RATIO = "BF_ORB_RATIO"

class FeatureMatching:
    """
    كلاس متقدم لمطابقة الميزات في الصور باستخدام OpenCV
    يدعم ثلاث طرق رئيسية: FLANN، Brute-Force مع SIFT، و Brute-Force مع ORB
    """
    
    def __init__(self, image1: np.ndarray, image2: np.ndarray):
        """
        تهيئة الكلاس مع الصور المدخلة
        
        Parameters:
        -----------
        image1 : np.ndarray
            الصورة الأولى
        image2 : np.ndarray
            الصورة الثانية
            
        Raises:
        -------
        ValueError:
            إذا كانت الصور فارغة أو غير صالحة
        TypeError:
            إذا كان نوع الصور غير مدعوم
        """
        if image1 is None or image2 is None:
            raise ValueError("الصور المدخلة لا يمكن أن تكون None")
        
        if not isinstance(image1, np.ndarray) or not isinstance(image2, np.ndarray):
            raise TypeError("نوع الصور يجب أن يكون numpy.ndarray")
        
        if image1.size == 0 or image2.size == 0:
            raise ValueError("الصور المدخلة فارغة")
        
        # تحويل إلى تدرج الرمادي إذا لزم الأمر
        if len(image1.shape) == 3:
            self.image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        else:
            self.image1 = image1.copy()
            
        if len(image2.shape) == 3:
            self.image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        else:
            self.image2 = image2.copy()
            
        self.keypoints1 = None
        self.keypoints2 = None
        self.descriptors1 = None
        self.descriptors2 = None
        self.matches = None
        self.good_matches = None
        self.homography = None
        self.detector = None
        self.matcher = None
        self.matching_method = None
        
    def _validate_images(self) -> None:
        """التحقق من وجود الصور"""
        if self.image1 is None or self.image2 is None:
            raise ValueError("الصور غير موجودة")
    
    def _validate_features_detected(self) -> None:
        """التحقق من اكتشاف الميزات"""
        if self.keypoints1 is None or self.descriptors1 is None:
            raise RuntimeError("يجب اكتشاف الميزات أولاً باستخدام detect_features()")
    
    def _validate_matches_calculated(self) -> None:
        """التحقق من حساب المطابقات"""
        if self.matches is None:
            raise RuntimeError("يجب حساب المطابقات أولاً باستخدام match_features()")
    
    def detect_features(self, method: MatchingMethod) -> 'FeatureMatching':
        """
        اكتشاف الميزات في الصورتين بناءً على الطريقة المحددة
        
        Parameters:
        -----------
        method : MatchingMethod
            طريقة المطابقة المطلوبة
            
        Returns:
        --------
        self : FeatureMatching
        """
        try:
            self._validate_images()
            self.matching_method = method
            
            if method == MatchingMethod.FLANN or method == MatchingMethod.BF_SIFT_RATIO:
                # استخدام SIFT للكشف عن الميزات
                self.detector = cv2.SIFT_create()
            elif method == MatchingMethod.BF_ORB_RATIO:
                # استخدام ORB للكشف عن الميزات
                self.detector = cv2.ORB_create(nfeatures=1000)
            else:
                raise ValueError(f"طريقة المطابقة {method} غير مدعومة")
            
            # اكتشاف الميزات في الصورة الأولى
            self.keypoints1, self.descriptors1 = self.detector.detectAndCompute(self.image1, None)
            
            # اكتشاف الميزات في الصورة الثانية
            self.keypoints2, self.descriptors2 = self.detector.detectAndCompute(self.image2, None)
            
            if len(self.keypoints1) == 0 or len(self.keypoints2) == 0:
                raise RuntimeError("لم يتم اكتشاف أي ميزات في إحدى الصور أو كلتيهما")
            
            if self.descriptors1 is None or self.descriptors2 is None:
                raise RuntimeError("فشل في حساب الواصفات للميزات")
            
            # تحويل الواصفات إلى النوع المناسب
            if method == MatchingMethod.FLANN:
                self.descriptors1 = self.descriptors1.astype(np.float32)
                self.descriptors2 = self.descriptors2.astype(np.float32)
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في اكتشاف الميزات: {str(e)}")
    
    def match_features(self, ratio_threshold: float = 0.75, max_distance: float = 100.0) -> 'FeatureMatching':
        """
        مطابقة الميزات بين الصورتين
        
        Parameters:
        -----------
        ratio_threshold : float
            عتبة نسبة الاختبار (لطرق Ratio Test)
        max_distance : float
            أقصى مسافة للمطابقة (لطرق Brute-Force)
            
        Returns:
        --------
        self : FeatureMatching
        """
        try:
            self._validate_features_detected()
            
            if self.matching_method == MatchingMethod.FLANN:
                # FLANN based Matcher
                index_params = dict(algorithm=1, trees=5)
                search_params = dict(checks=50)
                self.matcher = cv2.FlannBasedMatcher(index_params, search_params)
                self.matches = self.matcher.knnMatch(self.descriptors1, self.descriptors2, k=2)
                
            elif self.matching_method == MatchingMethod.BF_SIFT_RATIO:
                # Brute-Force Matching with SIFT
                self.matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
                self.matches = self.matcher.knnMatch(self.descriptors1, self.descriptors2, k=2)
                
            elif self.matching_method == MatchingMethod.BF_ORB_RATIO:
                # Brute-Force Matching with ORB
                self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
                self.matches = self.matcher.knnMatch(self.descriptors1, self.descriptors2, k=2)
            
            else:
                raise ValueError(f"طريقة المطابقة {self.matching_method} غير مدعومة")
            
            # تطبيق Ratio Test لتصفية المطابقات
            self.good_matches = []
            
            if self.matching_method in [MatchingMethod.FLANN, MatchingMethod.BF_SIFT_RATIO, MatchingMethod.BF_ORB_RATIO]:
                for match_pair in self.matches:
                    if len(match_pair) == 2:
                        m, n = match_pair
                        if m.distance < ratio_threshold * n.distance:
                            self.good_matches.append(m)
            
            if len(self.good_matches) == 0:
                raise RuntimeError("لم يتم العثور على أي مطابقات جيدة بعد التصفية")
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في مطابقة الميزات: {str(e)}")
    
    def calculate_homography(self, ransac_thresh: float = 5.0) -> 'FeatureMatching':
        """
        حساب تحويل homography بين الصورتين
        
        Parameters:
        -----------
        ransac_thresh : float
            عتبة RANSAC
            
        Returns:
        --------
        self : FeatureMatching
        """
        try:
            self._validate_matches_calculated()
            
            if len(self.good_matches) < 4:
                raise RuntimeError("يحتاج حساب homography إلى 4 مطابقات على الأقل")
            
            # استخراج النقاط المتطابقة
            src_pts = np.float32([self.keypoints1[m.queryIdx].pt for m in self.good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([self.keypoints2[m.trainIdx].pt for m in self.good_matches]).reshape(-1, 1, 2)
            
            # حساب homography
            self.homography, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, ransac_thresh)
            
            if self.homography is None:
                raise RuntimeError("فشل في حساب homography")
            
            return self
            
        except Exception as e:
            raise RuntimeError(f"فشل في حساب homography: {str(e)}")
    
    def draw_matches(self, output_image: Optional[np.ndarray] = None, 
                    flags: int = cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS) -> np.ndarray:
        """
        رسم المطابقات على الصورة
        
        Parameters:
        -----------
        output_image : Optional[np.ndarray]
            صورة الإخراج (افتراضي: سيتم إنشاء صورة جديدة)
        flags : int
            إعدادات الرسم
            
        Returns:
        --------
        output_image : np.ndarray
            الصورة مع المطابقات المرسومة
        """
        try:
            self._validate_matches_calculated()
            
            # تحويل الصور إلى BGR للرسم الملون
            if len(self.image1.shape) == 2:
                img1_color = cv2.cvtColor(self.image1, cv2.COLOR_GRAY2BGR)
            else:
                img1_color = self.image1
                
            if len(self.image2.shape) == 2:
                img2_color = cv2.cvtColor(self.image2, cv2.COLOR_GRAY2BGR)
            else:
                img2_color = self.image2
            
            # رسم المطابقات
            output_image = cv2.drawMatches(
                img1_color, self.keypoints1,
                img2_color, self.keypoints2,
                self.good_matches, output_image,
                flags=flags,
                matchColor=(0, 255, 0),  # لون المطابقات (أخضر)
                singlePointColor=(255, 0, 0),  # لون النقاط المفردة (أزرق)
                matchesThickness=2
            )
            
            return output_image
            
        except Exception as e:
            raise RuntimeError(f"فشل في رسم المطابقات: {str(e)}")
    
    def get_match_statistics(self) -> Dict[str, Any]:
        """
        الحصول على إحصاءات المطابقات
        
        Returns:
        --------
        statistics : Dict[str, Any]
            قاموس يحتوي على إحصاءات المطابقات
        """
        try:
            self._validate_matches_calculated()
            
            if not self.good_matches:
                return {}
            
            distances = [m.distance for m in self.good_matches]
            
            statistics = {
                'total_matches': len(self.good_matches),
                'min_distance': min(distances),
                'max_distance': max(distances),
                'avg_distance': sum(distances) / len(distances),
                'matching_method': self.matching_method.value if self.matching_method else "Unknown",
                'keypoints_image1': len(self.keypoints1),
                'keypoints_image2': len(self.keypoints2)
            }
            
            return statistics
            
        except Exception as e:
            raise RuntimeError(f"فشل في حساب الإحصاءات: {str(e)}")
    
    def get_matching_result(self) -> Dict[str, Any]:
        """
        الحصول على نتائج المطابقة كاملة
        
        Returns:
        --------
        result : Dict[str, Any]
            قاموس يحتوي على جميع نتائج المطابقة
        """
        try:
            return {
                'keypoints1': self.keypoints1,
                'keypoints2': self.keypoints2,
                'descriptors1': self.descriptors1,
                'descriptors2': self.descriptors2,
                'matches': self.matches,
                'good_matches': self.good_matches,
                'homography': self.homography,
                'matching_method': self.matching_method.value if self.matching_method else "Unknown",
                'statistics': self.get_match_statistics()
            }
            
        except Exception as e:
            raise RuntimeError(f"فشل في الحصول على نتائج المطابقة: {str(e)}")
