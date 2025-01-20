from typing import Dict, Any, Optional
import os
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class ModelConfig:
    model_class: str
    model_id: str
    api_base: Optional[str] = None
    api_key: Optional[str] = None


class ConfigLoader:
    @staticmethod
    def load_model_configs(config_path: Path) -> Dict[str, ModelConfig]:
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path) as f:
            raw_configs = yaml.safe_load(f)
            
        configs = {}
        for model_name, config in raw_configs.get('models', {}).items():
            # Replace environment variables in api_key
            if 'api_key' in config:
                config['api_key'] = os.getenv(config['api_key'], config['api_key'])
                
            configs[model_name] = ModelConfig(**config)
            
        return configs