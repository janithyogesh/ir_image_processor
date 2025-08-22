import ttkbootstrap as ttk
import yaml
import os
from gui.main_window import MainWindow
from utils.logger import setup_logging

def load_config(config_path):
    """Loads and returns the application configuration."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing configuration file: {e}")
        return None

def main():
    # Set up logger
    logger = setup_logging()
    
    # Load configuration
    config_path = os.path.join("config", "config.yaml")
    config = load_config(config_path)
    if not config:
        logger.error("Failed to load configuration. Exiting.")
        return

    logger.info("Starting IR Image Processor application...")
    
    root = ttk.Window(title="IR Image Processor", themename=config['gui_settings']['theme'])
    app = MainWindow(config)
    
    root.mainloop()

if __name__ == "__main__":
    # Create the directory structure if it doesn't exist
    for path in ['config', 'core', 'gui', 'utils', 'assets/icons', 'assets/themes', 'output/enhanced', 'output/reports', 'output/temp']:
        os.makedirs(path, exist_ok=True)
        
    main()