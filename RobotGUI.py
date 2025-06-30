import tkinter as tk
from tkinter import ttk, messagebox
import serial

class ServoControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Servo Controller")
        self.root.geometry("500x350")
        self.root.resizable(False, False)

        self.serial_connection = None
        self.selected_servo = 9

        # Servo ranges [min, max] and default positions
        self.servo_ranges = {
            9 : (0, 180),
            10: (0, 180),
            11: (20, 40),
            12: (0, 180)
        }
        
        self.default_positions = {
            9 : 90,
            10: 90,
            11: 20,
            12: 90 
        }

     
        self.servo_increments = {
            9 : 5, 
            10: 5, 
            11: 10,
            12: 5  
        }

        # Servo name mappings
        self.servo_names = {
            9: "Tangan Kiri",
            10: "Bawah", 
            11: "Capit",
            12: "Tangan Kanan"
        }

        connection_frame = ttk.LabelFrame(root, text="Koneksi")
        connection_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(connection_frame, text="Port: COM6").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.connect_button = ttk.Button(connection_frame, text="Connect", command=self.connect_serial)
        self.connect_button.grid(row=0, column=1, padx=5, pady=5)

        self.disconnect_button = ttk.Button(connection_frame, text="Disconnect", command=self.disconnect_serial, state="disabled")
        self.disconnect_button.grid(row=0, column=2, padx=5, pady=5)

        self.reset_button = ttk.Button(connection_frame, text="Reset", command=self.reset_servos)
        self.reset_button.grid(row=0, column=3, padx=5, pady=5)

        self.status_label = ttk.Label(connection_frame, text="Status: Disconnected", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        control_frame = ttk.LabelFrame(root, text="Kontrol Servo")
        control_frame.pack(padx=10, pady=5, fill="x")

        self.sliders = []
        self.servo_buttons = []
        
        for i in range(4):
            servo_num = i + 9
            min_pos, max_pos = self.servo_ranges[servo_num]
            default_pos = self.default_positions[servo_num]
            
            select_btn = ttk.Button(control_frame, text=self.servo_names[servo_num], width=12,
                                   command=lambda s=servo_num: self.select_servo(s))
            select_btn.grid(row=i, column=0, padx=5, pady=5)
            self.servo_buttons.append(select_btn)
            
            ttk.Label(control_frame, text=f"S{i+1} ({min_pos}-{max_pos}°):", width=20).grid(row=i, column=1, padx=5, pady=5, sticky="w")
            
            slider = ttk.Scale(control_frame, from_=min_pos, to=max_pos, orient="horizontal", length=200,
                               command=lambda value, s=servo_num: self.send_command(s, int(float(value))))
            slider.set(default_pos)
            slider.grid(row=i, column=2, padx=5, pady=5)
            self.sliders.append(slider)
            
            value_label = ttk.Label(control_frame, text=f"{default_pos}°", width=6)
            value_label.grid(row=i, column=3, padx=5, pady=5)
            
            slider.configure(command=lambda value, s=servo_num, lbl=value_label: self.update_slider(s, value, lbl))

        self.select_servo(9)
        
        self.root.bind('<Key>', self.on_key_press)
        self.root.focus_set()

        ttk.Label(root, text="Keys: 1,2,3,4 untuk pilih servo, Arrow keys untuk kontrol", 
                 font=('Arial', 8)).pack(pady=5)

        # Auto-connect to COM6 on startup
        self.auto_connect()

    def auto_connect(self):
        try:
            self.serial_connection = serial.Serial("COM6", 115200, timeout=1)
            self.status_label.config(text="Connected to COM6", foreground="green")
            self.connect_button.config(state="disabled")
            self.disconnect_button.config(state="normal")
        except Exception as e:
            self.status_label.config(text=f"Auto-connect failed: {e}", foreground="orange")

    def connect_serial(self):
        try:
            self.serial_connection = serial.Serial("COM6", 115200, timeout=1)
            self.status_label.config(text="Connected to COM6", foreground="green")
            self.connect_button.config(state="disabled")
            self.disconnect_button.config(state="normal")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal connect: {e}")

    def disconnect_serial(self):
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
        self.status_label.config(text="Disconnected", foreground="red")
        self.connect_button.config(state="normal")
        self.disconnect_button.config(state="disabled")
    
    def reset_servos(self):
        if self.serial_connection:
            try:
                command = "default\n"
                self.serial_connection.write(command.encode())
                print("Sent: default")
            except Exception as e:
                print(f"Error sending default command: {e}")
        
    def send_command(self, servo_num, value):
        if self.serial_connection:
            try:
                command = f"S{servo_num},{value}\n"
                self.serial_connection.write(command.encode())
                print(f"Sent: {command.strip()}")
            except Exception as e:
                print(f"Error: {e}")

    def update_slider(self, servo_num, value, label):
        pos = int(float(value))
        label.config(text=f"{pos}°")
        self.send_command(servo_num, pos)

    def select_servo(self, servo_index):
        self.selected_servo = servo_index
        for i, btn in enumerate(self.servo_buttons):
            servo_num = i + 9
            if servo_num == servo_index:
                btn.config(text=f"{self.servo_names[servo_num]}*")
            else:
                btn.config(text=self.servo_names[servo_num])

    def on_key_press(self, event):
        increment = self.servo_increments[self.selected_servo]
        
        if event.keysym in ['Up', 'Right']:
            slider_index = self.selected_servo - 9 
            current_pos = self.sliders[slider_index].get()
            min_pos, max_pos = self.servo_ranges[self.selected_servo]
            new_pos = min(max_pos, current_pos + increment)
            self.sliders[slider_index].set(new_pos)
            
        elif event.keysym in ['Down', 'Left']:
            slider_index = self.selected_servo - 9 
            current_pos = self.sliders[slider_index].get()
            min_pos, max_pos = self.servo_ranges[self.selected_servo]
            new_pos = max(min_pos, current_pos - increment)
            self.sliders[slider_index].set(new_pos)
            
        elif event.keysym in ['1', '2', '3', '4']:
            if event.keysym == '1':
                self.select_servo(9)
            elif event.keysym == '2':
                self.select_servo(10)
            elif event.keysym == '3':
                self.select_servo(11)
            elif event.keysym == '4':
                self.select_servo(12)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServoControllerApp(root)
    root.mainloop()