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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT,
            class_name TEXT,
            subject TEXT,
            test_name TEXT,
            obtained_marks REAL,
            total_marks REAL,
            date TEXT,
            FOREIGN KEY (roll_no) REFERENCES students (roll_no)
        )
    """)
    conn.commit()
    conn.close()

# Page Configuration
st.set_page_config(
    page_title="AIMS Science Academy - Attendance & Test System",
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

# Session State Initialization for Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# ==========================================
# LOGIN SCREEN
# ==========================================
if not st.session_state.logged_in:
    st.title("🎓 AIMS Science Academy - Login Portal")
    
    col_l1, col_l2 = st.columns([1, 1])
    with col_l1:
        st.markdown("### لاگ ان کریں (Please Login)")
        login_role = st.selectbox("اکاؤنٹ کی قسم منتخب کریں", ["کلاس ٹیچر (Class Teacher)", "ایڈمن / پروگرامر (Admin / Programmer)"])
        
        username_input = st.text_input("یوزر نیم (Username)")
        password_input = st.text_input("پاسورڈ (Password)", type="password")
        
        if st.button("لاگ ان کریں"):
            if login_role == "ایڈمن / پروگرامر (Admin / Programmer)":
                if username_input == "admin" and password_input == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.role = "admin"
                    st.success("ایڈمن لاگ ان کامیاب!")
                    st.rerun()
                else:
                    st.error("غلط ایڈمن یوزر نیم یا پاسورڈ!")
            else:
                if username_input == "teacher" and password_input == "teacher123":
                    st.session_state.logged_in = True
                    st.session_state.role = "teacher"
                    st.success("کلاس ٹیچر لاگ ان کامیاب!")
                    st.rerun()
                else:
                    st.error("غلط ٹیچر یوزر نیم یا پاسورڈ!")
    with col_l2:
        st.markdown("""
            <div style="background-color: #f0f4f8; padding: 25px; border-radius: 10px; border: 2px solid #b0c4de; margin-top: 30px;">
                <h3 style="color: #1e3a8a; margin-top: 0;">AIMS</h3>
                <p style="color: #7f1d1d; font-weight: bold; font-size: 12px;">AIMS SCIENCE ACADEMY</p>
                <hr>
                <p style="font-size: 14px;"><b>ہدایات:</b><br>
                - ایڈمن (آپ) اسٹوڈنٹس کا ڈیٹا درج کرنے اور مینج کرنے کے مجاز ہیں۔<br>
                - کلاس ٹیچر صرف حاضری (Attendance) اور ٹیسٹ مارکس درج کر سکتے ہیں۔</p>
            </div>
        """, unsafe_allow_html=True)
    st.stop()

# ==========================================
# MAIN APPLICATION (AFTER LOGIN)
# ==========================================
st.sidebar.markdown(f"👤 لاگ ان بطور: **{st.session_state.role.upper()}**")
if st.sidebar.button("لاگ آؤٹ (Logout)"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.rerun()

st.title("🎓 AIMS Science Academy - Management System")

# Role-based Navigation Tabs
if st.session_state.role == "admin":
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Manage Students", 
        "📝 Mark Attendance", 
        "📊 Attendance Reports", 
        "📈 Test Reports"
    ])
else:
    # Teacher view: No access to 'Manage Students' tab
    tab2, tab3, tab4 = st.tabs([
        "📝 Mark Attendance", 
        "📊 Attendance Reports", 
        "📈 Test Reports"
    ])
    tab1 = None

# ==========================================
# TAB 1: MANAGE STUDENTS (ADMIN ONLY)
# ==========================================
if tab1 is not None:
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
                <div style="background-color: #f0f4f8; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #b0c4de; margin-top: 25px;">
                    <h3 style="color: #1e3a8a; margin: 0; font-size: 28px; font-weight: bold;">AIMS</h3>
                    <p style="color: #7f1d1d; margin: 5px 0 0 0; font-size: 11px; font-weight: bold; letter-spacing: 1px;">AIMS SCIENCE ACADEMY</p>
                </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.subheader("Enrolled Students")
        
        conn = sqlite3.connect("academy_attendance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, roll_no, class_name, subjects FROM students")
        students_data = cursor.fetchall()
        conn.close()

        if students_data:
            table_data = [{"ID": r[0], "Name": r[1], "Roll No": r[2], "Class": r[3], "Subjects": r[4]} for r in students_data]
            st.dataframe(table_data, use_container_width=True)

            col_del1, col_del2 = st.columns(2)
            with col_del1:
                roll_to_delete = st.selectbox("Select Roll No to Delete", options=[r[2] for r in students_data], key="delete_select")
                if st.button("Delete Selected Student"):
                    conn = sqlite3.connect("academy_attendance.db")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM attendance WHERE roll_no = ?", (roll_to_delete,))
                    cursor.execute("DELETE FROM test_marks WHERE roll_no = ?", (roll_to_delete,))
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
                    cursor.execute("DELETE FROM test_marks")
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
        st.warning("No classes found. Please add students first.")
    else:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            selected_class = st.selectbox("Select Class", options=classes, key="att_class")

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
                selected_subject = st.selectbox("Select Subject", options=subject_list, key="att_sub")
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
# TAB 3: ATTENDANCE REPORTS
# ==========================================
with tab3:
    st.subheader("Attendance Reports")
    
    filter_roll = st.text_input("Filter by Roll Number (Leave blank for all records):", key="att_filter").strip()

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

# ==========================================
# TAB 4: TEST REPORTS
# ==========================================
with tab4:
    st.subheader("Student Test Marks & Reports")

    test_action = st.radio("Choose Action", options=["Enter / Update Test Marks", "View Test Records"], horizontal=True)

    conn = sqlite3.connect("academy_attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT class_name FROM students")
    classes = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()

    if test_action == "Enter / Update Test Marks":
        st.markdown("### Enter Test Scores")
        if not classes:
            st.warning("No classes found. Please add students first.")
        else:
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                test_class = st.selectbox("Test Class", options=classes, key="test_class")
            
            conn = sqlite3.connect("academy_attendance.db")
            cursor = conn.cursor()
            cursor.execute("SELECT subjects FROM students WHERE class_name = ?", (test_class,))
            rows = cursor.fetchall()
            conn.close()

            t_subjects = set()
            for row in rows:
                for sub in row[0].split(","):
                    clean_sub = sub.strip()
                    if clean_sub:
                        t_subjects.add(clean_sub)
            test_subject_list = sorted(list(t_subjects))

            with col_t2:
                if test_subject_list:
                    test_subject = st.selectbox("Test Subject", options=test_subject_list, key="test_sub")
                else:
                    test_subject = None
                    st.warning("No subjects available.")

            with col_t3:
                test_name = st.text_input("Test Title / Name", value="Weekly Test 1")

            col_t4, col_t5 = st.columns(2)
            with col_t4:
                total_marks = st.number_input("Total Marks", min_value=1.0, value=50.0, step=1.0)
            with col_t5:
                test_date = st.date_input("Test Date", value=date.today())

            if test_class and test_subject:
                conn = sqlite3.connect("academy_attendance.db")
                cursor = conn.cursor()
                cursor.execute("SELECT roll_no, name, subjects FROM students WHERE class_name = ?", (test_class,))
                students = cursor.fetchall()

                enrolled_students = []
                for roll_no, name, subjects in students:
                    if test_subject in [s.strip() for s in subjects.split(",")]:
                        enrolled_students.append((roll_no, name))

                if not enrolled_students:
                    st.info(f"No students in class '{test_class}' enrolled in '{test_subject}'.")
                else:
                    st.write(f"Entering marks for **{test_class}** - **{test_subject}** ({test_name})")
                    
                    test_scores = {}
                    with st.form("test_marks_form"):
                        for roll_no, name in enrolled_students:
                            cursor.execute(
                                "SELECT obtained_marks FROM test_marks WHERE roll_no = ? AND class_name = ? AND subject = ? AND test_name = ? AND date = ?",
                                (roll_no, test_class, test_subject, test_name, str(test_date))
                            )
                            existing_score = cursor.fetchone()
                            default_score = existing_score[0] if existing_score else 0.0

                            col_s1, col_s2 = st.columns([2, 2])
                            with col_s1:
                                st.write(f"**{name}** `({roll_no})`")
                            with col_s2:
                                score = st.number_input(
                                    f"Marks for {roll_no}",
                                    min_value=0.0,
                                    max_value=float(total_marks),
                                    value=float(default_score),
                                    step=0.5,
                                    key=f"score_{roll_no}",
                                    label_visibility="collapsed"
                                )
                                test_scores[roll_no] = score

                        submit_marks = st.form_submit_button("Save Test Marks")
                        if submit_marks:
                            for roll_no, obtained in test_scores.items():
                                cursor.execute(
                                    "SELECT * FROM test_marks WHERE roll_no = ? AND class_name = ? AND subject = ? AND test_name = ? AND date = ?",
                                    (roll_no, test_class, test_subject, test_name, str(test_date))
                                )
                                record = cursor.fetchone()

                                if record:
                                    cursor.execute(
                                        "UPDATE test_marks SET obtained_marks = ?, total_marks = ? WHERE roll_no = ? AND class_name = ? AND subject = ? AND test_name = ? AND date = ?",
                                        (obtained, total_marks, roll_no, test_class, test_subject, test_name, str(test_date))
                                    )
                                else:
                                    cursor.execute(
                                        "INSERT INTO test_marks (roll_no, class_name, subject, test_name, obtained_marks, total_marks, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                        (roll_no, test_class, test_subject, test_name, obtained, total_marks, str(test_date))
                                    )
                            conn.commit()
                            st.success("Test marks saved successfully!")
                conn.close()

    else:
        st.markdown("### View Test Records & Reports")
        filter_test_roll = st.text_input("Filter by Roll Number (Leave blank for all records):", key="test_filter").strip()

        conn = sqlite3.connect("academy_attendance.db")
        cursor = conn.cursor()

        if filter_test_roll:
            cursor.execute("""
                SELECT students.name, students.roll_no, test_marks.class_name, test_marks.subject, test_marks.test_name, test_marks.obtained_marks, test_marks.total_marks, test_marks.date 
                FROM test_marks 
                JOIN students ON students.roll_no = test_marks.roll_no 
                WHERE test_marks.roll_no = ?
            """, (filter_test_roll,))
        else:
            cursor.execute("""
                SELECT students.name, students.roll_no, test_marks.class_name, test_marks.subject, test_marks.test_name, test_marks.obtained_marks, test_marks.total_marks, test_marks.date 
                FROM test_marks 
                JOIN students ON students.roll_no = test_marks.roll_no
            """)

        test_records = cursor.fetchall()
        conn.close()

        if test_records:
            test_report_table = [
                {
                    "Student Name": r[0],
                    "Roll Number": r[1],
                    "Class": r[2],
                    "Subject": r[3],
                    "Test Title": r[4],
                    "Obtained Marks": r[5],
                    "Total Marks": r[6],
                    "Percentage": f"{(r[5]/r[6])*100:.1f}%" if r[6] > 0 else "0.0%",
                    "Date": r[7]
                }
                for r in test_records
            ]
            st.dataframe(test_report_table, use_container_width=True)
        else:
            st.info("No test records found.")
