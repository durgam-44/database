import customtkinter as ctk
import tkinter as tk
import sqlite3
import hashlib
import os
import re

DB_PATH = "users.db"


# ===========================
# Utility Functions
# ===========================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Initialize database with required fields."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create users table with employee details
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT,
            fullname TEXT,
            address TEXT,
            dob TEXT,
            gender TEXT,
            mobile TEXT,
            email TEXT,
            national_id TEXT
        )
    """)

    # Hardcode manager if not exists
    try:
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    ("manager", hash_password("manager123"), "manager"))
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()


# ===========================
# Main Application
# ===========================

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("XYZ Restaurant Manager")
        self.geometry("1000x600")
        self.resizable(False, False)

        init_db()
        self.build_welcome_page()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ===========================
    # Welcome Page
    # ===========================
    def build_welcome_page(self):
        self.clear_window()

        title = ctk.CTkLabel(self, text="Welcome to XYZ Restaurant Manager", font=("Arial", 26, "bold"))
        title.pack(pady=40)

        subtitle = ctk.CTkLabel(self, text="Continue as:", font=("Arial", 20))
        subtitle.pack(pady=20)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        manager_btn = ctk.CTkButton(btn_frame, text="Manager", width=200, command=self.manager_login_page)
        manager_btn.pack(pady=10)

        employee_btn = ctk.CTkButton(btn_frame, text="Employee", width=200, command=self.employee_login_page)
        employee_btn.pack(pady=10)

        customer_btn = ctk.CTkButton(btn_frame, text="Customer", width=200, command=self.customer_welcome_page)
        customer_btn.pack(pady=10)

    # ===========================
    # Manager Login
    # ===========================
    def manager_login_page(self):
        self.clear_window()

        label = ctk.CTkLabel(self, text="Welcome, Manager!", font=("Arial", 24, "bold"))
        label.pack(pady=30)

        username_label = ctk.CTkLabel(self, text="Username:", font=("Arial", 16))
        username_label.pack()
        username_entry = ctk.CTkEntry(self, width=250, justify="center")
        username_entry.pack(pady=5)

        password_label = ctk.CTkLabel(self, text="Password:", font=("Arial", 16))
        password_label.pack()
        password_entry = ctk.CTkEntry(self, width=250, show="*", justify="center")
        password_entry.pack(pady=5)

        message = ctk.CTkLabel(self, text="", font=("Arial", 14), text_color="red")
        message.pack(pady=5)

        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not password:
                message.configure(text="Please enter both username and password.")
                return

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE username=? AND role='manager'", (username,))
            result = cur.fetchone()
            conn.close()

            if result and result[0] == hash_password(password):
                message.configure(text="Login successful!", text_color="green")
            else:
                message.configure(text="Invalid username/password.", text_color="red")

        login_btn = ctk.CTkButton(self, text="Login", width=120, command=login)
        login_btn.pack(pady=15)

        back_btn = ctk.CTkButton(self, text="← Back", width=100, command=self.build_welcome_page)
        back_btn.pack(pady=10)

    # ===========================
    # Employee Login & Register
    # ===========================
    def employee_login_page(self):
        self.clear_window()

        label = ctk.CTkLabel(self, text="Welcome, Employee!", font=("Arial", 24, "bold"))
        label.pack(pady=20)

        tabview = ctk.CTkTabview(self, width=700, height=400)
        tabview.pack(pady=10)
        login_tab = tabview.add("Login")
        register_tab = tabview.add("Register")

        # ===== LOGIN TAB =====
        login_frame = ctk.CTkFrame(login_tab, fg_color="transparent")
        login_frame.pack(pady=20)

        username_label = ctk.CTkLabel(login_frame, text="Username:", font=("Arial", 16))
        username_label.pack()
        username_entry = ctk.CTkEntry(login_frame, width=250, justify="center")
        username_entry.pack(pady=5)

        password_label = ctk.CTkLabel(login_frame, text="Password:", font=("Arial", 16))
        password_label.pack()
        password_entry = ctk.CTkEntry(login_frame, width=250, show="*", justify="center")
        password_entry.pack(pady=5)

        message_login = ctk.CTkLabel(login_frame, text="", font=("Arial", 14), text_color="red")
        message_login.pack(pady=5)

        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not password:
                message_login.configure(text="Please enter both username and password.")
                return

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE username=? AND role='employee'", (username,))
            result = cur.fetchone()
            conn.close()

            if result and result[0] == hash_password(password):
                message_login.configure(text="Login successful!", text_color="green")
            else:
                message_login.configure(text="Invalid username/password.", text_color="red")

        login_btn = ctk.CTkButton(login_frame, text="Login", width=120, command=login)
        login_btn.pack(pady=10)

        # ===== REGISTER TAB =====
        reg_frame = ctk.CTkScrollableFrame(register_tab, width=650, height=350)
        reg_frame.pack(pady=10)

        # Enable mouse scrolling
        reg_frame.bind_all("<MouseWheel>", lambda e: reg_frame._parent_canvas.yview_scroll(-1*(e.delta//120), "units"))

        fields = {}
        def add_field(label_text, is_entry=True, **kwargs):
            lbl = ctk.CTkLabel(reg_frame, text=label_text, font=("Arial", 14))
            lbl.pack(pady=(10, 0))
            if is_entry:
                ent = ctk.CTkEntry(reg_frame, width=300, justify="center", **kwargs)
                ent.pack(pady=2)
                return ent

        fields["fullname"] = add_field("Full Name:")
        fields["address"] = add_field("Primary Address:")

        # DOB
        dob_label = ctk.CTkLabel(reg_frame, text="Date of Birth:", font=("Arial", 14))
        dob_label.pack(pady=(10, 0))
        dob_frame = ctk.CTkFrame(reg_frame, fg_color="transparent")
        dob_frame.pack()
        day = tk.StringVar(value="Day")
        month = tk.StringVar(value="Month")
        year = tk.StringVar(value="Year")

        day_menu = ctk.CTkOptionMenu(dob_frame, variable=day, values=[str(i) for i in range(1, 32)], width=80)
        month_menu = ctk.CTkOptionMenu(dob_frame, variable=month, values=[str(i) for i in range(1, 13)], width=80)
        year_menu = ctk.CTkOptionMenu(dob_frame, variable=year, values=[str(i) for i in range(1950, 2026)], width=100)
        day_menu.grid(row=0, column=0, padx=5)
        month_menu.grid(row=0, column=1, padx=5)
        year_menu.grid(row=0, column=2, padx=5)

        # Gender
        gender_label = ctk.CTkLabel(reg_frame, text="Gender:", font=("Arial", 14))
        gender_label.pack(pady=(10, 0))
        gender = tk.StringVar(value="Select")
        gender_menu = ctk.CTkOptionMenu(reg_frame, variable=gender, values=["Male", "Female", "Other"])
        gender_menu.pack()

        fields["mobile"] = add_field("Mobile (format: 01X-XXXXXXXX):")
        fields["email"] = add_field("Email:")
        fields["national_id"] = add_field("National ID (11 digits):")
        fields["username"] = add_field("Username:")
        fields["password"] = add_field("Password:", show="*")
        fields["confirm_password"] = add_field("Confirm Password:", show="*")

        message_reg = ctk.CTkLabel(reg_frame, text="", font=("Arial", 14), text_color="red")
        message_reg.pack(pady=5)

        def register():
            data = {key: field.get().strip() for key, field in fields.items()}
            dob_value = f"{day.get()}-{month.get()}-{year.get()}"
            gender_value = gender.get()

            # Validation
            if any(v == "" for v in data.values()):
                message_reg.configure(text="Please fill all fields.")
                return
            if day.get() in ("Day", "") or month.get() in ("Month", "") or year.get() in ("Year", ""):
                message_reg.configure(text="Please select a valid Date of Birth.")
                return
            if gender_value == "Select":
                message_reg.configure(text="Please select a gender.")
                return
            if not re.match(r"^01\d-\d{8}$", data["mobile"]):
                message_reg.configure(text="Invalid mobile number. Format: 01X-XXXXXXXX.")
                return
            if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
                message_reg.configure(text="Invalid email address.")
                return
            if not re.fullmatch(r"\d{11}", data["national_id"]):
                message_reg.configure(text="National ID must be 11 digits.")
                return
            if data["password"] != data["confirm_password"]:
                message_reg.configure(text="Passwords do not match.")
                return

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO users (username, password, role, fullname, address, dob, gender, mobile, email, national_id)
                    VALUES (?, ?, 'employee', ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data["username"], hash_password(data["password"]), data["fullname"],
                    data["address"], dob_value, gender_value,
                    data["mobile"], data["email"], data["national_id"]
                ))
                conn.commit()
                message_reg.configure(text="Registration successful!", text_color="green")
            except sqlite3.IntegrityError:
                message_reg.configure(text="Username already exists.", text_color="red")
            conn.close()

        register_btn = ctk.CTkButton(reg_frame, text="Register", width=120, command=register)
        register_btn.pack(pady=10)

        # Back button
        back_btn = ctk.CTkButton(self, text="← Back", width=100, command=self.build_welcome_page)
        back_btn.pack(pady=10)

    # ===========================
    # Customer Welcome
    # ===========================
    def customer_welcome_page(self):
        self.clear_window()

        label = ctk.CTkLabel(self, text="Welcome, Customer!", font=("Arial", 26, "bold"))
        label.pack(pady=80)

        sublabel = ctk.CTkLabel(self, text="Enjoy exploring the app!", font=("Arial", 18))
        sublabel.pack(pady=10)

        back_btn = ctk.CTkButton(self, text="← Back", width=120, command=self.build_welcome_page)
        back_btn.pack(pady=30)


# ===========================
# Run App
# ===========================
if __name__ == "__main__":
    app = App()
    app.mainloop()
