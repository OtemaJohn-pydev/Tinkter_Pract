import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib

# SMART STUDENT MANAGEMENT SYSTEM 

DATABASE = "smart_student_management.db"


# DATABASE

def connect_db():
    return sqlite3.connect(DATABASE)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def setup_database():
    conn = connect_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Programs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    # Course units table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            program_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY(program_id) REFERENCES programs(id)
        )
    """)

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age TEXT,
            program_id INTEGER NOT NULL,
            username TEXT UNIQUE NOT NULL,
            FOREIGN KEY(program_id) REFERENCES programs(id)
        )
    """)

    # Lecturers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lecturers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lecturer_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL
        )
    """)

    # Lecturer assignments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lecturer_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lecturer_id INTEGER NOT NULL,
            program_id INTEGER NOT NULL,
            course_unit_id INTEGER NOT NULL
        )
    """)

    # Marks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_unit_id INTEGER NOT NULL,
            quiz REAL DEFAULT 0,
            assignment REAL DEFAULT 0,
            exam REAL DEFAULT 0
        )
    """)

    # DEFAULT DEAN

    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        ("dean",)
    )

    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO users(username, password, role)
            VALUES (?, ?, ?)
        """, (
            "dean",
            hash_password("dean123"),
            "Dean"
        ))

    # PROGRAMS 

    programs = {
        "Computer Science": [
            "AI/ML",
            "Cyber Security",
            "Unix Shell Programming",
            "Data Science"
        ],

        "Information Technology": [
            "System and Networks Administration",
            "Computer Graphics",
            "Embedded Systems",
            "UI/UX"
        ],

        "Software Engineering": [
            "Data Engineering",
            "Database Administration",
            "AI/ML",
            "Software Project Management"
        ]
    }

    for program_name, units in programs.items():

        cursor.execute(
            "INSERT OR IGNORE INTO programs(name) VALUES (?)",
            (program_name,)
        )

        cursor.execute(
            "SELECT id FROM programs WHERE name = ?",
            (program_name,)
        )

        program_id = cursor.fetchone()[0]

        for unit in units:

            cursor.execute("""
                SELECT * FROM course_units
                WHERE program_id = ? AND name = ?
            """, (program_id, unit))

            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO course_units(program_id, name)
                    VALUES (?, ?)
                """, (program_id, unit))

    conn.commit()
    conn.close()


# MAIN APPLICATION

class StudentManagementApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Smart Student Management System"
        )

        self.root.geometry("1050x650")

        self.current_user = None
        self.current_role = None

        self.login_screen()

    # GENERAL FUNCTIONS

    def clear_screen(self):

        for widget in self.root.winfo_children():
            widget.destroy()

    def logout(self):

        self.current_user = None
        self.current_role = None

        self.login_screen()

    def title(self, text):

        tk.Label(
            self.root,
            text=text,
            font=("Arial", 22, "bold")
        ).pack(pady=20)

    # LOGIN

    def login_screen(self):

        self.clear_screen()

        frame = tk.Frame(self.root)

        frame.pack(expand=True)

        tk.Label(
            frame,
            text="SMART STUDENT MANAGEMENT SYSTEM",
            font=("Arial", 22, "bold")
        ).pack(pady=20)

        tk.Label(
            frame,
            text="Login",
            font=("Arial", 15)
        ).pack(pady=10)

        tk.Label(
            frame,
            text="Username"
        ).pack()

        username = tk.Entry(
            frame,
            width=35
        )

        username.pack(pady=5)

        tk.Label(
            frame,
            text="Password"
        ).pack()

        password = tk.Entry(
            frame,
            width=35,
            show="*"
        )

        password.pack(pady=5)

        def login():

            user = username.get().strip()
            pwd = password.get()

            if user == "" or pwd == "":

                messagebox.showwarning(
                    "Login",
                    "Please enter username and password."
                )

                return

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, role
                FROM users
                WHERE username = ?
                AND password = ?
            """, (
                user,
                hash_password(pwd)
            ))

            result = cursor.fetchone()

            conn.close()

            if result:

                self.current_user = result[0]
                self.current_role = result[1]

                if self.current_role == "Dean":
                    self.dean_dashboard()

                elif self.current_role == "Lecturer":
                    self.lecturer_dashboard()

                elif self.current_role == "Student":
                    self.student_dashboard()

            else:

                messagebox.showerror(
                    "Login Failed",
                    "Incorrect username or password."
                )

        tk.Button(
            frame,
            text="LOGIN",
            width=25,
            height=2,
            command=login
        ).pack(pady=20)

        tk.Label(
            frame,
            text="""
            Users are adviced to use here correct usernames and passwords
            """,
            fg="gray"
        ).pack()

    # DEAN DASHBOARD

    def dean_dashboard(self):

        self.clear_screen()

        self.title("DEAN DASHBOARD")

        tk.Label(
            self.root,
            text="Administrator",
            font=("Arial", 12)
        ).pack()

        frame = tk.Frame(self.root)
        frame.pack(pady=30)

        buttons = [
            ("Manage Students", self.manage_students),
            ("Manage Lecturers", self.manage_lecturers),
            ("Programs & Course Units", self.programs_page),
            ("Assign Lecturers", self.assign_lecturers),
            ("View Students", self.view_students),
            ("Academic Reports", self.academic_reports),
            ("Logout", self.logout)
        ]

        for i, (text, command) in enumerate(buttons):

            row = i // 2
            column = i % 2

            tk.Button(
                frame,
                text=text,
                width=25,
                height=2,
                command=command
            ).grid(
                row=row,
                column=column,
                padx=10,
                pady=10
            )

    # PROGRAMS

    def programs_page(self):

        self.clear_screen()

        self.title("PROGRAMS AND COURSE UNITS")

        form = tk.Frame(self.root)
        form.pack(pady=10)

        # Program
        tk.Label(
            form,
            text="Program Name"
        ).grid(row=0, column=0, padx=5, pady=5)

        program_entry = tk.Entry(
            form,
            width=30
        )

        program_entry.grid(
            row=0,
            column=1
        )

        def add_program():

            name = program_entry.get().strip()

            if name == "":
                messagebox.showwarning(
                    "Program",
                    "Enter program name."
                )
                return

            conn = connect_db()

            try:

                conn.execute(
                    "INSERT INTO programs(name) VALUES (?)",
                    (name,)
                )

                conn.commit()

                messagebox.showinfo(
                    "Success",
                    "Program added."
                )

                program_entry.delete(
                    0,
                    tk.END
                )

                load_data()

            except sqlite3.IntegrityError:

                messagebox.showerror(
                    "Error",
                    "Program already exists."
                )

            conn.close()

        tk.Button(
            form,
            text="Add Program",
            command=add_program
        ).grid(
            row=0,
            column=2,
            padx=10
        )

        # Course unit
        tk.Label(
            form,
            text="Select Program"
        ).grid(
            row=1,
            column=0,
            padx=5,
            pady=5
        )

        program_combo = ttk.Combobox(
            form,
            width=28,
            state="readonly"
        )

        program_combo.grid(
            row=1,
            column=1
        )

        tk.Label(
            form,
            text="Course Unit"
        ).grid(
            row=2,
            column=0,
            padx=5,
            pady=5
        )

        unit_entry = tk.Entry(
            form,
            width=30
        )

        unit_entry.grid(
            row=2,
            column=1
        )

        def add_course_unit():

            program = program_combo.get()
            unit = unit_entry.get().strip()

            if program == "" or unit == "":

                messagebox.showwarning(
                    "Course Unit",
                    "Select a program and enter course unit."
                )

                return

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM programs WHERE name = ?",
                (program,)
            )

            program_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO course_units(program_id, name)
                VALUES (?, ?)
            """, (
                program_id,
                unit
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                "Course unit added."
            )

            unit_entry.delete(
                0,
                tk.END
            )

            load_data()

        tk.Button(
            form,
            text="Add Course Unit",
            command=add_course_unit
        ).grid(
            row=2,
            column=2,
            padx=10
        )

        # Treeview
        tree = ttk.Treeview(
            self.root,
            columns=("Program", "Course Unit"),
            show="headings"
        )

        tree.heading(
            "Program",
            text="Program"
        )

        tree.heading(
            "Course Unit",
            text="Course Unit"
        )

        tree.column(
            "Program",
            width=400
        )

        tree.column(
            "Course Unit",
            width=400
        )

        tree.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        def load_data():

            for item in tree.get_children():
                tree.delete(item)

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT programs.name,
                       course_units.name
                FROM programs
                JOIN course_units
                ON programs.id = course_units.program_id
                ORDER BY programs.name
            """)

            for row in cursor.fetchall():

                tree.insert(
                    "",
                    tk.END,
                    values=row
                )

            cursor.execute(
                "SELECT name FROM programs ORDER BY name"
            )

            programs = [
                row[0]
                for row in cursor.fetchall()
            ]

            program_combo["values"] = programs

            conn.close()

        load_data()

        tk.Button(
            self.root,
            text="Back to Dean Dashboard",
            command=self.dean_dashboard
        ).pack(pady=10)

    # MANAGE STUDENTS

    def manage_students(self):

        self.clear_screen()

        self.title("MANAGE STUDENTS")

        form = tk.Frame(self.root)
        form.pack(pady=10)

        fields = [
            "Student ID",
            "Student Name",
            "Age",
            "Username",
            "Password"
        ]

        entries = {}

        for i, field in enumerate(fields):

            tk.Label(
                form,
                text=field
            ).grid(
                row=i,
                column=0,
                padx=5,
                pady=5,
                sticky="w"
            )

            entry = tk.Entry(
                form,
                width=30
            )

            entry.grid(
                row=i,
                column=1,
                padx=10
            )

            entries[field] = entry

        tk.Label(
            form,
            text="Program"
        ).grid(
            row=5,
            column=0,
            sticky="w"
        )

        program_combo = ttk.Combobox(
            form,
            values=self.get_programs(),
            width=28,
            state="readonly"
        )

        program_combo.grid(
            row=5,
            column=1,
            padx=10,
            pady=5
        )

        def add_student():

            student_id = entries["Student ID"].get().strip()
            name = entries["Student Name"].get().strip()
            age = entries["Age"].get().strip()
            username = entries["Username"].get().strip()
            password = entries["Password"].get()
            program = program_combo.get()

            if not all([
                student_id,
                name,
                username,
                password,
                program
            ]):

                messagebox.showwarning(
                    "Student",
                    "Please fill in all required fields."
                )

                return

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM programs WHERE name = ?",
                (program,)
            )

            program_id = cursor.fetchone()[0]

            try:

                cursor.execute("""
                    INSERT INTO users
                    (username, password, role)
                    VALUES (?, ?, 'Student')
                """, (
                    username,
                    hash_password(password)
                ))

                cursor.execute("""
                    INSERT INTO students
                    (student_id, name, age,
                     program_id, username)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    student_id,
                    name,
                    age,
                    program_id,
                    username
                ))

                conn.commit()

                messagebox.showinfo(
                    "Success",
                    "Student account created successfully."
                )

                for entry in entries.values():
                    entry.delete(0, tk.END)

                program_combo.set("")

                load_students()

            except sqlite3.IntegrityError:

                conn.rollback()

                messagebox.showerror(
                    "Error",
                    "Student ID or username already exists."
                )

            conn.close()

        tk.Button(
            form,
            text="Add Student",
            command=add_student
        ).grid(
            row=6,
            column=0,
            columnspan=2,
            pady=10
        )

        # Students table
        tree = ttk.Treeview(
            self.root,
            columns=(
                "ID",
                "Name",
                "Program",
                "Username"
            ),
            show="headings"
        )

        for column in (
            "ID",
            "Name",
            "Program",
            "Username"
        ):

            tree.heading(
                column,
                text=column
            )

            tree.column(
                column,
                width=200
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        def load_students():

            for item in tree.get_children():
                tree.delete(item)

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT students.student_id,
                       students.name,
                       programs.name,
                       students.username
                FROM students
                JOIN programs
                ON students.program_id = programs.id
            """)

            for row in cursor.fetchall():

                tree.insert(
                    "",
                    tk.END,
                    values=row
                )

            conn.close()

        def delete_student():

            selected = tree.selection()

            if not selected:

                messagebox.showwarning(
                    "Delete",
                    "Select a student first."
                )

                return

            values = tree.item(
                selected[0],
                "values"
            )

            student_id = values[0]
            username = values[3]

            answer = messagebox.askyesno(
                "Delete Student",
                "Are you sure you want to delete this student?"
            )

            if not answer:
                return

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM students WHERE student_id = ?",
                (student_id,)
            )

            cursor.execute(
                "DELETE FROM users WHERE username = ?",
                (username,)
            )

            conn.commit()
            conn.close()

            load_students()

        tk.Button(
            self.root,
            text="Delete Selected Student",
            command=delete_student
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Back",
            command=self.dean_dashboard
        ).pack(pady=5)

        load_students()

    # MANAGE LECTURERS

    def manage_lecturers(self):

        self.clear_screen()

        self.title("MANAGE LECTURERS")

        form = tk.Frame(self.root)
        form.pack(pady=15)

        fields = [
            "Lecturer ID",
            "Lecturer Name",
            "Username",
            "Password"
        ]

        entries = {}

        for i, field in enumerate(fields):

            tk.Label(
                form,
                text=field
            ).grid(
                row=i,
                column=0,
                padx=10,
                pady=5
            )

            entry = tk.Entry(
                form,
                width=30
            )

            entry.grid(
                row=i,
                column=1,
                padx=10,
                pady=5
            )

            entries[field] = entry

        def add_lecturer():

            lecturer_id = entries["Lecturer ID"].get().strip()
            name = entries["Lecturer Name"].get().strip()
            username = entries["Username"].get().strip()
            password = entries["Password"].get()

            if not all([
                lecturer_id,
                name,
                username,
                password
            ]):

                messagebox.showwarning(
                    "Lecturer",
                    "Please fill in all fields."
                )

                return

            conn = connect_db()
            cursor = conn.cursor()

            try:

                cursor.execute("""
                    INSERT INTO users
                    (username, password, role)
                    VALUES (?, ?, 'Lecturer')
                """, (
                    username,
                    hash_password(password)
                ))

                cursor.execute("""
                    INSERT INTO lecturers
                    (lecturer_id, name, username)
                    VALUES (?, ?, ?)
                """, (
                    lecturer_id,
                    name,
                    username
                ))

                conn.commit()

                messagebox.showinfo(
                    "Success",
                    "Lecturer account created."
                )

                for entry in entries.values():
                    entry.delete(0, tk.END)

                load_lecturers()

            except sqlite3.IntegrityError:

                conn.rollback()

                messagebox.showerror(
                    "Error",
                    "Lecturer ID or username already exists."
                )

            conn.close()

        tk.Button(
            form,
            text="Add Lecturer",
            command=add_lecturer
        ).grid(
            row=4,
            column=0,
            columnspan=2,
            pady=10
        )

        tree = ttk.Treeview(
            self.root,
            columns=(
                "Lecturer ID",
                "Name",
                "Username"
            ),
            show="headings"
        )

        for column in (
            "Lecturer ID",
            "Name",
            "Username"
        ):

            tree.heading(
                column,
                text=column
            )

            tree.column(
                column,
                width=280
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=15
        )

        def load_lecturers():

            for item in tree.get_children():
                tree.delete(item)

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT lecturer_id,
                       name,
                       username
                FROM lecturers
            """)

            for row in cursor.fetchall():

                tree.insert(
                    "",
                    tk.END,
                    values=row
                )

            conn.close()

        load_lecturers()

        tk.Button(
            self.root,
            text="Back",
            command=self.dean_dashboard
        ).pack(pady=10)

    # ASSIGN LECTURERS

    def assign_lecturers(self):

        self.clear_screen()

        self.title("ASSIGN LECTURERS")

        form = tk.Frame(self.root)
        form.pack(pady=15)

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, lecturer_id, name
            FROM lecturers
        """)

        lecturers = cursor.fetchall()

        cursor.execute("""
            SELECT id, name
            FROM programs
        """)

        programs = cursor.fetchall()

        conn.close()

        lecturer_combo = ttk.Combobox(
            form,
            width=40,
            state="readonly"
        )

        lecturer_combo["values"] = [
            f"{x[0]} - {x[1]} - {x[2]}"
            for x in lecturers
        ]

        lecturer_combo.grid(
            row=0,
            column=1,
            pady=5
        )

        tk.Label(
            form,
            text="Lecturer"
        ).grid(
            row=0,
            column=0,
            padx=10
        )

        program_combo = ttk.Combobox(
            form,
            width=40,
            state="readonly"
        )

        program_combo["values"] = [
            f"{x[0]} - {x[1]}"
            for x in programs
        ]

        program_combo.grid(
            row=1,
            column=1,
            pady=5
        )

        tk.Label(
            form,
            text="Program"
        ).grid(
            row=1,
            column=0
        )

        unit_combo = ttk.Combobox(
            form,
            width=40,
            state="readonly"
        )

        unit_combo.grid(
            row=2,
            column=1,
            pady=5
        )

        tk.Label(
            form,
            text="Course Unit"
        ).grid(
            row=2,
            column=0
        )

        def load_units(event):

            selected = program_combo.get()

            if selected == "":
                return

            program_id = selected.split(" - ")[0]

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name
                FROM course_units
                WHERE program_id = ?
            """, (program_id,))

            units = cursor.fetchall()

            unit_combo["values"] = [
                f"{x[0]} - {x[1]}"
                for x in units
            ]

            conn.close()

        program_combo.bind(
            "<<ComboboxSelected>>",
            load_units
        )

        def assign():

            lecturer = lecturer_combo.get()
            program = program_combo.get()
            unit = unit_combo.get()

            if not all([
                lecturer,
                program,
                unit
            ]):

                messagebox.showwarning(
                    "Assignment",
                    "Select all fields."
                )

                return

            lecturer_id = lecturer.split(" - ")[0]
            program_id = program.split(" - ")[0]
            unit_id = unit.split(" - ")[0]

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO lecturer_assignments
                (lecturer_id, program_id, course_unit_id)
                VALUES (?, ?, ?)
            """, (
                lecturer_id,
                program_id,
                unit_id
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                "Lecturer assigned."
            )

            load_assignments()

        tk.Button(
            form,
            text="Assign Lecturer",
            command=assign
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            pady=10
        )

        tree = ttk.Treeview(
            self.root,
            columns=(
                "Lecturer",
                "Program",
                "Course Unit"
            ),
            show="headings"
        )

        for column in (
            "Lecturer",
            "Program",
            "Course Unit"
        ):

            tree.heading(
                column,
                text=column
            )

            tree.column(
                column,
                width=300
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        def load_assignments():

            for item in tree.get_children():
                tree.delete(item)

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT lecturers.name,
                       programs.name,
                       course_units.name
                FROM lecturer_assignments

                JOIN lecturers
                ON lecturer_assignments.lecturer_id = lecturers.id

                JOIN programs
                ON lecturer_assignments.program_id = programs.id

                JOIN course_units
                ON lecturer_assignments.course_unit_id = course_units.id
            """)

            for row in cursor.fetchall():

                tree.insert(
                    "",
                    tk.END,
                    values=row
                )

            conn.close()

        load_assignments()

        tk.Button(
            self.root,
            text="Back",
            command=self.dean_dashboard
        ).pack(pady=10)

    # VIEW STUDENTS

    def view_students(self):

        self.clear_screen()

        self.title("ALL STUDENTS")

        tree = ttk.Treeview(
            self.root,
            columns=(
                "Student ID",
                "Name",
                "Program",
                "Username"
            ),
            show="headings"
        )

        for column in (
            "Student ID",
            "Name",
            "Program",
            "Username"
        ):

            tree.heading(
                column,
                text=column
            )

            tree.column(
                column,
                width=220
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT students.student_id,
                   students.name,
                   programs.name,
                   students.username

            FROM students

            JOIN programs
            ON students.program_id = programs.id
        """)

        for row in cursor.fetchall():

            tree.insert(
                "",
                tk.END,
                values=row
            )

        conn.close()

        tk.Button(
            self.root,
            text="Back",
            command=self.dean_dashboard
        ).pack(pady=10)

    # ACADEMIC REPORTS

    def academic_reports(self):

        self.clear_screen()

        self.title("ACADEMIC REPORTS")

        tk.Label(
            self.root,
            text="""
            Marks and overall academic reports will be expanded in Version 3.
            """,
            font=("Arial", 13)
        ).pack(pady=40)

        tk.Button(
            self.root,
            text="Back",
            command=self.dean_dashboard
        ).pack()

    # LECTURER DASHBOARD

    def lecturer_dashboard(self):

        self.clear_screen()

        self.title("LECTURER DASHBOARD")

        tk.Label(
            self.root,
            text="Welcome Lecturer",
            font=("Arial", 13)
        ).pack()

        frame = tk.Frame(self.root)
        frame.pack(pady=30)

        buttons = [
            (
                "My Course Units",
                self.lecturer_course_units
            ),
            (
                "Add Student",
                self.lecturer_add_student
            ),
            (
                "View Students",
                self.view_students_lecturer
            ),
            (
                "Enter Marks",
                self.enter_marks
            ),
            (
                "Update Marks",
                self.update_marks
            ),
            (
                "Student Performance",
                self.lecturer_performance
            ),
            (
                "Logout",
                self.logout
            )
        ]

        for i, (text, command) in enumerate(buttons):

            row = i // 2
            column = i % 2

            tk.Button(
                frame,
                text=text,
                width=25,
                height=2,
                command=command
            ).grid(
                row=row,
                column=column,
                padx=10,
                pady=10
            )

    # LECTURER COURSE UNITS

    def lecturer_course_units(self):

        self.clear_screen()

        self.title("MY ASSIGNED COURSE UNITS")

        tree = ttk.Treeview(
            self.root,
            columns=(
                "Program",
                "Course Unit"
            ),
            show="headings"
        )

        tree.heading(
            "Program",
            text="Program"
        )

        tree.heading(
            "Course Unit",
            text="Course Unit"
        )

        tree.column(
            "Program",
            width=400
        )

        tree.column(
            "Course Unit",
            width=400
        )

        tree.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT programs.name,
                   course_units.name

            FROM lecturer_assignments

            JOIN lecturers
            ON lecturer_assignments.lecturer_id =
               lecturers.id

            JOIN programs
            ON lecturer_assignments.program_id =
               programs.id

            JOIN course_units
            ON lecturer_assignments.course_unit_id =
               course_units.id

            WHERE lecturers.username = (
                SELECT username
                FROM users
                WHERE id = ?
            )
        """, (self.current_user,))

        for row in cursor.fetchall():

            tree.insert(
                "",
                tk.END,
                values=row
            )

        conn.close()

        tk.Button(
            self.root,
            text="Back",
            command=self.lecturer_dashboard
        ).pack(pady=10)

    # LECTURER ADD STUDENT

    def lecturer_add_student(self):

        self.clear_screen()

        self.title("ADD STUDENT")

        form = tk.Frame(self.root)
        form.pack(pady=20)

        fields = [
            "Student ID",
            "Student Name",
            "Age",
            "Username",
            "Password"
        ]

        entries = {}

        for i, field in enumerate(fields):

            tk.Label(
                form,
                text=field
            ).grid(
                row=i,
                column=0,
                pady=5
            )

            entry = tk.Entry(
                form,
                width=30
            )

            entry.grid(
                row=i,
                column=1,
                padx=10
            )

            entries[field] = entry

        tk.Label(
            form,
            text="Program"
        ).grid(
            row=5,
            column=0
        )

        program_combo = ttk.Combobox(
            form,
            values=self.get_programs(),
            width=28,
            state="readonly"
        )

        program_combo.grid(
            row=5,
            column=1,
            pady=5
        )

        def add():

            values = {
                key: entry.get().strip()
                for key, entry in entries.items()
            }

            program = program_combo.get()

            if not all(values.values()) or not program:

                messagebox.showwarning(
                    "Student",
                    "Fill in all fields."
                )

                return

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM programs WHERE name = ?",
                (program,)
            )

            program_id = cursor.fetchone()[0]

            try:

                cursor.execute("""
                    INSERT INTO users
                    (username, password, role)
                    VALUES (?, ?, 'Student')
                """, (
                    values["Username"],
                    hash_password(values["Password"])
                ))

                cursor.execute("""
                    INSERT INTO students
                    (student_id, name, age,
                     program_id, username)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    values["Student ID"],
                    values["Student Name"],
                    values["Age"],
                    program_id,
                    values["Username"]
                ))

                conn.commit()

                messagebox.showinfo(
                    "Success",
                    "Student account created."
                )

                self.lecturer_dashboard()

            except sqlite3.IntegrityError:

                conn.rollback()

                messagebox.showerror(
                    "Error",
                    "Student ID or username already exists."
                )

            conn.close()

        tk.Button(
            form,
            text="Create Student Account",
            command=add,
            width=25
        ).grid(
            row=6,
            column=0,
            columnspan=2,
            pady=15
        )

        tk.Button(
            self.root,
            text="Back",
            command=self.lecturer_dashboard
        ).pack()

    # LECTURER VIEW STUDENTS

    def view_students_lecturer(self):

        self.clear_screen()

        self.title("STUDENTS")

        tree = ttk.Treeview(
            self.root,
            columns=(
                "Student ID",
                "Name",
                "Program"
            ),
            show="headings"
        )

        for column in (
            "Student ID",
            "Name",
            "Program"
        ):

            tree.heading(
                column,
                text=column
            )

            tree.column(
                column,
                width=280
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT students.student_id,
                   students.name,
                   programs.name

            FROM students

            JOIN programs
            ON students.program_id = programs.id
        """)

        for row in cursor.fetchall():

            tree.insert(
                "",
                tk.END,
                values=row
            )

        conn.close()

        tk.Button(
            self.root,
            text="Back",
            command=self.lecturer_dashboard
        ).pack(pady=10)

    # ENTER MARKS

    def enter_marks(self):

        self.clear_screen()

        self.title("ENTER STUDENT MARKS")

        form = tk.Frame(self.root)
        form.pack(pady=20)

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, student_id, name
            FROM students
            ORDER BY name
        """)

        students = cursor.fetchall()

        cursor.execute("""
            SELECT id, name
            FROM course_units
            ORDER BY name
        """)

        units = cursor.fetchall()

        conn.close()

        tk.Label(
            form,
            text="Student"
        ).grid(row=0, column=0, pady=8)

        student_combo = ttk.Combobox(
            form,
            width=40,
            state="readonly"
        )

        student_combo["values"] = [
            f"{x[0]} - {x[1]} - {x[2]}"
            for x in students
        ]

        student_combo.grid(
            row=0,
            column=1
        )

        tk.Label(
            form,
            text="Course Unit"
        ).grid(row=1, column=0, pady=8)

        unit_combo = ttk.Combobox(
            form,
            width=40,
            state="readonly"
        )

        unit_combo["values"] = [
            f"{x[0]} - {x[1]}"
            for x in units
        ]

        unit_combo.grid(
            row=1,
            column=1
        )

        entries = {}

        for i, name in enumerate(
            ["Quiz", "Assignment", "Exam"],
            start=2
        ):

            tk.Label(
                form,
                text=name + " Mark"
            ).grid(
                row=i,
                column=0,
                pady=8
            )

            entry = tk.Entry(
                form,
                width=30
            )

            entry.grid(
                row=i,
                column=1
            )

            entries[name] = entry

        def save_marks():

            student = student_combo.get()
            unit = unit_combo.get()

            if not student or not unit:

                messagebox.showwarning(
                    "Marks",
                    "Select student and course unit."
                )

                return

            try:

                quiz = float(
                    entries["Quiz"].get()
                )

                assignment = float(
                    entries["Assignment"].get()
                )

                exam = float(
                    entries["Exam"].get()
                )

                if not (
                    0 <= quiz <= 30
                    and 0 <= assignment <= 20
                    and 0 <= exam <= 50
                ):

                    messagebox.showerror(
                        "Marks",
                        "Quiz must be 0-30, Assignment 0-20 and Exam 0-50."
                    )

                    return

            except ValueError:

                messagebox.showerror(
                    "Marks",
                    "Enter valid numbers."
                )

                return

            student_id = student.split(" - ")[0]
            unit_id = unit.split(" - ")[0]

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id
                FROM students
                WHERE id = ?
            """, (student_id,))

            actual_student = cursor.fetchone()[0]

            cursor.execute("""
                SELECT id
                FROM marks
                WHERE student_id = ?
                AND course_unit_id = ?
            """, (
                actual_student,
                unit_id
            ))

            existing = cursor.fetchone()

            if existing:

                cursor.execute("""
                    UPDATE marks
                    SET quiz = ?,
                        assignment = ?,
                        exam = ?
                    WHERE student_id = ?
                    AND course_unit_id = ?
                """, (
                    quiz,
                    assignment,
                    exam,
                    actual_student,
                    unit_id
                ))

            else:

                cursor.execute("""
                    INSERT INTO marks
                    (student_id, course_unit_id,
                     quiz, assignment, exam)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    actual_student,
                    unit_id,
                    quiz,
                    assignment,
                    exam
                ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                "Marks saved successfully."
            )

        tk.Button(
            form,
            text="SAVE MARKS",
            width=25,
            height=2,
            command=save_marks
        ).grid(
            row=5,
            column=0,
            columnspan=2,
            pady=20
        )

        tk.Button(
            self.root,
            text="Back",
            command=self.lecturer_dashboard
        ).pack()

    # UPDATE MARKS

    def update_marks(self):

        self.enter_marks()

    # LECTURER PERFORMANCE

    def lecturer_performance(self):

        self.clear_screen()

        self.title("STUDENT PERFORMANCE")

        tree = ttk.Treeview(
            self.root,
            columns=(
                "Student",
                "Course Unit",
                "Quiz",
                "Assignment",
                "Exam",
                "Final",
                "Grade"
            ),
            show="headings"
        )

        for column in (
            "Student",
            "Course Unit",
            "Quiz",
            "Assignment",
            "Exam",
            "Final",
            "Grade"
        ):

            tree.heading(
                column,
                text=column
            )

            tree.column(
                column,
                width=130
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=20
        )

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT students.name,
                   course_units.name,
                   marks.quiz,
                   marks.assignment,
                   marks.exam
            FROM marks

            JOIN students
            ON marks.student_id = students.id

            JOIN course_units
            ON marks.course_unit_id = course_units.id
        """)

        for row in cursor.fetchall():

            final = (
                row[2]
                + row[3]
                + row[4]
            )

            grade = self.get_grade(final)

            tree.insert(
                "",
                tk.END,
                values=(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    final,
                    grade
                )
            )

        conn.close()

        tk.Button(
            self.root,
            text="Back",
            command=self.lecturer_dashboard
        ).pack(pady=10)

    # STUDENT DASHBOARD

    def student_dashboard(self):

        self.clear_screen()

        self.title("STUDENT DASHBOARD")

        student = self.get_current_student()

        if student:

            tk.Label(
                self.root,
                text="Welcome, " + student[1],
                font=("Arial", 14)
            ).pack()

            tk.Label(
                self.root,
                text="Program: " + student[3]
            ).pack()

        frame = tk.Frame(self.root)
        frame.pack(pady=30)

        buttons = [
            (
                "My Profile",
                self.student_profile
            ),
            (
                "My Course Units",
                self.student_course_units
            ),
            (
                "My Marks",
                self.student_marks
            ),
            (
                "Academic Performance",
                self.student_performance
            ),
            (
                "Logout",
                self.logout
            )
        ]

        for i, (text, command) in enumerate(buttons):

            row = i // 2
            column = i % 2

            tk.Button(
                frame,
                text=text,
                width=25,
                height=2,
                command=command
            ).grid(
                row=row,
                column=column,
                padx=10,
                pady=10
            )

    # GET CURRENT STUDENT

    def get_current_student(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT students.student_id,
                   students.name,
                   students.age,
                   programs.name,
                   students.username

            FROM students

            JOIN programs
            ON students.program_id = programs.id

            JOIN users
            ON students.username = users.username

            WHERE users.id = ?
        """, (
            self.current_user,
        ))

        student = cursor.fetchone()

        conn.close()

        return student

    # STUDENT PROFILE

    def student_profile(self):

        self.clear_screen()

        self.title("MY PROFILE")

        student = self.get_current_student()

        if student:

            information = [
                ("Student ID", student[0]),
                ("Name", student[1]),
                ("Age", student[2]),
                ("Program", student[3]),
                ("Username", student[4])
            ]

            for label, value in information:

                tk.Label(
                    self.root,
                    text=f"{label}: {value}",
                    font=("Arial", 13)
                ).pack(
                    anchor="w",
                    padx=150,
                    pady=7
                )

        tk.Button(
            self.root,
            text="Back",
            command=self.student_dashboard
        ).pack(pady=20)

    # STUDENT COURSE UNITS

    def student_course_units(self):

        self.clear_screen()

        self.title("MY COURSE UNITS")

        student = self.get_current_student()

        tree = ttk.Treeview(
            self.root,
            columns=("Course Unit",),
            show="headings"
        )

        tree.heading(
            "Course Unit",
            text="Course Unit"
        )

        tree.column(
            "Course Unit",
            width=500
        )

        tree.pack(
            fill="both",
            expand=True,
            padx=100,
            pady=20
        )

        if student:

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT course_units.name

                FROM course_units

                JOIN programs
                ON course_units.program_id = programs.id

                WHERE programs.name = ?

                ORDER BY course_units.name
            """, (
                student[3],
            ))

            for row in cursor.fetchall():

                tree.insert(
                    "",
                    tk.END,
                    values=row
                )

            conn.close()

        tk.Button(
            self.root,
            text="Back",
            command=self.student_dashboard
        ).pack(pady=10)

    # STUDENT MARKS

    def student_marks(self):

        self.clear_screen()

        self.title("MY MARKS")

        student = self.get_current_student()

        tree = ttk.Treeview(
            self.root,
            columns=(
                "Course Unit",
                "Quiz",
                "Assignment",
                "Exam",
                "Final",
                "Grade"
            ),
            show="headings"
        )

        for column in (
            "Course Unit",
            "Quiz",
            "Assignment",
            "Exam",
            "Final",
            "Grade"
        ):

            tree.heading(
                column,
                text=column
            )

            tree.column(
                column,
                width=140
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        if student:

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT course_units.name,
                       marks.quiz,
                       marks.assignment,
                       marks.exam

                FROM marks

                JOIN course_units
                ON marks.course_unit_id = course_units.id

                JOIN students
                ON marks.student_id = students.id

                WHERE students.student_id = ?
            """, (
                student[0],
            ))

            for row in cursor.fetchall():

                final = (
                    row[1]
                    + row[2]
                    + row[3]
                )

                grade = self.get_grade(final)

                tree.insert(
                    "",
                    tk.END,
                    values=(
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        final,
                        grade
                    )
                )

            conn.close()

        tk.Button(
            self.root,
            text="Back",
            command=self.student_dashboard
        ).pack(pady=10)

    # STUDENT PERFORMANCE

    def student_performance(self):

        self.clear_screen()

        self.title("ACADEMIC PERFORMANCE")

        student = self.get_current_student()

        if not student:
            return

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT marks.quiz,
                   marks.assignment,
                   marks.exam

            FROM marks

            JOIN students
            ON marks.student_id = students.id

            WHERE students.student_id = ?
        """, (
            student[0],
        ))

        rows = cursor.fetchall()

        conn.close()

        if len(rows) == 0:

            tk.Label(
                self.root,
                text="No marks have been entered yet.",
                font=("Arial", 14)
            ).pack(pady=50)

        else:

            totals = []

            for row in rows:

                total = (
                    row[0]
                    + row[1]
                    + row[2]
                )

                totals.append(total)

            average = sum(totals) / len(totals)

            grade = self.get_grade(average)

            tk.Label(
                self.root,
                text=f"Overall Average: {average:.2f}%",
                font=("Arial", 18, "bold")
            ).pack(pady=15)

            tk.Label(
                self.root,
                text=f"Grade: {grade}",
                font=("Arial", 16)
            ).pack(pady=10)

            tk.Label(
                self.root,
                text=self.get_status(average),
                font=("Arial", 15)
            ).pack(pady=10)

        tk.Button(
            self.root,
            text="Back",
            command=self.student_dashboard
        ).pack(pady=20)

    # GRADING

    def get_grade(self, mark):

        if mark >= 70:
            return "A"

        elif mark >= 60:
            return "B"

        elif mark >= 50:
            return "C"

        elif mark >= 40:
            return "D"

        else:
            return "F"

    def get_status(self, mark):

        if mark >= 50:
            return "Status: PASS"

        else:
            return "Status: FAIL"

    # GET PROGRAMS

    def get_programs(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM programs ORDER BY name"
        )

        programs = [
            row[0]
            for row in cursor.fetchall()
        ]

        conn.close()

        return programs


# START APPLICATION

setup_database()

root = tk.Tk()

app = StudentManagementApp(root)

root.mainloop()