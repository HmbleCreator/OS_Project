# components/optimization.py
import customtkinter as ctk
import psutil
import platform
import subprocess
import threading
from tkinter import messagebox
import os

class OptimizationFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Create main scrollable frame
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Performance Mode Section
        self.create_performance_section()
        
        # Memory Optimization Section
        self.create_memory_section()
        
        # CPU Optimization Section
        self.create_cpu_section()
        
        # Battery Optimization Section (if applicable)
        if hasattr(psutil, "sensors_battery"):
            self.create_battery_section()
        
        # Status Section
        self.create_status_section()
        
        # Initialize optimization status
        self.is_optimizing = False
    
    def create_performance_section(self):
        """Create the performance mode section"""
        performance_frame = ctk.CTkFrame(self.main_frame)
        performance_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(performance_frame, text="Performance Mode",
                    font=("Arial", 16, "bold")).pack(pady=5)
        
        self.mode_var = ctk.StringVar(value="Balanced")
        modes = ["Power Saver", "Balanced", "Performance"]
        
        for mode in modes:
            radio = ctk.CTkRadioButton(
                performance_frame,
                text=mode,
                variable=self.mode_var,
                value=mode,
                command=self.change_mode
            )
            radio.pack(pady=2)
        
        # Mode description
        self.mode_description = ctk.CTkLabel(
            performance_frame,
            text="Balanced mode provides optimal performance and energy usage",
            wraplength=300
        )
        self.mode_description.pack(pady=5)
    
    def create_memory_section(self):
        """Create the memory optimization section"""
        memory_frame = ctk.CTkFrame(self.main_frame)
        memory_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(memory_frame, text="Memory Optimization",
                    font=("Arial", 16, "bold")).pack(pady=5)
        
        # Memory usage progress bar
        self.memory_progress = ctk.CTkProgressBar(memory_frame)
        self.memory_progress.pack(pady=5)
        
        self.memory_label = ctk.CTkLabel(memory_frame, text="Memory Usage: 0%")
        self.memory_label.pack(pady=2)
        
        # Memory optimization options
        options_frame = ctk.CTkFrame(memory_frame)
        options_frame.pack(fill="x", pady=5, padx=10)
        
        self.clear_standby = ctk.CTkCheckBox(options_frame, text="Clear Standby List")
        self.clear_standby.pack(pady=2)
        
        self.clear_cache = ctk.CTkCheckBox(options_frame, text="Clear System Cache")
        self.clear_cache.pack(pady=2)
        
        ctk.CTkButton(
            memory_frame,
            text="Optimize Memory",
            command=self.optimize_memory,
            fg_color="green",
            hover_color="dark green"
        ).pack(pady=10)
    
    def create_cpu_section(self):
        """Create the CPU optimization section"""
        cpu_frame = ctk.CTkFrame(self.main_frame)
        cpu_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(cpu_frame, text="CPU Optimization",
                    font=("Arial", 16, "bold")).pack(pady=5)
        
        # CPU usage progress bar
        self.cpu_progress = ctk.CTkProgressBar(cpu_frame)
        self.cpu_progress.pack(pady=5)
        
        self.cpu_label = ctk.CTkLabel(cpu_frame, text="CPU Usage: 0%")
        self.cpu_label.pack(pady=2)
        
        # CPU optimization options
        options_frame = ctk.CTkFrame(cpu_frame)
        options_frame.pack(fill="x", pady=5, padx=10)
        
        self.optimize_services = ctk.CTkCheckBox(
            options_frame,
            text="Optimize Background Services"
        )
        self.optimize_services.pack(pady=2)
        
        self.optimize_processes = ctk.CTkCheckBox(
            options_frame,
            text="Adjust Process Priorities"
        )
        self.optimize_processes.pack(pady=2)
        
        ctk.CTkButton(
            cpu_frame,
            text="Optimize CPU",
            command=self.optimize_cpu,
            fg_color="green",
            hover_color="dark green"
        ).pack(pady=10)
    
    def create_battery_section(self):
        """Create the battery optimization section"""
        battery_frame = ctk.CTkFrame(self.main_frame)
        battery_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(battery_frame, text="Battery Optimization",
                    font=("Arial", 16, "bold")).pack(pady=5)
        
        # Battery status
        self.battery_label = ctk.CTkLabel(battery_frame, text="Battery Status: N/A")
        self.battery_label.pack(pady=2)
        
        # Battery optimization options
        options_frame = ctk.CTkFrame(battery_frame)
        options_frame.pack(fill="x", pady=5, padx=10)
        
        self.screen_brightness = ctk.CTkCheckBox(
            options_frame,
            text="Optimize Screen Brightness"
        )
        self.screen_brightness.pack(pady=2)
        
        self.background_apps = ctk.CTkCheckBox(
            options_frame,
            text="Limit Background Apps"
        )
        self.background_apps.pack(pady=2)
        
        ctk.CTkButton(
            battery_frame,
            text="Optimize Battery",
            command=self.optimize_battery,
            fg_color="green",
            hover_color="dark green"
        ).pack(pady=10)
    
    def create_status_section(self):
        """Create the status section"""
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill="x", pady=10)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready to optimize",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=5)
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self.monitor_system,
            daemon=True
        )
        self.monitoring_thread.start()
    
    def change_mode(self):
        """Handle performance mode changes"""
        mode = self.mode_var.get()
        descriptions = {
            "Power Saver": "Maximizes battery life by reducing system performance",
            "Balanced": "Provides optimal performance and energy usage",
            "Performance": "Maximizes system performance at the cost of higher energy usage"
        }
        
        self.mode_description.configure(text=descriptions[mode])
        
        try:
            if platform.system() == "Windows":
                if mode == "Power Saver":
                    os.system("powercfg /s a1841308-3541-4fab-bc81-f71556f20b4a")
                elif mode == "Balanced":
                    os.system("powercfg /s 381b4222-f694-41f0-9685-ff5bb260df2e")
                elif mode == "Performance":
                    os.system("powercfg /s 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c")
            
            self.status_label.configure(
                text=f"Successfully switched to {mode} mode"
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to change performance mode: {str(e)}"
            )
    
    def optimize_memory(self):
        """Optimize system memory"""
        if self.is_optimizing:
            return
        
        self.is_optimizing = True
        self.status_label.configure(text="Optimizing memory...")
        
        def optimize():
            try:
                if platform.system() == "Windows":
                    if self.clear_standby.get():
                        subprocess.run(["powershell", "Clear-RecycleBin", "-Force"],
                                    capture_output=True)
                    
                    if self.clear_cache.get():
                        subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
                        if os.path.exists(os.path.expanduser("~\\AppData\\Local\\Temp")):
                            for item in os.listdir(os.path.expanduser("~\\AppData\\Local\\Temp")):
                                try:
                                    path = os.path.join(os.path.expanduser("~\\AppData\\Local\\Temp"), item)
                                    if os.path.isfile(path):
                                        os.unlink(path)
                                except Exception:
                                    pass
                
                elif platform.system() == "Linux":
                    if self.clear_cache.get():
                        os.system("sync && echo 3 > /proc/sys/vm/drop_caches")
                
                self.status_label.configure(text="Memory optimization completed")
            except Exception as e:
                self.status_label.configure(
                    text=f"Memory optimization failed: {str(e)}"
                )
            finally:
                self.is_optimizing = False
        
        threading.Thread(target=optimize, daemon=True).start()
    
    def optimize_cpu(self):
        """Optimize CPU performance"""
        if self.is_optimizing:
            return
        
        self.is_optimizing = True
        self.status_label.configure(text="Optimizing CPU...")
        
        def optimize():
            try:
                if platform.system() == "Windows":
                    if self.optimize_services.get():
                        # Optimize non-essential services
                        subprocess.run(
                            ["sc", "config", "SysMain", "start=", "disabled"],
                            capture_output=True
                        )
                    
                    if self.optimize_processes.get():
                        # Set process priorities
                        for proc in psutil.process_iter(['name', 'pid']):
                            try:
                                if proc.name().lower() in ['chrome.exe', 'firefox.exe', 'edge.exe']:
                                    p = psutil.Process(proc.pid)
                                    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                            except Exception:
                                continue
                
                self.status_label.configure(text="CPU optimization completed")
            except Exception as e:
                self.status_label.configure(
                    text=f"CPU optimization failed: {str(e)}"
                )
            finally:
                self.is_optimizing = False
        
        threading.Thread(target=optimize, daemon=True).start()
    
    def optimize_battery(self):
        """Optimize battery life"""
        if self.is_optimizing:
            return
        
        self.is_optimizing = True
        self.status_label.configure(text="Optimizing battery...")
        
        def optimize():
            try:
                if platform.system() == "Windows":
                    if self.screen_brightness.get():
                        # Reduce screen brightness
                        subprocess.run(
                            ["powershell", "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,50)"],
                            capture_output=True
                        )
                    
                    if self.background_apps.get():
                        # Limit background apps
                        subprocess.run(
                            ["powercfg", "/setacvalueindex", "scheme_current", "sub_processor", "PROCTHROTTLEMAX", "50"],
                            capture_output=True
                        )
                
                self.status_label.configure(text="Battery optimization completed")
            except Exception as e:
                self.status_label.configure(
                    text=f"Battery optimization failed: {str(e)}"
                )
            finally:
                self.is_optimizing = False
        
        threading.Thread(target=optimize, daemon=True).start()
    
    def monitor_system(self):
        """Monitor system resources"""
        while True:
            try:
                # Update CPU usage
                cpu_percent = psutil.cpu_percent()
                self.cpu_progress.set(cpu_percent / 100)
                self.cpu_label.configure(text=f"CPU Usage: {cpu_percent}%")
                
                # Update memory usage
                memory = psutil.virtual_memory()
                self.memory_progress.set(memory.percent / 100)
                self.memory_label.configure(text=f"Memory Usage: {memory.percent}%")
                
                # Update battery status if available
                if hasattr(psutil, "sensors_battery"):
                    battery = psutil.sensors_battery()
                    if battery:
                        status = "Plugged In" if battery.power_plugged else "On Battery"
                        self.battery_label.configure(
                            text=f"Battery Status: {battery.percent}% ({status})"
                        )
            
            except Exception:
                pass
            
            finally:
                threading.Event().wait(2)  # Update every 2 seconds