import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageFilter
import sqlite3
import hashlib
import os
import re
from datetime import datetime

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

        self.menu_bg = ctk.CTkImage(
            light_image=Image.open("images/For Menu Final.png"),
            dark_image=Image.open("images/For Menu Final.png"),
            size=(1000, 600)
        )


        # runtime state
        self.cart = {}  # item_id -> {"name": str, "price": float, "qty": int}
        self.availability_changes = {}  # item_id -> new_available (0/1) (employee staging)
        self.total_amount = 0.0

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


        x_scroll = tk.Scrollbar(table_frame, orient="horizontal")
        x_scroll.pack(side="bottom", fill="x")

        # Add Salary column
        self.tree = ttk.Treeview(
            table_frame,
            columns=("username", "fullname", "address", "dob", "gender",
                    "mobile", "email", "national_id", "approved", "salary"),
            show="headings",
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
            height=18
        )
        self.tree.pack(fill="both", expand=True)
        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)

        headings = [
            "Username", "Full Name", "Address", "Date of Birth", "Gender",
            "Mobile", "Email", "National ID", "Approved", "Salary Due ($)"
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

        # ✔ FIXED — Pay Salary Button
        pay_btn = ctk.CTkButton(btn_frame, text="💵 Pay Salary", width=150, command=self.pay_salary)
        pay_btn.grid(row=0, column=4, padx=10)

        # ✔ FIXED — Logout Button
        logout_btn = ctk.CTkButton(btn_frame, text="Logout", width=100, command=self.build_welcome_page)
        logout_btn.grid(row=0, column=5, padx=10)

        self.load_employee_data()


    def load_employee_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            SELECT username, fullname, address, dob, gender, mobile, email, national_id, approved
            FROM users
            WHERE role='employee'
        """)
        employees = cur.fetchall()

        for emp in employees:
            username = emp[0]

            # Calculate due salary
            cur.execute("SELECT SUM(amount) FROM attendance WHERE username=? AND paid=0", (username,))
            due = cur.fetchone()[0]
            due = due if due else 0.0

            self.tree.insert("", "end", values=(
                emp[0], emp[1], emp[2], emp[3], emp[4],
                emp[5], emp[6], emp[7], emp[8], f"{due:.2f}"
            ))

        conn.close()



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
                    # record clock-in and open employee dashboard
                    clock_in_time = record_clock_in(username)
                    # if a previous open session existed, record_clock_in returns that clock-in
                    message_login.configure(text="Login successful! Clock-in recorded.", text_color="green")
                    self.employee_dashboard_page(username)
                else:
                    message_login.configure(text="Your account is not approved yet.", text_color="orange")
            else:
                message_login.configure(text="Invalid username/password.", text_color="red")
                login_btn = ctk.CTkButton(login_frame, text="Login", width=120, command=login)
                login_btn.pack(pady=10)

        login_btn = ctk.CTkButton(login_frame, text="Login", width=120, command=login)
        login_btn.pack(pady=10)
        # ----- Back button for Login -----
        back_login_btn = ctk.CTkButton(login_frame, text="← Back", width=120, command=self.build_welcome_page)
        back_login_btn.pack(pady=20)

        # ===== REGISTER TAB =====
        reg_frame = ctk.CTkScrollableFrame(register_tab, width=850, height=450)
        reg_frame.pack(pady=10)

        reg_frame.bind_all("<MouseWheel>", lambda e: reg_frame._parent_canvas.yview_scroll(-1*(e.delta//120), "units"))

        # Split register into two columns
        left_frame = ctk.CTkFrame(reg_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=20, pady=10, fill="y")

        right_frame = ctk.CTkFrame(reg_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)

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

        # Automatically insert dash after 3 digits and take only first 11 digits
        def format_mobile(event):
            value = ''.join(filter(str.isdigit, fields["mobile"].get()))  # keep digits only
            value = value[:11]  # limit to first 11 digits
            if len(value) > 3:
                value = value[:3] + "-" + value[3:]
            fields["mobile"].delete(0, tk.END)
            fields["mobile"].insert(0, value)

        fields["mobile"].bind("<KeyRelease>", format_mobile)
        fields["email"] = add_field(left_frame, "Email:")

        # ----- RIGHT COLUMN -----
        fields["national_id"] = add_field(right_frame, "National ID (11 digits):")
        # Limit National ID to 11 digits only
        def format_national_id(event):
            value = ''.join(filter(str.isdigit, fields["national_id"].get()))
            value = value[:11]
            fields["national_id"].delete(0, tk.END)
            fields["national_id"].insert(0, value)
        fields["national_id"].bind("<KeyRelease>", format_national_id)

        fields["username"] = add_field(right_frame, "Username:")
        fields["password"] = add_field(right_frame, "Password:", show="*")
        fields["confirm_password"] = add_field(right_frame, "Confirm Password:", show="*")

        message_reg = ctk.CTkLabel(right_frame, text="", font=("Arial", 14), text_color="red")
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

        register_btn = ctk.CTkButton(right_frame, text="Register", width=120, command=register)
        register_btn.pack(pady=10)

        # ----- Back Button for Register -----
        back_reg_btn = ctk.CTkButton(right_frame, text="← Back", width=120, command=self.build_welcome_page)
        back_reg_btn.pack(pady=10)



    # ---------------- CUSTOMER PAGE ----------------
    def customer_welcome_page(self):
        self.clear_window()

        bg_label = ctk.CTkLabel(self, image=self.bg_customer, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        title = ctk.CTkLabel(self, text="Restaurant Menu", font=("Arial", 28, "bold"))
        title.pack(pady=40)

        # Load menu with customer role (NO editing)
        self.build_menu_pages("customer")



    
    def employee_dashboard_page(self, username):
        """
        Simplified employee dashboard:
        - Shows a welcome message only.
        - Logout silently records clock-out and returns to welcome page.
        """

        self.clear_window()

        # background image
        bg_label = ctk.CTkLabel(self, image=self.bg_employee, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Welcome text
        title = ctk.CTkLabel(
            self,
            text=f"Welcome Employee, {username}!",
            font=("Arial", 26, "bold")
        )
        title.pack(pady=40)
        self.build_menu_pages("employee")

        spacer = ctk.CTkLabel(self, text="")
        spacer.pack(pady=20)

        def do_logout():
            # silently record clock-out
            record_clock_out(username)

            # no messagebox shown to employee
            self.build_welcome_page()

        logout_btn = ctk.CTkButton(self, text="Logout", width=140, command=do_logout)
        logout_btn.place(relx=0.98, rely=0.97, anchor="se")  # bottom-right corner

    
    def pay_salary(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Employee", "Please select an employee to pay salary.")
            return

        username = self.tree.item(selected[0])["values"][0]

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Mark all unpaid attendance as paid
        cur.execute("UPDATE attendance SET paid=1 WHERE username=? AND paid=0", (username,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Salary Paid", f"Salary for {username} has been cleared.")

        self.load_employee_data()


    def build_menu_pages(self, role):
        """Create a 3-page menu system using the same background."""
        self.menu_role = role
        self.menu_page_index = 0  # 0=Appetizer, 1=Main, 2=Dessert

        self.menu_categories = ["appetizer", "main", "dessert"]
        self.menu_titles = ["APPETIZERS", "MAIN COURSE", "DESSERTS"]

        self.show_menu_page()


    def show_menu_page(self):
        self.clear_window()

        # ===== BACKGROUND =====
        bg = ctk.CTkLabel(self, image=self.menu_bg, text="")
        bg.place(relx=0.5, rely=0.5, anchor="center")

        # ===== TOP TITLE + TOTAL =====
        title_text = self.menu_titles[self.menu_page_index]
        title = ctk.CTkLabel(self, text=title_text, font=("DejaVu Serif", 30, "bold"))
        title.place(relx=0.5, rely=0.08, anchor="center")

        total_frame = ctk.CTkFrame(self, fg_color="transparent")
        total_frame.place(relx=0.92, rely=0.06, anchor="ne")
        self.total_label = ctk.CTkLabel(total_frame, text=f"Total: ${self.total_amount:.2f}",
                                        font=("Arial", 14, "bold"))
        self.total_label.pack()

        # ===== CONTENT FRAME =====
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.place(relx=0.5, rely=0.55, anchor="center")

        # ===== LOAD ITEMS =====
        category = self.menu_categories[self.menu_page_index]
        items = self.load_menu_items(category)

        if not items:
            ctk.CTkLabel(main_frame, text="No items added yet.", font=("Lobster", 22)).pack(pady=20)
            return

        # ===== POPULATE ITEMS =====
        for item_id, name, price, available in items:
            # Determine staged availability
            shown_available = self.availability_changes.get(item_id, available)
            color = "white" if shown_available else "#ff4d4d"

            # ===== ITEM ROW =====
            item_row = ctk.CTkFrame(main_frame, fg_color="transparent")
            item_row.pack(fill="x", pady=10)

            # LEFT: Name + Description
            left_item = ctk.CTkFrame(item_row, width=300, fg_color="transparent")
            left_item.pack(side="left", padx=10, fill="y")
            ctk.CTkLabel(left_item, text=name, font=("Arial", 13, "bold"), text_color=color).pack(anchor="w")
            ctk.CTkLabel(left_item, text="A delicious choice loved by customers.",
                        font=("Arial", 11), text_color="#cccccc").pack(anchor="w")

            # MIDDLE: Price
            middle_item = ctk.CTkFrame(item_row, width=120, fg_color="transparent")
            middle_item.pack(side="left", padx=10, fill="y")
            ctk.CTkLabel(middle_item, text=f"${price:.2f}", font=("Arial", 13), text_color=color).pack(expand=True)

            # RIGHT: Role-specific button
            right_item = ctk.CTkFrame(item_row, width=140, fg_color="transparent")
            right_item.pack(side="left", padx=10, fill="y")
            if self.menu_role == "customer":
                if shown_available:
                    ctk.CTkButton(right_item, text="Add to Cart", width=120,
                                command=lambda iid=item_id, n=name, p=price: self.add_to_cart(iid, n, p)).pack(expand=True)
                else:
                    ctk.CTkLabel(right_item, text="Unavailable", font=("Arial", 12), text_color="#ff4d4d").pack(expand=True)
            elif self.menu_role == "employee":
                btn_text = "Set Unavailable" if shown_available else "Set Available"
                ctk.CTkButton(right_item, text=btn_text, width=140,
                            command=lambda iid=item_id, curr=shown_available: self.toggle_availability_staged(iid, curr)).pack(expand=True)

        # ===== NAV BUTTONS =====
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.place(relx=0.5, rely=0.92, anchor="center")

        ctk.CTkButton(btn_frame, text="← Previous", width=120,
                    state="normal" if self.menu_page_index > 0 else "disabled",
                    command=self.menu_prev_page).grid(row=0, column=0, padx=10)

        ctk.CTkButton(btn_frame, text="Next →", width=120,
                    state="normal" if self.menu_page_index < 2 else "disabled",
                    command=self.menu_next_page).grid(row=0, column=1, padx=10)

        ctk.CTkButton(btn_frame, text="Back", width=120, command=self.build_welcome_page).grid(row=0, column=2, padx=10)

        # Employee-only: Save Changes Button
        if self.menu_role == "employee":
            ctk.CTkButton(
                btn_frame,
                text="💾 Save Changes",
                width=140,
                command=self.save_availability_changes
            ).grid(row=0, column=3, padx=10)

        # Pay Now button on last page for customer
        if self.menu_page_index == 2 and self.menu_role == "customer":
            ctk.CTkButton(btn_frame, text="💳 Pay Now", width=140, command=self.open_pay_page).grid(row=0, column=3, padx=10)




        # customer: add item to in-memory cart
    def add_to_cart(self, item_id, name, price):
        entry = self.cart.get(item_id)
        if entry:
            entry["qty"] += 1
        else:
            self.cart[item_id] = {"name": name, "price": price, "qty": 1}
        self.update_total_amount()
        # quick visual feedback: update total label
        self.total_label.configure(text=f"Total: ${self.total_amount:.2f}")

    def update_total_amount(self):
        total = 0.0
        for entry in self.cart.values():
            total += entry["price"] * entry["qty"]
        self.total_amount = total

    # Customer: payment summary window and pay action
    def open_pay_page(self):
        if not self.cart:
            messagebox.showinfo("Cart Empty", "You have no items in the cart.")
            return

        pay_win = ctk.CTkToplevel(self)
        pay_win.title("Payment Summary")
        pay_win.geometry("420x520")
        pay_win.transient(self)

        header = ctk.CTkLabel(pay_win, text="Your Order", font=("Arial", 18, "bold"))
        header.pack(pady=10)

        frame = ctk.CTkFrame(pay_win)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Tree-like summary
        tree = ttk.Treeview(frame, columns=("name", "qty", "price"), show="headings", height=10)
        tree.heading("name", text="Item")
        tree.heading("qty", text="Qty")
        tree.heading("price", text="Price")
        tree.pack(fill="both", expand=True, padx=5, pady=5)

        for iid, e in self.cart.items():
            tree.insert("", "end", values=(e["name"], e["qty"], f"${e['price']*e['qty']:.2f}"))

        total_lbl = ctk.CTkLabel(pay_win, text=f"Total: ${self.total_amount:.2f}", font=("Arial", 14, "bold"))
        total_lbl.pack(pady=8)

        def do_pay():
            # Payment complete: clear cart and update ui
            self.cart.clear()
            self.update_total_amount()
            self.total_label.configure(text=f"Total: ${self.total_amount:.2f}")
            messagebox.showinfo("Payment Successful", "Payment completed successfully!")
            pay_win.destroy()
            # refresh menu page so add buttons/availability still reflect DB state
            self.show_menu_page()

        pay_btn = ctk.CTkButton(pay_win, text="Pay", width=120, command=do_pay)
        pay_btn.pack(pady=10)

    # EMPLOYEE: toggle availability staging (doesn't write to DB until Save pressed)
    def toggle_availability_staged(self, item_id, current_shown_value):
        # flip (current_shown_value is 1 or 0)
        new_val = 0 if current_shown_value == 1 else 1
        self.availability_changes[item_id] = new_val
        # refresh page to update UI (buttons & colors)
        self.show_menu_page()

    # EMPLOYEE: save staged availability changes to DB
    def save_availability_changes(self):
        if not self.availability_changes:
            messagebox.showinfo("No Changes", "There are no changes to save.")
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        for item_id, new_val in self.availability_changes.items():
            cur.execute("UPDATE menu_items SET available=? WHERE id=?", (new_val, item_id))
        conn.commit()
        conn.close()

        self.availability_changes.clear()
        messagebox.showinfo("Saved", "Availability changes saved.")
        # Refresh page so new availability is reflected for all roles
        self.show_menu_page()



    def load_menu_items(self, category):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, name, price, available FROM menu_items WHERE category = ?", (category,))
        items = cur.fetchall()
        conn.close()
        return items



    def menu_next_page(self):
        if self.menu_page_index < 2:
            self.menu_page_index += 1
        self.show_menu_page()

    def menu_prev_page(self):
        if self.menu_page_index > 0:
            self.menu_page_index -= 1
        self.show_menu_page()


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

    # new attendance table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            clock_in TEXT NOT NULL,
            clock_out TEXT,
            hours REAL,
            amount REAL,
            paid INTEGER DEFAULT 0
        )
    """)

    # new menu items table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,      -- appetizer, main, dessert
            price REAL NOT NULL,
            available INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Seed default manager if not exists
    cur.execute("SELECT COUNT(*) FROM users WHERE role='manager'")
    manager_count = cur.fetchone()[0]

    if manager_count == 0:
        cur.execute("""
            INSERT INTO users (username, password, role, fullname, approved)
            VALUES ('manager', 'manager123', 'manager', 'Default Manager', 'Yes')
        """)
        print("Manager account created.")

    cur.execute("SELECT COUNT(*) FROM menu_items")
    count = cur.fetchone()[0]

    if count == 0:
        print("Seeding menu items...")

        menu_seed_data = [
            # --- APPETIZERS ---
            ("French Fries", "appetizer", 120, 1),
            ("Chicken Wings (6 pcs)", "appetizer", 220, 1),
            ("Cheese Balls (6 pcs)", "appetizer", 150, 1),
            ("Garlic Bread (4 pcs)", "appetizer", 90, 1),

            # --- MAIN COURSE ---
            ("Margherita Pizza", "main", 320, 1),
            ("Chicken Supreme Pizza", "main", 520, 1),
            ("Pepperoni Pizza", "main", 360, 1),
            ("Double Decker Pizza", "main", 480, 1),
            ("Classic Beef Burger", "main", 250, 1),

            # --- DESSERT / DRINKS ---
            ("Espresso", "dessert", 120, 1),
            ("Cappuccino", "dessert", 180, 1),
            ("Latte", "dessert", 200, 1),
            ("Mocha", "dessert", 230, 1),
            ("Lemon Mint Drink", "dessert", 60, 1),
        ]

        cur.executemany(
            "INSERT INTO menu_items (name, category, price, available) VALUES (?, ?, ?, ?)",
            menu_seed_data
        )
        print("Menu items inserted successfully!")

    conn.commit()
    conn.close()

def reset_menu():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Delete all existing menu items
    cur.execute("DELETE FROM menu_items")

    # Seed only current items
    menu_seed_data = [
        # --- APPETIZERS ---
        ("French Fries", "appetizer", 120, 1),
        ("Chicken Wings (6 pcs)", "appetizer", 220, 1),
        ("Cheese Balls (6 pcs)", "appetizer", 150, 1),
        ("Garlic Bread (4 pcs)", "appetizer", 90, 1),

        # --- MAIN COURSE ---
        ("Margherita Pizza", "main", 320, 1),
        ("Chicken Supreme Pizza", "main", 520, 1),
        ("Pepperoni Pizza", "main", 360, 1),
        ("Double Decker Pizza", "main", 480, 1),
        ("Classic Beef Burger", "main", 250, 1),

        # --- DESSERT / DRINKS ---
        ("Espresso", "dessert", 120, 1),
        ("Cappuccino", "dessert", 180, 1),
        ("Latte", "dessert", 200, 1),
        ("Mocha", "dessert", 230, 1),
        ("Lemon Mint Drink", "dessert", 60, 1),
    ]

    cur.executemany(
        "INSERT INTO menu_items (name, category, price, available) VALUES (?, ?, ?, ?)",
        menu_seed_data
    )

    conn.commit()
    conn.close()
    print("Menu reset and seeded successfully!")


def record_clock_in(username):
    """
    Insert a new attendance record with current timestamp as clock_in,
    but if there's already an open attendance row (clock_out IS NULL) for this user,
    return that existing clock-in timestamp instead of creating a duplicate.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # check for open attendance first
    cur.execute("""
        SELECT id, clock_in FROM attendance
        WHERE username=? AND clock_out IS NULL
        ORDER BY id DESC LIMIT 1
    """, (username,))
    open_row = cur.fetchone()
    if open_row:
        # already clocked-in; return existing clock_in
        existing_clock_in = open_row[1]
        conn.close()
        return existing_clock_in

    # otherwise create a new clock-in
    now = datetime.now().isoformat(timespec="seconds")
    cur.execute("INSERT INTO attendance (username, clock_in) VALUES (?, ?)", (username, now))
    conn.commit()
    conn.close()
    return now



def record_clock_out(username):
    """
    Find the most recent attendance row for username with clock_out IS NULL,
    set clock_out to now, compute hours and amount, and update the row.
    Returns (hours, amount, clock_in, clock_out) or None if no open session.
    """
    now_dt = datetime.now()
    now = now_dt.isoformat(timespec="seconds")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # find last open attendance
    cur.execute("""
        SELECT id, clock_in FROM attendance
        WHERE username=? AND clock_out IS NULL
        ORDER BY id DESC LIMIT 1
    """, (username,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None  # no open session found

    attendance_id, clock_in_str = row
    
    clock_in_dt = datetime.fromisoformat(clock_in_str)

    seconds = (now_dt - clock_in_dt).total_seconds()
    hours = round(seconds / 3600, 4)  # hours as float, rounded

    # determine rate by role
    cur.execute("SELECT role FROM users WHERE username=?", (username,))
    user_row = cur.fetchone()
    role = user_row[0] if user_row else None

    # Rates (assumption: chef = $30/hour)
    rates = {
        "waiter": 15.0,
        "chef": 30.0,
        "cashier": 12.0,
        "cleaner": 12.0
    }
    rate = rates.get(role.lower() if isinstance(role, str) else "", 12.0)  # default 12 if unknown

    amount = round(hours * rate, 2)

    # update attendance record
    cur.execute("""
        UPDATE attendance
        SET clock_out=?, hours=?, amount=?
        WHERE id=?
    """, (now, hours, amount, attendance_id))
    conn.commit()
    conn.close()

    return hours, amount, clock_in_str, now



if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    #init_db()
    #reset_menu()
    app = App()
    app.mainloop()
