import cv2
import numpy as np
from skimage import exposure
from skimage.util import img_as_ubyte

class EnhancementEngine:
    """Contains various image enhancement and analysis algorithms."""
    def __init__(self, contrast_limit=15.0, num_clusters=4):
        self.contrast_limit = contrast_limit
        self.num_clusters = num_clusters

    def enhance_basic(self, img):
        """Basic enhancement using CLAHE."""
        gray = self._to_grayscale(img)
        clahe = cv2.createCLAHE(clipLimit=self.contrast_limit, tileGridSize=(16, 16))
        enhanced = clahe.apply(gray)
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

    def enhance_advanced(self, img):
        """Advanced enhancement with bilateral filtering and sharpening."""
        gray = self._to_grayscale(img)
        
        p2, p98 = np.percentile(gray, (2, 98))
        stretched = exposure.rescale_intensity(gray, in_range=(p2, p98))
        stretched = img_as_ubyte(stretched)
        
        bilateral = cv2.bilateralFilter(stretched, 9, 75, 75)
        
        clahe = cv2.createCLAHE(clipLimit=self.contrast_limit, tileGridSize=(16, 16))
        clahe_applied = clahe.apply(bilateral)
        
        gaussian = cv2.GaussianBlur(clahe_applied, (0, 0), 3)
        sharpened = cv2.addWeighted(clahe_applied, 1.5, gaussian, -0.5, 0)
        
        return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

    def segment(self, img):
        """Segments the image using k-means clustering."""
        gray = self._to_grayscale(img)
        
        clahe = cv2.createCLAHE(clipLimit=self.contrast_limit, tileGridSize=(16, 16))
        enhanced = clahe.apply(gray)
        
        pixel_vals = enhanced.reshape((-1, 1))
        pixel_vals = np.float32(pixel_vals)
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 15, 1.0)
        _, labels, centers = cv2.kmeans(pixel_vals, self.num_clusters, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        centers = np.uint8(centers)
        segmented_data = centers[labels.flatten()]
        segmented = segmented_data.reshape(enhanced.shape)
        
        return cv2.cvtColor(segmented, cv2.COLOR_GRAY2BGR)

    def false_color(self, img):
        """Converts grayscale to a false-color representation."""
        gray = self._to_grayscale(img)
        
        clahe = cv2.createCLAHE(clipLimit=self.contrast_limit, tileGridSize=(16, 16))
        enhanced = clahe.apply(gray)
        
        dimensions = enhanced.shape
        temp_frame = np.zeros((dimensions[0], dimensions[1], 3), dtype=np.uint8)
        
        # Simple mapping
        for i in range(dimensions[0]):
            for j in range(dimensions[1]):
                intensity = enhanced[i, j]
                if intensity < 85:
                    temp_frame[i, j] = (intensity * 2, intensity, 0)
                elif intensity < 170:
                    temp_frame[i, j] = (0, intensity, intensity)
                else:
                    temp_frame[i, j] = (0, 255 - intensity, intensity)
        
        return temp_frame

    def _to_grayscale(self, img):
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img.copy()