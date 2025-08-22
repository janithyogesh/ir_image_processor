import os
import cv2
import reportlab
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from tkinter import filedialog, messagebox

class FileHandler:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.report_dir = os.path.join(output_dir, "reports")
        os.makedirs(self.report_dir, exist_ok=True)

    def select_file(self):
        """Opens a file dialog for the user to select an image."""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.tif *.tiff *.bmp"),
            ("All files", "*.*")
        ]
        return filedialog.askopenfilename(title="Select an Image File", filetypes=file_types)

    def save_file_dialog(self):
        """Opens a save dialog for the user to choose a save location."""
        file_types = [
            ("JPEG files", "*.jpg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        return filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=file_types,
            initialdir=self.output_dir
        )

    def save_image(self, img, file_path):
        """Saves an image to a specified path."""
        try:
            # Convert to RGB for saving, then back to BGR for OpenCV
            save_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cv2.imwrite(file_path, cv2.cvtColor(save_img, cv2.COLOR_RGB2BGR))
        except Exception as e:
            raise IOError(f"Failed to save image: {e}")

    def plot_histogram(self, img):
        """Displays the histogram of a grayscale image."""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
            
        plt.figure(figsize=(8, 4))
        plt.hist(gray.ravel(), 256, [0, 256])
        plt.title('Image Histogram')
        plt.xlabel('Intensity')
        plt.ylabel('Frequency')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()