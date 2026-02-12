import streamlit as st
import requests

# ===== API ENDPOINTS =====
MAIN_API = "http://0.0.0.0:8000"
AI_API = "http://0.0.0.0:6000"

st.set_page_config(page_title="Shiksha Sahayak", layout="wide")

# ===== SESSION STATE =====
if "token" not in st.session_state:
    st.session_state.token = None

if "role" not in st.session_state:
    st.session_state.role = None

if "tid" not in st.session_state:
    st.session_state.tid = None

if "sid" not in st.session_state:
    st.session_state.sid = None


# ===== AUTH HELPERS =====
def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def login(role, name, password):
    endpoint = f"{MAIN_API}/login/{role}"
    res = requests.post(endpoint, json={"name": name, "password": password})

    if res.status_code == 200:
        data = res.json()

        st.session_state.token = data["access_token"]
        st.session_state.role = role

        st.success("Login Successful!")
        st.rerun()

    else:
        st.error("Invalid Credentials")


# ===== LANDING PAGE =====
def landing_page():
    st.title("📚 Shiksha Sahayak Platform")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Teacher Login")
        tname = st.text_input("Teacher Name")
        tpass = st.text_input("Password", type="password", key="tpass")

        if st.button("Login as Teacher"):
            login("teacher", tname, tpass)

    with col2:
        st.subheader("Student Login")
        sname = st.text_input("Student Name")
        spass = st.text_input("Password", type="password")

        if st.button("Login as Student"):
            login("student", sname, spass)


# ================== TEACHER PORTAL ===================
def teacher_portal():
    st.title("👩‍🏫 Teacher Portal")

    menu = st.sidebar.selectbox("Teacher Menu", [
        "View Students",
        "View Classes",
        "Create Class",
        "View Worksheets",
        "Add Worksheet",
        "Add Assessment",
        "View Assessments",
        "Update Marks",
        "Add Knowledge",
        "Worksheet Generator",
        "Assessment Generator",
        "Backup to Firebase"        # NEW OPTION ADDED
    ])

    if menu == "View Students":
        st.header("Students Database")

        res = requests.get(f"{MAIN_API}/student/getall", headers=auth_headers())
        if res.status_code == 200:
            st.table(res.json()["students"])
        else:
            st.error("Failed to fetch students")

    elif menu == "View Classes":
        st.header("Your Classes")

        tid = st.number_input("Enter Teacher ID", step=1)

        if st.button("Get Classes"):
            res = requests.get(f"{MAIN_API}/getclassbytid/{tid}", headers=auth_headers())
            if res.status_code == 200:
                st.table(res.json()["classes"])

    elif menu == "Create Class":
        st.header("Create Class")

        name = st.text_input("Class Name")
        tid = st.number_input("Teacher ID", step=1)
        start_sid = st.number_input("Start Student ID", step=1)
        end_sid = st.number_input("End Student ID", step=1)
        time = st.text_input("Time")

        if st.button("Create"):
            payload = {
                "name": name,
                "tid": tid,
                "start_sid": start_sid,
                "end_sid": end_sid,
                "time": time
            }

            res = requests.post(
                f"{MAIN_API}/class/create",
                json=payload,
                headers=auth_headers()
            )

            if res.status_code == 200:
                st.success("Class Created!")
            else:
                st.error(res.text)

    elif menu == "View Worksheets":
        st.header("Worksheets")

        tid = st.number_input("Teacher ID", step=1)

        if st.button("Load Worksheets"):
            res = requests.get(f"{MAIN_API}/worksheets/{tid}", headers=auth_headers())
            if res.status_code == 200:
                st.table(res.json()["worksheets"])

    elif menu == "Add Worksheet":
        st.header("Upload Worksheet")

        name = st.text_input("Worksheet Name")
        wid = st.number_input("Worksheet ID", step=1)
        questions = st.text_area("Questions")
        tid = st.number_input("Teacher ID", step=1, key="w_tid")

        if st.button("Upload Worksheet"):
            payload = {
                "name": name,
                "wid": wid,
                "questions": questions,
                "tid": tid
            }

            res = requests.post(
                f"{MAIN_API}/teachers/createworksheet",
                json=payload,
                headers=auth_headers()
            )

            if res.status_code == 200:
                st.success("Worksheet Uploaded!")
            else:
                st.error(res.text)

    elif menu == "Add Assessment":
        st.header("Create Assessments")

        aid = st.number_input("Assessment ID", step=1)
        tid = st.number_input("Teacher ID", step=1)
        questions = st.text_area("Questions")
        marks = st.number_input("Marks", step=1)
        start_sid = st.number_input("Start Student ID", step=1)
        end_sid = st.number_input("End Student ID", step=1)

        if st.button("Create Assessments"):
            payload = {
                "aid": aid,
                "tid": tid,
                "questions": questions,
                "marks": marks,
                "start_sid": start_sid,
                "end_sid": end_sid
            }

            res = requests.post(
                f"{MAIN_API}/assessments/bulkcreate",
                json=payload,
                headers=auth_headers()
            )

            if res.status_code == 200:
                st.success("Assessments Created!")
            else:
                st.error(res.text)

    elif menu == "View Assessments":
        st.header("Assessments by Teacher")

        tid = st.number_input("Teacher ID", step=1)

        if st.button("Load Assessments"):
            res = requests.get(
                f"{MAIN_API}/assessmentbyteacher/{tid}",
                headers=auth_headers()
            )

            if res.status_code == 200:
                st.table(res.json()["assessments"])

    elif menu == "Update Marks":
        st.header("Update Student Marks")

        aid = st.number_input("Assessment ID", step=1)
        sid = st.number_input("Student ID", step=1)
        marks = st.number_input("New Marks", step=1)

        if st.button("Update"):
            payload = {"aid": aid, "sid": sid, "marks": marks}

            res = requests.put(
                f"{MAIN_API}/assessments/updatemarks",
                json=payload,
                headers=auth_headers()
            )

            if res.status_code == 200:
                st.success("Marks Updated!")
            else:
                st.error(res.text)

    elif menu == "Add Knowledge":
        st.header("Upload Knowledge for AI")

        file = st.file_uploader("Upload Document")

        if file and st.button("Upload"):
            files = {"file": file}
            res = requests.post(f"{AI_API}/upload", files=files)

            if res.status_code == 200:
                st.success("Uploaded to AI!")

    elif menu == "Worksheet Generator":
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

        if st.button("Generate"):
            res = requests.post(
                f"{AI_API}/generate/worksheet",
                json={"difficulty": difficulty}
            )

            if res.status_code == 200:
                st.write(res.json()["worksheet"])

    elif menu == "Assessment Generator":
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

        if st.button("Generate"):
            res = requests.post(
                f"{AI_API}/generate/assessment",
                json={"difficulty": difficulty}
            )

            if res.status_code == 200:
                st.write(res.json()["assessment"])

    # ======= NEW FIREBASE BACKUP FEATURE =======
    elif menu == "Backup to Firebase":
        st.header("Backup Database to Firebase")

        st.write("This will push full MySQL backup to Firebase Firestore.")

        if st.button("Push Backup Now"):

            res = requests.post(
                f"{MAIN_API}/admin/backup-to-firebase",
                headers=auth_headers()
            )

            if res.status_code == 200:
                st.success("Backup Successfully Pushed to Firebase!")
            else:
                st.error(f"Backup Failed: {res.text}")


# ================== STUDENT PORTAL ===================
def student_portal():
    st.title("🎓 Student Portal")

    st.session_state.sid = st.sidebar.number_input("Your Student ID", step=1)

    menu = st.sidebar.selectbox("Student Menu", [
        "View My Classes",
        "View My Worksheets",
        "View My Assessments",
        "AI Chatbot"
    ])

    if menu == "View My Classes":
        if st.button("Load Classes"):
            res = requests.get(
                f"{MAIN_API}/getclassbysid/{st.session_state.sid}",
                headers=auth_headers()
            )
            if res.status_code == 200:
                st.table(res.json()["classes"])

    elif menu == "View My Worksheets":
        tid = st.number_input("Teacher ID", step=1)

        if st.button("Load Worksheets"):
            res = requests.get(
                f"{MAIN_API}/worksheets/{tid}",
                headers=auth_headers()
            )
            if res.status_code == 200:
                st.table(res.json()["worksheets"])

    elif menu == "View My Assessments":
        if st.button("Load Assessments"):
            res = requests.get(
                f"{MAIN_API}/assesmentforstud/{st.session_state.sid}",
                headers=auth_headers()
            )
            if res.status_code == 200:
                st.table(res.json()["assessments"])

    elif menu == "AI Chatbot":
        question = st.text_input("Ask AI")

        if st.button("Ask"):
            res = requests.post(f"{AI_API}/ask", json={"question": question})
            if res.status_code == 200:
                st.write(res.json()["answer"])


# ===== MAIN APP FLOW =====
if st.session_state.token is None:
    landing_page()
else:
    if st.session_state.role == "teacher":
        teacher_portal()
    else:
        student_portal()

    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.role = None
        st.session_state.tid = None
        st.session_state.sid = None
        st.rerun()
