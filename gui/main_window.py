import ttkbootstrap as ttk
from .image_display import ImageDisplay
from .control_panel import ControlPanel
from core.image_processor import ImageProcessor
from core.background_remover import BackgroundRemover
from core.enhancement_engine import EnhancementEngine
from utils.file_handler import FileHandler
from utils.logger import setup_logging
import threading
import yaml
import os

class MainWindow(ttk.Window):
    def __init__(self, config):
        self.config = config
        super().__init__(title=self.config['app_name'], themename=self.config['gui_settings']['theme'])
        self.geometry(self.config['gui_settings']['window_size'])
        
        # Initialize core components
        self.logger = setup_logging()
        self.enhancement_engine = EnhancementEngine(
            contrast_limit=self.config['processing_settings']['default_contrast_limit'],
            num_clusters=self.config['processing_settings']['default_num_clusters']
        )
        self.background_remover = BackgroundRemover()
        self.processor = ImageProcessor(self.enhancement_engine, self.background_remover)
        self.file_handler = FileHandler(self.config['paths']['output_dir'])
        
        # --- UI Layout ---
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=ttk.BOTH, expand=True, padx=10, pady=10)
        
        # Image display area
        self.display_frame = ttk.Frame(self.main_frame)
        self.display_frame.pack(side=ttk.LEFT, fill=ttk.BOTH, expand=True)
        self.image_display = ImageDisplay(self.display_frame, self.logger)
        
        # Control panel area
        self.control_panel_frame = ttk.Frame(self.main_frame, width=300)
        self.control_panel_frame.pack(side=ttk.RIGHT, fill=ttk.Y, padx=(10, 0))
        self.control_panel = ControlPanel(self.control_panel_frame, self.enhancement_engine, self.logger)
        
        self.setup_bindings()
        self.setup_callbacks()
        
    def setup_bindings(self):
        """Set up keyboard shortcuts and events."""
        self.bind('<Control-o>', lambda e: self.open_image_dialog())
        self.bind('<Control-s>', lambda e: self.save_image())
        self.bind('<Control-z>', lambda e: self.undo_action())
        self.bind('<Control-y>', lambda e: self.redo_action())
        self.bind("<Configure>", self.on_resize)
        
    def setup_callbacks(self):
        """Connect button clicks and slider changes to methods."""
        self.control_panel.open_button.configure(command=self.open_image_dialog)
        self.control_panel.save_button.configure(command=self.save_image)
        self.control_panel.process_button.configure(command=self.process_image)
        self.control_panel.histogram_button.configure(command=self.show_histogram)
        self.control_panel.undo_button.configure(command=self.undo_action)
        self.control_panel.redo_button.configure(command=self.redo_action)
        
        self.control_panel.on_contrast_change = self.process_image
        self.control_panel.on_clusters_change = self.process_image
        self.control_panel.on_mode_change = self.process_image
        
    def open_image_dialog(self):
        """Opens a file dialog and starts the image loading process."""
        file_path = self.file_handler.select_file()
        if file_path:
            self.control_panel.status_bar.set_text("Loading and removing background...")
            self.control_panel.progress_bar.start()
            threading.Thread(target=self._load_and_process_thread, args=(file_path,), daemon=True).start()

    def _load_and_process_thread(self, file_path):
        """Threaded function to load and process the initial image."""
        try:
            self.processor.load_image(file_path)
            self.image_display.show_image(self.processor.original_image, 'original')
            self.processor.remove_background(file_path)
            self.image_display.show_image(self.processor.background_removed_image, 'bg_removed')
            self.processor.enhanced_image = self.processor.background_removed_image
            self.image_display.show_image(self.processor.enhanced_image, 'enhanced')
            self.control_panel.status_bar.set_text("Image loaded. Ready to enhance.")
        except Exception as e:
            self.logger.error(f"Error loading or removing background: {e}")
            self.control_panel.status_bar.set_text("Error: See log for details.")
            ttk.dialogs.Messagebox.show_error(title="Error", message=f"Failed to load image: {e}")
        finally:
            self.control_panel.progress_bar.stop()
            
    def process_image(self, *args):
        """Applies the selected enhancement mode to the image."""
        if self.processor.image is None:
            self.control_panel.status_bar.set_text("No image loaded.")
            return
            
        self.control_panel.status_bar.set_text("Processing image...")
        self.control_panel.progress_bar.start()
        
        threading.Thread(target=self._process_thread, daemon=True).start()
    
    def _process_thread(self):
        """Threaded function for image processing."""
        try:
            mode = self.control_panel.mode_var.get()
            self.processor.process_image(mode)
            self.image_display.show_image(self.processor.enhanced_image, 'enhanced')
            self.control_panel.status_bar.set_text("Processing complete.")
        except Exception as e:
            self.logger.error(f"Error processing image: {e}")
            self.control_panel.status_bar.set_text("Error: See log for details.")
            ttk.dialogs.Messagebox.show_error(title="Error", message=f"Failed to process image: {e}")
        finally:
            self.control_panel.progress_bar.stop()

    def save_image(self):
        """Saves the current enhanced image."""
        if self.processor.enhanced_image is None:
            self.control_panel.status_bar.set_text("No enhanced image to save.")
            return
            
        try:
            file_path = self.file_handler.save_file_dialog()
            if file_path:
                self.file_handler.save_image(self.processor.enhanced_image, file_path)
                self.control_panel.status_bar.set_text(f"Image saved to {os.path.basename(file_path)}")
        except Exception as e:
            self.logger.error(f"Error saving image: {e}")
            self.control_panel.status_bar.set_text("Error: Failed to save image.")
            ttk.dialogs.Messagebox.show_error(title="Error", message=f"Failed to save image: {e}")
            
    def show_histogram(self):
        """Displays the histogram of the current enhanced image."""
        if self.processor.enhanced_image is None:
            self.control_panel.status_bar.set_text("No image to analyze.")
            return
        self.file_handler.plot_histogram(self.processor.enhanced_image)
        
    def undo_action(self):
        """Handles the undo functionality."""
        img = self.processor.undo()
        if img is not None:
            self.image_display.show_image(img, 'enhanced')
            self.control_panel.status_bar.set_text("Undo successful.")
        else:
            self.control_panel.status_bar.set_text("No more steps to undo.")

    def redo_action(self):
        """Handles the redo functionality."""
        img = self.processor.redo()
        if img is not None:
            self.image_display.show_image(img, 'enhanced')
            self.control_panel.status_bar.set_text("Redo successful.")
        else:
            self.control_panel.status_bar.set_text("No more steps to redo.")

    def on_resize(self, event):
        """Handles window resize events to update image displays."""
        if event.widget == self:
            self.after(100, self.image_display.update_all_displays, 
                       self.processor.original_image, 
                       self.processor.background_removed_image, 
                       self.processor.enhanced_image)