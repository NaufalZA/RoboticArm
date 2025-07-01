import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import serial
import threading
import time

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # "light" or "dark"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

class ModernServoControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Robotic Arm Controller")
        self.root.geometry("500x520")  # Increased height to show all servos
        self.root.minsize(100, 100)  # Increased minimum height
        self.root.resizable(True, True)
        
        # Center the window on screen
        self.center_window()

        self.serial_connection = None
        self.selected_servo = 9
        self.connection_status = False

        # Servo configuration
        self.servo_ranges = {
            9: (0, 180),
            10: (0, 180),
            11: (15, 35),
            12: (0, 180)
        }
        
        self.default_positions = {
            9: 90,
            10: 90,
            11: 35,
            12: 40 
        }

        self.servo_increments = {
            9: 10, 
            10: 10, 
            11: 30,  # Smaller increment for gripper
            12: 10  
        }

        self.servo_names = {
            9: "🦾 Tangan Kiri",
            10: "🔄 Base Rotasi", 
            11: "🤏 Gripper",
            12: "🦾 Tangan Kanan"
        }

        self.servo_colors = {
            9: "#FF6B6B",   # Red
            10: "#4ECDC4",  # Teal
            11: "#45B7D1",  # Blue
            12: "#96CEB4"   # Green
        }

        self.setup_ui()
        self.auto_connect()

    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        # Main container with minimal padding
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)  # Reduced padding

        # Title with slightly larger font
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🤖 Robotic Arm Controller", 
            font=ctk.CTkFont(size=22, weight="bold")  # Slightly smaller font
        )
        title_label.pack(pady=(12, 15))  # Reduced padding

        # Connection frame
        self.setup_connection_frame(main_frame)
        
        # Control frame
        self.setup_control_frame(main_frame)

        # Keyboard bindings
        self.root.bind('<Key>', self.on_key_press)
        self.root.focus_set()

    def setup_connection_frame(self, parent):
        connection_frame = ctk.CTkFrame(parent)
        connection_frame.pack(fill="x", padx=6, pady=(0, 10))  # Reduced padding

        # Connection title with slightly larger font
        ctk.CTkLabel(
            connection_frame, 
            text="🔌 Koneksi Serial", 
            font=ctk.CTkFont(size=15, weight="bold")  # Slightly smaller font
        ).pack(pady=(10, 8))  # Reduced padding

        # Connection controls
        button_frame = ctk.CTkFrame(connection_frame)
        button_frame.pack(pady=(0, 10))  # Reduced padding

        self.connect_button = ctk.CTkButton(
            button_frame,
            text="🔗 Connect",
            command=self.connect_serial,
            width=120,  # Slightly larger width
            height=35,  # Slightly larger height
            font=ctk.CTkFont(size=12, weight="bold")  # Slightly larger font
        )
        self.connect_button.pack(side="left", padx=8)  # Slightly more padding

        self.disconnect_button = ctk.CTkButton(
            button_frame,
            text="🔌 Disconnect",
            command=self.disconnect_serial,
            state="disabled",
            width=120,  # Slightly larger width
            height=35,  # Slightly larger height
            font=ctk.CTkFont(size=12, weight="bold"),  # Slightly larger font
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        self.disconnect_button.pack(side="left", padx=8)  # Slightly more padding

        self.reset_button = ctk.CTkButton(
            button_frame,
            text="🔄 Reset All",
            command=self.reset_servos,
            width=120,  # Slightly larger width
            height=35,  # Slightly larger height
            font=ctk.CTkFont(size=12, weight="bold"),  # Slightly larger font
            fg_color="#F39C12",
            hover_color="#E67E22"
        )
        self.reset_button.pack(side="left", padx=8)  # Slightly more padding

        # Status indicator
        self.status_frame = ctk.CTkFrame(connection_frame)
        self.status_frame.pack(pady=(0, 10))  # Reduced padding

        self.status_indicator = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=ctk.CTkFont(size=16),  # Slightly larger font
            text_color="#E74C3C"
        )
        self.status_indicator.pack(side="left", padx=(12, 6))  # Slightly more padding

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Disconnected from COM6",
            font=ctk.CTkFont(size=12)  # Slightly larger font
        )
        self.status_label.pack(side="left", padx=(0, 12))  # Slightly more padding

    def setup_control_frame(self, parent):
        control_frame = ctk.CTkFrame(parent)
        control_frame.pack(fill="both", expand=True, padx=6, pady=(0, 10))  # Reduced padding

        # Control title with slightly larger font
        ctk.CTkLabel(
            control_frame, 
            text="🎮 Kontrol Servo", 
            font=ctk.CTkFont(size=15, weight="bold")  # Slightly smaller font
        ).pack(pady=(10, 12))  # Reduced padding

        # Servo controls container (no scrollable frame)
        controls_container = ctk.CTkFrame(control_frame)
        controls_container.pack(fill="both", expand=True, padx=6, pady=(0, 10))

        # Servo controls
        self.servo_frames = {}
        self.sliders = {}
        self.value_labels = {}
        self.servo_buttons = {}

        for i, servo_num in enumerate([9, 10, 11, 12]):
            self.create_servo_control(controls_container, servo_num, i)

        # Select first servo
        self.select_servo(9)

    def create_servo_control(self, parent, servo_num, index):
        min_pos, max_pos = self.servo_ranges[servo_num]
        default_pos = self.default_positions[servo_num]
        color = self.servo_colors[servo_num]
        increment = self.servo_increments[servo_num]

        # Servo frame - slightly larger
        servo_frame = ctk.CTkFrame(parent)
        servo_frame.pack(fill="x", padx=6, pady=4)  # Reduced padding
        self.servo_frames[servo_num] = servo_frame

        # Top row: Name button and value - slightly larger
        top_frame = ctk.CTkFrame(servo_frame)
        top_frame.pack(fill="x", padx=8, pady=(8, 6))  # Reduced padding

        # Servo selection button - slightly larger
        select_btn = ctk.CTkButton(
            top_frame,
            text=self.servo_names[servo_num],
            command=lambda s=servo_num: self.select_servo(s),
            width=180,  # Larger width
            height=32,  # Larger height
            font=ctk.CTkFont(size=12, weight="bold"),  # Larger font
            fg_color=color,
            hover_color=self.darken_color(color)
        )
        select_btn.pack(side="left", padx=(0, 15))  # More padding
        self.servo_buttons[servo_num] = select_btn

        # Range info next to servo name
        range_label = ctk.CTkLabel(
            top_frame,
            text=f"{min_pos}-{max_pos}°",
            font=ctk.CTkFont(size=10)
        )
        range_label.pack(side="left", padx=(0, 15))

        # Value display and reset button
        controls_frame = ctk.CTkFrame(top_frame)
        controls_frame.pack(side="right")

        # Value display
        value_frame = ctk.CTkFrame(controls_frame)
        value_frame.pack(side="left", padx=(8, 5))

        ctk.CTkLabel(
            value_frame,
            text="Position:",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=(5, 3))

        value_label = ctk.CTkLabel(
            value_frame,
            text=f"{default_pos}°",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=color
        )
        value_label.pack(side="left", padx=(0, 5))
        self.value_labels[servo_num] = value_label

        # Reset button for individual servo
        reset_btn = ctk.CTkButton(
            controls_frame,
            text="↺",
            command=lambda s=servo_num: self.reset_single_servo(s),
            width=30,
            height=25,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#95A5A6",
            hover_color="#7F8C8D"
        )
        reset_btn.pack(side="left", padx=(0, 8))

        # Bottom row: Slider only
        bottom_frame = ctk.CTkFrame(servo_frame)
        bottom_frame.pack(fill="x", padx=8, pady=(0, 8))  # Reduced padding

        # Slider - larger
        slider = ctk.CTkSlider(
            bottom_frame,
            from_=min_pos,
            to=max_pos,
            width=450,  # Larger width
            height=16,  # Slightly smaller height
            button_color=color,
            button_hover_color=self.darken_color(color),
            progress_color=color,
            command=lambda value, s=servo_num: self.update_slider(s, value)
        )
        slider.set(default_pos)
        slider.pack(fill="x", pady=(3, 6))  # Reduced padding
        self.sliders[servo_num] = slider

    def setup_status_frame(self, parent):
        # Remove the status frame completely
        pass

    def darken_color(self, hex_color):
        """Darken a hex color for hover effect"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        dark_rgb = tuple(max(0, int(c * 0.8)) for c in rgb)
        return f"#{dark_rgb[0]:02x}{dark_rgb[1]:02x}{dark_rgb[2]:02x}"

    def auto_connect(self):
        """Auto-connect to COM6 on startup"""
        try:
            self.serial_connection = serial.Serial("COM6", 115200, timeout=1)
            self.connection_status = True
            self.update_connection_status(True, "Auto-connected to COM6")
        except Exception as e:
            self.update_connection_status(False, f"Auto-connect failed: {str(e)[:30]}...")

    def connect_serial(self):
        try:
            if not self.serial_connection:
                self.serial_connection = serial.Serial("COM6", 115200, timeout=1)
            self.connection_status = True
            self.update_connection_status(True, "Connected to COM6")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            self.update_connection_status(False, f"Connection failed")

    def disconnect_serial(self):
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
        self.connection_status = False
        self.update_connection_status(False, "Disconnected")

    def update_connection_status(self, connected, message):
        if connected:
            self.status_indicator.configure(text_color="#27AE60")
            self.connect_button.configure(state="disabled")
            self.disconnect_button.configure(state="normal")
        else:
            self.status_indicator.configure(text_color="#E74C3C")
            self.connect_button.configure(state="normal")
            self.disconnect_button.configure(state="disabled")
        
        self.status_label.configure(text=message)

    def reset_servos(self):
        if self.serial_connection:
            try:
                for servo_num, default_pos in self.default_positions.items():
                    command = f"S{servo_num},{default_pos}\n"
                    self.serial_connection.write(command.encode())
                    self.sliders[servo_num].set(default_pos)
                    self.value_labels[servo_num].configure(text=f"{default_pos}°")
                    time.sleep(0.1)  # Small delay between commands
                    
            except Exception as e:
                messagebox.showerror("Error", f"Reset failed: {e}")

    def send_command(self, servo_num, value):
        if self.serial_connection:
            try:
                command = f"S{servo_num},{value}\n"
                self.serial_connection.write(command.encode())
                print(f"Sent: {command.strip()}")
            except Exception as e:
                print(f"Serial error: {e}")
                self.update_connection_status(False, "Connection lost")

    def update_slider(self, servo_num, value):
        pos = int(float(value))
        self.value_labels[servo_num].configure(text=f"{pos}°")
        self.send_command(servo_num, pos)

    def select_servo(self, servo_num):
        self.selected_servo = servo_num
        
        # Update button appearances
        for num, button in self.servo_buttons.items():
            if num == servo_num:
                button.configure(text=f"➤ {self.servo_names[num]}")
                self.servo_frames[num].configure(border_width=2, border_color=self.servo_colors[num])
            else:
                button.configure(text=self.servo_names[num])
                self.servo_frames[num].configure(border_width=0)

    def on_key_press(self, event):
        if not hasattr(self, 'selected_servo'):
            return
            
        increment = self.servo_increments[self.selected_servo]
        
        if event.keysym in ['Up', 'Right']:
            current_pos = self.sliders[self.selected_servo].get()
            min_pos, max_pos = self.servo_ranges[self.selected_servo]
            new_pos = min(max_pos, current_pos + increment)
            self.sliders[self.selected_servo].set(new_pos)
            # Update the value display and send command
            self.update_slider(self.selected_servo, new_pos)
            
        elif event.keysym in ['Down', 'Left']:
            current_pos = self.sliders[self.selected_servo].get()
            min_pos, max_pos = self.servo_ranges[self.selected_servo]
            new_pos = max(min_pos, current_pos - increment)
            self.sliders[self.selected_servo].set(new_pos)
            # Update the value display and send command
            self.update_slider(self.selected_servo, new_pos)
            
        elif event.keysym == 'space':
            # Reset selected servo to default
            default_pos = self.default_positions[self.selected_servo]
            self.sliders[self.selected_servo].set(default_pos)
            # Update the value display and send command
            self.update_slider(self.selected_servo, default_pos)
            
        elif event.keysym in ['1', '2', '3', '4']:
            servo_map = {'1': 9, '2': 10, '3': 11, '4': 12}
            if event.keysym in servo_map:
                self.select_servo(servo_map[event.keysym])

    def reset_single_servo(self, servo_num):
        """Reset a single servo to its default position"""
        default_pos = self.default_positions[servo_num]
        self.sliders[servo_num].set(default_pos)
        self.update_slider(servo_num, default_pos)

if __name__ == "__main__":
    # Create the main window
    root = ctk.CTk()
    
    # Create and run the application
    app = ModernServoControllerApp(root)
    
    # Start the main loop
    root.mainloop()
