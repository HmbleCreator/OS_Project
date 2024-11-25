import customtkinter as ctk
import platform
import psutil
import os
import wmi
from datetime import datetime

class SystemInfoFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        try:
            self.wmi = wmi.WMI()
        except Exception:
            self.wmi = None

        self.grid_columnconfigure(1, weight=1)
        self.create_system_info()

    def get_processor_info(self):
        try:
            if self.wmi:
                cpu_info = self.wmi.Win32_Processor()[0]
                return cpu_info.Name
            return platform.processor()
        except Exception:
            return "Unable to detect CPU info"

    def get_gpu_info(self):
        try:
            if self.wmi:
                gpu_info = self.wmi.Win32_VideoController()[0]
                return f"{gpu_info.Name} ({gpu_info.AdapterRAM / (1024**3):.2f} GB)"
            return "Unable to detect GPU info"
        except Exception:
            return "Unable to detect GPU info"

    def get_ram_info(self):
        try:
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            used_gb = (memory.total - memory.available) / (1024**3)
            return f"{used_gb:.2f} GB / {total_gb:.2f} GB ({memory.percent}%)"
        except Exception:
            return "Unable to detect RAM info"

    def get_disk_info(self):
        try:
            partitions = psutil.disk_partitions()
            disk_info = []
            for partition in partitions:
                if os.name == 'nt' and ('cdrom' in partition.opts or partition.fstype == ''):
                    continue
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    total_gb = usage.total / (1024**3)
                    used_gb = usage.used / (1024**3)
                    disk_info.append(f"{partition.device}: {used_gb:.2f}GB/{total_gb:.2f}GB ({usage.percent}%)")
                except Exception:
                    continue
            return "\n".join(disk_info) if disk_info else "Unable to detect disk info"
        except Exception:
            return "Unable to detect disk info"

    def get_network_info(self):
        try:
            network_info = []
            for interface_name, interface_addresses in psutil.net_if_addrs().items():
                for addr in interface_addresses:
                    if addr.family == 2:  # IPv4
                        network_info.append(f"{interface_name}: {addr.address}")
            return "\n".join(network_info) if network_info else "No network interfaces found"
        except Exception:
            return "Unable to detect network info"

    def get_os_info(self):
        try:
            os_info = []
            os_info.append(f"System: {platform.system()}")
            os_info.append(f"Release: {platform.release()}")
            os_info.append(f"Version: {platform.version()}")
            if os.name == 'nt':
                os_info.append(f"Windows Edition: {platform.win32_edition()}")
            return " | ".join(os_info)
        except Exception:
            return f"System: {platform.system()}"

    def get_boot_time(self):
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            return boot_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "Unable to detect boot time"

    def add_info_row(self, label, value, row):
        label_widget = ctk.CTkLabel(self, text=f"{label}:", anchor="e")
        label_widget.grid(row=row, column=0, padx=(10, 5), pady=5, sticky="e")
        
        if "\n" in str(value):
            # For multiline values, create a text widget
            value_widget = ctk.CTkTextbox(self, height=60, width=300)
            value_widget.insert("1.0", value)
            value_widget.configure(state="disabled")
        else:
            value_widget = ctk.CTkLabel(self, text=str(value), anchor="w", wraplength=300)
        
        value_widget.grid(row=row, column=1, padx=(5, 10), pady=5, sticky="w")

    def create_system_info(self):
        row = 0
        
        # Operating System Information
        self.add_info_row("Operating System", self.get_os_info(), row)
        row += 1
        
        # CPU Information
        self.add_info_row("Processor", self.get_processor_info(), row)
        row += 1
        
        # GPU Information
        self.add_info_row("Graphics Card", self.get_gpu_info(), row)
        row += 1
        
        # RAM Information
        self.add_info_row("Memory (RAM)", self.get_ram_info(), row)
        row += 1
        
        # Disk Information
        self.add_info_row("Storage", self.get_disk_info(), row)
        row += 1
        
        # Network Information
        self.add_info_row("Network", self.get_network_info(), row)
        row += 1
        
        # System Boot Time
        self.add_info_row("System Boot Time", self.get_boot_time(), row)
        row += 1

        # Battery Information (if available)
        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery:
                battery_status = f"{battery.percent}% {'(Plugged In)' if battery.power_plugged else '(On Battery)'}"
                self.add_info_row("Battery", battery_status, row)
                row += 1