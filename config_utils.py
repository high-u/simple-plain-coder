from pathlib import Path
from typing import Optional, Dict, Any, List
import tomli
import tomli_w
import yaml
import json
import os

APP_NAME = "simple-plain-coder"
CONFIG_FILENAME = "config.toml"
MCP_SERVERS_FILENAME = "mcp-servers.yaml"

# カレントディレクトリの.simple-plain-coderディレクトリを使用
CONFIG_DIR = Path(".") / ".simple-plain-coder"
CONFIG_PATH = CONFIG_DIR / CONFIG_FILENAME
MCP_SERVERS_PATH = CONFIG_DIR / MCP_SERVERS_FILENAME

def ensure_config_dir() -> None:
    """設定ディレクトリが存在することを保証する"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> dict:
    """設定を読み込む"""
    if not CONFIG_PATH.exists():
        return {}
    
    try:
        with open(CONFIG_PATH, 'rb') as f:
            return tomli.load(f)
    except (tomli.TOMLDecodeError, OSError):
        return {}

def save_config(config: dict) -> None:
    """設定を保存する"""
    ensure_config_dir()
    with open(CONFIG_PATH, 'wb') as f:
        tomli_w.dump(config, f)

def get_model_name() -> Optional[str]:
    """設定ファイルからモデル名を取得する"""
    config = load_config()
    return config.get('llm', {}).get('model_name')

def get_llm_config() -> Dict[str, Any]:
    """LLMの設定を取得する"""
    config = load_config()
    return config.get('llm', {})

def load_file_content(file_path: str) -> str:
    """ファイルからテキストを読み込む
    
    Args:
        file_path: 読み込むファイルのパス
        
    Returns:
        ファイルの内容、ファイルが存在しない場合や読み込みに失敗した場合は空文字列("")  
    """
    if not file_path:
        return ""
        
    path = Path(file_path)
    if not path.is_absolute():
        # 相対パスの場合、カレントディレクトリからのパスとして解決
        path = Path(os.getcwd()) / path
        
    if not path.exists() or not path.is_file():
        return ""
        
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except OSError:
        return ""

def load_mcp_servers() -> Dict[str, Any]:
    """MCPサーバー設定をYAMLファイルから読み込み、JSON形式に変換する
    
    ファイルが存在しない場合は空の辞書を返す
    """
    if not MCP_SERVERS_PATH.exists():
        return {}
    
    try:
        with open(MCP_SERVERS_PATH, 'r', encoding='utf-8') as f:
            # YAMLをロードしてJSON形式に変換
            yaml_data = yaml.safe_load(f)
            if yaml_data is None:
                return {}
            return yaml_data
    except (yaml.YAMLError, OSError):
        return {}
