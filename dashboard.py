import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
import os

DB_PATH = "database/attendance.db"


class AttendanceDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Face Attendance Dashboard")
        self.root.geometry("1100x650")
        self.root.configure(bg="#f4f7fb")
        self.root.minsize(1000, 600)

        self.setup_styles()
        self.build_ui()
        self.refresh_data()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="white",
            foreground="#1f2937",
            rowheight=35,
            fieldbackground="white",
            font=("Segoe UI", 11)
        )

        style.configure(
            "Treeview.Heading",
            background="#1d4ed8",
            foreground="white",
            font=("Segoe UI", 11, "bold"),
            padding=10
        )

        style.map("Treeview", background=[("selected", "#dbeafe")])

        style.configure(
            "TButton",
            font=("Segoe UI", 11, "bold"),
            padding=8
        )

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#0f172a", height=80)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Face Attendance Dashboard",
            font=("Segoe UI", 28, "bold"),
            bg="#0f172a",
            fg="white"
        ).pack(side="left", padx=25, pady=18)

        self.time_label = tk.Label(
            header,
            text="",
            font=("Segoe UI", 13, "bold"),
            bg="#0f172a",
            fg="#cbd5e1"
        )
        self.time_label.pack(side="right", padx=25)

        # Top cards section
        cards_frame = tk.Frame(self.root, bg="#f4f7fb")
        cards_frame.pack(fill="x", padx=20, pady=20)

        self.card_date = self.create_card(cards_frame, "Today's Date", "#2563eb")
        self.card_date.pack(side="left", fill="both", expand=True, padx=10)

        self.card_count = self.create_card(cards_frame, "Present Count", "#059669")
        self.card_count.pack(side="left", fill="both", expand=True, padx=10)

        self.card_latest = self.create_card(cards_frame, "Latest Entry", "#ea580c")
        self.card_latest.pack(side="left", fill="both", expand=True, padx=10)

        # Controls
        controls = tk.Frame(self.root, bg="#f4f7fb")
        controls.pack(fill="x", padx=20, pady=(0, 10))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            controls,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            width=30,
            relief="solid",
            bd=1
        )
        search_entry.pack(side="left", padx=(0, 10), ipady=6)
        search_entry.insert(0, "Search by ID or Name")
        search_entry.bind("<FocusIn>", self.clear_placeholder)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        ttk.Button(controls, text="Refresh", command=self.refresh_data).pack(side="left", padx=5)

        # Table section
        table_card = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        table_card.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(
            table_card,
            text="Attendance Records",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg="#111827"
        ).pack(anchor="w", padx=15, pady=12)

        table_frame = tk.Frame(table_card, bg="white")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("ID", "Name", "Date", "Time")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=200)

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=y_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

    def create_card(self, parent, title, color):
        card = tk.Frame(parent, bg="white", bd=1, relief="solid", height=110)

        tk.Label(
            card,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#6b7280"
        ).pack(anchor="w", padx=15, pady=(12, 5))

        value_label = tk.Label(
            card,
            text="---",
            font=("Segoe UI", 20, "bold"),
            bg="white",
            fg=color
        )
        value_label.pack(anchor="w", padx=15)

        card.value_label = value_label
        return card

    def clear_placeholder(self, event):
        if self.search_var.get() == "Search by ID or Name":
            self.search_var.set("")

    def get_attendance_data(self):
        if not os.path.exists(DB_PATH):
            return []

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, name, date, time FROM attendance ORDER BY date DESC, time DESC")
        rows = cur.fetchall()
        conn.close()
        return rows

    def refresh_data(self):
        rows = self.get_attendance_data()

        # Search filter
        search_text = self.search_var.get().strip().lower()
        if search_text and search_text != "search by id or name":
            rows = [
                row for row in rows
                if search_text in str(row[0]).lower() or search_text in str(row[1]).lower()
            ]

        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add rows
        for row in rows:
            self.tree.insert("", "end", values=row)

        today = datetime.now().strftime("%Y-%m-%d")
        today_rows = [r for r in self.get_attendance_data() if r[2] == today]

        self.card_date.value_label.config(text=today)
        self.card_count.value_label.config(text=str(len(today_rows)))

        if today_rows:
            latest = today_rows[0]
            self.card_latest.value_label.config(text=f"{latest[1]} ({latest[0]})")
        else:
            self.card_latest.value_label.config(text="No Entry")

        now_time = datetime.now().strftime("%d-%m-%Y  %I:%M:%S %p")
        self.time_label.config(text=now_time)

        self.root.after(2000, self.refresh_data)


if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceDashboard(root)
    root.mainloop()
