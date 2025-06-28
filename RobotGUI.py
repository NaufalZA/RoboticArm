import tkinter as tk
from tkinter import ttk, messagebox
import serial
import time
import threading

class ServoControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Servo Controller")
        self.root.geometry("420x420")
        self.root.resizable(False, False)

        self.serial_connection = None
        self.connection_lock = threading.Lock()
        self.selected_servo = 0  # Currently selected servo (0-3)

        # --- Frame Koneksi ---
        connection_frame = ttk.LabelFrame(root, text="Koneksi")
        connection_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(connection_frame, text="Port COM:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.com_port_entry = ttk.Entry(connection_frame, width=10)
        self.com_port_entry.grid(row=0, column=1, padx=5, pady=5)
        self.com_port_entry.insert(0, "COM6") # Ganti dengan port umum Anda

        self.connect_button = ttk.Button(connection_frame, text="Connect", command=self.connect_serial)
        self.connect_button.grid(row=0, column=2, padx=5, pady=5)

        self.disconnect_button = ttk.Button(connection_frame, text="Disconnect", command=self.disconnect_serial, state="disabled")
        self.disconnect_button.grid(row=0, column=3, padx=5, pady=5)

        self.reset_button = ttk.Button(connection_frame, text="Reset", command=self.reset_servos)
        self.reset_button.grid(row=0, column=4, padx=5, pady=5)

        self.status_label = ttk.Label(connection_frame, text="Status: Disconnected", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=5, padx=5, pady=5)

        # --- Frame Kontrol Servo ---
        control_frame = ttk.LabelFrame(root, text="Kontrol Servo")
        control_frame.pack(padx=10, pady=5, fill="x")

        self.sliders = []
        self.slider_labels = []
        self.entry_vars = []
        self.servo_buttons = []
        servo_numbers = [0, 1, 2, 3]  # Change to servos 0, 1, 2, 3
        for i, servo_num in enumerate(servo_numbers):
            
            # Button untuk memilih servo aktif
            select_btn = ttk.Button(control_frame, text=f"S{servo_num}", width=4,
                                   command=lambda s=i: self.select_servo(s))
            select_btn.grid(row=i, column=0, padx=5, pady=5)
            self.servo_buttons.append(select_btn)
            
            ttk.Label(control_frame, text=f"Servo {servo_num}:").grid(row=i, column=1, padx=5, pady=10, sticky="w")
            
            # Variabel untuk menampung nilai slider
            slider_var = tk.DoubleVar()
            
            # Fungsi command di slider dengan increment 5 derajat
            slider = ttk.Scale(control_frame, from_=0, to=180, orient="horizontal", length=120, variable=slider_var,
                               command=lambda value, s=servo_num: self.send_command(s, self.round_to_five(float(value))))
            slider.set(0) # Atur posisi awal ke 0 derajat
            slider.grid(row=i, column=2, padx=5)
            self.sliders.append(slider)
            
            # Entry untuk input manual
            entry_var = tk.StringVar(value="0")
            entry = ttk.Entry(control_frame, textvariable=entry_var, width=5)
            entry.grid(row=i, column=3, padx=5)
            entry.bind('<Return>', lambda event, s=servo_num, var=entry_var: self.set_servo_from_entry(s, var))
            self.entry_vars.append(entry_var)
            
            # Label untuk menampilkan nilai posisi
            value_label = ttk.Label(control_frame, text="0°")
            value_label.grid(row=i, column=4, padx=5)
            self.slider_labels.append(value_label)
            
            # Hubungkan slider dengan label nilainya
            slider_var.trace_add("write", lambda *args, label=value_label, var=slider_var, entry_var=entry_var: self.update_display(label, var, entry_var))

        self.servo_numbers = servo_numbers  # Store for reference
        
        # Set servo 0 as default selected
        self.select_servo(0)
        
        # Bind keyboard events
        self.root.bind('<Key>', self.on_key_press)
        self.root.focus_set()  # Make sure window can receive key events

        # Add instruction label
        instruction_frame = ttk.Frame(root)
        instruction_frame.pack(padx=10, pady=5, fill="x")
        ttk.Label(instruction_frame, text="Gunakan tombol S0,S1,S2,S3 untuk pilih servo, Arrow keys untuk kontrol", 
                 font=('Arial', 8)).pack()

    def connect_serial(self):
        port = self.com_port_entry.get()
        
        # Disable button to prevent multiple connection attempts
        self.connect_button.config(state="disabled")
        self.status_label.config(text="Connecting...", foreground="orange")
        
        def connect_thread():
            try:
                with self.connection_lock:
                    self.serial_connection = serial.Serial(port, 9600, timeout=1)
                    time.sleep(1)  # Reduced wait time
                
                # Update GUI in main thread
                self.root.after(0, self.on_connect_success, port)
                
            except serial.SerialException as e:
                # Update GUI in main thread
                self.root.after(0, self.on_connect_error, port, str(e))
        
        # Start connection in separate thread
        threading.Thread(target=connect_thread, daemon=True).start()

    def on_connect_success(self, port):
        self.status_label.config(text=f"Status: Connected to {port}", foreground="green")
        self.disconnect_button.config(state="normal")
        self.com_port_entry.config(state="disabled")

    def on_connect_error(self, port, error):
        self.status_label.config(text="Status: Connection Failed", foreground="red")
        self.connect_button.config(state="normal")
        messagebox.showerror("Connection Error", f"Gagal terhubung ke {port}.\nError: {error}\n\nPastikan port COM benar dan tidak digunakan program lain.")

    def disconnect_serial(self):
        with self.connection_lock:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
        
        self.status_label.config(text="Status: Disconnected", foreground="red")
        self.connect_button.config(state="normal")
        self.disconnect_button.config(state="disabled")
        self.com_port_entry.config(state="normal")
    
    def reset_servos(self):
        """Reset all servos to their default position (0 degrees)"""
        for slider in self.sliders:
            slider.set(0)
    
    def send_command(self, servo_num, value):
        def send_thread():
            with self.connection_lock:
                if self.serial_connection and self.serial_connection.is_open:
                    try:
                        pos = int(float(value))
                        command = f"S{servo_num},{pos}\n"
                        self.serial_connection.write(command.encode('utf-8'))
                        print(f"Sent: {command.strip()}")
                    except Exception as e:
                        print(f"Error sending command: {e}")
        
        # Send command in separate thread to prevent GUI blocking
        threading.Thread(target=send_thread, daemon=True).start()
            
    def on_closing(self):
        self.disconnect_serial()
        self.root.destroy()

    def round_to_five(self, value):
        """Round value to nearest 5 degrees"""
        return round(value / 5) * 5

    def update_display(self, label, slider_var, entry_var):
        """Update both label and entry when slider moves"""
        rounded_value = self.round_to_five(slider_var.get())
        label.config(text=f"{int(rounded_value)}°")
        entry_var.set(str(int(rounded_value)))

    def set_servo_from_entry(self, servo_num, entry_var):
        """Set servo position from entry box input"""
        try:
            value = int(entry_var.get())
            if 0 <= value <= 180:
                rounded_value = self.round_to_five(value)
                entry_var.set(str(int(rounded_value)))
                # Find the correct slider index for this servo number
                servo_index = self.servo_numbers.index(servo_num)
                self.sliders[servo_index].set(rounded_value)
                self.send_command(servo_num, rounded_value)
            else:
                messagebox.showwarning("Invalid Input", "Nilai harus antara 0-180 derajat")
                entry_var.set("0")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Masukkan angka yang valid")
            entry_var.set("0")

    def select_servo(self, servo_index):
        """Select which servo to control with arrow keys"""
        self.selected_servo = servo_index
        
        # Update button colors to show selection
        for i, btn in enumerate(self.servo_buttons):
            if i == servo_index:
                btn.config(style="Selected.TButton")
            else:
                btn.config(style="TButton")

    def on_key_press(self, event):
        """Handle arrow key presses"""
        if event.keysym in ['Up', 'Right']:
            # Increase servo position
            current_pos = self.sliders[self.selected_servo].get()
            new_pos = min(180, self.round_to_five(current_pos + 5))
            self.sliders[self.selected_servo].set(new_pos)
            
        elif event.keysym in ['Down', 'Left']:
            # Decrease servo position
            current_pos = self.sliders[self.selected_servo].get()
            new_pos = max(0, self.round_to_five(current_pos - 5))
            self.sliders[self.selected_servo].set(new_pos)
            
        elif event.keysym in ['0', '1', '2', '3']:
            # Select servo with number keys (0, 1, 2, 3)
            if event.keysym == '0':
                self.select_servo(0)
            elif event.keysym == '1':
                self.select_servo(1)
            elif event.keysym == '2':
                self.select_servo(2)
            elif event.keysym == '3':
                self.select_servo(3)


if __name__ == "__main__":
    root = tk.Tk()
    app = ServoControllerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing) # Pastikan port serial ditutup saat window diclose
    root.mainloop()