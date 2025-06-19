import tkinter as tk
from tkinter import ttk, messagebox
import serial
import time

class ServoControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kontrol Servo Arduino")
        self.root.geometry("320x420")
        self.root.resizable(False, False)

        self.serial_connection = None

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

        self.status_label = ttk.Label(connection_frame, text="Status: Disconnected", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        # --- Frame Kontrol Servo ---
        control_frame = ttk.LabelFrame(root, text="Kontrol Servo")
        control_frame.pack(padx=10, pady=5, fill="x")

        self.sliders = []
        self.slider_labels = []
        for i in range(4):
            servo_num = i + 1
            
            ttk.Label(control_frame, text=f"Servo {servo_num}:").grid(row=i, column=0, padx=5, pady=10, sticky="w")
            
            # Variabel untuk menampung nilai slider
            slider_var = tk.DoubleVar()
            
            # Fungsi command di slider harus menggunakan lambda untuk menangkap nilai servo_num saat ini
            slider = ttk.Scale(control_frame, from_=0, to=180, orient="horizontal", length=150, variable=slider_var,
                               command=lambda value, s=servo_num: self.send_command(s, value))
            slider.set(90) # Atur posisi awal
            slider.grid(row=i, column=1, padx=5)
            self.sliders.append(slider)
            
            # Label untuk menampilkan nilai posisi
            value_label = ttk.Label(control_frame, text="90")
            value_label.grid(row=i, column=2, padx=5)
            self.slider_labels.append(value_label)
            
            # Hubungkan slider dengan label nilainya
            slider_var.trace_add("write", lambda *args, label=value_label, var=slider_var: label.config(text=f"{int(var.get())}"))


    def connect_serial(self):
        port = self.com_port_entry.get()
        try:
            self.serial_connection = serial.Serial(port, 9600, timeout=1)
            time.sleep(2) # Beri waktu untuk Arduino reset setelah koneksi
            
            self.status_label.config(text=f"Status: Connected to {port}", foreground="green")
            self.connect_button.config(state="disabled")
            self.disconnect_button.config(state="normal")
            self.com_port_entry.config(state="disabled")
            
        except serial.SerialException as e:
            messagebox.showerror("Connection Error", f"Gagal terhubung ke {port}.\nError: {e}\n\nPastikan port COM benar dan tidak digunakan program lain.")

    def disconnect_serial(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.status_label.config(text="Status: Disconnected", foreground="red")
            self.connect_button.config(state="normal")
            self.disconnect_button.config(state="disabled")
            self.com_port_entry.config(state="normal")
    
    def send_command(self, servo_num, value):
        if self.serial_connection and self.serial_connection.is_open:
            pos = int(float(value))
            command = f"S{servo_num},{pos}\n"
            self.serial_connection.write(command.encode('utf-8'))
            print(f"Sent: {command.strip()}") # Untuk debug di console
        else:
            # Bisa juga menampilkan warning kecil jika mencoba menggerakkan saat disconnect
            pass
            
    def on_closing(self):
        self.disconnect_serial()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ServoControllerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing) # Pastikan port serial ditutup saat window diclose
    root.mainloop()