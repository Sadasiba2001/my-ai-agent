from pathlib import Path

WORKSPACE = Path("workspace").resolve()

IGNORED_DIRECTORIES = {
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    "node_modules",
    ".env",
    ".env.example",
    ".gitignore",
}

'''
    Check if the path exists and is a directory
    then list files and directories in it
'''
def list_files(path: str = ".") -> str:
    """List files and directories recursively."""

    target = Path(path).resolve()

    if not target.exists():
        return f"Path does not exist: {path}"

    if not target.is_dir():
        return f"Path is not a directory: {path}"

    items = []

    for item in target.rglob("*"):
        
        if any(
            ignored in item.parts
            for ignored in IGNORED_DIRECTORIES
        ):
            continue

        relative = item.relative_to(target)

        if item.is_dir():
            items.append(f"[DIR]  {relative}")
        else:
            items.append(f"[FILE] {relative}")

    if not items:
        return "Directory is empty."

    return "\n".join(sorted(items))


'''
    Read the contents of a file and return it as a string
'''
def read_file(path: str) -> str:

    target = Path(path)

    if not target.exists():
        return f"File does not exist: {path}"

    if not target.is_file():
        return f"Path is not a file: {path}"

    try:
        return target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Cannot read binary file: {path}"
    except Exception as e:
        return f"Error reading file: {e}"

'''
    Write the contents to a file inside the workspace
'''
def write_file(path: str, content: str) -> str:

    target = (WORKSPACE / path).resolve()

    if WORKSPACE not in target.parents:
        return (
            "Permission denied. "
            "The agent can only write inside workspace/."
        )

    try:

        target.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        target.write_text(
            content,
            encoding="utf-8"
        )

        return f"File successfully written: {target}"

    except Exception as e:
        return f"Error writing file: {e}"
