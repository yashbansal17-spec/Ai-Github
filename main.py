from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import git
import os
import json

from analyzer import analyze_project
from visualizer import create_language_chart
from code_search import search_repo

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/charts", StaticFiles(directory="."), name="charts")

BASE_DIR = "repos"
CACHE = {}

os.makedirs(BASE_DIR, exist_ok=True)

# -------------------------
# HOME
# -------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------------
# CLONE (SAFE + FAST)
# -------------------------
def clone_repo(repo_url):
    repo_name = repo_url.rstrip("/").split("/")[-1]
    repo_path = os.path.join(BASE_DIR, repo_name)

    # ✅ reuse existing repo (prevents permission errors)
    if os.path.exists(repo_path):
        return repo_path

    try:
        git.Repo.clone_from(
            repo_url,
            repo_path,
            depth=1,
            single_branch=True
        )
        return repo_path
    except Exception as e:
        print("Clone Error:", e)
        return None

# -------------------------
# ANALYZE
# -------------------------
@app.post("/analyze")
def analyze_repo(repo_url: str = Form(...)):

    if repo_url in CACHE:
        return CACHE[repo_url]

    repo_path = clone_repo(repo_url)

    if not repo_path:
        return {"error": "Failed to clone repository."}

    result = analyze_project(repo_path, repo_url)

    chart = create_language_chart(result["language_percentages"])
    result["language_chart"] = chart

    CACHE[repo_url] = result

    return result

# -------------------------
# SEARCH
# -------------------------
@app.post("/search")
def search_code(repo_url: str = Form(...), query: str = Form(...)):

    repo_name = repo_url.rstrip("/").split("/")[-1]
    repo_path = os.path.join(BASE_DIR, repo_name)

    if not os.path.exists(repo_path):
        return {"error": "Analyze repository first."}

    results = search_repo(repo_path, query)

    return {"results": results[:20]}

# -------------------------
# DOWNLOAD
# -------------------------
@app.get("/download")
def download_report(repo_url: str):

    if repo_url not in CACHE:
        return {"error": "Analyze repository first."}

    result = CACHE[repo_url]

    repo_name = repo_url.rstrip("/").split("/")[-1]
    filename = f"{repo_name}_analysis.json"

    with open(filename, "w") as f:
        json.dump(result, f, indent=4)

    return FileResponse(filename, media_type="application/json", filename=filename)

# -------------------------
# Q&A LOGIC
# -------------------------
def build_context(data):
    text = f"{data.get('summary')} {data.get('framework')} {data.get('project_type')}"
    text += " ".join(data.get("insights", []))
    text += " ".join(data.get("language_percentages", {}).keys())
    return text.lower()

def is_related(question, context):
    keywords = ["framework", "language", "files", "folders", "lines", "project", "summary", "purpose"]

    q = question.lower()

    for word in keywords:
        if word in q:
            return True

    return True  # 🔥 allow most questions (better UX)

def generate_answer(question, data):
    q = question.lower()
    stats = data["repo_stats"]

    if "framework" in q:
        return f"Framework: {data['framework']}"
    if "language" in q:
        return f"Languages: {', '.join(data['language_percentages'].keys())}"
    if "files" in q:
        return f"{stats['total_files']} files"
    if "folders" in q:
        return f"{stats['total_folders']} folders"
    if "lines" in q or "size" in q:
        return f"{stats['total_lines']} lines of code"
    if "what" in q or "purpose" in q or "about" in q:
        return data["summary"]

    return data["summary"]

# -------------------------
# ASK
# -------------------------
@app.post("/ask")
def ask(repo_url: str = Form(...), question: str = Form(...)):

    if repo_url not in CACHE:
        return {
            "question": question,
            "answer": "Please analyze the repository first."
        }

    data = CACHE[repo_url]

    return {
        "question": question,
        "answer": generate_answer(question, data)
    }
