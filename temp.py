import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageFilter
import sqlite3
import hashlib
import os
import re

DB_PATH = "users.db"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ---------------- LOAD BACKGROUND IMAGES ----------------
        self.bg_main = ctk.CTkImage(
            light_image=Image.open("images/main_background.png"),
            dark_image=Image.open("images/main_background.png"),
            size=(1000, 600)
        )

        self.bg_manager = ctk.CTkImage(
            light_image=Image.open("images/For Manager Final.png"),
            dark_image=Image.open("images/For Manager Final.png"),
            size=(1000, 600)
        )

        self.bg_employee = ctk.CTkImage(
            light_image=Image.open("images/For Employee Final.png"),
            dark_image=Image.open("images/For Employee Final.png"),
            size=(1000, 600)
        )

        self.bg_customer = ctk.CTkImage(
            light_image=Image.open("images/For Menu Final.png"),
            dark_image=Image.open("images/For Menu Final.png"),
            size=(1000, 600)
        )

        # --------------------------------------------------------

        self.title("XYZ Restaurant")
        self.geometry("1000x600")
        self.resizable(False, False)

        init_db()
        self.build_welcome_page()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ---------------- WELCOME PAGE ----------------
    def build_welcome_page(self):
        self.clear_window()

        bg_label = ctk.CTkLabel(self, image=self.bg_main, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        title = ctk.CTkLabel(self, text="Welcome to XYZ Restaurant", font=("Arial", 26, "bold"))
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

    # ---------------- MANAGER LOGIN ----------------
    def manager_login_page(self):
        self.clear_window()

        bg_label = ctk.CTkLabel(self, image=self.bg_manager, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        label = ctk.CTkLabel(self, text="Welcome, Manager!", font=("Arial", 24, "bold"))
        label.pack(pady=30)

        username_label = ctk.CTkLabel(self, text="Username:", font=("Arial", 16))
        username_label.pack()
        username_entry = ctk.CTkEntry(self, width=250)
        username_entry.pack(pady=5)

        password_label = ctk.CTkLabel(self, text="Password:", font=("Arial", 16))
        password_label.pack()
        password_entry = ctk.CTkEntry(self, width=250, show="*")
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
                self.manager_dashboard_page()
            else:
                message.configure(text="Invalid username/password. Please try again.", text_color="red")

        login_btn = ctk.CTkButton(self, text="Login", width=120, command=login)
        login_btn.pack(pady=15)

        back_btn = ctk.CTkButton(self, text="← Back", width=100, command=self.build_welcome_page)
        back_btn.pack(pady=10)

    # ---------------- MANAGER DASHBOARD ----------------
    def manager_dashboard_page(self):
        self.clear_window()

        bg_label = ctk.CTkLabel(self, image=self.bg_manager, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        title = ctk.CTkLabel(self, text="Manager Dashboard - Employee Records", font=("Arial", 26, "bold"))
        title.pack(pady=20)

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(pady=10, padx=20, fill="both", expand=True)

        y_scroll = tk.Scrollbar(table_frame, orient="vertical")
        y_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            table_frame,
            columns=("username", "fullname", "address", "dob", "gender", "mobile", "email", "national_id", "approved"),
            show="headings",
            yscrollcommand=y_scroll.set,
            height=18
        )
        self.tree.pack(fill="both", expand=True)
        y_scroll.config(command=self.tree.yview)

        headings = [
            "Username", "Full Name", "Address", "Date of Birth", "Gender",
            "Mobile", "Email", "National ID", "Approved"
        ]
        for col, text in zip(self.tree["columns"], headings):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=120, anchor="center")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        refresh_btn = ctk.CTkButton(btn_frame, text="🔄 Refresh", width=120, command=self.load_employee_data)
        refresh_btn.grid(row=0, column=0, padx=10)

        edit_btn = ctk.CTkButton(btn_frame, text="✏️ Edit Employee", width=150, command=self.edit_employee_page)
        edit_btn.grid(row=0, column=1, padx=10)

        approve_btn = ctk.CTkButton(btn_frame, text="✅ Approve", width=150, command=self.approve_employee)
        approve_btn.grid(row=0, column=2, padx=10)

        delete_btn = ctk.CTkButton(btn_frame, text="🗑 Delete", width=150, command=self.delete_employee)
        delete_btn.grid(row=0, column=3, padx=10)

        back_btn = ctk.CTkButton(btn_frame, text="← Back", width=100, command=self.manager_login_page)
        back_btn.grid(row=0, column=4, padx=10)

        self.load_employee_data()

    def load_employee_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT username, fullname, address, dob, gender, mobile, email, national_id, approved
            FROM users WHERE role='employee'
        """)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", "end", values=row)

    def edit_employee_page(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an employee to edit.")
            return

        username = self.tree.item(selected, "values")[0]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT fullname, address, dob, gender, mobile, email, national_id
            FROM users WHERE username=?
        """, (username,))
        data = cur.fetchone()
        conn.close()

        if not data:
            messagebox.showerror("Error", "Employee not found.")
            return

        self.clear_window()
        title = ctk.CTkLabel(self, text=f"Edit Employee - {username}", font=("Arial", 22, "bold"))
        title.pack(pady=15)

        labels = ["Full Name", "Address", "Date of Birth (DD-MM-YYYY)", "Gender",
                  "Mobile (01X-XXXXXXXX)", "Email", "National ID (11 digits)"]
        self.edit_entries = {}

        for label_text, value in zip(labels, data):
            lbl = ctk.CTkLabel(self, text=label_text, font=("Arial", 14))
            lbl.pack(pady=(10, 0))
            ent = ctk.CTkEntry(self, width=300)
            ent.pack()
            ent.insert(0, str(value))
            self.edit_entries[label_text] = ent

        def save_changes():
            fullname = self.edit_entries["Full Name"].get().strip()
            address = self.edit_entries["Address"].get().strip()
            dob = self.edit_entries["Date of Birth (DD-MM-YYYY)"].get().strip()
            gender = self.edit_entries["Gender"].get().strip()
            mobile = self.edit_entries["Mobile (01X-XXXXXXXX)"].get().strip()
            email = self.edit_entries["Email"].get().strip()
            national_id = self.edit_entries["National ID (11 digits)"].get().strip()

            if not all([fullname, address, dob, gender, mobile, email, national_id]):
                messagebox.showwarning("Warning", "All fields are required.")
                return
            if not re.match(r"^01\d-\d{8}$", mobile):
                messagebox.showerror("Error", "Invalid mobile format. Use 01X-XXXXXXXX.")
                return
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
                messagebox.showerror("Error", "Invalid email format.")
                return
            if not (national_id.isdigit() and len(national_id) == 11):
                messagebox.showerror("Error", "National ID must be 11 digits.")
                return

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE users
                SET fullname=?, address=?, dob=?, gender=?, mobile=?, email=?, national_id=?
                WHERE username=?
            """, (fullname, address, dob, gender, mobile, email, national_id, username))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Employee details updated successfully.")
            self.manager_dashboard_page()

        save_btn = ctk.CTkButton(self, text="💾 Save Changes", width=160, command=save_changes)
        save_btn.pack(pady=20)

        back_btn = ctk.CTkButton(self, text="← Back", width=120, command=self.manager_dashboard_page)
        back_btn.pack(pady=10)

    def approve_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an employee to approve.")
            return

        username = self.tree.item(selected, "values")[0]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE users SET approved='Yes' WHERE username=?", (username,))
        conn.commit()
        conn.close()
        self.load_employee_data()
        messagebox.showinfo("Approved", f"Employee '{username}' approved successfully.")

    def delete_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an employee to delete.")
            return

        username = self.tree.item(selected, "values")[0]
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete '{username}'?")
        if confirm:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
            conn.close()
            self.load_employee_data()
            messagebox.showinfo("Deleted", f"Employee '{username}' deleted successfully.")

    # ---------------- EMPLOYEE LOGIN/REGISTER ----------------
    def employee_login_page(self):
        self.clear_window()

        bg_label = ctk.CTkLabel(self, image=self.bg_employee, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        label = ctk.CTkLabel(self, text="Welcome, Employee!", font=("Arial", 24, "bold"))
        label.pack(pady=20)

        # ----- Bigger TabView -----
        tabview = ctk.CTkTabview(self, width=900, height=500, fg_color="transparent")
        tabview.pack(pady=10)

        login_tab = tabview.add("Login")
        register_tab = tabview.add("Register")

        # ===== LOGIN TAB =====
        login_frame = ctk.CTkFrame(login_tab, fg_color="transparent")
        login_frame.pack(pady=50)

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
            cur.execute("SELECT password, approved FROM users WHERE username=? AND role='employee'", (username,))
            result = cur.fetchone()
            conn.close()

            if result and result[0] == hash_password(password):
                if result[1] == "Yes":
                    message_login.configure(text="Login successful!", text_color="green")
                else:
                    message_login.configure(text="Your account is not approved yet.", text_color="orange")
            else:
                message_login.configure(text="Invalid username/password.", text_color="red")

        login_btn = ctk.CTkButton(login_frame, text="Login", width=120, command=login)
        login_btn.pack(pady=10)

        # ===== REGISTER TAB =====
        reg_frame = ctk.CTkScrollableFrame(register_tab, width=850, height=450)
        reg_frame.pack(pady=10)

        reg_frame.bind_all("<MouseWheel>", lambda e: reg_frame._parent_canvas.yview_scroll(-1*(e.delta//120), "units"))

        # Split register into two columns
        left_frame = ctk.CTkFrame(reg_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=20, pady=10, fill="y")

        right_frame = ctk.CTkFrame(reg_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=10, fill="y")

        fields = {}

        def add_field(frame, label_text, **kwargs):
            lbl = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
            lbl.pack(pady=(10, 0))
            ent = ctk.CTkEntry(frame, width=300, justify="center", **kwargs)
            ent.pack(pady=2)
            return ent

        # ----- LEFT COLUMN -----
        fields["fullname"] = add_field(left_frame, "Full Name:")
        fields["address"] = add_field(left_frame, "Primary Address:")

        dob_label = ctk.CTkLabel(left_frame, text="Date of Birth:", font=("Arial", 14))
        dob_label.pack(pady=(10, 0))
        dob_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        dob_frame.pack(pady=(0,5))
        day, month, year = tk.StringVar(value="Day"), tk.StringVar(value="Month"), tk.StringVar(value="Year")
        ctk.CTkOptionMenu(dob_frame, variable=day, values=[str(i) for i in range(1,32)], width=80).grid(row=0,column=0,padx=5)
        ctk.CTkOptionMenu(dob_frame, variable=month, values=[str(i) for i in range(1,13)], width=80).grid(row=0,column=1,padx=5)
        ctk.CTkOptionMenu(dob_frame, variable=year, values=[str(i) for i in range(1950,2026)], width=100).grid(row=0,column=2,padx=5)

        gender_label = ctk.CTkLabel(left_frame, text="Gender:", font=("Arial", 14))
        gender_label.pack(pady=(10, 0))
        gender = tk.StringVar(value="Select")
        ctk.CTkOptionMenu(left_frame, variable=gender, values=["Male","Female","Other"]).pack()

        fields["mobile"] = add_field(left_frame, "Mobile (01X-XXXXXXXX):")

        # Automatically insert dash after 3 digits
        def format_mobile(event):
            value = fields["mobile"].get().replace("-", "")
            if len(value) > 3:
                value = value[:3] + "-" + value[3:]
            fields["mobile"].delete(0, tk.END)
            fields["mobile"].insert(0, value)

        fields["mobile"].bind("<KeyRelease>", format_mobile)
        fields["email"] = add_field(left_frame, "Email:")

        # ----- RIGHT COLUMN -----
        fields["national_id"] = add_field(right_frame, "National ID (11 digits):")
        fields["username"] = add_field(right_frame, "Username:")
        fields["password"] = add_field(right_frame, "Password:", show="*")
        fields["confirm_password"] = add_field(right_frame, "Confirm Password:", show="*")

        message_reg = ctk.CTkLabel(reg_frame, text="", font=("Arial", 14), text_color="red")
        message_reg.pack(pady=10)

        def register():
            data = {k: v.get().strip() for k, v in fields.items()}
            dob_value = f"{day.get()}-{month.get()}-{year.get()}"
            gender_value = gender.get()

            if any(v == "" for v in data.values()):
                message_reg.configure(text="Please fill all fields.")
                return
            if day.get() in ("Day", "") or month.get() in ("Month", "") or year.get() in ("Year", ""):
                message_reg.configure(text="Select valid DOB.")
                return
            if gender_value == "Select":
                message_reg.configure(text="Select a gender.")
                return
            if not re.match(r"^01[3-9]-\d{8}$", data["mobile"]):
                message_reg.configure(text="Invalid mobile format. Third digit must be 3-9.")
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
                    data["address"], dob_value, gender_value, data["mobile"], data["email"], data["national_id"]
                ))
                conn.commit()
                message_reg.configure(text="Registration successful! Pending approval.", text_color="green")
            except sqlite3.IntegrityError:
                message_reg.configure(text="Username already exists.", text_color="red")
            conn.close()

        register_btn = ctk.CTkButton(reg_frame, text="Register", width=120, command=register)
        register_btn.pack(pady=10)

        # ----- Back Button -----
        back_btn = ctk.CTkButton(self, text="← Back", width=100, command=self.build_welcome_page)
        back_btn.pack(pady=10)


    # ---------------- CUSTOMER PAGE ----------------
    def customer_welcome_page(self):
        self.clear_window()

        # Background image
        bg_label = ctk.CTkLabel(self, image=self.bg_customer, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Back button at bottom center
        back_btn = ctk.CTkButton(self, text="← Back", width=120, command=self.build_welcome_page)
        back_btn.place(relx=0.5, rely=0.9, anchor="center")   # 90% down the page



# ---------------- HELPERS ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            fullname TEXT,
            address TEXT,
            dob TEXT,
            gender TEXT,
            mobile TEXT,
            email TEXT,
            national_id TEXT,
            approved TEXT DEFAULT 'No'
        )
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
