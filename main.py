import tkinter as tk
from tkinter import ttk, messagebox

students = []

# Academic decision functions


def calculate_average(mark1, mark2, mark3):
    return (mark1 + mark2 + mark3) / 3


def calculate_grade(average):
    if average >= 70:
        return "A"
    elif average >= 60:
        return "B"
    elif average >= 50:
        return "C"
    elif average >= 40:
        return "D"
    else:
        return "F"


def calculate_status(average):
    if average >= 70:
        return "Excellent"
    elif average >= 60:
        return "Very Good"
    elif average >= 50:
        return "Good"
    elif average >= 40:
        return "Pass"
    else:
        return "Fail"


# Clear input fields


def clear_fields():
    name_entry.delete(0, tk.END)
    id_entry.delete(0, tk.END)
    course_entry.delete(0, tk.END)
    mark1_entry.delete(0, tk.END)
    mark2_entry.delete(0, tk.END)
    mark3_entry.delete(0, tk.END)

    name_entry.focus()


# Add student


def add_student():
    name = name_entry.get()
    student_id = id_entry.get()
    course = course_entry.get()

    if name == "" or student_id == "" or course == "":
        messagebox.showwarning("Missing Information",
                               "Please enter name, student ID and course.")
        return

    try:
        mark1 = float(mark1_entry.get())
        mark2 = float(mark2_entry.get())
        mark3 = float(mark3_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Marks",
                             "Please enter numbers for all marks.")
        return

    if (mark1 < 0 or mark1 > 100 or
            mark2 < 0 or mark2 > 100 or
            mark3 < 0 or mark3 > 100):
        messagebox.showerror("Invalid Marks",
                             "Marks must be between 0 and 100.")
        return

    # Check for duplicate ID
    for student in students:
        if student["id"] == student_id:
            messagebox.showwarning("Duplicate ID",
                                   "Student ID already exists.")
            return

    average = calculate_average(mark1, mark2, mark3)
    grade = calculate_grade(average)
    status = calculate_status(average)

    student = {
        "name": name,
        "id": student_id,
        "course": course,
        "mark1": mark1,
        "mark2": mark2,
        "mark3": mark3,
        "average": average,
        "grade": grade,
        "status": status
    }

    students.append(student)

    display_students()
    clear_fields()

    messagebox.showinfo("Success", "Student added successfully.")


# Display students


def display_students(student_list=None):
    # Remove old rows
    for item in student_table.get_children():
        student_table.delete(item)

    if student_list is None:
        student_list = students

    for student in student_list:
        student_table.insert(
            "",
            tk.END,
            values=(
                student["name"],
                student["id"],
                student["course"],
                student["mark1"],
                student["mark2"],
                student["mark3"],
                round(student["average"], 2),
                student["grade"],
                student["status"]
            )
        )


# Search student


def search_student():
    search_text = search_entry.get().lower()

    if search_text == "":
        display_students()
        return

    found_students = []

    for student in students:
        if (search_text in student["name"].lower() or
                search_text in student["id"].lower()):
            found_students.append(student)

    display_students(found_students)


# Show selected student's status


def show_status():
    selected = student_table.selection()

    if not selected:
        messagebox.showwarning("No Selection",
                               "Please select a student first.")
        return

    item = student_table.item(selected[0])
    student_id = item["values"][1]

    for student in students:
        if student["id"] == student_id:
            messagebox.showinfo(
                "Academic Status",
                "Student: " + student["name"] +
                "\nAverage: " + str(round(student["average"], 2)) +
                "\nGrade: " + student["grade"] +
                "\nStatus: " + student["status"]
            )
            return


# Remove student


def remove_student():
    selected = student_table.selection()

    if not selected:
        messagebox.showwarning("No Selection",
                               "Please select a student to remove.")
        return

    item = student_table.item(selected[0])
    student_id = item["values"][1]

    answer = messagebox.askyesno(
        "Confirm Removal",
        "Are you sure you want to remove this student?"
    )

    if answer:
        for student in students:
            if student["id"] == student_id:
                students.remove(student)
                break

        display_students()
        messagebox.showinfo("Success", "Student removed successfully.")


# Exit application


def exit_program():
    answer = messagebox.askyesno(
        "Exit",
        "Are you sure you want to exit?"
    )

    if answer:
        window.destroy()


# Create main window

window = tk.Tk()
window.title("Smart Student Management and Academic Decision System")
window.geometry("1150x650")
window.resizable(True, True)


# Title


title_label = tk.Label(
    window,
    text="SMART STUDENT MANAGEMENT AND ACADEMIC DECISION SYSTEM",
    font=("Arial", 18, "bold")
)
title_label.pack(pady=15)


# Student information frame

input_frame = tk.LabelFrame(
    window,
    text="Student Information",
    font=("Arial", 11, "bold"),
    padx=10,
    pady=10
)
input_frame.pack(fill="x", padx=15, pady=5)


# Student name
tk.Label(input_frame, text="Student Name:").grid(
    row=0, column=0, padx=5, pady=5, sticky="w"
)

name_entry = tk.Entry(input_frame, width=25)
name_entry.grid(row=0, column=1, padx=5, pady=5)


# Student ID
tk.Label(input_frame, text="Student ID:").grid(
    row=0, column=2, padx=5, pady=5, sticky="w"
)

id_entry = tk.Entry(input_frame, width=20)
id_entry.grid(row=0, column=3, padx=5, pady=5)


# Course
tk.Label(input_frame, text="Course:").grid(
    row=0, column=4, padx=5, pady=5, sticky="w"
)

course_entry = tk.Entry(input_frame, width=25)
course_entry.grid(row=0, column=5, padx=5, pady=5)


# Marks
tk.Label(input_frame, text="Course 1 Mark:").grid(
    row=1, column=0, padx=5, pady=5, sticky="w"
)

mark1_entry = tk.Entry(input_frame, width=10)
mark1_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")


tk.Label(input_frame, text="Course 2 Mark:").grid(
    row=1, column=2, padx=5, pady=5, sticky="w"
)

mark2_entry = tk.Entry(input_frame, width=10)
mark2_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")


tk.Label(input_frame, text="Course 3 Mark:").grid(
    row=1, column=4, padx=5, pady=5, sticky="w"
)

mark3_entry = tk.Entry(input_frame, width=10)
mark3_entry.grid(row=1, column=5, padx=5, pady=5, sticky="w")


# Buttons

button_frame = tk.Frame(window)
button_frame.pack(pady=10)

tk.Button(
    button_frame,
    text="Add Student",
    width=15,
    command=add_student
).grid(row=0, column=0, padx=5)

tk.Button(
    button_frame,
    text="Clear",
    width=15,
    command=clear_fields
).grid(row=0, column=1, padx=5)

tk.Button(
    button_frame,
    text="Show Status",
    width=15,
    command=show_status
).grid(row=0, column=2, padx=5)

tk.Button(
    button_frame,
    text="Remove Student",
    width=15,
    command=remove_student
).grid(row=0, column=3, padx=5)

tk.Button(
    button_frame,
    text="Exit",
    width=15,
    command=exit_program
).grid(row=0, column=4, padx=5)


# Search area

search_frame = tk.Frame(window)
search_frame.pack(fill="x", padx=15, pady=5)

tk.Label(
    search_frame,
    text="Search Student:"
).pack(side="left", padx=5)

search_entry = tk.Entry(search_frame, width=30)
search_entry.pack(side="left", padx=5)

tk.Button(
    search_frame,
    text="Search",
    command=search_student
).pack(side="left", padx=5)

tk.Button(
    search_frame,
    text="Show All",
    command=display_students
).pack(side="left", padx=5)


# Student table

table_frame = tk.Frame(window)
table_frame.pack(fill="both", expand=True, padx=15, pady=10)

columns = (
    "Name",
    "ID",
    "Course",
    "Mark 1",
    "Mark 2",
    "Mark 3",
    "Average",
    "Grade",
    "Status"
)

student_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

for column in columns:
    student_table.heading(column, text=column)
    student_table.column(column, width=100)

student_table.column("Name", width=150)
student_table.column("Course", width=150)
student_table.column("Status", width=100)

student_table.pack(
    side="left",
    fill="both",
    expand=True
)


# Scrollbar
scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=student_table.yview
)

student_table.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(
    side="right",
    fill="y"
)


# Start application
name_entry.focus()
window.mainloop()
