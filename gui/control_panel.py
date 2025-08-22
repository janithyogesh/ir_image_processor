import ttkbootstrap as ttk
from utils.logger import setup_logging
import threading

class ControlPanel(ttk.Frame):
    def __init__(self, parent, enhancement_engine, logger):
        super().__init__(parent)
        self.pack(fill=ttk.BOTH, expand=True)
        self.enhancement_engine = enhancement_engine
        self.logger = logger
        
        self.setup_widgets()
        
    def setup_widgets(self):
        """Creates all control widgets."""
        self.file_frame = ttk.LabelFrame(self, text="File Operations")
        self.file_frame.pack(fill=ttk.X, padx=5, pady=5)
        self.open_button = ttk.Button(self.file_frame, text="Open Image")
        self.open_button.pack(fill=ttk.X, padx=5, pady=5)
        self.save_button = ttk.Button(self.file_frame, text="Save Enhanced Image")
        self.save_button.pack(fill=ttk.X, padx=5, pady=5)
        
        self.process_frame = ttk.LabelFrame(self, text="Processing Options")
        self.process_frame.pack(fill=ttk.X, padx=5, pady=5)
        
        # Mode selection
        ttk.Label(self.process_frame, text="Mode:").pack(padx=5, pady=2, anchor=ttk.W)
        self.mode_var = ttk.IntVar(value=0)
        modes = ["Background Removed Only", "Basic Enhancement", "Advanced Enhancement", "Segmentation", "False Color"]
        self.mode_combo = ttk.Combobox(self.process_frame, values=modes, state="readonly", textvariable=self.mode_var)
        self.mode_combo.pack(fill=ttk.X, padx=5, pady=2)
        self.mode_combo.bind("<<ComboboxSelected>>", self.on_mode_change)

        # Contrast slider
        ttk.Label(self.process_frame, text="Contrast Limit:").pack(padx=5, pady=2, anchor=ttk.W)
        self.contrast_var = ttk.DoubleVar(value=self.enhancement_engine.contrast_limit)
        contrast_slider = ttk.Scale(self.process_frame, from_=1.0, to=40.0, variable=self.contrast_var)
        contrast_slider.pack(fill=ttk.X, padx=5, pady=2)
        contrast_slider.bind("<ButtonRelease-1>", self.on_contrast_change)
        
        # Clusters slider
        ttk.Label(self.process_frame, text="K-Means Clusters:").pack(padx=5, pady=2, anchor=ttk.W)
        self.clusters_var = ttk.IntVar(value=self.enhancement_engine.num_clusters)
        clusters_slider = ttk.Scale(self.process_frame, from_=2, to=10, variable=self.clusters_var, orient=ttk.HORIZONTAL)
        clusters_slider.pack(fill=ttk.X, padx=5, pady=2)
        clusters_slider.bind("<ButtonRelease-1>", self.on_clusters_change)
        
        self.process_button = ttk.Button(self.process_frame, text="Process Image", bootstyle="success")
        self.process_button.pack(fill=ttk.X, padx=5, pady=5)

        self.analysis_frame = ttk.LabelFrame(self, text="Analysis & Tools")
        self.analysis_frame.pack(fill=ttk.X, padx=5, pady=5)
        self.histogram_button = ttk.Button(self.analysis_frame, text="Show Histogram")
        self.histogram_button.pack(fill=ttk.X, padx=5, pady=5)
        
        self.history_frame = ttk.LabelFrame(self, text="History")
        self.history_frame.pack(fill=ttk.X, padx=5, pady=5)
        history_button_frame = ttk.Frame(self.history_frame)
        history_button_frame.pack(fill=ttk.X, padx=5, pady=5)
        self.undo_button = ttk.Button(history_button_frame, text="Undo", bootstyle="secondary")
        self.undo_button.pack(side=ttk.LEFT, expand=True, fill=ttk.X, padx=2)
        self.redo_button = ttk.Button(history_button_frame, text="Redo", bootstyle="secondary")
        self.redo_button.pack(side=ttk.RIGHT, expand=True, fill=ttk.X, padx=2)
        
        self.status_bar_frame = ttk.Frame(self)
        self.status_bar_frame.pack(side=ttk.BOTTOM, fill=ttk.X, padx=5, pady=5)
        self.status_bar = ttk.Label(self.status_bar_frame, text="Ready", relief=ttk.SUNKEN, anchor=ttk.W)
        self.status_bar.pack(fill=ttk.X, side=ttk.BOTTOM)
        self.progress_bar = ttk.Progressbar(self.status_bar_frame, orient=ttk.HORIZONTAL, mode='indeterminate')
        self.progress_bar.pack(fill=ttk.X, side=ttk.BOTTOM)

    def on_mode_change(self, event):
        """Callback for when the enhancement mode is changed."""
        self.enhancement_engine.mode = self.mode_combo.current()
        if hasattr(self, 'on_mode_change'):
            self.on_mode_change()

    def on_contrast_change(self, event):
        """Callback for when the contrast slider is changed."""
        self.enhancement_engine.contrast_limit = self.contrast_var.get()
        if hasattr(self, 'on_contrast_change'):
            self.on_contrast_change()
    
    def on_clusters_change(self, event):
        """Callback for when the clusters slider is changed."""
        self.enhancement_engine.num_clusters = self.clusters_var.get()
        if hasattr(self, 'on_clusters_change'):
            self.on_clusters_change()