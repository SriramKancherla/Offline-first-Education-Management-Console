from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import mysql.connector
import jwt
from datetime import datetime, timedelta
from fastapi.openapi.utils import get_openapi


SECRET_KEY = "your_super_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI(title="Shiksa Sahayak Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


def get_db():
    return mysql.connector.connect(
        host="localhost",
        port=3316,
        user="root",
        password="",
        database="shiksha"
    )


class Student(BaseModel):
    name: str
    password: str
    rollno: int
    dob: str

class Teacher(BaseModel):
    Name: str
    TID: int
    DOB: str
    Subject: str
    password: str


class Worksheet(BaseModel):
    name: str
    wid: int
    questions: str
    tid: int

class DeleteWorksheet(BaseModel):
    wid: int

class AssessmentBulk(BaseModel):
    aid: int
    tid: int
    questions: str
    marks: int
    start_sid: int
    end_sid: int

class BulkDeleteAssessments(BaseModel):
    aids: List[int]

class UpdateMarks(BaseModel):
    aid: int
    sid: int
    marks: int
class CreateClass(BaseModel):
    name: str
    tid: int
    start_sid: int
    end_sid: int
    time: str
class LoginData(BaseModel):
    name: str
    password: str



def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return verify_token(token)


@app.get("/")
def home():
    return {"message": "Welcome to Shiksa Sahayak Server"}


@app.post("/admin/addStudent")
def add_student(student: Student, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO students (name, password, rollno, dob) VALUES (%s,%s,%s,%s)",
        (student.name, student.password, student.rollno, student.dob)
    )
    db.commit()
    cursor.close()
    return {"message": f"Student {student.name} added successfully"}

@app.post("/admin/addTeachers")
def add_teacher(teacher: Teacher):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO teachers (Name, TID, DOB, Subject, password) VALUES (%s, %s, %s, %s, %s)",
        (teacher.Name, teacher.TID, teacher.DOB, teacher.Subject, teacher.password)
    )
    db.commit()
    cursor.close()
    return {"message": f"Teacher {teacher.Name} added successfully"}


@app.post("/login/student")
def login_student(data: LoginData):
    name = data.name
    password = data.password
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE name=%s AND password=%s", (name, password))
    user = cursor.fetchone()
    cursor.close()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"role": "student", "sid": user["rollno"], "name": user["name"]})
    return {"access_token": token}

@app.post("/login/teacher")
def login_teacher(data: LoginData):
    name = data.name
    password = data.password
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teachers WHERE Name=%s AND password=%s", (name, password))
    user = cursor.fetchone()
    cursor.close()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"role": "teacher", "tid": user["tid"], "name": user["name"]})
    return {"access_token": token}




@app.get("/student/getall")
def get_students(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    result = cursor.fetchall()
    cursor.close()
    return {"students": result}

@app.get("/teachers/getall")
def get_teachers(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teachers")
    result = cursor.fetchall()
    cursor.close()
    return {"teachers": result}

@app.get("/worksheets/{teacherid}")
def get_worksheets(teacherid: int, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM worksheets WHERE TID=%s", (teacherid,))
    result = cursor.fetchall()
    cursor.close()
    return {"worksheets": result}

@app.post("/teachers/createworksheet")
def create_worksheet(data: Worksheet, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
    "INSERT INTO worksheets (name, wid, questions, tid) VALUES (%s,%s,%s,%s)",
    (data.name, data.wid, data.questions, data.tid)
)

    db.commit()
    cursor.close()
    return {"message": "Worksheet created successfully"}

@app.delete("/worksheets/delete")
def delete_worksheet(data: DeleteWorksheet, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM worksheets WHERE wid=%s", (data.wid,))
    db.commit()
    cursor.close()
    return {"message": f"Deleted worksheet with WID {data.wid}"}


@app.post("/assessments/bulkcreate")
def bulk_create_assessments(data: AssessmentBulk, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    values = [
        (f"Student {sid}", sid, data.tid, data.questions, data.marks, data.aid)
        for sid in range(data.start_sid, data.end_sid + 1)
    ]
    cursor.executemany(
        "INSERT INTO assessments (Name, SID, TID, Questions, marks, AID) VALUES (%s,%s,%s,%s,%s,%s)",
        values
    )
    db.commit()
    cursor.close()
    return {"message": "Assessments created successfully"}

@app.get("/assesmentforstud/{sid}")
def get_assessments_by_student(sid: int, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM assessments WHERE SID=%s", (sid,))
    result = cursor.fetchall()
    cursor.close()
    return {"assessments": result}

@app.get("/assessmentbyteacher/{tid}")
def get_assessments_by_teacher(tid: int, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM assessments WHERE TID=%s", (tid,))
    result = cursor.fetchall()
    cursor.close()
    return {"assessments": result}

@app.put("/assessments/updatemarks")
def update_marks(data: UpdateMarks, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE assessments SET marks=%s WHERE AID=%s AND SID=%s",
        (data.marks, data.aid, data.sid)
    )
    db.commit()
    cursor.close()
    return {"message": f"Updated marks for AID {data.aid}, SID {data.sid}"}

@app.delete("/assessments/bulkdelete")
def bulk_delete_assessments(data: BulkDeleteAssessments, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM assessments WHERE AID IN (%s)" % ','.join(['%s']*len(data.aids)),
        tuple(data.aids)
    )
    db.commit()
    cursor.close()
    return {"message": f"Deleted assessments with AIDs {data.aids}"}


@app.get("/getclassbytid/{tid}")
def get_class_by_tid(tid: int, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM class WHERE TID=%s", (tid,))
    result = cursor.fetchall()
    cursor.close()
    return {"classes": result}

@app.get("/getclassbysid/{sid}")
def get_class_by_sid(sid: int, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM class WHERE SID=%s", (sid,))
    result = cursor.fetchall()
    cursor.close()
    return {"classes": result}
@app.post("/class/create")
def create_class(data: CreateClass, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()

    num_students = data.end_sid - data.start_sid + 1
    values = [
        (data.name, data.tid, num_students, data.time, sid)
        for sid in range(data.start_sid, data.end_sid + 1)
    ]

    cursor.executemany(
        "INSERT INTO class (`name`, tid, `no_of_studs`, `time`, SID) VALUES (%s, %s, %s, %s, %s)",
        values
    )
    
    db.commit()
    cursor.close()
    return {"message": f"Class '{data.name}' created for SIDs {data.start_sid}-{data.end_sid} with TID {data.tid}"}
@app.get("/class/bysid/{sid}")
def get_classes_by_sid(sid: int, user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM class WHERE SID=%s", (sid,))
    classes = cursor.fetchall()
    cursor.close()
    return {"classes": classes}
@app.get("/classes/all")
def get_all_classes(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM class")
    result = cursor.fetchall()
    cursor.close()
    return {"classes": result}



def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Shiksa Sahayak Server",
        version="1.0",
        description="API with JWT auth for students and teachers",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method in ["get","post","put","delete"]:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi