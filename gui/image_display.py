import ttkbootstrap as ttk
import cv2
from PIL import Image, ImageTk

class ImageDisplay(ttk.Frame):
    """Manages the display of original, background-removed, and enhanced images."""
    def __init__(self, parent, logger):
        super().__init__(parent)
        self.pack(fill=ttk.BOTH, expand=True, padx=10, pady=10)
        self.logger = logger
        self.canvases = {}
        self.images = {'original': None, 'bg_removed': None, 'enhanced': None}
        self.setup_canvases()
        
    def setup_canvases(self):
        """Creates and organizes the canvas widgets."""
        labels = ["Original Image", "Background Removed", "Enhanced Image"]
        keys = ['original', 'bg_removed', 'enhanced']
        
        for i, (label, key) in enumerate(zip(labels, keys)):
            frame = ttk.LabelFrame(self, text=label)
            frame.pack(side=ttk.LEFT, fill=ttk.BOTH, expand=True, padx=5)
            
            canvas = ttk.Canvas(frame, bg="black")
            canvas.pack(fill=ttk.BOTH, expand=True, padx=5, pady=5)
            self.canvases[key] = canvas
            
    def show_image(self, img, canvas_key):
        """Displays a given OpenCV image on the specified canvas."""
        if img is None:
            return
            
        self.images[canvas_key] = img.copy()
        canvas = self.canvases[canvas_key]
        
        # This call handles the actual display logic, including resizing
        self._display_on_canvas(img, canvas)

    def _display_on_canvas(self, img, canvas):
        if img is None:
            canvas.delete("all")
            return
        
        # Convert to RGB for PIL
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Get canvas dimensions
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            # Calculate resize ratio
            img_height, img_width = img_rgb.shape[:2]
            ratio = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            if new_width > 0 and new_height > 0:
                img_resized = cv2.resize(img_rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)
                photo = ImageTk.PhotoImage(image=Image.fromarray(img_resized))
                
                canvas.delete("all")
                canvas.create_image(canvas_width // 2, canvas_height // 2, image=photo, anchor=ttk.CENTER)
                canvas.image = photo  # Keep a reference

    def update_all_displays(self, original_img, bg_removed_img, enhanced_img):
        """Re-renders all images, typically on a resize event."""
        self._display_on_canvas(original_img, self.canvases['original'])
        self._display_on_canvas(bg_removed_img, self.canvases['bg_removed'])
        self._display_on_canvas(enhanced_img, self.canvases['enhanced'])