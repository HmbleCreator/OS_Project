import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from collections import deque
import GPUtil
import datetime
import matplotlib.animation as animation

class PerformanceFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Initialize data storage with empty values
        self.max_points = 50
        self.cpu_data = deque([0] * self.max_points, maxlen=self.max_points)
        self.memory_data = deque([0] * self.max_points, maxlen=self.max_points)
        self.temp_data = deque([0] * self.max_points, maxlen=self.max_points)
        self.network_sent_data = deque([0] * self.max_points, maxlen=self.max_points)
        self.network_recv_data = deque([0] * self.max_points, maxlen=self.max_points)
        self.last_net_io = psutil.net_io_counters()
        self.last_update_time = datetime.datetime.now()

        # Create matplotlib figure with dark theme
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(12, 8))
        self.fig.patch.set_facecolor('#1e1e1e')
        
        # Setup subplots
        self.setup_plots()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Start animation
        self.ani = animation.FuncAnimation(
            self.fig, self.update_plots, interval=1000, blit=False)

    def setup_plots(self):
        # CPU Usage
        self.ax_cpu = self.fig.add_subplot(321)
        self.cpu_line, = self.ax_cpu.plot([], [], 'b-', label='CPU Usage')
        self.ax_cpu.set_ylim(0, 100)
        self.ax_cpu.set_xlim(0, self.max_points)
        self.ax_cpu.set_title('CPU Usage (%)')
        self.ax_cpu.grid(True, linestyle='--', alpha=0.7)
        
        # Memory Usage
        self.ax_mem = self.fig.add_subplot(322)
        self.mem_line, = self.ax_mem.plot([], [], 'g-', label='Memory Usage')
        self.ax_mem.set_ylim(0, 100)
        self.ax_mem.set_xlim(0, self.max_points)
        self.ax_mem.set_title('Memory Usage (%)')
        self.ax_mem.grid(True, linestyle='--', alpha=0.7)
        
        # CPU Temperature
        self.ax_temp = self.fig.add_subplot(323)
        self.temp_line, = self.ax_temp.plot([], [], 'r-', label='Temperature')
        self.ax_temp.set_ylim(0, 100)
        self.ax_temp.set_xlim(0, self.max_points)
        self.ax_temp.set_title('CPU Temperature (°C)')
        self.ax_temp.grid(True, linestyle='--', alpha=0.7)
        
        # GPU Usage
        self.ax_gpu = self.fig.add_subplot(324)
        self.ax_gpu.set_title('GPU Usage')
        self.ax_gpu.grid(True, linestyle='--', alpha=0.7)
        
        # Network Usage
        self.ax_net = self.fig.add_subplot(325)
        self.net_sent_line, = self.ax_net.plot([], [], 'c-', label='Upload')
        self.net_recv_line, = self.ax_net.plot([], [], 'm-', label='Download')
        self.ax_net.set_ylim(0, 1)  # Will auto-adjust based on actual usage
        self.ax_net.set_xlim(0, self.max_points)
        self.ax_net.set_title('Network Usage (MB/s)')
        self.ax_net.grid(True, linestyle='--', alpha=0.7)
        self.ax_net.legend()
        
        # Disk Usage
        self.ax_disk = self.fig.add_subplot(326)
        self.ax_disk.set_title('Disk Usage')
        
        # Style adjustments
        for ax in [self.ax_cpu, self.ax_mem, self.ax_temp, self.ax_gpu, self.ax_net, self.ax_disk]:
            ax.set_facecolor('#2d2d2d')
            
        self.fig.tight_layout()

    def update_network_data(self):
        current_time = datetime.datetime.now()
        current_net_io = psutil.net_io_counters()
        time_delta = (current_time - self.last_update_time).total_seconds()
        
        # Calculate MB/s
        sent_speed = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / (1024 * 1024 * time_delta)
        recv_speed = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / (1024 * 1024 * time_delta)
        
        self.network_sent_data.append(sent_speed)
        self.network_recv_data.append(recv_speed)
        
        self.last_net_io = current_net_io
        self.last_update_time = current_time
        
        return sent_speed, recv_speed

    def update_plots(self, frame):
        # Update CPU data
        cpu_percent = psutil.cpu_percent()
        self.cpu_data.append(cpu_percent)
        self.cpu_line.set_data(range(len(self.cpu_data)), self.cpu_data)
        
        # Update Memory data
        memory = psutil.virtual_memory()
        self.memory_data.append(memory.percent)
        self.mem_line.set_data(range(len(self.memory_data)), self.memory_data)
        
        # Update Temperature data
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        current_temp = entries[0].current
                        self.temp_data.append(current_temp)
                        self.temp_line.set_data(range(len(self.temp_data)), self.temp_data)
                        break
        
        # Update GPU info
        self.ax_gpu.clear()
        self.ax_gpu.set_title('GPU Usage')
        self.ax_gpu.grid(True, linestyle='--', alpha=0.7)
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_loads = [gpu.load * 100 for gpu in gpus]
                gpu_memories = [gpu.memoryUtil * 100 for gpu in gpus]
                x = np.arange(len(gpus))
                width = 0.35
                
                self.ax_gpu.bar(x - width/2, gpu_loads, width, label='Load %')
                self.ax_gpu.bar(x + width/2, gpu_memories, width, label='Memory %')
                self.ax_gpu.set_xticks(x)
                self.ax_gpu.set_xticklabels([f'GPU {i}' for i in range(len(gpus))])
                self.ax_gpu.legend()
        except:
            self.ax_gpu.text(0.5, 0.5, 'No GPU Info Available', 
                           horizontalalignment='center')
        
        # Update Network data
        sent_speed, recv_speed = self.update_network_data()
        self.net_sent_line.set_data(range(len(self.network_sent_data)), self.network_sent_data)
        self.net_recv_line.set_data(range(len(self.network_recv_data)), self.network_recv_data)
        
        # Auto-adjust network graph scale
        max_speed = max(max(self.network_sent_data), max(self.network_recv_data))
        self.ax_net.set_ylim(0, max_speed * 1.2 if max_speed > 0 else 1)
        
        # Update Disk Usage
        self.ax_disk.clear()
        self.ax_disk.set_title('Disk Usage')
        disk = psutil.disk_usage('/')
        sizes = [disk.used, disk.free]
        labels = [f'Used\n{disk.percent}%', f'Free\n{100-disk.percent}%']
        colors = ['#ff9999', '#66b3ff']
        self.ax_disk.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
        
        self.fig.canvas.draw()
        return self.cpu_line, self.mem_line, self.temp_line, self.net_sent_line, self.net_recv_line

# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    root.title("System Performance Monitor")
    root.geometry("1200x800")
    
    app = PerformanceFrame(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()