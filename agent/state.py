class AgentState:

    def __init__(self):
        self.task = ""
        self.iteration = 0
        self.tool_calls = 0
        self.completed = False
        self.history = []

    def reset(self, task: str):
        self.task = task
        self.iteration = 0
        self.tool_calls = 0
        self.completed = False
        self.history = []