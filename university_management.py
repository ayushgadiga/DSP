import sqlite3
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------------------------------------------------------------
# Simple color palette / fonts kept in one place so they're easy to tweak
# ---------------------------------------------------------------------
BG_COLOR = "#f0f2f5"
HEADER_BG = "#2c3e50"
HEADER_FG = "#ffffff"
ACCENT_BLUE = "#2e86de"
ACCENT_GREEN = "#27ae60"
TEXT_COLOR = "#2c3e50"
MUTED_TEXT = "#6b7280"

FONT_NORMAL = ("Segoe UI", 10)
FONT_LABEL = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_HEADER = ("Segoe UI", 15, "bold")

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UniversityManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("University Management System")
        self.root.geometry("760x600")
        self.root.minsize(680, 520)
        self.root.config(bg=BG_COLOR)

        self.init_db()
        self.create_widgets()

        # Make sure the DB connection closes cleanly when the window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # -------------------------------------------------------------
    # Database setup
    # -------------------------------------------------------------
    def init_db(self):
        """Initialize database connection and tables."""
        self.conn = sqlite3.connect("university.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                dept_id TEXT PRIMARY KEY,
                dept_name TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                user_id TEXT,
                first_name TEXT,
                last_name TEXT,
                dept_id TEXT,
                enrollment_year INTEGER
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id TEXT PRIMARY KEY,
                user_id TEXT,
                first_name TEXT,
                last_name TEXT,
                dept_id TEXT,
                specialization TEXT
            )
        ''')

        # Seed default departments if the table is empty
        self.cursor.execute("SELECT COUNT(*) FROM departments")
        if self.cursor.fetchone()[0] == 0:
            default_depts = [
                ("CS", "Computer Science"),
                ("EE", "Electrical Engineering"),
                ("ME", "Mechanical Engineering"),
            ]
            self.cursor.executemany(
                "INSERT INTO departments (dept_id, dept_name) VALUES (?, ?)",
                default_depts,
            )
            self.conn.commit()

    def get_departments(self):
        """Fetch department IDs for dropdown menus."""
        self.cursor.execute("SELECT dept_id FROM departments")
        return [row[0] for row in self.cursor.fetchall()]

    # -------------------------------------------------------------
    # Top-level layout
    # -------------------------------------------------------------
    def create_widgets(self):
        """Set up header bar, notebook tabs and status bar."""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=(16, 8))
        style.map("TNotebook.Tab", background=[("selected", "#ffffff")],
                  foreground=[("selected", ACCENT_BLUE)])

        style.configure("TFrame", background=BG_COLOR)
        style.configure("Form.TFrame", background="#ffffff")
        style.configure("TLabelframe", background="#ffffff", font=FONT_LABEL)
        style.configure("TLabelframe.Label", background="#ffffff",
                         foreground=TEXT_COLOR, font=("Segoe UI", 10, "bold"))

        style.configure("Treeview", rowheight=24, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

        style.configure("TCombobox", padding=4)

        # --- Header bar ---
        header = tk.Frame(self.root, bg=HEADER_BG, height=56)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(
            header, text="University Management System",
            bg=HEADER_BG, fg=HEADER_FG, font=FONT_HEADER
        ).pack(side="left", padx=16)

        # --- Status bar ---
        # Created before the tabs below, because the "View Records" tab
        # calls load_table_data() while it's being built, and that method
        # writes to status_var. Packed with side="bottom" so it still docks
        # at the bottom of the window regardless of creation order.
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root, textvariable=self.status_var, bd=1, relief="sunken",
            anchor="w", bg="#dfe4ea", fg=MUTED_TEXT, font=("Segoe UI", 8), padx=6
        )
        status_bar.pack(side="bottom", fill="x")

        # --- Notebook (tabs) ---
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.student_tab = ttk.Frame(notebook)
        notebook.add(self.student_tab, text="Register Student")
        self.build_student_form(self.student_tab)

        self.teacher_tab = ttk.Frame(notebook)
        notebook.add(self.teacher_tab, text="Register Teacher")
        self.build_teacher_form(self.teacher_tab)

        self.view_tab = ttk.Frame(notebook)
        notebook.add(self.view_tab, text="View Records")
        self.build_view_records(self.view_tab)

    # -------------------------------------------------------------
    # Student registration tab
    # -------------------------------------------------------------
    def build_student_form(self, parent):
        parent.config(style="TFrame")

        wrapper = tk.Frame(parent, bg=BG_COLOR)
        wrapper.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(wrapper, text="Student Registration", font=FONT_TITLE,
                 bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 12))

        box = ttk.LabelFrame(wrapper, text="Student Details", padding=16)
        box.pack(fill="x")

        self.s_fname = self._add_field(box, "First Name:", 0)
        self.s_lname = self._add_field(box, "Last Name:", 1)
        self.s_email = self._add_field(box, "Email Address:", 2)

        tk.Label(box, text="Department:", bg="#ffffff", font=FONT_LABEL,
                 anchor="w").grid(row=3, column=0, sticky="w", pady=8, padx=(0, 12))
        self.s_dept = ttk.Combobox(box, values=self.get_departments(), width=23, state="readonly")
        self.s_dept.grid(row=3, column=1, pady=8, sticky="w")
        if self.get_departments():
            self.s_dept.current(0)

        btn_frame = tk.Frame(wrapper, bg=BG_COLOR)
        btn_frame.pack(pady=18)

        tk.Button(btn_frame, text="Register Student", bg=ACCENT_GREEN, fg="white",
                  activebackground="#219150", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=16, pady=6, cursor="hand2",
                  command=self.save_student).pack(side="left", padx=6)

        tk.Button(btn_frame, text="Clear", bg="#e5e7eb", fg=TEXT_COLOR,
                  font=("Segoe UI", 10), relief="flat", padx=16, pady=6,
                  cursor="hand2",
                  command=lambda: self._clear_fields(
                      self.s_fname, self.s_lname, self.s_email)).pack(side="left", padx=6)

    # -------------------------------------------------------------
    # Teacher registration tab
    # -------------------------------------------------------------
    def build_teacher_form(self, parent):
        parent.config(style="TFrame")

        wrapper = tk.Frame(parent, bg=BG_COLOR)
        wrapper.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(wrapper, text="Teacher Registration", font=FONT_TITLE,
                 bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 12))

        box = ttk.LabelFrame(wrapper, text="Teacher Details", padding=16)
        box.pack(fill="x")

        self.t_fname = self._add_field(box, "First Name:", 0)
        self.t_lname = self._add_field(box, "Last Name:", 1)
        self.t_email = self._add_field(box, "Email Address:", 2)

        tk.Label(box, text="Department:", bg="#ffffff", font=FONT_LABEL,
                 anchor="w").grid(row=3, column=0, sticky="w", pady=8, padx=(0, 12))
        self.t_dept = ttk.Combobox(box, values=self.get_departments(), width=23, state="readonly")
        self.t_dept.grid(row=3, column=1, pady=8, sticky="w")
        if self.get_departments():
            self.t_dept.current(0)

        self.t_spec = self._add_field(box, "Specialization:", 4)

        btn_frame = tk.Frame(wrapper, bg=BG_COLOR)
        btn_frame.pack(pady=18)

        tk.Button(btn_frame, text="Register Teacher", bg=ACCENT_BLUE, fg="white",
                  activebackground="#2166b5", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=16, pady=6, cursor="hand2",
                  command=self.save_teacher).pack(side="left", padx=6)

        tk.Button(btn_frame, text="Clear", bg="#e5e7eb", fg=TEXT_COLOR,
                  font=("Segoe UI", 10), relief="flat", padx=16, pady=6,
                  cursor="hand2",
                  command=lambda: self._clear_fields(
                      self.t_fname, self.t_lname, self.t_email, self.t_spec)).pack(side="left", padx=6)

    def _add_field(self, parent, label_text, row):
        """Helper to add a label + entry row to a form grid, returns the Entry."""
        tk.Label(parent, text=label_text, bg="#ffffff", font=FONT_LABEL,
                 anchor="w").grid(row=row, column=0, sticky="w", pady=8, padx=(0, 12))
        entry = tk.Entry(parent, width=27, font=FONT_NORMAL, relief="solid",
                          borderwidth=1)
        entry.grid(row=row, column=1, pady=8, sticky="w", ipady=3)
        return entry

    def _clear_fields(self, *entries):
        for e in entries:
            e.delete(0, tk.END)

    # -------------------------------------------------------------
    # View records tab
    # -------------------------------------------------------------
    def build_view_records(self, parent):
        parent.config(style="TFrame")

        wrapper = tk.Frame(parent, bg=BG_COLOR)
        wrapper.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(wrapper, text="Database Records", font=FONT_TITLE,
                 bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 12))

        filter_frame = tk.Frame(wrapper, bg=BG_COLOR)
        filter_frame.pack(fill="x", pady=(0, 10))

        tk.Label(filter_frame, text="Select View:", bg=BG_COLOR,
                 font=("Segoe UI", 10, "bold"), fg=TEXT_COLOR).pack(side=tk.LEFT, padx=(0, 8))
        self.view_selector = ttk.Combobox(filter_frame, values=["Students", "Teachers"],
                                           width=15, state="readonly")
        self.view_selector.pack(side=tk.LEFT, padx=(0, 8))
        self.view_selector.current(0)

        tk.Button(filter_frame, text="Load Records", bg=ACCENT_BLUE, fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=4,
                  cursor="hand2", command=self.load_table_data).pack(side=tk.LEFT)

        self.record_count_var = tk.StringVar(value="")
        tk.Label(filter_frame, textvariable=self.record_count_var, bg=BG_COLOR,
                 fg=MUTED_TEXT, font=("Segoe UI", 9)).pack(side=tk.RIGHT)

        # Row of action buttons that act on whichever row is selected below
        action_frame = tk.Frame(wrapper, bg=BG_COLOR)
        action_frame.pack(fill="x", pady=(0, 10))

        tk.Button(action_frame, text="Modify Selected", bg=ACCENT_BLUE, fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=4,
                  cursor="hand2", command=self.modify_record).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(action_frame, text="Delete Selected", bg="#e74c3c", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=4,
                  cursor="hand2", command=self.delete_record).pack(side=tk.LEFT)

        tk.Label(action_frame, text="(click a row in the table, then Modify or Delete)",
                 bg=BG_COLOR, fg=MUTED_TEXT, font=("Segoe UI", 8, "italic")).pack(side=tk.LEFT, padx=10)

        # Table
        table_frame = tk.Frame(wrapper, bg="#ffffff", bd=1, relief="solid")
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(table_frame, show="headings")

        tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.load_table_data()

    def load_table_data(self):
        """Fetch and populate records based on the selected dropdown view."""
        selection = self.view_selector.get()
        # Remembered separately from the live dropdown value so that if the
        # user flips the dropdown without hitting "Load Records", a selected
        # row still matches the type actually shown in the table.
        self.current_view_type = selection

        self.tree.delete(*self.tree.get_children())

        if selection == "Students":
            columns = [
                ("ID", "Student ID", 110),
                ("Name", "Full Name", 150),
                ("Email", "Email Address", 180),
                ("Department", "Dept", 80),
                ("Year", "Year", 70),
            ]
            query = '''
                SELECT s.student_id, s.first_name || ' ' || s.last_name, u.email, s.dept_id, s.enrollment_year
                FROM students s JOIN users u ON s.user_id = u.user_id
                ORDER BY s.student_id
            '''
        else:
            columns = [
                ("ID", "Teacher ID", 110),
                ("Name", "Full Name", 150),
                ("Email", "Email Address", 180),
                ("Department", "Dept", 80),
                ("Specialization", "Specialization", 140),
            ]
            query = '''
                SELECT t.teacher_id, t.first_name || ' ' || t.last_name, u.email, t.dept_id, t.specialization
                FROM teachers t JOIN users u ON t.user_id = u.user_id
                ORDER BY t.teacher_id
            '''

        self.tree["columns"] = [c[0] for c in columns]
        for col_id, heading, width in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor="w")

        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

        self.record_count_var.set(f"{len(rows)} record(s)")
        self.status_var.set(f"Loaded {len(rows)} {selection.lower()} record(s)")

    # -------------------------------------------------------------
    # Modify / delete handlers
    # -------------------------------------------------------------
    def get_selected_record(self):
        """Return (record_id, view_type) for the row selected in the table, or (None, None)."""
        selection = self.tree.selection()
        if not selection:
            return None, None
        values = self.tree.item(selection[0], "values")
        return values[0], getattr(self, "current_view_type", self.view_selector.get())

    def modify_record(self):
        """Open an edit dialog pre-filled with the selected record's data."""
        record_id, view_type = self.get_selected_record()
        if not record_id:
            messagebox.showwarning("No Selection", "Please select a record in the table first.")
            return

        if view_type == "Students":
            self.cursor.execute('''
                SELECT s.student_id, s.first_name, s.last_name, u.email, s.dept_id, s.user_id
                FROM students s JOIN users u ON s.user_id = u.user_id
                WHERE s.student_id = ?
            ''', (record_id,))
            row = self.cursor.fetchone()
            if not row:
                messagebox.showerror("Error", "That record no longer exists.")
                self.load_table_data()
                return
            self.open_student_edit_dialog(row)
        else:
            self.cursor.execute('''
                SELECT t.teacher_id, t.first_name, t.last_name, u.email, t.dept_id, t.specialization, t.user_id
                FROM teachers t JOIN users u ON t.user_id = u.user_id
                WHERE t.teacher_id = ?
            ''', (record_id,))
            row = self.cursor.fetchone()
            if not row:
                messagebox.showerror("Error", "That record no longer exists.")
                self.load_table_data()
                return
            self.open_teacher_edit_dialog(row)

    def delete_record(self):
        """Delete the selected record and its linked user row, after confirmation."""
        record_id, view_type = self.get_selected_record()
        if not record_id:
            messagebox.showwarning("No Selection", "Please select a record in the table first.")
            return

        if not messagebox.askyesno("Confirm Delete",
                                    f"Delete record {record_id}? This cannot be undone."):
            return

        try:
            if view_type == "Students":
                self.cursor.execute("SELECT user_id FROM students WHERE student_id = ?", (record_id,))
                row = self.cursor.fetchone()
                if row:
                    self.cursor.execute("DELETE FROM students WHERE student_id = ?", (record_id,))
                    self.cursor.execute("DELETE FROM users WHERE user_id = ?", (row[0],))
            else:
                self.cursor.execute("SELECT user_id FROM teachers WHERE teacher_id = ?", (record_id,))
                row = self.cursor.fetchone()
                if row:
                    self.cursor.execute("DELETE FROM teachers WHERE teacher_id = ?", (record_id,))
                    self.cursor.execute("DELETE FROM users WHERE user_id = ?", (row[0],))
            self.conn.commit()
            self.status_var.set(f"Deleted record {record_id}")
            self.load_table_data()
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Could not delete record:\n{e}")

    def open_student_edit_dialog(self, row):
        """Small popup form for editing an existing student."""
        student_id, fname, lname, email, dept_id, user_id = row

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Student - {student_id}")
        dialog.configure(bg="#ffffff")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        form = tk.Frame(dialog, bg="#ffffff", padx=20, pady=20)
        form.pack()

        tk.Label(form, text=f"Editing {student_id}", font=FONT_TITLE, bg="#ffffff",
                 fg=TEXT_COLOR).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        e_fname = self._add_field(form, "First Name:", 1)
        e_fname.insert(0, fname)
        e_lname = self._add_field(form, "Last Name:", 2)
        e_lname.insert(0, lname)
        e_email = self._add_field(form, "Email Address:", 3)
        e_email.insert(0, email)

        tk.Label(form, text="Department:", bg="#ffffff", font=FONT_LABEL,
                 anchor="w").grid(row=4, column=0, sticky="w", pady=8, padx=(0, 12))
        depts = self.get_departments()
        e_dept = ttk.Combobox(form, values=depts, width=24, state="readonly")
        e_dept.grid(row=4, column=1, pady=8, sticky="w")
        if dept_id in depts:
            e_dept.current(depts.index(dept_id))
        elif depts:
            e_dept.current(0)

        btn_frame = tk.Frame(dialog, bg="#ffffff", pady=16)
        btn_frame.pack()

        def on_save():
            new_fname = e_fname.get().strip()
            new_lname = e_lname.get().strip()
            new_email = e_email.get().strip()
            new_dept = e_dept.get().strip()

            if not new_fname or not new_lname or not new_email:
                messagebox.showerror("Error", "All fields must be filled out!", parent=dialog)
                return
            if not EMAIL_PATTERN.match(new_email):
                messagebox.showerror("Error", "Please enter a valid email address.", parent=dialog)
                return

            try:
                self.cursor.execute("UPDATE users SET email = ? WHERE user_id = ?",
                                     (new_email, user_id))
                self.cursor.execute('''
                    UPDATE students SET first_name = ?, last_name = ?, dept_id = ?
                    WHERE student_id = ?
                ''', (new_fname, new_lname, new_dept, student_id))
                self.conn.commit()
                self.status_var.set(f"Updated student {student_id}")
                dialog.destroy()
                self.load_table_data()
            except sqlite3.IntegrityError:
                self.conn.rollback()
                messagebox.showerror("Database Error",
                                      "Email address already exists in the system!", parent=dialog)

        tk.Button(btn_frame, text="Save Changes", bg=ACCENT_GREEN, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=6,
                  cursor="hand2", command=on_save).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Cancel", bg="#e5e7eb", fg=TEXT_COLOR,
                  font=("Segoe UI", 10), relief="flat", padx=16, pady=6,
                  cursor="hand2", command=dialog.destroy).pack(side="left", padx=6)

    def open_teacher_edit_dialog(self, row):
        """Small popup form for editing an existing teacher."""
        teacher_id, fname, lname, email, dept_id, spec, user_id = row

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Teacher - {teacher_id}")
        dialog.configure(bg="#ffffff")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        form = tk.Frame(dialog, bg="#ffffff", padx=20, pady=20)
        form.pack()

        tk.Label(form, text=f"Editing {teacher_id}", font=FONT_TITLE, bg="#ffffff",
                 fg=TEXT_COLOR).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        e_fname = self._add_field(form, "First Name:", 1)
        e_fname.insert(0, fname)
        e_lname = self._add_field(form, "Last Name:", 2)
        e_lname.insert(0, lname)
        e_email = self._add_field(form, "Email Address:", 3)
        e_email.insert(0, email)

        tk.Label(form, text="Department:", bg="#ffffff", font=FONT_LABEL,
                 anchor="w").grid(row=4, column=0, sticky="w", pady=8, padx=(0, 12))
        depts = self.get_departments()
        e_dept = ttk.Combobox(form, values=depts, width=24, state="readonly")
        e_dept.grid(row=4, column=1, pady=8, sticky="w")
        if dept_id in depts:
            e_dept.current(depts.index(dept_id))
        elif depts:
            e_dept.current(0)

        e_spec = self._add_field(form, "Specialization:", 5)
        e_spec.insert(0, spec)

        btn_frame = tk.Frame(dialog, bg="#ffffff", pady=16)
        btn_frame.pack()

        def on_save():
            new_fname = e_fname.get().strip()
            new_lname = e_lname.get().strip()
            new_email = e_email.get().strip()
            new_dept = e_dept.get().strip()
            new_spec = e_spec.get().strip()

            if not new_fname or not new_lname or not new_email or not new_spec:
                messagebox.showerror("Error", "All fields must be filled out!", parent=dialog)
                return
            if not EMAIL_PATTERN.match(new_email):
                messagebox.showerror("Error", "Please enter a valid email address.", parent=dialog)
                return

            try:
                self.cursor.execute("UPDATE users SET email = ? WHERE user_id = ?",
                                     (new_email, user_id))
                self.cursor.execute('''
                    UPDATE teachers SET first_name = ?, last_name = ?, dept_id = ?, specialization = ?
                    WHERE teacher_id = ?
                ''', (new_fname, new_lname, new_dept, new_spec, teacher_id))
                self.conn.commit()
                self.status_var.set(f"Updated teacher {teacher_id}")
                dialog.destroy()
                self.load_table_data()
            except sqlite3.IntegrityError:
                self.conn.rollback()
                messagebox.showerror("Database Error",
                                      "Email address already exists in the system!", parent=dialog)

        tk.Button(btn_frame, text="Save Changes", bg=ACCENT_GREEN, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=6,
                  cursor="hand2", command=on_save).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Cancel", bg="#e5e7eb", fg=TEXT_COLOR,
                  font=("Segoe UI", 10), relief="flat", padx=16, pady=6,
                  cursor="hand2", command=dialog.destroy).pack(side="left", padx=6)

    # -------------------------------------------------------------
    # Save handlers
    # -------------------------------------------------------------
    def save_student(self):
        """Handle student submission logic."""
        fname = self.s_fname.get().strip()
        lname = self.s_lname.get().strip()
        email = self.s_email.get().strip()
        dept = self.s_dept.get().strip()

        if not fname or not lname or not email:
            messagebox.showerror("Error", "All fields must be filled out!")
            return

        if not EMAIL_PATTERN.match(email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return

        year = datetime.now().year
        self.cursor.execute(
            "SELECT COUNT(*) FROM students WHERE dept_id = ? AND enrollment_year = ?",
            (dept, year),
        )
        count = self.cursor.fetchone()[0] + 1
        student_id = f"STU-{year}-{dept}-{count:03d}"
        user_id = f"USR-{student_id}"

        try:
            self.cursor.execute(
                "INSERT INTO users (user_id, email, role) VALUES (?, ?, ?)",
                (user_id, email, 'student'),
            )
            self.cursor.execute('''
                INSERT INTO students (student_id, user_id, first_name, last_name, dept_id, enrollment_year)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, user_id, fname, lname, dept, year))
            self.conn.commit()

            messagebox.showinfo("Success", f"Student registered successfully!\nAssigned ID: {student_id}")
            self._clear_fields(self.s_fname, self.s_lname, self.s_email)
            self.status_var.set(f"Registered student {student_id}")
            self.load_table_data()
        except sqlite3.IntegrityError:
            self.conn.rollback()
            messagebox.showerror("Database Error", "Email address already exists in the system!")

    def save_teacher(self):
        """Handle teacher submission logic."""
        fname = self.t_fname.get().strip()
        lname = self.t_lname.get().strip()
        email = self.t_email.get().strip()
        dept = self.t_dept.get().strip()
        spec = self.t_spec.get().strip()

        if not fname or not lname or not email or not spec:
            messagebox.showerror("Error", "All fields must be filled out!")
            return

        if not EMAIL_PATTERN.match(email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return

        self.cursor.execute("SELECT COUNT(*) FROM teachers WHERE dept_id = ?", (dept,))
        count = self.cursor.fetchone()[0] + 1
        teacher_id = f"TCH-{dept}-{count:03d}"
        user_id = f"USR-{teacher_id}"

        try:
            self.cursor.execute(
                "INSERT INTO users (user_id, email, role) VALUES (?, ?, ?)",
                (user_id, email, 'teacher'),
            )
            self.cursor.execute('''
                INSERT INTO teachers (teacher_id, user_id, first_name, last_name, dept_id, specialization)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (teacher_id, user_id, fname, lname, dept, spec))
            self.conn.commit()

            messagebox.showinfo("Success", f"Teacher registered successfully!\nAssigned ID: {teacher_id}")
            self._clear_fields(self.t_fname, self.t_lname, self.t_email, self.t_spec)
            self.status_var.set(f"Registered teacher {teacher_id}")
            self.load_table_data()
        except sqlite3.IntegrityError:
            self.conn.rollback()
            messagebox.showerror("Database Error", "Email address already exists in the system!")

    # -------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------
    def on_close(self):
        if hasattr(self, 'conn'):
            self.conn.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = UniversityManagementGUI(root)
    root.mainloop()
