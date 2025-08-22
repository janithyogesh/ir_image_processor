import cv2
import numpy as np
import io
from rembg import remove
from PIL import Image

class ImageProcessor:
    """
    Manages the loading, state, and processing pipeline of an image.
    Acts as an orchestrator for the background removal and enhancement engines.
    """
    def __init__(self, enhancement_engine, background_remover):
        self.image = None
        self.original_image = None
        self.background_removed_image = None
        self.enhanced_image = None
        self.history = []
        self.history_index = -1
        self.enhancement_engine = enhancement_engine
        self.background_remover = background_remover

    def load_image(self, image_path):
        """Loads an image from the specified path."""
        try:
            self.original_image = cv2.imread(image_path)
            if self.original_image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Store initial state for undo functionality
            self.history = [self.original_image.copy()]
            self.history_index = 0
            
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False

    def remove_background(self, image_path):
        """Removes the background and updates the image state."""
        try:
            self.background_removed_image = self.background_remover.remove(image_path)
            self.image = self.background_removed_image.copy()
            self.push_history(self.image)
            return True
        except Exception as e:
            print(f"Error removing background: {e}")
            return False

    def process_image(self, mode):
        """Applies enhancement based on the selected mode."""
        if self.image is None:
            raise RuntimeError("No image loaded to process.")
        
        # Apply the enhancement
        if mode == 0:  # Background Removed Only
            self.enhanced_image = self.image.copy()
        elif mode == 1:  # Basic Enhancement
            self.enhanced_image = self.enhancement_engine.enhance_basic(self.image)
        elif mode == 2:  # Advanced Enhancement
            self.enhanced_image = self.enhancement_engine.enhance_advanced(self.image)
        elif mode == 3:  # Segmentation
            self.enhanced_image = self.enhancement_engine.segment(self.image)
        elif mode == 4:  # False Color
            self.enhanced_image = self.enhancement_engine.false_color(self.image)
        
        self.push_history(self.enhanced_image)
        return self.enhanced_image

    def push_history(self, new_state):
        """Adds a new image state to the history stack for undo/redo."""
        # Discard any "future" states if we're not at the end of the history
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(new_state.copy())
        self.history_index += 1

    def undo(self):
        """Reverts to the previous image state."""
        if self.history_index > 0:
            self.history_index -= 1
            self.enhanced_image = self.history[self.history_index]
            return self.enhanced_image
        return None

    def redo(self):
        """Moves to the next image state in the history."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.enhanced_image = self.history[self.history_index]
            return self.enhanced_image
        return None