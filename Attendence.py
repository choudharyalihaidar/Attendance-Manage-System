import base64
from datetime import date, timedelta
import psycopg2
import streamlit as st

# ReportLab imports for professional PDF generation
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# ==========================================
# NEON POSTGRESQL CONNECTION CONFIGURATION
# ==========================================
DATABASE_URL = "postgresql://neondb_owner:npg_UGwX3Z0ygdho@ep-cold-sound-beiwqd0u-pooler.c-9.us-east-2.aws.neon.tech/neondb?sslmode=require"


def get_db_connection():
    try:
        return psycopg2.connect(DATABASE_URL)
    except psycopg2.OperationalError as e:
        if "unexpected eof while reading" in str(e):
            return psycopg2.connect(DATABASE_URL)
        raise e


# Initialize Database (Ensuring phone column exists)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            class_name TEXT NOT NULL,
            subjects TEXT NOT NULL,
            phone TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
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
    cursor.close()
    conn.close()


# Page Configuration
st.set_page_config(
    page_title="AIMS Science Academy - Attendance & Test System",
    page_icon="monomono.png",
    layout="wide",
)

# Initialize database on startup
init_db()


# Function to safely convert local monogram image to base64
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return (
                base64.b64encode(image_file.read())
                .decode("utf-8")
                .replace("\n", "")
                .replace("\r", "")
            )
    except Exception:
        return ""


# Load monogram image as base64 safely
img_base64 = get_image_base64("monomono.png")
img_src = f"data:image/png;base64,{img_base64}" if img_base64 else ""

# Custom Styling & Header Design
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }
    /* Login button styling */
    .stButton>button {
        width: 100%;
        background-color: #6b1426;
        color: white;
        border-radius: 5px;
        height: 45px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #851a31;
        color: white;
    }
    /* Side panels look */
    .side-panel-left {
        background: linear-gradient(135deg, #1e1e2f 0%, #0f0f1a 100%);
        padding: 30px;
        border-radius: 10px;
        color: white;
        text-align: center;
        height: 100%;
    }
    .side-panel-right {
        background-color: #f0f2f6;
        padding: 25px;
        border-radius: 10px;
        color: #333333;
        height: 100%;
    }
    /* Circular monogram container styling */
    .monogram-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: 3px solid #ffd700;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin: 0 auto 10px auto;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: white;
    }
    .monogram-circle img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Session State Initialization for Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# ==========================================
# LOGIN SCREEN (3-COLUMN LAYOUT WITH MONOGRAM)
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1.2, 2, 1.2])

    with col1:
        st.markdown(
            """
            <div class="side-panel-left">
                <h3 style="color: #ffffff; margin-bottom: 20px;">AIMS SCIENCE ACADEMY</h3>
                <div style="font-size: 50px; margin: 20px 0;">🎓</div>
                <p style="font-size: 16px; color: #d1d5db; font-style: italic;">
                    "ILLUMINATING MINDS, SHAPING FUTURES."
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            "<h2 style='text-align: center; color: #FFD700;'>Welcome to</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h1 style='text-align: center; color: #6b1426; font-size: 28px;"
            " margin-bottom: 30px;'>AIMS Science Academy</h1>",
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            login_role = st.selectbox(
                "Select Account Type", ["Class Teacher", "Admin / Programmer"]
            )
            username_input = st.text_input("Username", placeholder="Your Username")
            password_input = st.text_input(
                "Password", type="password", placeholder="Your Password"
            )

            st.markdown(
                "<p style='text-align: right; font-size: 12px;'><a"
                " href='#' style='text-decoration: none; color: #aaa;'>Forgot"
                " Password?</a></p>",
                unsafe_allow_html=True,
            )

            login_submitted = st.form_submit_button("Login")

            if login_submitted:
                if login_role == "Admin / Programmer":
                    if (
                        username_input == "admin"
                        and password_input == "19072009"
                    ):
                        st.session_state.logged_in = True
                        st.session_state.role = "admin"
                        st.success("Admin login successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect Admin username or password!")
                else:
                    if username_input == "teacher" and password_input == "abcd4321":
                        st.session_state.logged_in = True
                        st.session_state.role = "teacher"
                        st.success("Class Teacher login successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect Teacher username or password!")

    with col3:
        st.markdown(
            f"""
            <div class="side-panel-right">
                <div style="text-align: center;">
                    <div class="monogram-circle">
                        <img src="{img_src}" alt="Monogram">
                    </div>
                    <h4 style="margin: 0; color: #6b1426; font-weight: bold;">AIMS SCIENCE ACADEMY</h4>
                    <p style="font-size: 11px; color: #666; margin-bottom: 15px;">Official Portal & Monogram</p>
                </div>
                <hr style="border: 0; border-top: 1px solid #ccc; margin: 15px 0;">
                <div style="font-size: 13px; color: #333;">
                    <p><b> Mission:</b><br>A Community of Scholars</p>
                    <p><b> Vision:</b><br>Providing exceptional, accessible education and fostering growth.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.stop()

# ==========================================
# MAIN APPLICATION (AFTER LOGIN)
# ==========================================
role_display = st.session_state.role.upper() if st.session_state.role else ""
st.sidebar.markdown(f" Logged in as: **{role_display}**")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.rerun()

st.title(" AIMS Science Academy - Management System")

# Role-based Navigation Tabs
if st.session_state.role == "admin":
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "👥 Manage Students",
            "📝 Mark Attendance",
            "📊 Attendance Reports",
            "📈 Test Reports",
        ]
    )
else:
    tab2, tab3, tab4 = st.tabs(
        ["📝 Mark Attendance", "📊 Attendance Reports", "📈 Test Reports"]
    )
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
                subjects = st.text_input(
                    "Subjects (comma separated, e.g. Math, Physics, Chemistry)"
                )
                phone = st.text_input("Home Phone Number (Admin Only)")

                submit_student = st.form_submit_button("Add Student")

                if submit_student:
                    if (
                        not name.strip()
                        or not roll_no.strip()
                        or not class_name.strip()
                        or not subjects.strip()
                    ):
                        st.error("Please fill in all mandatory fields.")
                    else:
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO students (name, roll_no, class_name, subjects, phone)"
                                " VALUES (%s, %s, %s, %s, %s)",
                                (
                                    name.strip(),
                                    roll_no.strip(),
                                    class_name.strip(),
                                    subjects.strip(),
                                    phone.strip(),
                                ),
                            )
                            conn.commit()
                            cursor.close()
                            conn.close()
                            st.success(f"Student {name} added successfully!")
                            st.rerun()
                        except psycopg2.errors.UniqueViolation:
                            st.error("Roll number already exists.")

        with col_logo:
            st.markdown(
                f"""
                <div class="side-panel-right" style="margin-top: 30px; text-align: center;">
                    <div class="monogram-circle" style="width: 60px; height: 60px; margin: 0 auto 5px auto;">
                        <img src="{img_src}" alt="Monogram">
                    </div>
                    <h4 style="color: #6b1426; font-weight: bold; margin: 0; font-size: 16px;">AIMS SCIENCE ACADEMY</h4>
                    <p style="font-size: 10px; color: #666; margin: 2px 0 0 0;">Admin Portal Controls</p>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.divider()
        st.subheader("Enrolled Students (Admin View)")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, roll_no, class_name, subjects, phone FROM students ORDER BY roll_no ASC"
        )
        students_data = cursor.fetchall()
        cursor.close()
        conn.close()

        if students_data:
            table_data = [
                {
                    "ID": r[0],
                    "Name": r[1],
                    "Roll No": r[2],
                    "Class": r[3],
                    "Subjects": r[4],
                    "Home Phone": r[5] if r[5] else "N/A",
                }
                for r in students_data
            ]
            st.dataframe(table_data, use_container_width=True)

            # --- EDIT STUDENT SECTION ---
            st.divider()
            st.subheader(" Edit Student Details")
            edit_roll_no = st.selectbox(
                "Select Roll No to Edit",
                options=[r[2] for r in students_data],
                key="edit_select_box",
            )

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, class_name, subjects, phone FROM students WHERE roll_no = %s",
                (edit_roll_no,),
            )
            curr_student = cursor.fetchone()
            cursor.close()
            conn.close()

            if curr_student:
                curr_name, curr_class, curr_subjects, curr_phone = curr_student
                with st.form("edit_student_form"):
                    new_name = st.text_input(
                        "Update Student Name", value=curr_name
                    )
                    new_class = st.text_input(
                        "Update Class Name", value=curr_class
                    )
                    new_subjects = st.text_input(
                        "Update Subjects (comma separated)", value=curr_subjects
                    )
                    new_phone = st.text_input(
                        "Update Home Phone Number", value=curr_phone if curr_phone else ""
                    )

                    update_btn = st.form_submit_button("Save Changes")
                    if update_btn:
                        if (
                            not new_name.strip()
                            or not new_class.strip()
                            or not new_subjects.strip()
                        ):
                            st.error("Please fill in all mandatory fields.")
                        else:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE students SET name = %s, class_name = %s, subjects = %s, phone = %s"
                                " WHERE roll_no = %s",
                                (
                                    new_name.strip(),
                                    new_class.strip(),
                                    new_subjects.strip(),
                                    new_phone.strip(),
                                    edit_roll_no,
                                ),
                            )
                            conn.commit()
                            cursor.close()
                            conn.close()
                            st.success(
                                f"Student with Roll No {edit_roll_no} updated successfully!"
                            )
                            st.rerun()

            st.divider()
            col_del1, col_del2 = st.columns(2)
            with col_del1:
                roll_to_delete = st.selectbox(
                    "Select Roll No to Delete",
                    options=[r[2] for r in students_data],
                    key="delete_select",
                )
                if st.button("Delete Selected Student"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM attendance WHERE roll_no = %s",
                        (roll_to_delete,),
                    )
                    cursor.execute(
                        "DELETE FROM test_marks WHERE roll_no = %s",
                        (roll_to_delete,),
                    )
                    cursor.execute(
                        "DELETE FROM students WHERE roll_no = %s",
                        (roll_to_delete,),
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(
                        f"Student with Roll No {roll_to_delete} deleted successfully."
                    )
                    st.rerun()

            with col_del2:
                st.write("")
                st.write("")
                if st.button(
                    "Clear All Students & Reset Database", type="primary"
                ):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM attendance")
                    cursor.execute("DELETE FROM test_marks")
                    cursor.execute("DELETE FROM students")
                    conn.commit()
                    cursor.close()
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
    
    selected_date = st.date_input("Select Attendance Date", value=date.today(), key="att_date_picker")
    today_str = str(selected_date)
    st.info(f"Active Attendance Date: **{today_str}**")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT class_name FROM students")
    classes = [row[0] for row in cursor.fetchall() if row[0]]
    cursor.close()
    conn.close()

    if not classes:
        st.warning("No classes found. Please add students first.")
    else:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            selected_class = st.selectbox(
                "Select Class", options=classes, key="att_class"
            )

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT subjects FROM students WHERE class_name = %s",
            (selected_class,),
        )
        rows = cursor.fetchall()
        cursor.close()
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
                selected_subject = st.selectbox(
                    "Select Subject", options=subject_list, key="att_sub"
                )
            else:
                selected_subject = None
                st.warning("No subjects found for this class.")

        if selected_class and selected_subject:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT roll_no, name, subjects FROM students WHERE class_name = %s ORDER BY roll_no ASC",
                (selected_class,),
            )
            students = cursor.fetchall()

            enrolled_students = []
            for roll_no, name, subjects in students:
                if selected_subject in [s.strip() for s in subjects.split(",")]:
                    enrolled_students.append((roll_no, name))

            if not enrolled_students:
                st.info(
                    f"No students in class '{selected_class}' enrolled in"
                    f" '{selected_subject}'."
                )
            else:
                st.write(
                    f"Marking attendance for **{selected_class}** -"
                    f" **{selected_subject}** on **{today_str}**"
                )

                attendance_status = {}

                with st.form("attendance_form"):
                    for roll_no, name in enrolled_students:
                        cursor.execute(
                            "SELECT status FROM attendance WHERE roll_no = %s AND"
                            " class_name = %s AND subject = %s AND date = %s",
                            (roll_no, selected_class, selected_subject, today_str),
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
                                label_visibility="collapsed",
                            )
                            attendance_status[roll_no] = status

                    submit_attendance = st.form_submit_button("Save Attendance")
                    if submit_attendance:
                        for roll_no, status in attendance_status.items():
                            cursor.execute(
                                "SELECT * FROM attendance WHERE roll_no = %s AND class_name ="
                                " %s AND subject = %s AND date = %s",
                                (roll_no, selected_class, selected_subject, today_str),
                            )
                            existing = cursor.fetchone()

                            if existing:
                                cursor.execute(
                                    "UPDATE attendance SET status = %s WHERE roll_no = %s AND"
                                    " class_name = %s AND subject = %s AND date = %s",
                                    (
                                        status,
                                        roll_no,
                                        selected_class,
                                        selected_subject,
                                        today_str,
                                    ),
                                )
                            else:
                                cursor.execute(
                                    "INSERT INTO attendance (roll_no, class_name, subject,"
                                    " date, status) VALUES (%s, %s, %s, %s, %s)",
                                    (
                                        roll_no,
                                        selected_class,
                                        selected_subject,
                                        today_str,
                                        status,
                                    ),
                                )
                        conn.commit()
                        st.success("Attendance saved successfully!")
            cursor.close()
            conn.close()

# ==========================================
# TAB 3: ATTENDANCE REPORTS
# ==========================================
with tab3:
    st.subheader("Attendance Reports")

    filter_roll = st.text_input(
        "Filter by Roll Number (Leave blank for all records):", key="att_filter"
    ).strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    if filter_roll:
        cursor.execute(
            """
            SELECT students.name, students.roll_no, attendance.class_name, attendance.subject, attendance.date, attendance.status 
            FROM attendance 
            JOIN students ON students.roll_no = attendance.roll_no 
            WHERE attendance.roll_no = %s
            ORDER BY attendance.date DESC, students.roll_no ASC
        """,
            (filter_roll,),
        )
    else:
        cursor.execute("""
            SELECT students.name, students.roll_no, attendance.class_name, attendance.subject, attendance.date, attendance.status 
            FROM attendance 
            JOIN students ON students.roll_no = attendance.roll_no
            ORDER BY attendance.date DESC, students.roll_no ASC
        """)

    records = cursor.fetchall()
    cursor.close()
    conn.close()

    if records:
        report_table = [
            {
                "Student Name": r[0],
                "Roll Number": r[1],
                "Class": r[2],
                "Subject": r[3],
                "Date": r[4],
                "Status": r[5],
            }
            for r in records
        ]
        st.dataframe(report_table, use_container_width=True)

        def generate_aims_attendance_pdf(selected_records, selected_pdf_subjects, days_range_label):
            first_rec = selected_records[0]
            name, roll_no, class_name, _, _, _ = first_rec
            current_printing_date = str(date.today())

            date_map = {}
            all_dates_set = set()
            for r in selected_records:
                _, _, _, sub_name, d_str, status_val = r
                all_dates_set.add(d_str)
                if d_str not in date_map:
                    date_map[d_str] = {}
                date_map[d_str][sub_name] = status_val

            sorted_dates = sorted(list(all_dates_set), reverse=False)

            total_days = len(sorted_dates)
            days_present = 0
            days_absent = 0

            processed_rows_data = []
            for d_str in sorted_dates:
                try:
                    dt_obj = date.fromisoformat(d_str)
                    formatted_date = dt_obj.strftime("%d-%b-%Y")
                except Exception:
                    formatted_date = d_str

                present_count = 0
                subject_statuses = []
                for sub in selected_pdf_subjects:
                    status = date_map.get(d_str, {}).get(sub, "-")
                    if status.lower() == "present":
                        present_count += 1
                        subject_statuses.append("P")
                    elif status.lower() == "absent":
                        subject_statuses.append("A")
                    else:
                        subject_statuses.append("-")

                threshold = (len(selected_pdf_subjects) + 1) // 2 if selected_pdf_subjects else 1
                if selected_pdf_subjects and present_count >= threshold:
                    overall_status = "P"
                    days_present += 1
                else:
                    overall_status = "A" if selected_pdf_subjects else "-"
                    if selected_pdf_subjects:
                        days_absent += 1

                processed_rows_data.append({
                    "date": formatted_date,
                    "subjects": subject_statuses,
                    "overall": overall_status
                })

            attendance_pct = (days_present / total_days) * 100 if total_days > 0 else 0.0

            if attendance_pct >= 85.0:
                remarks_text = "Punctuality is excellent. Keep it up for consistent academic progress."
            elif attendance_pct >= 60.0:
                remarks_text = "Good attendance, but try to maintain regularity."
            else:
                remarks_text = "Attendance is below required criteria. Immediate improvement needed."

            filename = f"AIMS_Attendance_Report_{roll_no}.pdf"
            doc = SimpleDocTemplate(
                filename,
                pagesize=letter,
                rightMargin=36,
                leftMargin=36,
                topMargin=36,
                bottomMargin=36,
            )
            story = []

            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "TitleStyle",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=15,
                leading=18,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#2A2B6E"),
            )

            subtitle_style = ParagraphStyle(
                "SubtitleStyle",
                parent=styles["Normal"],
                fontName="Helvetica-Oblique",
                fontSize=8.5,
                leading=11,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#444444"),
            )

            report_title_style = ParagraphStyle(
                "ReportTitleStyle",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13,
                alignment=TA_CENTER,
                textColor=colors.white,
            )

            section_heading = ParagraphStyle(
                "SectionHeading",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=12,
                alignment=TA_CENTER,
                textColor=colors.white,
            )

            cell_style = ParagraphStyle(
                "CellStyle",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#111111"),
            )

            cell_center = ParagraphStyle(
                "CellCenter",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#111111"),
            )

            cell_bold = ParagraphStyle(
                "CellBold",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#111111"),
            )

            cell_center_bold = ParagraphStyle(
                "CellCenterBold",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=12,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#111111"),
            )

            try:
                logo_img = Image("monomono.png", width=55, height=55)
            except Exception:
                logo_img = Paragraph("<b>[LOGO]</b>", cell_bold)

            header_text_content = [
                Paragraph("<b>AIMS SCIENCE ACADEMY</b>", title_style),
                Spacer(1, 2),
                Paragraph('"Illuminating Minds, Shaping Futures"', subtitle_style),
                Spacer(1, 3),
                Paragraph(
                    "Phone: +92-319-8717772 &nbsp;&nbsp;|&nbsp;&nbsp; Email:"
                    " aimsscienceacademy6@gmail.com",
                    subtitle_style,
                ),
                Spacer(1, 2),
                Paragraph(
                    "Address: Inside Staff Gala, Near TIPS Model School Sargodha"
                    " Road, Gujrat.",
                    subtitle_style,
                ),
            ]

            header_table = Table(
                [[logo_img, header_text_content]], colWidths=[70, 470]
            )
            header_table.setStyle(
                TableStyle([
                    ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#2A2B6E")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9F9F9")),
                ])
            )
            story.append(header_table)
            story.append(Spacer(1, 10))

            report_title = Table(
                [[Paragraph("STUDENT ATTENDANCE REPORT", report_title_style)]],
                colWidths=[540],
            )
            report_title.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#5A1818")),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ])
            )
            story.append(report_title)
            story.append(Spacer(1, 5))

            principal_p = Paragraph(
                "<b>Principal: Choudhary Asim Walyat</b>",
                ParagraphStyle(
                    "Prin",
                    parent=styles["Normal"],
                    fontName="Helvetica-Bold",
                    fontSize=10,
                    alignment=TA_CENTER,
                ),
            )
            story.append(principal_p)
            story.append(Spacer(1, 8))

            subj_label_str = ", ".join(selected_pdf_subjects) if selected_pdf_subjects else "None"

            info_data = [
                [
                    Paragraph("<b>Student Name</b>", cell_bold),
                    Paragraph(f": {name}", cell_style),
                    Paragraph("<b>Subject(s)</b>", cell_bold),
                    Paragraph(f": {subj_label_str}", cell_style),
                ],
                [
                    Paragraph("<b>Roll No.</b>", cell_bold),
                    Paragraph(f": {roll_no}", cell_style),
                    Paragraph("<b>Report Date</b>", cell_bold),
                    Paragraph(f": {current_printing_date}", cell_style),
                ],
                [
                    Paragraph("<b>Class/Batch</b>", cell_bold),
                    Paragraph(f": {class_name}", cell_style),
                    Paragraph("<b>Duration</b>", cell_bold),
                    Paragraph(f": {days_range_label}", cell_style),
                ],
            ]
            info_table = Table(info_data, colWidths=[90, 180, 90, 180])
            info_table.setStyle(
                TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CCCCCC")),
                ])
            )
            story.append(info_table)
            story.append(Spacer(1, 10))

            log_title = Table(
                [[Paragraph("DAILY ATTENDANCE", report_title_style)]],
                colWidths=[540],
            )
            log_title.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#5A1818")),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ])
            )
            story.append(log_title)

            num_subs = len(selected_pdf_subjects)
            if num_subs > 0:
                sub_col_width = 330.0 / num_subs
            else:
                sub_col_width = 330.0

            col_widths = [100.0] + [sub_col_width] * max(num_subs, 1) + [110.0]

            header_row_1 = [Paragraph("<b>Date</b>", section_heading), Paragraph("<b>Subjects</b>", section_heading)]
            for _ in range(1, max(num_subs, 1)):
                header_row_1.append("")
            header_row_1.append(Paragraph("<b>Overall Attendance</b>", section_heading))

            header_row_2 = [Paragraph("", section_heading)]
            for sub in selected_pdf_subjects:
                header_row_2.append(Paragraph(f"<b>{sub}</b>", section_heading))
            if num_subs == 0:
                header_row_2.append(Paragraph("<b>-</b>", section_heading))
            header_row_2.append(Paragraph("", section_heading))

            matrix_rows = [header_row_1, header_row_2]

            for row in processed_rows_data:
                r_cells = [Paragraph(row["date"], cell_style)]
                for st_val in row["subjects"]:
                    color_code = "#006600" if st_val == "P" else ("#990000" if st_val == "A" else "#333333")
                    r_cells.append(Paragraph(f"<font color='{color_code}'><b>{st_val}</b></font>", cell_center))
                r_cells.append(Paragraph(f"<b>{row['overall']}</b>", cell_center_bold))
                matrix_rows.append(r_cells)

            total_cols = len(col_widths)
            span_size = total_cols // 3
            rem = total_cols % 3

            c1_start = 0
            c1_end = span_size + (1 if rem > 0 else 0) - 1

            c2_start = c1_end + 1
            c2_end = c2_start + span_size + (1 if rem > 1 else 0) - 1

            c3_start = c2_end + 1
            c3_end = total_cols - 1

            summary_row = [Paragraph("", cell_bold)] * total_cols
            summary_row[c1_start] = Paragraph(f"<b>Total Days: {total_days}</b>", cell_bold)
            summary_row[c2_start] = Paragraph(f"<b>Days Present: {days_present}</b>", cell_bold)
            summary_row[c3_start] = Paragraph(f"<b>Days Absent: {days_absent}</b>", cell_bold)
            matrix_rows.append(summary_row)

            table_style_commands = [
                ("BACKGROUND", (0, 0), (-1, 1), colors.HexColor("#7A2222")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("SPAN", (1, 0), (num_subs if num_subs > 0 else 1, 0)),
                ("SPAN", (0, 0), (0, 1)),
                ("SPAN", (-1, 0), (-1, 1)),
                ("SPAN", (c1_start, -1), (c1_end, -1)),
                ("SPAN", (c2_start, -1), (c2_end, -1)),
                ("SPAN", (c3_start, -1), (c3_end, -1)),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EFEFEF")),
            ]

            matrix_table = Table(matrix_rows, colWidths=col_widths)
            matrix_table.setStyle(TableStyle(table_style_commands))

            story.append(matrix_table)
            story.append(Spacer(1, 40))

            remarks_title = Paragraph(
                "<b>TEACHER'S REMARKS</b>",
                ParagraphStyle(
                    "RT",
                    parent=styles["Normal"],
                    fontName="Helvetica-Bold",
                    fontSize=10,
                    textColor=colors.HexColor("#111111"),
                ),
            )
            remarks_p = Paragraph(
                f'"{remarks_text}"',
                ParagraphStyle(
                    "RText",
                    parent=styles["Normal"],
                    fontName="Helvetica-Oblique",
                    fontSize=9,
                    textColor=colors.HexColor("#333333"),
                ),
            )

            remarks_table = Table(
                [[remarks_title], [remarks_p]], colWidths=[540]
            )
            remarks_table.setStyle(
                TableStyle([
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ])
            )
            story.append(remarks_table)
            story.append(Spacer(1, 20))

            # 5. Signatures Section
            try:
                sign_img = Image("azim_sign.png", width=110, height=45)
            except Exception:
                sign_img = Paragraph("<b>Choudhary Asim Walyat</b>", cell_style)

            sig_data = [
                [
                    Paragraph("____________________________", cell_style),
                    sign_img,
                ],
                [
                    Paragraph("<b>Parent's Signature</b>", cell_style),
                    Paragraph("<b>Principal / Teacher's Signature</b>", cell_style),
                ],
            ]
            sig_table = Table(sig_data, colWidths=[270, 270])
            sig_table.setStyle(
                TableStyle([
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (1, 0), (1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (1, 0), (1, -1), 40),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ])
            )
            story.append(sig_table)

            doc.build(story)
            with open(filename, "rb") as f:
                return f.read()

        st.divider()
        st.subheader(" Download Student Attendance PDF Report")

        student_dict = {}
        student_subjects_dict = {}
        for r in records:
            s_name, s_roll, _, s_sub, _, _ = r
            student_dict[s_roll] = s_name
            if s_roll not in student_subjects_dict:
                student_subjects_dict[s_roll] = set()
            if s_sub:
                student_subjects_dict[s_roll].add(s_sub)

        col_att_sel1, col_att_sel2 = st.columns(2)
        with col_att_sel1:
            selected_att_roll = st.selectbox(
                "Select Student for Attendance Report",
                options=list(student_dict.keys()),
                format_func=lambda roll: f"{student_dict[roll]} (Roll: {roll})",
                key="att_pdf_roll",
            )
        with col_att_sel2:
            days_option = st.selectbox(
                "Select Attendance Duration",
                options=[
                    "All Records",
                    "Last 7 Days",
                    "Last 15 Days",
                    "Last 30 Days",
                ],
                key="att_days_range",
            )

        if selected_att_roll:
            available_student_subjects = sorted(
                list(student_subjects_dict.get(selected_att_roll, []))
            )
            selected_pdf_subjects = st.multiselect(
                "Select Subject(s) for PDF Report Matrix",
                options=available_student_subjects,
                default=available_student_subjects,
                key="att_pdf_subjects",
            )

            student_att_records = [
                r
                for r in records
                if r[1] == selected_att_roll
                and (
                    not selected_pdf_subjects
                    or r[3] in selected_pdf_subjects
                )
            ]

            if days_option == "Last 7 Days":
                cutoff_date = date.today() - timedelta(days=7)
                student_att_records = [
                    r
                    for r in student_att_records
                    if date.fromisoformat(r[4]) >= cutoff_date
                ]
            elif days_option == "Last 15 Days":
                cutoff_date = date.today() - timedelta(days=15)
                student_att_records = [
                    r
                    for r in student_att_records
                    if date.fromisoformat(r[4]) >= cutoff_date
                ]
            elif days_option == "Last 30 Days":
                cutoff_date = date.today() - timedelta(days=30)
                student_att_records = [
                    r
                    for r in student_att_records
                    if date.fromisoformat(r[4]) >= cutoff_date
                ]

            if not student_att_records:
                st.warning(
                    "No attendance records found for the selected student, subjects, and duration."
                )
            else:
                pdf_att_data = generate_aims_attendance_pdf(
                    student_att_records, selected_pdf_subjects, days_option
                )
                st.download_button(
                    label=" Click here to download Attendance PDF",
                    data=pdf_att_data,
                    file_name=f"AIMS_Attendance_Report_{selected_att_roll}.pdf",
                    mime="application/pdf",
                )
    else:
        st.info("No attendance records found.")

# ==========================================
# TAB 4: TEST REPORTS
# ==========================================
with tab4:
    st.subheader("Student Test Marks & Reports")

    test_action = st.radio(
        "Choose Action",
        options=["Enter / Update Test Marks", "View Test Records"],
        horizontal=True,
    )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT class_name FROM students")
    classes = [row[0] for row in cursor.fetchall() if row[0]]
    cursor.close()
    conn.close()

    if test_action == "Enter / Update Test Marks":
        st.markdown("### Enter Test Scores")
        if not classes:
            st.warning("No classes found. Please add students first.")
        else:
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                test_class = st.selectbox(
                    "Test Class", options=classes, key="test_class"
                )

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT subjects FROM students WHERE class_name = %s",
                (test_class,),
            )
            rows = cursor.fetchall()
            cursor.close()
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
                    test_subject = st.selectbox(
                        "Test Subject",
                        options=test_subject_list,
                        key="test_sub",
                    )
                else:
                    test_subject = None
                    st.warning("No subjects available.")

            with col_t3:
                test_name = st.text_input(
                    "Test Title / Name", value="Weekly Test 1"
                )

            col_t4, col_t5 = st.columns(2)
            with col_t4:
                total_marks = st.number_input(
                    "Total Marks", min_value=1.0, value=50.0, step=1.0
                )
            with col_t5:
                test_date = st.date_input("Test Date", value=date.today())

            if test_class and test_subject:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT roll_no, name, subjects FROM students WHERE class_name = %s ORDER BY roll_no ASC",
                    (test_class,),
                )
                students = cursor.fetchall()

                enrolled_students = []
                for roll_no, name, subjects in students:
                    if test_subject in [s.strip() for s in subjects.split(",")]:
                        enrolled_students.append((roll_no, name))

                if not enrolled_students:
                    st.info(
                        f"No students in class '{test_class}' enrolled in"
                        f" '{test_subject}'."
                    )
                else:
                    st.write(
                        f"Entering marks for **{test_class}** - **{test_subject}**"
                        f" ({test_name})"
                    )
                    st.info(
                        " Uncheck 'Include' for any student who was absent or whose"
                        " marks shouldn't be added."
                    )

                    test_scores = {}
                    test_includes = {}

                    with st.form("test_marks_form"):
                        for roll_no, name in enrolled_students:
                            cursor.execute(
                                "SELECT obtained_marks FROM test_marks WHERE roll_no = %s AND"
                                " class_name = %s AND subject = %s AND test_name = %s AND date"
                                " = %s",
                                (
                                    roll_no,
                                    test_class,
                                    test_subject,
                                    test_name,
                                    str(test_date),
                                ),
                            )
                            existing_score = cursor.fetchone()
                            default_score = (
                                existing_score[0] if existing_score else 0.0
                            )
                            default_include = (
                                True if existing_score else True
                            )

                            col_inc, col_s1, col_s2 = st.columns([1, 2, 2])
                            with col_inc:
                                include_student = st.checkbox(
                                    "Include",
                                    value=default_include,
                                    key=f"inc_{roll_no}",
                                )
                                test_includes[roll_no] = include_student
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
                                    label_visibility="collapsed",
                                )
                                test_scores[roll_no] = score

                        submit_marks = st.form_submit_button("Save Test Marks")
                        if submit_marks:
                            for roll_no, obtained in test_scores.items():
                                is_included = test_includes.get(roll_no, True)

                                cursor.execute(
                                    "SELECT * FROM test_marks WHERE roll_no = %s AND class_name ="
                                    " %s AND subject = %s AND test_name = %s AND date = %s",
                                    (
                                        roll_no,
                                        test_class,
                                        test_subject,
                                        test_name,
                                        str(test_date),
                                    ),
                                )
                                record = cursor.fetchone()

                                if not is_included:
                                    if record:
                                        cursor.execute(
                                            "DELETE FROM test_marks WHERE roll_no = %s AND"
                                            " class_name = %s AND subject = %s AND test_name = %s"
                                            " AND date = %s",
                                            (
                                                roll_no,
                                                test_class,
                                                test_subject,
                                                test_name,
                                                str(test_date),
                                            ),
                                        )
                                else:
                                    if record:
                                        cursor.execute(
                                            "UPDATE test_marks SET obtained_marks = %s, total_marks ="
                                            " %s WHERE roll_no = %s AND class_name = %s AND subject ="
                                            " %s AND test_name = %s AND date = %s",
                                            (
                                                obtained,
                                                total_marks,
                                                roll_no,
                                                test_class,
                                                test_subject,
                                                test_name,
                                                str(test_date),
                                            ),
                                        )
                                    else:
                                        cursor.execute(
                                            "INSERT INTO test_marks (roll_no, class_name, subject,"
                                            " test_name, obtained_marks, total_marks, date) VALUES"
                                            " (%s, %s, %s, %s, %s, %s, %s)",
                                            (
                                                roll_no,
                                                test_class,
                                                test_subject,
                                                test_name,
                                                obtained,
                                                total_marks,
                                                str(test_date),
                                            ),
                                        )
                            conn.commit()
                            st.success("Test marks saved successfully!")
                cursor.close()
                conn.close()

    else:
        st.markdown("### View Test Records & Reports")
        filter_test_roll = st.text_input(
            "Filter by Roll Number (Leave blank for all records):",
            key="test_filter",
        ).strip()

        conn = get_db_connection()
        cursor = conn.cursor()

        if filter_test_roll:
            cursor.execute(
                """
                SELECT students.name, students.roll_no, test_marks.class_name, test_marks.subject, test_marks.test_name, test_marks.obtained_marks, test_marks.total_marks, test_marks.date 
                FROM test_marks 
                JOIN students ON students.roll_no = test_marks.roll_no 
                WHERE test_marks.roll_no = %s
                ORDER BY students.roll_no ASC, test_marks.date DESC
            """,
                (filter_test_roll,),
            )
        else:
            cursor.execute("""
                SELECT students.name, students.roll_no, test_marks.class_name, test_marks.subject, test_marks.test_name, test_marks.obtained_marks, test_marks.total_marks, test_marks.date 
                FROM test_marks 
                JOIN students ON students.roll_no = test_marks.roll_no
                ORDER BY students.roll_no ASC, test_marks.date DESC
            """)

        test_records = cursor.fetchall()
        cursor.close()
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
                    "Percentage": (
                        f"{(r[5]/r[6])*100:.1f}%" if r[6] > 0 else "0.0%"
                    ),
                    "Date": r[7],
                }
                for r in test_records
            ]
            st.dataframe(test_report_table, use_container_width=True)

            def generate_aims_report_pdf(selected_records):
                first_rec = selected_records[0]
                name, roll_no, class_name, subject, _, _, _, _ = first_rec
                current_printing_date = str(date.today())

                all_test_subjects = sorted(list(set([r[3] for r in selected_records if r[3]])))
                subj_label_str = ", ".join(all_test_subjects) if all_test_subjects else subject

                filename = f"AIMS_Report_{roll_no}.pdf"
                doc = SimpleDocTemplate(
                    filename,
                    pagesize=letter,
                    rightMargin=36,
                    leftMargin=36,
                    topMargin=36,
                    bottomMargin=36,
                )
                story = []

                styles = getSampleStyleSheet()

                title_style = ParagraphStyle(
                    "TitleStyle",
                    parent=styles["Normal"],
                    fontName="Helvetica-Bold",
                    fontSize=15,
                    leading=18,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor("#2A2B6E"),
                )

                subtitle_style = ParagraphStyle(
                    "SubtitleStyle",
                    parent=styles["Normal"],
                    fontName="Helvetica-Oblique",
                    fontSize=8.5,
                    leading=11,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor("#444444"),
                )

                report_title_style = ParagraphStyle(
                    "ReportTitleStyle",
                    parent=styles["Normal"],
                    fontName="Helvetica-Bold",
                    fontSize=10,
                    leading=13,
                    alignment=TA_CENTER,
                    textColor=colors.white,
                )

                section_heading = ParagraphStyle(
                    "SectionHeading",
                    parent=styles["Normal"],
                    fontName="Helvetica-Bold",
                    fontSize=10,
                    leading=13,
                    textColor=colors.white,
                )

                cell_style = ParagraphStyle(
                    "CellStyle",
                    parent=styles["Normal"],
                    fontName="Helvetica",
                    fontSize=9,
                    leading=12,
                    textColor=colors.HexColor("#111111"),
                )

                cell_bold = ParagraphStyle(
                    "CellBold",
                    parent=styles["Normal"],
                    fontName="Helvetica-Bold",
                    fontSize=9,
                    leading=12,
                    textColor=colors.HexColor("#111111"),
                )

                cell_center_bold = ParagraphStyle(
                    "CellCenterBold",
                    parent=styles["Normal"],
                    fontName="Helvetica-Bold",
                    fontSize=9,
                    leading=12,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor("#111111"),
                )

                try:
                    logo_img = Image("monomono.png", width=55, height=55)
                except Exception:
                    logo_img = Paragraph("<b>[LOGO]</b>", cell_bold)

                header_text_content = [
                    Paragraph("<b>AIMS SCIENCE ACADEMY</b>", title_style),
                    Spacer(1, 2),
                    Paragraph(
                        '"Illuminating Minds, Shaping Futures"', subtitle_style
                    ),
                    Spacer(1, 3),
                    Paragraph(
                        "Phone: +92-319-8717772 &nbsp;&nbsp;|&nbsp;&nbsp; Email:"
                        " aimsscienceacademy6@gmail.com",
                        subtitle_style,
                    ),
                    Spacer(1, 2),
                    Paragraph(
                        "Address: Inside Staff Gala, Near TIPS Model School"
                        " Sargodha Road, Gujrat.",
                        subtitle_style,
                    ),
                ]

                header_table = Table(
                    [[logo_img, header_text_content]], colWidths=[70, 470]
                )
                header_table.setStyle(
                    TableStyle([
                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            1.5,
                            colors.HexColor("#2A2B6E"),
                        ),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            colors.HexColor("#F9F9F9"),
                        ),
                    ])
                )
                story.append(header_table)
                story.append(Spacer(1, 10))

                report_title = Table(
                    [[Paragraph("STUDENT TEST PERFORMANCE REPORT", report_title_style)]],
                    colWidths=[540],
                )
                report_title.setStyle(
                    TableStyle([
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            colors.HexColor("#5A1818"),
                        ),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ])
                )
                story.append(report_title)
                story.append(Spacer(1, 5))

                principal_p = Paragraph(
                    "<b>Principal: Choudhary Asim Walyat</b>",
                    ParagraphStyle(
                        "Prin",
                        parent=styles["Normal"],
                        fontName="Helvetica-Bold",
                        fontSize=10,
                        alignment=TA_CENTER,
                    ),
                )
                story.append(principal_p)
                story.append(Spacer(1, 8))

                info_data = [
                    [
                        Paragraph("<b>Student Name</b>", cell_bold),
                        Paragraph(f": {name}", cell_style),
                        Paragraph("<b>Subject(s)</b>", cell_bold),
                        Paragraph(f": {subj_label_str}", cell_style),
                    ],
                    [
                        Paragraph("<b>Roll No.</b>", cell_bold),
                        Paragraph(f": {roll_no}", cell_style),
                        Paragraph("<b>Date</b>", cell_bold),
                        Paragraph(f": {current_printing_date}", cell_style),
                    ],
                    [
                        Paragraph("<b>Class/Batch</b>", cell_bold),
                        Paragraph(f": {class_name}", cell_style),
                        Paragraph("", cell_style),
                        Paragraph("", cell_style),
                    ],
                ]
                info_table = Table(
                    info_data, colWidths=[90, 180, 90, 180]
                )
                info_table.setStyle(
                    TableStyle([
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CCCCCC")),
                    ])
                )
                story.append(info_table)
                story.append(Spacer(1, 10))

                breakdown_title = Table(
                    [[Paragraph("DETAILED MARKS BREAKDOWN", section_heading)]],
                    colWidths=[540],
                )
                breakdown_title.setStyle(
                    TableStyle([
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            colors.HexColor("#5A1818"),
                        ),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ])
                )
                story.append(breakdown_title)

                marks_rows = [
                    [
                        Paragraph("<b>Test Title</b>", section_heading),
                        Paragraph("<b>Date</b>", section_heading),
                        Paragraph("<b>Subject</b>", section_heading),
                        Paragraph("<b>Marks Obtained</b>", section_heading),
                        Paragraph("<b>Total Marks</b>", section_heading),
                    ]
                ]

                total_obt_all = 0.0
                total_tot_all = 0.0

                for r in selected_records:
                    _, _, _, t_sub, t_name, obt, tot, t_date = r
                    total_obt_all += obt
                    total_tot_all += tot
                    
                    marks_rows.append([
                        Paragraph(t_name, cell_style),
                        Paragraph(str(t_date), cell_style),
                        Paragraph(str(t_sub), cell_style),
                        Paragraph(str(obt), cell_style),
                        Paragraph(str(tot), cell_style),
                    ])

                overall_pct = (
                    (total_obt_all / total_tot_all) * 100
                    if total_tot_all > 0
                    else 0.0
                )

                if overall_pct >= 80.0:
                    behaviour_text = "Excellent"
                elif overall_pct >= 45.0:
                    behaviour_text = "Good"
                else:
                    behaviour_text = "Poor"

                marks_rows.append([
                    Paragraph("<b>Overall Behaviour</b>", cell_bold),
                    "",
                    "",
                    Paragraph(f"<b>{behaviour_text}</b>", cell_center_bold),
                    "",
                ])

                marks_table = Table(marks_rows, colWidths=[150, 90, 100, 100, 100])
                marks_table.setStyle(
                    TableStyle([
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#7A2222"),
                        ),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (3, 0), (-1, -1), "CENTER"),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ("SPAN", (0, -1), (2, -1)),
                        ("SPAN", (3, -1), (4, -1)),
                        (
                            "BACKGROUND",
                            (0, -1),
                            (-1, -1),
                            colors.HexColor("#EFEFEF"),
                        ),
                    ])
                )
                story.append(marks_table)

                story.append(Spacer(1, 120))

                remarks_title = Paragraph(
                    "<b>TEACHER'S REMARKS</b>",
                    ParagraphStyle(
                        "RT",
                        parent=styles["Normal"],
                        fontName="Helvetica-Bold",
                        fontSize=10,
                        textColor=colors.HexColor("#111111"),
                    ),
                )
                remarks_text = Paragraph(
                    '"Excellent progress. Keep focusing on concepts for further'
                    ' improvement."',
                    ParagraphStyle(
                        "RText",
                        parent=styles["Normal"],
                        fontName="Helvetica-Oblique",
                        fontSize=9,
                        textColor=colors.HexColor("#333333"),
                    ),
                )

                remarks_table = Table(
                    [[remarks_title], [remarks_text]], colWidths=[540]
                )
                remarks_table.setStyle(
                    TableStyle([
                        ("TOPPADDING", (0, 0), (-1, -1), 2),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ])
                )
                story.append(remarks_table)
                story.append(Spacer(1, 20))

                # Signatures Section
                try:
                    sign_img = Image("azim_sign.png", width=110, height=45)
                except Exception:
                    sign_img = Paragraph("<b>Choudhary Asim Walyat</b>", cell_style)

                sig_data = [
                    [
                        Paragraph("____________________________", cell_style),
                        sign_img,
                    ],
                    [
                        Paragraph("<b>Parent's Signature</b>", cell_style),
                        Paragraph(
                            "<b>Principal / Teacher's Signature</b>", cell_style
                        ),
                    ],
                ]
                sig_table = Table(sig_data, colWidths=[270, 270])
                sig_table.setStyle(
                    TableStyle([
                        ("ALIGN", (0, 0), (0, -1), "CENTER"),
                        ("ALIGN", (1, 0), (1, -1), "LEFT"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (1, 0), (1, -1), 40),
                        ("TOPPADDING", (0, 0), (-1, -1), 2),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ])
                )
                story.append(sig_table)

                doc.build(story)
                with open(filename, "rb") as f:
                    return f.read()

            st.write("---")
            st.subheader(
                " Download Student Test Performance Report (Multi-Test Selection)"
            )

            student_dict = {}
            for r in test_records:
                s_name, s_roll = r[0], r[1]
                student_dict[s_roll] = s_name

            selected_roll = st.selectbox(
                "Select Student Roll Number",
                options=list(student_dict.keys()),
                format_func=lambda roll: f"{student_dict[roll]} (Roll: {roll})",
                key="test_pdf_roll_select",
            )

            if selected_roll:
                # Fetch student's enrolled subjects from database
                conn_sub = get_db_connection()
                cur_sub = conn_sub.cursor()
                cur_sub.execute("SELECT subjects FROM students WHERE roll_no = %s", (selected_roll,))
                sub_row = cur_sub.fetchone()
                cur_sub.close()
                conn_sub.close()

                student_enrolled_subjects = []
                if sub_row and sub_row[0]:
                    student_enrolled_subjects = [s.strip() for s in sub_row[0].split(",") if s.strip()]

                # Subject selection box right below roll number selection
                selected_test_subjects = st.multiselect(
                    "Select Subject(s) for Test Report",
                    options=student_enrolled_subjects,
                    default=student_enrolled_subjects,
                    key="test_pdf_subject_multiselect"
                )

                # Filter student tests based on selected roll no and selected subjects
                student_tests = [
                    r for r in test_records 
                    if r[1] == selected_roll and (not selected_test_subjects or r[3] in selected_test_subjects)
                ]

                if not student_tests:
                    st.warning("No test records found for the selected student and subject(s).")
                else:
                    st.info(
                        f"This student has a total of **{len(student_tests)}**"
                        " test(s) matching your selection. Which tests would you like to include in the PDF file?"
                    )

                    selected_tests_indices = []

                    with st.form("select_tests_form"):
                        for idx, test in enumerate(student_tests):
                            test_label = (
                                f"Subject: **{test[3]}** | Test: **{test[4]}** |"
                                f" Marks: {test[5]}/{test[6]} | Date: {test[7]}"
                            )
                            is_checked = st.checkbox(
                                test_label, value=True, key=f"test_chk_{idx}"
                            )
                            if is_checked:
                                selected_tests_indices.append(idx)

                        generate_btn = st.form_submit_button("Generate Report Data")

                    if generate_btn:
                        if not selected_tests_indices:
                            st.warning(
                                "Please select at least one test to generate the"
                                " PDF report!"
                            )
                        else:
                            st.session_state["selected_tests_indices"] = (
                                selected_tests_indices
                            )
                            st.session_state["selected_roll"] = selected_roll
                            st.success("Report data generated successfully!")

                    if (
                        "selected_tests_indices" in st.session_state
                        and st.session_state.get("selected_roll") == selected_roll
                    ):
                        chosen_records = [
                            student_tests[i]
                            for i in st.session_state["selected_tests_indices"]
                        ]
                        pdf_data = generate_aims_report_pdf(chosen_records)
                        st.download_button(
                            label=" Click here to download PDF",
                            data=pdf_data,
                            file_name=f"AIMS_Report_{selected_roll}.pdf",
                            mime="application/pdf",
                        )
        else:
            st.info("No test records found.")
