import tkinter as tk
from tkinter import ttk, messagebox
import serial

class ServoControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Servo Controller")
        self.root.geometry("400x350")
        self.root.resizable(False, False)

        self.serial_connection = None
        self.selected_servo = 9

        connection_frame = ttk.LabelFrame(root, text="Koneksi")
        connection_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(connection_frame, text="Port COM:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.com_port_entry = ttk.Entry(connection_frame, width=10)
        self.com_port_entry.grid(row=0, column=1, padx=5, pady=5)
        self.com_port_entry.insert(0, "COM6")

        self.connect_button = ttk.Button(connection_frame, text="Connect", command=self.connect_serial)
        self.connect_button.grid(row=0, column=2, padx=5, pady=5)

        self.disconnect_button = ttk.Button(connection_frame, text="Disconnect", command=self.disconnect_serial, state="disabled")
        self.disconnect_button.grid(row=0, column=3, padx=5, pady=5)

        self.reset_button = ttk.Button(connection_frame, text="Reset", command=self.reset_servos)
        self.reset_button.grid(row=0, column=4, padx=5, pady=5)

        self.status_label = ttk.Label(connection_frame, text="Status: Disconnected", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=5, padx=5, pady=5)

        control_frame = ttk.LabelFrame(root, text="Kontrol Servo")
        control_frame.pack(padx=10, pady=5, fill="x")

        self.sliders = []
        self.servo_buttons = []
        
        default_positions = [0, 0, 0, 0]
        
        for i in range(4):
            servo_num = i + 9
            
            select_btn = ttk.Button(control_frame, text=f"S{servo_num}", width=4,
                                   command=lambda s=servo_num: self.select_servo(s))
            select_btn.grid(row=i, column=0, padx=5, pady=5)
            self.servo_buttons.append(select_btn)
            
            ttk.Label(control_frame, text=f"Servo {servo_num}:").grid(row=i, column=1, padx=5, pady=5, sticky="w")
            
            slider = ttk.Scale(control_frame, from_=0, to=180, orient="horizontal", length=150,
                               command=lambda value, s=servo_num: self.send_command(s, int(float(value))))
            slider.set(default_positions[i])
            slider.grid(row=i, column=2, padx=5, pady=5)
            self.sliders.append(slider)
            
            value_label = ttk.Label(control_frame, text=f"{default_positions[i]}°", width=5)
            value_label.grid(row=i, column=3, padx=5, pady=5)
            
            slider.configure(command=lambda value, s=servo_num, lbl=value_label: self.update_slider(s, value, lbl))

        self.select_servo(9)
        
        self.root.bind('<Key>', self.on_key_press)
        self.root.focus_set()

        ttk.Label(root, text="Keys: 9,0,1,2 untuk pilih servo, Arrow keys untuk kontrol", 
                 font=('Arial', 8)).pack(pady=5)

    def connect_serial(self):
        try:
            port = self.com_port_entry.get()
            self.serial_connection = serial.Serial(port, 115200, timeout=1)
            self.status_label.config(text=f"Connected to {port}", foreground="green")
            self.connect_button.config(state="disabled")
            self.disconnect_button.config(state="normal")
            self.com_port_entry.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal connect: {e}")

    def disconnect_serial(self):
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
        self.status_label.config(text="Disconnected", foreground="red")
        self.connect_button.config(state="normal")
        self.disconnect_button.config(state="disabled")
        self.com_port_entry.config(state="normal")
    
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
                btn.config(text=f"S{servo_num}*")
            else:
                btn.config(text=f"S{servo_num}")

    def on_key_press(self, event):
        if event.keysym in ['Up', 'Right']:
            slider_index = self.selected_servo - 9 
            current_pos = self.sliders[slider_index].get()
            new_pos = min(180, current_pos + 5)
            self.sliders[slider_index].set(new_pos)
            
        elif event.keysym in ['Down', 'Left']:
            slider_index = self.selected_servo - 9 
            current_pos = self.sliders[slider_index].get()
            new_pos = max(0, current_pos - 5)
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