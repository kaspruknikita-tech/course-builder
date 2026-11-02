#!/usr/bin/env python3
"""Проверки скилла для CI: frontmatter, пути из SKILL.md и справочников, скрипты, сборка папки курса."""
import os
import pathlib
import py_compile
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
errors = []

skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
fm = skill.split("---")[1]
name = re.search(r"^name:\s*(.+)$", fm, re.M)
desc = re.search(r"^description:\s*(.+)$", fm, re.M)
if not name or name.group(1).strip() != "course-builder":
    errors.append("name в frontmatter не course-builder")
if not desc:
    errors.append("нет description")
elif len(desc.group(1).strip()) > 1024:
    errors.append(f"description длиннее 1024 символов: {len(desc.group(1).strip())}")

for doc in [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]:
    for path in set(re.findall(r"`((?:references|scripts|assets)/[^`\s]+)`", doc.read_text(encoding="utf-8"))):
        if not (ROOT / path.rstrip("/")).exists():
            errors.append(f"{doc.name}: нет файла {path}")

for script in sorted((ROOT / "scripts").glob("*.py")):
    try:
        py_compile.compile(str(script), doraise=True)
    except py_compile.PyCompileError as e:
        errors.append(f"{script.name}: {e}")

with tempfile.TemporaryDirectory() as home:
    course = pathlib.Path(home) / "courses" / "smoke"
    env = {**os.environ, "HOME": home}
    run = subprocess.run([sys.executable, str(ROOT / "scripts/scaffold.py"), str(course), "--title", "Проверка"],
                         env=env, capture_output=True, text=True)
    if run.returncode:
        errors.append(f"scaffold.py упал: {run.stderr.strip()}")
    else:
        for f in course.rglob("*"):
            if f.is_file() and "{{" in f.read_text(encoding="utf-8"):
                errors.append(f"незаполненный шаблон: {f.relative_to(course)}")
        for must in ["_course/state.md", "_course/field/sources.md", "_course/field/seeds.md", "CLAUDE.md"]:
            if not (course / must).exists():
                errors.append(f"scaffold не создал {must}")

if errors:
    print("Проверки не прошли:")
    for e in errors:
        print("  - " + e)
    sys.exit(1)
print("Все проверки прошли.")
