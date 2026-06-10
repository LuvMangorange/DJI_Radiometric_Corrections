"""
Descripition:
Author: Pengcheng_Hu
Date: 2025-12-17 19:40:49
LastEditor:
LastEditTime: 2025-12-17 19:40:50
"""

import json
import os
from typing import Any, Dict

import yaml


class ConfigLoader:

    @staticmethod
    def json(json_path: str) -> Dict[str, Any]:
        """Read JSON configuration file"""
        abs_path = os.path.abspath(json_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"JSON file does not exist: {abs_path}")
        with open(abs_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def yaml(yaml_path: str) -> Dict[str, Any]:
        """Read YAML configuration file"""
        abs_path = os.path.abspath(yaml_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"YAML file does not exist:{abs_path}")
        with open(abs_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def ini(ini_path: str) -> Dict[str, Any]:
        import configparser

        abs_path = os.path.abspath(ini_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"INI file does not exist:{abs_path}")
        config = configparser.ConfigParser()
        config.read(abs_path, encoding="utf-8")
        # Convert to dictionary
        return {section: dict(config[section]) for section in config.sections()}
