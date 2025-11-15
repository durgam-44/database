import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import os
import re

DB_PATH = "users.db"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("XYZ Restaurant")
        self.geometry("1000x600")
        self.resizable(False, False)

        init_db()

        self.build_welcome_page()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def build_welcome_page(self):
        self.clear_window()

        title = ctk.CTkLabel(self, text="Welcome to XYZ Restaurant", font=("Arial", 26, "bold"))
        title.pack(pady=40)

        subtitle = ctk.CTkLabel(self, text="Continue as:", font=("Arial", 20))
        subtitle.pack(pady=20)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        manager_btn = ctk.CTkButton(btn_frame, text="Manager", width=200, command=self.manager_login_page)
        manager_btn.pack(pady=10)

       # employee_btn = ctk.CTkButton(btn_frame, text="Employee", width=200, command=self.employee_login_page)
       # employee_btn.pack(pady=10)

       # customer_btn = ctk.CTkButton(btn_frame, text="Customer", width=200, command=self.customer_welcome_page)
       # customer_btn.pack(pady=10)

    # ---------------- MANAGER LOGIN ----------------
    def manager_login_page(self):
        self.clear_window()

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

        self.bind("<Return>", lambda event: login_btn.invoke())

    # ---------------- MANAGER DASHBOARD ----------------
    def manager_dashboard_page(self):
        self.clear_window()

        title = ctk.CTkLabel(self, text="Manager Dashboard - Employee Records", font=("Arial", 26, "bold"))
        title.pack(pady=20)

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(pady=10, padx=20, fill="both", expand=True)

        y_scroll = tk.Scrollbar(table_frame, orient="vertical")
        y_scroll.pack(side="right", fill="y")

        x_scroll = tk.Scrollbar(table_frame, orient="horizontal")
        x_scroll.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(
            table_frame,
            columns=("username", "fullname", "address", "dob", "gender", "mobile", "email", "national_id", "approved"),
            show="headings",
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
            height=18
        )
        self.tree.pack(fill="both", expand=True)

        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)

        headings = ["Username", "Full Name", "Address", "Date of Birth", "Gender",
                    "Mobile", "Email", "National ID", "Approved"]
        for col, text in zip(self.tree["columns"], headings):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=120, anchor="center")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        refresh_btn = ctk.CTkButton(btn_frame, text="🔄 Refresh", width=120, command=self.load_employee_data)
        refresh_btn.grid(row=0, column=0, padx=10)

        edit_btn = ctk.CTkButton(btn_frame, text="✏️ Edit Employee", width=150, command=self.edit_employee)
        edit_btn.grid(row=0, column=1, padx=10)

        delete_btn = ctk.CTkButton(btn_frame, text="🗑 Delete Employee", width=150, command=self.delete_employee)
        delete_btn.grid(row=0, column=2, padx=10)

        approve_btn = ctk.CTkButton(btn_frame, text="✅ Approve Employee", width=160, command=self.approve_employee)
        approve_btn.grid(row=0, column=3, padx=10)

        back_btn = ctk.CTkButton(btn_frame, text="← Back", width=100, command=self.build_welcome_page)
        back_btn.grid(row=0, column=4, padx=10)

        self.load_employee_data()

    def load_employee_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT username, fullname, address, dob, gender, mobile, email, national_id,
                   CASE WHEN approved=1 THEN '✅ Approved' ELSE '❌ Pending' END
            FROM users WHERE role='employee'
        """)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", "end", values=row)

    def edit_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an employee to edit.")
            return
        values = self.tree.item(selected, "values")
        EditEmployeeWindow(self, values[0])

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

    def approve_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an employee to approve.")
            return

        username = self.tree.item(selected, "values")[0]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE users SET approved=1 WHERE username=?", (username,))
        conn.commit()
        conn.close()

        self.load_employee_data()
        messagebox.showinfo("Success", f"Employee '{username}' approved successfully.")

    # ---------------- CUSTOMER PAGE ----------------
    def customer_welcome_page(self):
        self.clear_window()
        label = ctk.CTkLabel(self, text="Welcome, Customer!", font=("Arial", 26, "bold"))
        label.pack(pady=80)
        sublabel = ctk.CTkLabel(self, text="Enjoy exploring the app!", font=("Arial", 18))
        sublabel.pack(pady=10)
        back_btn = ctk.CTkButton(self, text="← Back", width=120, command=self.build_welcome_page)
        back_btn.pack(pady=30)


# ------------- Edit Employee Popup Window -------------
class EditEmployeeWindow(ctk.CTkToplevel):
    def __init__(self, parent, username):
        super().__init__(parent)
        self.title(f"Edit Employee - {username}")
        self.geometry("500x600")
        self.username = username

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT fullname, address, dob, gender, mobile, email, national_id
            FROM users WHERE username=?
        """, (username,))
        data = cur.fetchone()
        conn.close()

        if not data:
            messagebox.showerror("Error", "Employee record not found.")
            self.destroy()
            return

        labels = ["Full Name", "Address", "Date of Birth (DD-MM-YYYY)", "Gender",
                  "Mobile (01X-XXXXXXXX)", "Email", "National ID (11 digits)"]
        self.entries = {}

        for label_text, value in zip(labels, data):
            lbl = ctk.CTkLabel(self, text=label_text, font=("Arial", 14))
            lbl.pack(pady=(10, 0))
            ent = ctk.CTkEntry(self, width=300)
            ent.pack()
            ent.insert(0, str(value))
            self.entries[label_text] = ent

        save_btn = ctk.CTkButton(self, text="💾 Save Changes", width=160, command=self.save_changes)
        save_btn.pack(pady=20)

    def save_changes(self):
        fullname = self.entries["Full Name"].get().strip()
        address = self.entries["Address"].get().strip()
        dob = self.entries["Date of Birth (DD-MM-YYYY)"].get().strip()
        gender = self.entries["Gender"].get().strip()
        mobile = self.entries["Mobile (01X-XXXXXXXX)"].get().strip()
        email = self.entries["Email"].get().strip()
        national_id = self.entries["National ID (11 digits)"].get().strip()

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
        """, (fullname, address, dob, gender, mobile, email, national_id, self.username))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Employee details updated successfully.")
        self.destroy()


# ---------------- HELPER FUNCTIONS ----------------
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
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

    # Add 'approved' column if missing
    cur.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cur.fetchall()]
    if 'approved' not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN approved INTEGER DEFAULT 0")

    try:
        cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    ("manager", hash_password("manager123"), "manager",
                     "Admin Manager", "Head Office", "01-01-1980", "Male",
                     "010-12345678", "admin@travel.com", "12345678901", 1))
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


if __name__ == "__main__":
    app = App()
    app.mainloop()
