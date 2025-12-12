import requests
import json
import os
import yaml
from typing import Dict, Any, Optional

class ModelManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.ollama_base_url = self.config.get("ollama", {}).get("base_url", "http://localhost:11434")
        
    def _load_config(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def get_model_config(self, role: str) -> Dict[str, Any]:
        return self.config.get("agent_models", {}).get(role, {})

    def load_model(self, role: str):
        """
        Prepares the model. For Ollama, we could trigger a preload, 
        but usually it loads on demand.
        For now, this is a placeholder for any setup logic.
        """
        model_cfg = self.get_model_config(role)
        print(f"Loading model for role: {role} ({model_cfg.get('model')})")
        # Could add specific logic here if needed

    def unload_model(self, role: str):
        """
        Unloads the model to free resources.
        Critical for Local models on limited RAM.
        """
        model_cfg = self.get_model_config(role)
        provider = model_cfg.get("provider")
        model_name = model_cfg.get("model")

        if provider == "ollama":
            print(f"Unloading Ollama model: {model_name}")
            try:
                # Force unload by setting keep_alive to 0
                response = requests.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": model_name,
                        "keep_alive": 0
                    }
                )
                if response.status_code == 200:
                    print("Successfully unloaded model.")
                else:
                    print(f"Failed to unload model: {response.text}")
            except Exception as e:
                print(f"Error unloading model: {e}")
        elif provider == "ollama-cloud":
            # Cloud models don't need explicit unloading (managed by cloud)
            print(f"Cloud model {model_name} does not require explicit unload.")
        else:
            print(f"No explicit unload needed for provider: {provider}")

    def generate_response(self, role: str, prompt: str, system_prompt: str = "") -> str:
        model_cfg = self.get_model_config(role)
        provider = model_cfg.get("provider")
        model = model_cfg.get("model")
        temperature = model_cfg.get("temperature", 0.7)

        if provider == "ollama":
            return self._call_ollama(model, prompt, system_prompt, temperature)
        elif provider == "ollama-cloud":
            return self._call_ollama_cloud(model, prompt, system_prompt, temperature)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _call_ollama(self, model: str, prompt: str, system_prompt: str, temperature: float) -> str:
        """Call local Ollama instance."""
        url = f"{self.ollama_base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception as e:
            print(f"Ollama inference error: {e}")
            return ""

    def _call_ollama_cloud(self, model: str, prompt: str, system_prompt: str, temperature: float) -> str:
        """
        Call Ollama Cloud instance.
        Cloud models like 'gpt-oss:120b-cloud', 'deepseek-v3.1:671b-cloud' are accessed
        via a separate Ollama cloud endpoint.
        """
        # Get cloud URL from config, fallback to environment variable or default
        cloud_url = self.config.get("ollama", {}).get("cloud_url", os.getenv("OLLAMA_CLOUD_URL", "http://localhost:11434"))
        
        url = f"{cloud_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception as e:
            print(f"Ollama Cloud inference error: {e}")
            return ""
