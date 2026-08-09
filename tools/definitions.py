TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": (
                "List files and directories. "
                "Use this tool whenever the user asks "
                "about files, folders, directories, "
                "or project contents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Directory path to inspect. "
                            "Use '.' for the current directory."
                        )
                    }
                },
                "required": ["path"]
            }
        }
    },
    
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the contents of a text file. "
                "Use this tool when the user asks "
                "to read, inspect, analyze, or explain "
                "a file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Path of the text file to read."
                        )
                    }
                },
                "required": ["path"]
            }
        }
    },
    
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Create or overwrite a text file inside "
                "the workspace directory. "
                "Use this when the user asks you to create "
                "or write a file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "File path relative to workspace."
                        )
                    },
                    "content": {
                        "type": "string",
                        "description": (
                            "Complete content to write into the file."
                        )
                    }
                },
                "required": [
                    "path",
                    "content"
                ]
            }
        }
    },
    
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": (
                "Execute a Python script inside the workspace "
                "and return its output and errors. "
                "Use this tool when you need to test or execute "
                "a Python program."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Path of the Python script relative "
                            "to workspace."
                        )
                    }
                },
                "required": ["path"]
            }
        }
    }
]
