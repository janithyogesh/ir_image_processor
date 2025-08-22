import io
import cv2
import numpy as np
from rembg import remove
from PIL import Image

class BackgroundRemover:
    def remove(self, image_path):
        """
        Removes the background from an image using the `rembg` library.
        Returns the image with a black background in OpenCV (BGR) format.
        """
        try:
            with open(image_path, 'rb') as input_file:
                input_data = input_file.read()
            
            output_data = remove(input_data)
            
            removed_bg = Image.open(io.BytesIO(output_data))
            
            black_bg = Image.new("RGBA", removed_bg.size, (0, 0, 0, 255))
            final_img = Image.alpha_composite(black_bg, removed_bg)
            
            # Convert to OpenCV format (numpy array)
            opencv_image = np.array(final_img.convert('RGB'))
            # Convert RGB to BGR
            opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2BGR)
            
            return opencv_image
        except Exception as e:
            raise RuntimeError(f"Failed to remove background: {e}")