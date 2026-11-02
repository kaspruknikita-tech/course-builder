#!/usr/bin/env python3
"""Создаёт папку курса из шаблонов course-builder.

Пример:
    python3 scaffold.py ~/courses/ux-research --title "UX-исследования" --lang ru

Существующую папку курса не трогает. Записывает курс в реестр
~/.course-builder/courses.md.
"""
import argparse
import datetime
import pathlib
import sys

TEMPLATES = pathlib.Path(__file__).resolve().parent.parent / "assets" / "templates"

SERVICE_FILES = [
    "build.md", "brief.md", "research.md", "sources.md", "program.md",
    "case.md", "case-hidden.md", "drills.md", "notebook.md",
    "state.md", "log.md", "queue.md", "retro.md",
]
ROOT_FILES = {"course-CLAUDE.md": "CLAUDE.md", "course-README.md": "README.md"}
FIELD_FILES = {"field-sources.md": "sources.md", "field-vocab.txt": "vocab.txt", "field-seeds.md": "seeds.md"}
DIRS = ["_course/keys", "_course/field/raw", "lessons", "work/data", "materials"]

REGISTRY = pathlib.Path.home() / ".course-builder" / "courses.md"
REGISTRY_HEADER = (
    "# Курсы course-builder\n\n"
    "| Курс | Папка | Создан |\n"
    "|---|---|---|\n"
)


def render(name, values):
    text = (TEMPLATES / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def register(title, course, today):
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    if not REGISTRY.exists():
        REGISTRY.write_text(REGISTRY_HEADER, encoding="utf-8")
    registry = REGISTRY.read_text(encoding="utf-8")
    if f"| {course} |" not in registry:
        with REGISTRY.open("a", encoding="utf-8") as f:
            f.write(f"| {title} | {course} | {today} |\n")


def main():
    parser = argparse.ArgumentParser(description="Создать папку курса course-builder")
    parser.add_argument("course_dir", help="папка курса, например ~/courses/ux-research")
    parser.add_argument("--title", required=True, help="название курса")
    parser.add_argument("--lang", default="ru", help="язык уроков, по умолчанию ru")
    args = parser.parse_args()

    if not TEMPLATES.is_dir():
        sys.exit(f"Нет шаблонов: {TEMPLATES}. Скилл установлен не целиком.")

    course = pathlib.Path(args.course_dir).expanduser().resolve()
    if (course / "_course").exists():
        sys.exit(f"Курс уже есть: {course}. Ничего не изменено.")

    today = datetime.date.today().isoformat()
    values = {"TITLE": args.title, "DATE": today, "LANG": args.lang, "PATH": str(course)}

    for d in DIRS:
        (course / d).mkdir(parents=True, exist_ok=True)
    for name in SERVICE_FILES:
        (course / "_course" / name).write_text(render(name, values), encoding="utf-8")
    for name, target in ROOT_FILES.items():
        (course / target).write_text(render(name, values), encoding="utf-8")
    for name, target in FIELD_FILES.items():
        (course / "_course" / "field" / target).write_text(render(name, values), encoding="utf-8")

    register(args.title, course, today)

    print(f"Курс создан: {course}")
    for path in sorted(course.rglob("*")):
        print("  " + str(path.relative_to(course)) + ("/" if path.is_dir() else ""))
    print(f"Реестр: {REGISTRY}")


if __name__ == "__main__":
    main()
