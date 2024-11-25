import customtkinter as ctk
import psutil
import platform
from datetime import datetime
import threading
import time
from pathlib import Path
from components.system_info import SystemInfoFrame
from components.process_manager import ProcessManagerFrame
from components.performance import PerformanceFrame
from components.optimization import OptimizationFrame
from utils.system_utils import get_size

# Conditionally import WMI if on Windows
if platform.system() == "Windows":
    import wmi  # Ensure you have the wmi package installed

class TaskManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Advanced Task Manager")
        self.geometry("1200x800")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Add tabs
        self.tab_processes = self.tabview.add("Processes")
        self.tab_performance = self.tabview.add("Performance")
        self.tab_optimization = self.tabview.add("Optimization")
        self.tab_system = self.tabview.add("System Info")
        
        # Initialize components
        self.process_frame = ProcessManagerFrame(self.tab_processes)
        self.process_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.performance_frame = PerformanceFrame(self.tab_performance)
        self.performance_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.optimization_frame = OptimizationFrame(self.tab_optimization)
        self.optimization_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.system_frame = SystemInfoFrame(self.tab_system)
        self.system_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
    
    def update_loop(self):
        while True:
            try:
                # Use manual_refresh instead of update_processes
                self.process_frame.manual_refresh(0)
                self.performance_frame.update_metrics()
                time.sleep(1)
            except Exception as e:
                print(f"Error in update loop: {e}")

if __name__ == "__main__":
    app = TaskManager()
    app.mainloop()