import sqlite3
from datetime import date
import streamlit as st

# Initialize Database
def init_db():
    conn = sqlite3.connect("academy_attendance.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            class_name TEXT NOT NULL,
            subjects TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT,
            class_name TEXT,
            subject TEXT,
            date TEXT,
            status TEXT,
            FOREIGN KEY (roll_no) REFERENCES students (roll_no)
        )
    """)
    conn.commit()
    conn.close()

# Page Configuration
st.set_page_config(
    page_title="AIMS Science Academy - Attendance System",
    page_icon="🎓",
    layout="wide"
)

# Initialize database on startup
init_db()

# Custom Styling & Header Design
st.markdown("""
    <style>
    .main {
        background-color: #MintCream;
    }
    .monogram-box {
        background-color: #LightSteelBlue;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #b0c4de;
    }
    </style>
""", unsafe_allow_html=True)

# App Title & Navigation Tabs
st.title("🎓 AIMS Science Academy - Attendance System")

tab1, tab2, tab3 = st.tabs(["👥 Manage Students", "📝 Mark Attendance", "📊 View Reports"])

# ==========================================
# TAB 1: MANAGE STUDENTS
# ==========================================
with tab1:
    col_form, col_logo = st.columns([2, 1])

    with col_form:
        st.subheader("Student Details Form")
        with st.form("student_form", clear_on_submit=True):
            name = st.text_input("Student Name")
            roll_no = st.text_input("Roll Number / ID")
            class_name = st.text_input("Class Name")
            subjects = st.text_input("Subjects (comma separated, e.g. Math, Physics, Chemistry)")
            
            submit_student = st.form_submit_button("Add Student")
            
            if submit_student:
                if not name.strip() or not roll_no.strip() or not class_name.strip() or not subjects.strip():
                    st.error("Please fill in all fields.")
                else:
                    try:
                        conn = sqlite3.connect("academy_attendance.db")
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO students (name, roll_no, class_name, subjects) VALUES (?, ?, ?, ?)",
                            (name.strip(), roll_no.strip(), class_name.strip(), subjects.strip())
                        )
                        conn.commit()
                        conn.close()
                        st.success(f"Student {name} added successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Roll number already exists.")

    with col_logo:
        st.markdown("""
            <div class="monogram-box">
                <h3 style="color: #1e3a8a; margin: 0; font-size: 24px;">AIMS</h3>
                <p style="color: #7f1d1d; margin: 0; font-size: 11px; font-weight: bold;">AIMS SCIENCE ACADEMY</p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Enrolled Students")
    
    # Fetch students for table and deletion options
    conn = sqlite3.connect("academy_attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, roll_no, class_name, subjects FROM students")
    students_data = cursor.fetchall()
    conn.close()

    if students_data:
        # Display as a clean table
        table_data = [{"ID": r[0], "Name": r[1], "Roll No": r[2], "Class": r[3], "Subjects": r[4]} for r in students_data]
        st.dataframe(table_data, use_container_width=True)

        # Management buttons
        col_del1, col_del2 = st.columns(2)
        with col_del1:
            roll_to_delete = st.selectbox("Select Roll No to Delete", options=[r[2] for r in students_data], key="delete_select")
            if st.button("Delete Selected Student"):
                conn = sqlite3.connect("academy_attendance.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM attendance WHERE roll_no = ?", (roll_to_delete,))
                cursor.execute("DELETE FROM students WHERE roll_no = ?", (roll_to_delete,))
                conn.commit()
                conn.close()
                st.success(f"Student with Roll No {roll_to_delete} deleted successfully.")
                st.rerun()

        with col_del2:
            st.write("")
            st.write("")
            if st.button("Clear All Students & Reset Database", type="primary"):
                conn = sqlite3.connect("academy_attendance.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM attendance")
                cursor.execute("DELETE FROM students")
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='students'")
                conn.commit()
                conn.close()
                st.success("All student records cleared successfully.")
                st.rerun()
    else:
        st.info("No students enrolled yet.")

# ==========================================
# TAB 2: MARK ATTENDANCE
# ==========================================
with tab2:
    st.subheader("Mark Daily Attendance")
    today_str = str(date.today())
    st.info(f"Current Date: **{today_str}**")

    conn = sqlite3.connect("academy_attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT class_name FROM students")
    classes = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()

    if not classes:
        st.warning("No classes found. Please add students first in the 'Manage Students' tab.")
    else:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            selected_class = st.selectbox("Select Class", options=classes)

        # Get subjects for selected class
        conn = sqlite3.connect("academy_attendance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT subjects FROM students WHERE class_name = ?", (selected_class,))
        rows = cursor.fetchall()
        conn.close()

        all_subjects = set()
        for row in rows:
            for sub in row[0].split(","):
                clean_sub = sub.strip()
                if clean_sub:
                    all_subjects.add(clean_sub)

        subject_list = sorted(list(all_subjects))

        with col_c2:
            if subject_list:
                selected_subject = st.selectbox("Select Subject", options=subject_list)
            else:
                selected_subject = None
                st.warning("No subjects found for this class.")

        if selected_class and selected_subject:
            conn = sqlite3.connect("academy_attendance.db")
            cursor = conn.cursor()
            cursor.execute("SELECT roll_no, name, subjects FROM students WHERE class_name = ?", (selected_class,))
            students = cursor.fetchall()

            enrolled_students = []
            for roll_no, name, subjects in students:
                if selected_subject in [s.strip() for s in subjects.split(",")]:
                    enrolled_students.append((roll_no, name))

            if not enrolled_students:
                st.info(f"No students in class '{selected_class}' enrolled in '{selected_subject}'.")
            else:
                st.write(f"Marking attendance for **{selected_class}** - **{selected_subject}**")
                
                attendance_status = {}
                
                with st.form("attendance_form"):
                    for roll_no, name in enrolled_students:
                        # Fetch existing attendance status if saved previously today
                        cursor.execute(
                            "SELECT status FROM attendance WHERE roll_no = ? AND class_name = ? AND subject = ? AND date = ?",
                            (roll_no, selected_class, selected_subject, today_str)
                        )
                        res = cursor.fetchone()
                        default_val = res[0] if res else "Present"
                        
                        col_name, col_radio = st.columns([2, 2])
                        with col_name:
                            st.write(f"**{name}** `({roll_no})`")
                        with col_radio:
                            status = st.radio(
                                f"Status for {roll_no}",
                                options=["Present", "Absent"],
                                index=0 if default_val == "Present" else 1,
                                horizontal=True,
                                key=f"att_{roll_no}",
                                label_visibility="collapsed"
                            )
                            attendance_status[roll_no] = status

                    submit_attendance = st.form_submit_button("Save Attendance")
                    if submit_attendance:
                        for roll_no, status in attendance_status.items():
                            cursor.execute(
                                "SELECT * FROM attendance WHERE roll_no = ? AND class_name = ? AND subject = ? AND date = ?",
                                (roll_no, selected_class, selected_subject, today_str)
                            )
                            existing = cursor.fetchone()

                            if existing:
                                cursor.execute(
                                    "UPDATE attendance SET status = ? WHERE roll_no = ? AND class_name = ? AND subject = ? AND date = ?",
                                    (status, roll_no, selected_class, selected_subject, today_str)
                                )
                            else:
                                cursor.execute(
                                    "INSERT INTO attendance (roll_no, class_name, subject, date, status) VALUES (?, ?, ?, ?, ?)",
                                    (roll_no, selected_class, selected_subject, today_str, status)
                                )
                        conn.commit()
                        st.success("Attendance saved successfully!")
            conn.close()

# ==========================================
# TAB 3: VIEW REPORTS
# ==========================================
with tab3:
    st.subheader("Attendance Reports")
    
    filter_roll = st.text_input("Filter by Roll Number (Leave blank for all records):").strip()

    conn = sqlite3.connect("academy_attendance.db")
    cursor = conn.cursor()

    if filter_roll:
        cursor.execute("""
            SELECT students.name, students.roll_no, attendance.class_name, attendance.subject, attendance.date, attendance.status 
            FROM attendance 
            JOIN students ON students.roll_no = attendance.roll_no 
            WHERE attendance.roll_no = ?
        """, (filter_roll,))
    else:
        cursor.execute("""
            SELECT students.name, students.roll_no, attendance.class_name, attendance.subject, attendance.date, attendance.status 
            FROM attendance 
            JOIN students ON students.roll_no = attendance.roll_no
        """)

    records = cursor.fetchall()
    conn.close()

    if records:
        report_table = [
            {
                "Student Name": r[0],
                "Roll Number": r[1],
                "Class": r[2],
                "Subject": r[3],
                "Date": r[4],
                "Status": r[5]
            }
            for r in records
        ]
        st.dataframe(report_table, use_container_width=True)
    else:
        st.info("No attendance records found.")