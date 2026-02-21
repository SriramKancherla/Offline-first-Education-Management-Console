<h1 align="center">📚 Offline-first Education Management Console</h1>
<p align="center">
<b>An offline-first, comprehensive education management platform built for teachers and students with local AI capabilities.</b>
<br>
<br>
<i>Combines traditional classroom management features with powerful, localized AI (RAG, Worksheet/Assessment generation) that runs independently of cloud infrastructure.</i>
</p>
<hr>

<h3>🚀 Features</h3>
<ul>
<li><b>Teacher Portal:</b> Manage classes, register students, view directories, upload worksheets, bulk create assessments, and update marks.</li>
<li><b>Student Portal:</b> Dashboard to view enrolled classes, assignments, scores, and an offline AI Chatbot for queries.</li>
<li><b>Local AI Engine (RAG):</b> Runs entirely offline using Hugging Face Transformers ('all-MiniLM-L6-v2') and local LLMs (Gemma), ensuring zero cloud dependence.</li>
<li><b>Smart Document Parsing:</b> Extract text cleanly from PDFs, Word documents, PowerPoints, and web links for a local knowledge base.</li>
<li><b>AI Generators:</b> Automatically generate worksheets and assessments based on difficulty levels.</li>
<li><b>Cloud Backup:</b> Push a full MySQL database snapshot to Firebase Firestore with a single click.</li>
</ul>

<h3>🛠️ Getting Started</h3>
<p>Clone the repository:</p>
<pre>
git clone https://github.com/SriramKancherla/Offline-first-Education-Management-Console.git
cd Offline-first-Education-Management-Console
</pre>

<p>Database Setup:</p>
<p>Create a MySQL database named <code>shiksha</code> and ensure the following tables exist: <code>students</code>, <code>teachers</code>, <code>class</code>, <code>worksheets</code>, <code>assessments</code>.</p>

<p>Install dependencies:</p>
<pre>
pip install -r requirements.txt
pip install fastapi uvicorn mysql-connector-python pyjwt firebase-admin
</pre>

<p>Run the Microservices (Simultaneously in different terminals):</p>
<p>1. Main Backend Server (Port 8000):</p>
<pre>
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
</pre>
<p>2. AI Server (Port 6000):</p>
<pre>
uvicorn ai_server:app --host 0.0.0.0 --port 6000 --reload
</pre>
<p>3. Streamlit Frontend:</p>
<pre>
cd frontend
streamlit run app.py
</pre>

<p>Open in browser: <a href="http://localhost:8501">http://localhost:8501</a></p>

<h3>� Tech Stack</h3>
<ul>
<li><b>Frontend:</b> Streamlit (Python)</li>
<li><b>Backend:</b> FastAPI (Python), JWT Authentication</li>
<li><b>AI Engine:</b> FAISS, SentenceTransformers, Hugging Face transformers, Local LLMs</li>
<li><b>Database:</b> MySQL Connect</li>
<li><b>Cloud Integration:</b> Firebase Admin SDK (Firestore)</li>
</ul>

<h3>📁 Folder Structure</h3>
<pre>
├── frontend/
│   └── app.py                 # Streamlit UI (Teacher & Student Portals)
├── backend/
│   ├── main.py                # Core FastAPI server (Auth, DB, Classes)
│   ├── ai_local_server.py     # Local equivalent of AI server
│   └── gemma_service_local.py # Local LLM interaction service
├── uploads/                   # Local file uploads for AI knowledge base
├── data/                      # Local JSON knowledge base storage
├── ai_server.py               # AI FastAPI server (RAG, Generation, Embeddings)
├── gemma_service.py           # Remote/Local LLM generation handling
├── requirements.txt           # Python dependencies
└── README.md                  # This documentation file
</pre>

<h3>🌐 Deployment</h3>
<p>The system is designed to run offline on local hardware or edge servers. Ensure Python 3.8+ and MySQL are installed on the local deployment machine.</p>

