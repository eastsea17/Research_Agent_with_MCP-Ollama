import os
from core.model_manager import ModelManager

class BaseAgent:
    def __init__(self, model_manager: ModelManager, role: str):
        self.model_manager = model_manager
        self.role = role
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        model_cfg = self.model_manager.get_model_config(self.role)
        path = model_cfg.get("system_prompt_path")
        if path and os.path.exists(path):
            with open(path, 'r') as f:
                return f.read()
        return ""

    def generate(self, prompt: str) -> str:
        return self.model_manager.generate_response(self.role, prompt, self.system_prompt)
