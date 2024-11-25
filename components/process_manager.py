# components/process_manager.py

import customtkinter as ctk
import psutil
from datetime import datetime
import time
from utils.system_utils import get_size

class ProcessManagerFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Initialize variables
        self.processes = []
        self.sort_by = "cpu"
        self.sort_reverse = True
        self.process_limit = 25  # Default limit
        self.selected_pid = None
        
        # Column configurations
        self.columns = {
            "pid": {"name": "PID", "width": 100},
            "name": {"name": "Name", "width": 250},
            "cpu": {"name": "CPU %", "width": 100},
            "memory": {"name": "Memory", "width": 120},
            "status": {"name": "Status", "width": 100},
            "created": {"name": "Created", "width": 180}
        }
        
        # Create main layout
        self.create_header_frame()
        self.create_process_list()
        self.create_control_panel()

    def create_header_frame(self):
        # Header frame with controls
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(fill="x", padx=5, pady=5)
        
        # Left side controls
        left_frame = ctk.CTkFrame(self.header_frame)
        left_frame.pack(side="left", fill="x", expand=True)
        
        # Search entry
        self.search_entry = ctk.CTkEntry(left_frame, placeholder_text="Search processes...", width=200)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_processes)
        
        # Process count selection
        self.count_label = ctk.CTkLabel(left_frame, text="Show:")
        self.count_label.pack(side="left", padx=(20, 5))
        
        self.count_combobox = ctk.CTkComboBox(
            left_frame,
            values=["25", "50", "100", "All"],
            command=self.change_process_limit,
            width=100
        )
        self.count_combobox.pack(side="left", padx=5)
        self.count_combobox.set("25")
        
        # Right side controls
        right_frame = ctk.CTkFrame(self.header_frame)
        right_frame.pack(side="right", padx=5)
        
        # Sort controls
        self.sort_label = ctk.CTkLabel(right_frame, text="Sort by:")
        self.sort_label.pack(side="left", padx=5)
        
        self.sort_combobox = ctk.CTkComboBox(
            right_frame,
            values=["CPU", "Memory", "Name", "PID"],
            command=self.change_sort,
            width=100
        )
        self.sort_combobox.pack(side="left", padx=5)
        self.sort_combobox.set("CPU")

    def create_process_list(self):
        # Create table header
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        # Create headers with specific widths
        for col, config in self.columns.items():
            frame = ctk.CTkFrame(self.table_frame, width=config["width"], height=30)
            frame.pack_propagate(False)
            frame.pack(side="left", padx=1)
            
            label = ctk.CTkLabel(frame, text=config["name"], font=("Arial", 12, "bold"))
            label.pack(fill="both", expand=True)
        
        # Create scrollable frame for processes
        self.process_container = ctk.CTkScrollableFrame(self)
        self.process_container.pack(fill="both", expand=True, padx=5, pady=(0, 5))

    def create_control_panel(self):
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(fill="x", padx=5, pady=5)
        
        # End Process button
        self.end_process_btn = ctk.CTkButton(
            self.control_frame,
            text="End Process",
            command=self.end_selected_process,
            width=120
        )
        self.end_process_btn.pack(side="left", padx=5)
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            self.control_frame,
            text="Refresh",
            command=self.update_processes,
            width=120
        )
        self.refresh_btn.pack(side="left", padx=5)
        
        # Process count label
        self.process_count_label = ctk.CTkLabel(self.control_frame, text="")
        self.process_count_label.pack(side="right", padx=10)

    def create_process_row(self, process):
        frame = ctk.CTkFrame(self.process_container)
        frame.pack(fill="x", pady=1)
        
        # Create cells with specific widths
        pid_frame = ctk.CTkFrame(frame, width=self.columns["pid"]["width"])
        pid_frame.pack_propagate(False)
        pid_frame.pack(side="left", padx=1)
        ctk.CTkLabel(pid_frame, text=str(process['pid'])).pack(fill="both", expand=True)
        
        name_frame = ctk.CTkFrame(frame, width=self.columns["name"]["width"])
        name_frame.pack_propagate(False)
        name_frame.pack(side="left", padx=1)
        ctk.CTkLabel(name_frame, text=process['name']).pack(fill="both", expand=True)
        
        cpu_frame = ctk.CTkFrame(frame, width=self.columns["cpu"]["width"])
        cpu_frame.pack_propagate(False)
        cpu_frame.pack(side="left", padx=1)
        ctk.CTkLabel(cpu_frame, text=f"{process['cpu']:.1f}%").pack(fill="both", expand=True)
        
        memory_frame = ctk.CTkFrame(frame, width=self.columns["memory"]["width"])
        memory_frame.pack_propagate(False)
        memory_frame.pack(side="left", padx=1)
        ctk.CTkLabel(memory_frame, text=process['memory']).pack(fill="both", expand=True)
        
        status_frame = ctk.CTkFrame(frame, width=self.columns["status"]["width"])
        status_frame.pack_propagate(False)
        status_frame.pack(side="left", padx=1)
        ctk.CTkLabel(status_frame, text=process['status']).pack(fill="both", expand=True)
        
        created_frame = ctk.CTkFrame(frame, width=self.columns["created"]["width"])
        created_frame.pack_propagate(False)
        created_frame.pack(side="left", padx=1)
        ctk.CTkLabel(created_frame, text=process['created']).pack(fill="both", expand=True)
        
        # Bind click event
        frame.bind("<Button-1>", lambda e, p=process: self.select_process(e, p))
        for child in frame.winfo_children():
            child.bind("<Button-1>", lambda e, p=process: self.select_process(e, p))
        
        return frame

    def update_processes(self):
        # Clear existing process widgets
        for widget in self.process_container.winfo_children():
            widget.destroy()
        
        try:
            # Get process information
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info',
                                          'status', 'create_time']):
                try:
                    info = proc.info
                    memory = get_size(info['memory_info'].rss)
                    created = datetime.fromtimestamp(info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                    
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'],
                        'cpu': info['cpu_percent'],
                        'memory': memory,
                        'memory_raw': info['memory_info'].rss,
                        'status': info['status'],
                        'created': created
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Sort processes
            if self.sort_by == "cpu":
                processes.sort(key=lambda x: x['cpu'], reverse=self.sort_reverse)
            elif self.sort_by == "memory":
                processes.sort(key=lambda x: x['memory_raw'], reverse=self.sort_reverse)
            elif self.sort_by == "name":
                processes.sort(key=lambda x: x['name'].lower(), reverse=self.sort_reverse)
            elif self.sort_by == "pid":
                processes.sort(key=lambda x: x['pid'], reverse=self.sort_reverse)
            
            # Apply process limit
            if self.process_limit != "All":
                processes = processes[:int(self.process_limit)]
            
            # Display processes
            for proc in processes:
                self.create_process_row(proc)
            
            # Update process count label
            total_processes = len(psutil.pids())
            shown_processes = len(processes)
            self.process_count_label.configure(
                text=f"Showing {shown_processes} of {total_processes} processes"
            )
            
        except Exception as e:
            error_label = ctk.CTkLabel(self.process_container, 
                                     text=f"Error updating processes: {str(e)}")
            error_label.pack(pady=10)

    def select_process(self, event, process):
        # Deselect all other frames
        for widget in self.process_container.winfo_children():
            widget.configure(fg_color=("gray86", "gray17"))
            for child in widget.winfo_children():
                child.configure(fg_color=("gray86", "gray17"))
        
        # Select clicked frame
        event.widget.master.configure(fg_color=("gray76", "gray27"))
        for child in event.widget.master.winfo_children():
            child.configure(fg_color=("gray76", "gray27"))
        
        self.selected_pid = process['pid']

    def end_selected_process(self):
        if hasattr(self, 'selected_pid'):
            try:
                psutil.Process(self.selected_pid).terminate()
                self.update_processes()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def filter_processes(self, event=None):
        search_text = self.search_entry.get().lower()
        for frame in self.process_container.winfo_children():
            # Get process name from the second frame (name column)
            process_name = frame.winfo_children()[1].winfo_children()[0].cget("text").lower()
            if search_text in process_name:
                frame.pack(fill="x", pady=1)
            else:
                frame.pack_forget()

    def change_sort(self, choice):
        self.sort_by = choice.lower()
        self.update_processes()

    def change_process_limit(self, choice):
        self.process_limit = choice
        self.update_processes()