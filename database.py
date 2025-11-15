import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
import sqlite3

DB_PATH = "users.db"

class DatabaseViewer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Database Viewer - Travel Explorer")
        self.geometry("1000x600")
        self.resizable(False, False)

        title = ctk.CTkLabel(self, text="User Database Viewer", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        # Frame for table and scrollbar
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Scrollbars
        y_scroll = tk.Scrollbar(table_frame, orient="vertical")
        y_scroll.pack(side="right", fill="y")

        x_scroll = tk.Scrollbar(table_frame, orient="horizontal")
        x_scroll.pack(side="bottom", fill="x")

        # Table (Treeview)
        self.tree = ttk.Treeview(
            table_frame,
            columns=("username", "role", "fullname", "address", "dob", "gender",
                     "mobile", "email", "national_id"),
            show="headings",
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
            height=20
        )

        self.tree.pack(fill="both", expand=True)

        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)

        # Define column headings
        headings = [
            "Username", "Role", "Full Name", "Address", "Date of Birth", "Gender",
            "Mobile", "Email", "National ID"
        ]
        for col, text in zip(self.tree["columns"], headings):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=110, anchor="center")

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        refresh_btn = ctk.CTkButton(btn_frame, text="🔄 Refresh", width=120, command=self.load_data)
        refresh_btn.grid(row=0, column=0, padx=10)

        delete_btn = ctk.CTkButton(btn_frame, text="🗑 Delete Selected", width=160, command=self.delete_selected)
        delete_btn.grid(row=0, column=1, padx=10)

        exit_btn = ctk.CTkButton(btn_frame, text="❌ Close", width=120, command=self.destroy)
        exit_btn.grid(row=0, column=2, padx=10)

        self.load_data()

    def load_data(self):
        """Fetch all user data and display in table."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT username, role, fullname, address, dob, gender, mobile, email, national_id
            FROM users
        """)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", "end", values=row)

    def delete_selected(self):
        """Delete selected user from the database."""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        username = self.tree.item(selected_item, "values")[0]

        # Prevent deleting the manager account
        if username == "manager":
            tk.messagebox.showwarning("Warning", "You cannot delete the manager account.")
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        conn.close()

        self.tree.delete(selected_item)


if __name__ == "__main__":
    app = DatabaseViewer()
    app.mainloop()
