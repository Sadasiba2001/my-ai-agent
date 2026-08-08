from pathlib import Path


def list_files(path: str = ".") -> str:
    target = Path(path)

    if not target.exists():
        return f"Path does not exist: {path}"

    if not target.is_dir():
        return f"Path is not a directory: {path}"

    items = []

    for item in target.iterdir():
        if item.is_dir():
            items.append(f"[DIR]  {item.name}")
        else:
            items.append(f"[FILE] {item.name}")

    if not items:
        return "Directory is empty."

    return "\n".join(sorted(items))