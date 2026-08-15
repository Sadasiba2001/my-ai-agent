
import pytest

from my_ai_agent.tools import (
    ListFilesTool,
    ReadFileTool,
    RunPythonTool,
    ToolRegistry,
    WriteFileTool,
)


def test_tool_registry_registration():
    registry = ToolRegistry()
    schemas = registry.get_schemas()
    names = [s["function"]["name"] for s in schemas]

    assert "list_files" in names
    assert "read_file" in names
    assert "write_file" in names
    assert "run_python" in names


def test_duplicate_registration_raises():
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="already registered"):
        registry.register(ListFilesTool())


def test_unknown_tool_returns_error():
    registry = ToolRegistry()
    res = registry.execute("non_existent_tool", {})
    assert res.success is False
    assert res.error["type"] == "KeyError"


def test_filesystem_write_read_cycle(temp_dir, monkeypatch):
    # Patch WORKSPACE to use temp_dir for test safety
    monkeypatch.setattr("my_ai_agent.tools.filesystem.WORKSPACE", temp_dir)

    write_tool = WriteFileTool()
    read_tool = ReadFileTool()

    write_res = write_tool.execute({"path": "test.txt", "content": "Hello World!"})
    assert write_res.success is True

    read_res = read_tool.execute({"path": str(temp_dir / "test.txt")})
    assert read_res.success is True
    assert read_res.result == "Hello World!"


def test_write_outside_workspace_denied(temp_dir, monkeypatch):
    workspace = temp_dir / "workspace"
    workspace.mkdir()
    monkeypatch.setattr("my_ai_agent.tools.filesystem.WORKSPACE", workspace)

    write_tool = WriteFileTool()
    # Try relative path traversal outside workspace
    res = write_tool.execute({"path": "../outside.txt", "content": "Malicious"})
    assert res.success is False
    assert "Permission denied" in res.error["message"]


def test_python_tool_execution(temp_dir, monkeypatch):
    monkeypatch.setattr("my_ai_agent.tools.python.WORKSPACE", temp_dir)

    script_path = temp_dir / "hello.py"
    script_path.write_text("print('Hello from Python script!')")

    tool = RunPythonTool()
    res = tool.execute({"path": "hello.py"})

    assert res.success is True
    assert "Hello from Python script!" in res.result
    assert "EXIT CODE: 0" in res.result
