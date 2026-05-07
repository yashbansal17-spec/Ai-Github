import os
from collections import defaultdict

SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", "dist", "build"}

# -------------------------------
# FRAMEWORK DETECTION (IMPROVED)
# -------------------------------
def detect_framework(path):

    detected = set()

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            file_path = os.path.join(root, file)

            try:
                if file == "requirements.txt":
                    content = open(file_path, errors="ignore").read().lower()
                    if "django" in content:
                        detected.add("Django")
                    if "flask" in content:
                        detected.add("Flask")
                    if "fastapi" in content:
                        detected.add("FastAPI")

                if file == "package.json":
                    content = open(file_path, errors="ignore").read().lower()
                    if "react" in content:
                        detected.add("React")
                    if "next" in content:
                        detected.add("Next.js")
                    if "vue" in content:
                        detected.add("Vue")
                    if "express" in content:
                        detected.add("Express")

                if file == "manage.py":
                    detected.add("Django")

            except:
                pass

    return ", ".join(detected) if detected else "Unknown"


# -------------------------------
# LANGUAGE DETECTION (BY LINES ✅)
# -------------------------------
def detect_languages(path):

    ext_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".cpp": "C++",
        ".c": "C",
        ".go": "Go",
        ".rb": "Ruby",
        ".php": "PHP",
        ".html": "HTML",
        ".css": "CSS"
    }

    counts = defaultdict(int)
    total_lines = 0

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for f in files:
            ext = os.path.splitext(f)[1]

            if ext in ext_map:
                file_path = os.path.join(root, f)

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                        line_count = sum(1 for _ in file)   # ⚡ FAST

                    counts[ext_map[ext]] += line_count
                    total_lines += line_count

                except:
                    pass

    return {k: round(v / total_lines * 100, 2) for k, v in counts.items()} if total_lines else {}


# -------------------------------
# STATS (FAST + CORRECT)
# -------------------------------
def calculate_stats(path):

    total_files = 0
    total_dirs = 0
    total_lines = 0

    for root, dirs, files in os.walk(path):

        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        total_dirs += len(dirs)

        for f in files:
            total_files += 1

            try:
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as file:
                    total_lines += sum(1 for _ in file)  # ⚡ FAST
            except:
                pass

    return {
        "total_files": total_files,
        "total_folders": total_dirs,
        "total_lines": total_lines
    }


# -------------------------------
# SMART SUMMARY (🔥 MAIN FIX)
# -------------------------------
def generate_summary(stats, languages, framework):

    if not stats:
        return "No data available."

    main_lang = max(languages, key=languages.get) if languages else "Unknown"

    size = (
        "large-scale"
        if stats["total_files"] > 1000
        else "medium-sized"
        if stats["total_files"] > 200
        else "small"
    )

    return f"""
This repository is a {framework} based project primarily written in {main_lang}.

It contains approximately {stats['total_files']} files across {stats['total_folders']} folders
with around {stats['total_lines']} lines of code.

Overall, it appears to be a {size} codebase.
""".strip()


# -------------------------------
# INSIGHTS (DYNAMIC)
# -------------------------------
def generate_insights(languages, stats):

    insights = []

    if languages:
        main = max(languages, key=languages.get)
        insights.append(f"Main language: {main}")

    if len(languages) > 3:
        insights.append("Multi-language project")

    if stats["total_files"] > 1000:
        insights.append("Large codebase")

    if stats["total_lines"] > 500000:
        insights.append("High complexity project")

    return insights


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def analyze_project(path, url):

    languages = detect_languages(path)
    stats = calculate_stats(path)
    framework = detect_framework(path)

    summary = generate_summary(stats, languages, framework)
    insights = generate_insights(languages, stats)

    return {
        "framework": framework,
        "project_type": "Software Project",
        "summary": summary,
        "insights": insights,
        "score": 85,
        "quality": "Good",
        "health": "Stable",
        "language_percentages": languages,
        "repo_stats": stats
    }