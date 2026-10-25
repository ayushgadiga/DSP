import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB_FILE = "food_delivery.db"

# fixed menu with prices for now - could easily become its own table later
MENU = {
    "Margherita Pizza": 8.99,
    "Cheeseburger": 6.49,
    "Chicken Biryani": 7.99,
    "Caesar Salad": 5.49,
    "Pasta Alfredo": 7.49,
    "Butter Naan": 1.99,
    "Cold Coffee": 2.99,
    "Chocolate Brownie": 3.49,
}

# warm, food-y palette instead of the usual blue/grey admin-panel look
COLORS = {
    "bg": "#faf6f1",
    "card": "#ffffff",
    "border": "#e7dccb",
    "primary": "#c1440e",
    "success": "#588157",
    "danger": "#9e2a2b",
    "text": "#2b2320",
    "muted": "#8a7f76",
}

STATUS_COLORS = {
    "Placed": "#8a7f76",
    "Preparing": "#c98a2c",
    "Picked Up": "#3a6ea5",
    "Delivered": "#588157",
    "Cancelled": "#9e2a2b",
}

FONT_H1 = ("Segoe UI", 17, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_BTN = ("Segoe UI", 10, "bold")


def shade(hex_color, factor):
    """Lighten/darken a hex color a bit - used for button hover states."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (max(0, min(255, int(c * factor))) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def make_button(parent, text, command, bg, fg="white", width=None):
    btn = tk.Button(
        parent, text=text, command=command, bg=bg, fg=fg, font=FONT_BTN,
        relief="flat", bd=0, padx=14, pady=8, cursor="hand2",
        activebackground=shade(bg, 0.85), activeforeground=fg,
    )
    if width:
        btn.config(width=width)
    hover = shade(bg, 0.9)
    btn.bind("<Enter>", lambda e: btn.config(bg=hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def center_window(win, width, height):
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{width}x{height}+{(sw - width) // 2}+{(sh - height) // 3}")


def setup_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TEntry", padding=5)
    style.configure("TCombobox", padding=4)
    style.configure("TSpinbox", padding=4)
    style.configure("Treeview", font=FONT_BODY, rowheight=28,
                     background=COLORS["card"], fieldbackground=COLORS["card"], borderwidth=0)
    style.configure("Treeview.Heading", font=FONT_BOLD, background="#f1e9dc", foreground=COLORS["text"])
    style.map("Treeview", background=[("selected", "#f0dcc9")])


# ---- database stuff ----

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            price REAL NOT NULL DEFAULT 0,
            notes TEXT,
            status TEXT NOT NULL DEFAULT 'Placed',
            created_at TEXT
        )
    ''')

    # in case someone's running this against an older copy of the db
    for stmt in (
        "ALTER TABLE Orders ADD COLUMN price REAL NOT NULL DEFAULT 0",
        "ALTER TABLE Orders ADD COLUMN notes TEXT",
        "ALTER TABLE Orders ADD COLUMN created_at TEXT",
    ):
        try:
            cur.execute(stmt)
        except sqlite3.OperationalError:
            pass  # column's already there, nothing to do

    conn.commit()
    conn.close()


def insert_order(customer_name, item_name, quantity, price, notes=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO Orders (customer_name, item_name, quantity, price, notes, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (customer_name, item_name, quantity, price, notes, datetime.now().strftime("%b %d, %I:%M %p")),
    )
    conn.commit()
    conn.close()


def fetch_orders(include_finished=False):
    conn = get_connection()
    cur = conn.cursor()
    if include_finished:
        cur.execute("SELECT * FROM Orders ORDER BY order_id DESC")
    else:
        cur.execute("SELECT * FROM Orders WHERE status NOT IN ('Delivered', 'Cancelled') ORDER BY order_id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def update_order_status(order_id, new_status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Orders SET status = ? WHERE order_id = ?", (new_status, order_id))
    conn.commit()
    conn.close()


# ---- customer-facing order form ----

class CustomerWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Order Something Tasty")
        self.window.config(bg=COLORS["bg"])
        self.window.resizable(False, False)
        center_window(self.window, 420, 540)

        tk.Label(self.window, text="🍔  Place an Order", font=FONT_H1,
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(20, 4))
        tk.Label(self.window, text="pick something off the menu, or ask for anything else",
                 font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["muted"]).pack(pady=(0, 15))

        card = tk.Frame(self.window, bg=COLORS["card"], highlightbackground=COLORS["border"],
                         highlightthickness=1)
        card.pack(padx=20, fill="both", expand=True)

        inner = tk.Frame(card, bg=COLORS["card"])
        inner.pack(padx=20, pady=20, fill="both", expand=True)

        self._label(inner, "Your name")
        self.name_entry = self._entry(inner)

        self._label(inner, "What are you in the mood for?")
        self.item_var = tk.StringVar()
        self.item_box = ttk.Combobox(inner, textvariable=self.item_var, state="readonly", font=FONT_BODY,
                                      values=list(MENU.keys()) + ["Something else..."])
        self.item_box.pack(fill="x", pady=(0, 10))
        self.item_box.bind("<<ComboboxSelected>>", self.on_item_change)

        # only shows up if they pick "Something else..." above
        self.custom_frame = tk.Frame(inner, bg=COLORS["card"])
        self._label(self.custom_frame, "Dish name")
        self.custom_name_entry = self._entry(self.custom_frame)
        self._label(self.custom_frame, "Price ($)")
        self.custom_price_entry = self._entry(self.custom_frame)
        self.custom_price_entry.bind("<KeyRelease>", lambda e: self.update_total())

        self._label(inner, "Quantity")
        self.qty_var = tk.StringVar(value="1")
        qty_spin = ttk.Spinbox(inner, from_=1, to=10, textvariable=self.qty_var, font=FONT_BODY,
                                command=self.update_total)
        qty_spin.pack(fill="x", pady=(0, 10))
        self.qty_var.trace_add("write", lambda *a: self.update_total())

        self._label(inner, "Anything we should know? (optional)")
        self.notes_entry = self._entry(inner)

        self.total_label = tk.Label(inner, text="Total: $0.00", font=FONT_H2,
                                     bg=COLORS["card"], fg=COLORS["primary"])
        self.total_label.pack(pady=(12, 15))

        make_button(inner, "Place Order", self.submit_order, COLORS["success"]).pack(fill="x")

    def _label(self, parent, text):
        tk.Label(parent, text=text, font=FONT_BODY, bg=parent["bg"], fg=COLORS["text"],
                  anchor="w").pack(fill="x", pady=(6, 2))

    def _entry(self, parent):
        entry = ttk.Entry(parent, font=FONT_BODY)
        entry.pack(fill="x")
        return entry

    def on_item_change(self, event=None):
        if self.item_var.get() == "Something else...":
            self.custom_frame.pack(fill="x", pady=(0, 5))
        else:
            self.custom_frame.pack_forget()
        self.update_total()

    def current_price(self):
        choice = self.item_var.get()
        if choice in MENU:
            return MENU[choice]
        try:
            return float(self.custom_price_entry.get())
        except ValueError:
            return 0.0

    def update_total(self):
        try:
            qty = int(self.qty_var.get())
        except ValueError:
            qty = 0
        self.total_label.config(text=f"Total: ${qty * self.current_price():.2f}")

    def submit_order(self):
        name = self.name_entry.get().strip()
        choice = self.item_var.get()
        item = self.custom_name_entry.get().strip() if choice == "Something else..." else choice

        if not name or not item:
            messagebox.showerror("Missing info", "Please fill in your name and pick something to order.",
                                  parent=self.window)
            return

        try:
            qty = int(self.qty_var.get())
        except ValueError:
            messagebox.showerror("Bad quantity", "Quantity has to be a number.", parent=self.window)
            return

        insert_order(name, item, qty, self.current_price(), self.notes_entry.get().strip())
        messagebox.showinfo("Order placed!", f"Thanks {name}, your order is on its way to the kitchen.",
                             parent=self.window)

        self.name_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)
        self.item_box.set("")
        self.qty_var.set("1")
        self.custom_frame.pack_forget()
        self.update_total()


# ---- restaurant-side dashboard ----

class RestaurantDashboard:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Kitchen Dashboard")
        self.window.config(bg=COLORS["bg"])
        center_window(self.window, 900, 560)

        tk.Label(self.window, text="📋  Live Orders", font=FONT_H1,
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(18, 10), anchor="w", padx=25)

        toolbar = tk.Frame(self.window, bg=COLORS["bg"])
        toolbar.pack(fill="x", padx=25)

        tk.Label(toolbar, text="Search:", font=FONT_BODY, bg=COLORS["bg"]).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.load_orders())
        ttk.Entry(toolbar, textvariable=self.search_var, font=FONT_BODY, width=22).pack(side="left", padx=(5, 20))

        tk.Label(toolbar, text="Status:", font=FONT_BODY, bg=COLORS["bg"]).pack(side="left")
        self.status_filter = tk.StringVar(value="Active")
        status_box = ttk.Combobox(toolbar, textvariable=self.status_filter, state="readonly", width=12,
                                   values=["Active", "All", "Placed", "Preparing", "Picked Up", "Delivered", "Cancelled"])
        status_box.pack(side="left", padx=5)
        status_box.bind("<<ComboboxSelected>>", lambda e: self.load_orders())

        make_button(toolbar, "Refresh", self.load_orders, COLORS["primary"], width=10).pack(side="right")

        table_frame = tk.Frame(self.window, bg=COLORS["card"], highlightbackground=COLORS["border"],
                                highlightthickness=1)
        table_frame.pack(padx=25, pady=15, fill="both", expand=True)

        columns = ("ID", "Customer", "Item", "Qty", "Price", "Total", "Status", "Placed")
        widths = (40, 130, 160, 45, 70, 70, 100, 130)
        anchors = (tk.CENTER, tk.W, tk.W, tk.CENTER, tk.CENTER, tk.CENTER, tk.CENTER, tk.CENTER)

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col, w, anchor in zip(columns, widths, anchors):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor=anchor)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        vsb.pack(side="right", fill="y", pady=10)

        for status_name, color in STATUS_COLORS.items():
            self.tree.tag_configure(status_name, foreground=color)

        self.tree.bind("<Double-1>", self.show_notes)

        self.summary_label = tk.Label(self.window, text="", font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["muted"])
        self.summary_label.pack(anchor="w", padx=25)

        btn_frame = tk.Frame(self.window, bg=COLORS["bg"])
        btn_frame.pack(pady=(8, 20))

        make_button(btn_frame, "Mark Preparing", lambda: self.change_status("Preparing"),
                    STATUS_COLORS["Preparing"], fg="black").grid(row=0, column=0, padx=5)
        make_button(btn_frame, "Mark Picked Up", lambda: self.change_status("Picked Up"),
                    STATUS_COLORS["Picked Up"]).grid(row=0, column=1, padx=5)
        make_button(btn_frame, "Mark Delivered", lambda: self.change_status("Delivered"),
                    STATUS_COLORS["Delivered"]).grid(row=0, column=2, padx=5)
        make_button(btn_frame, "Cancel Order", lambda: self.change_status("Cancelled"),
                    STATUS_COLORS["Cancelled"]).grid(row=0, column=3, padx=5)

        # notes get stashed here by order id so double-clicking a row can show them
        self.notes_by_id = {}
        self.load_orders()

    def load_orders(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        status = self.status_filter.get()
        orders = fetch_orders(include_finished=status in ("All", "Delivered", "Cancelled"))
        search = self.search_var.get().lower().strip()

        revenue = 0.0
        active_count = 0
        self.notes_by_id = {}

        for o in orders:
            if status not in ("All", "Active") and o["status"] != status:
                continue
            if search and search not in o["customer_name"].lower() and search not in o["item_name"].lower():
                continue

            total = o["quantity"] * o["price"]
            self.notes_by_id[o["order_id"]] = o["notes"]
            self.tree.insert("", tk.END, values=(
                o["order_id"], o["customer_name"], o["item_name"], o["quantity"],
                f"${o['price']:.2f}", f"${total:.2f}", o["status"], o["created_at"] or "-",
            ), tags=(o["status"],))

            if o["status"] not in ("Delivered", "Cancelled"):
                revenue += total
                active_count += 1

        self.summary_label.config(text=f"{active_count} active order(s)   ·   ${revenue:.2f} in the pipeline")

    def selected_order_id(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Nothing selected", "Pick an order from the list first.", parent=self.window)
            return None
        return int(self.tree.item(selected, "values")[0])

    def change_status(self, new_status):
        order_id = self.selected_order_id()
        if order_id is None:
            return
        update_order_status(order_id, new_status)
        self.load_orders()

    def show_notes(self, event=None):
        order_id = self.selected_order_id()
        if order_id is None:
            return
        notes = self.notes_by_id.get(order_id)
        messagebox.showinfo("Order notes", notes if notes else "No notes for this order.", parent=self.window)


# ---- launcher window ----

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Food Delivery - Control Center")
        self.root.config(bg=COLORS["bg"])
        center_window(root, 420, 320)

        tk.Label(root, text="🍽️", font=("Segoe UI", 36), bg=COLORS["bg"]).pack(pady=(30, 0))
        tk.Label(root, text="Food Delivery System", font=FONT_H1, bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(5, 0))
        tk.Label(root, text="running locally on SQLite", font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["muted"]).pack(pady=(0, 25))

        make_button(root, "Open Customer Portal", self.open_customer, COLORS["primary"], width=28).pack(pady=6)
        make_button(root, "Open Kitchen Dashboard", self.open_restaurant, COLORS["text"], width=28).pack(pady=6)

    def open_customer(self):
        CustomerWindow(self.root)

    def open_restaurant(self):
        RestaurantDashboard(self.root)


if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    setup_style()
    app = MainApp(root)
    root.mainloop()
