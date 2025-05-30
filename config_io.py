"""
設定関連のI/O操作モジュール

このモジュールは、設定ファイルの読み込みや保存など、副作用を持つI/O操作を提供します。
"""
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import tomli
import tomli_w
import yaml
import os
import config_core

APP_NAME = "simple-plain-coder"
CODERS_FILENAME = "coders.toml"
MCP_SERVERS_FILENAME = "mcp-servers.yaml"

# カレントディレクトリの.simple-plain-coderディレクトリを使用
CONFIG_DIR = Path(".") / ".simple-plain-coder"
CODERS_PATH = CONFIG_DIR / CODERS_FILENAME
MCP_SERVERS_PATH = CONFIG_DIR / MCP_SERVERS_FILENAME

# 現在選択中のcoderのID
_current_coder_id = None

def ensure_config_dir() -> None:
    """設定ディレクトリが存在することを保証する"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_coders() -> Dict[str, Any]:
    """コーダー設定を読み込む
    
    Returns:
        コーダー設定辞書
    """
    if not CODERS_PATH.exists():
        return {}
    
    try:
        with open(CODERS_PATH, 'rb') as f:
            return tomli.load(f)
    except (tomli.TOMLDecodeError, OSError):
        return {}

def save_coders(coders: Dict[str, Any]) -> None:
    """コーダー設定を保存する
    
    Args:
        coders: 保存するコーダー設定辞書
    """
    ensure_config_dir()
    with open(CODERS_PATH, 'wb') as f:
        tomli_w.dump(coders, f)

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
    
    Returns:
        MCPサーバー設定辞書、ファイルが存在しない場合は空の辞書
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

def get_available_coders() -> List[Tuple[str, str]]:
    """設定ファイルから利用可能なコーダーのリストを取得する
    
    Returns:
        コーダーのリスト [(コーダーID, コーダー名)]
    """
    coders = load_coders()
    return config_core.extract_available_coders(coders)

def get_active_coder_id() -> str:
    """現在アクティブなコーダーIDを取得する
    
    Returns:
        アクティブなコーダーID（デフォルトは設定ファイルの最初のコーダー）
    """
    global _current_coder_id
    
    # 現在選択中のコーダーIDがあればそれを返す
    if _current_coder_id is not None:
        return _current_coder_id
    
    # 設定ファイルからコーダーリストを取得
    coders = load_coders()
    
    # コーダーが定義されていない場合は空文字列を返す
    if not coders:
        return ""
    
    # 最初のコーダーIDを取得して設定
    _current_coder_id = config_core.find_default_coder_id(coders)
    return _current_coder_id

def set_active_coder_id(coder_id: str) -> None:
    """アクティブなコーダーIDを設定する
    
    Args:
        coder_id: 設定するコーダーID
    """
    global _current_coder_id
    _current_coder_id = coder_id

def get_llm_config() -> Dict[str, Any]:
    """現在のコーダーの設定を取得する
    
    Returns:
        現在のコーダーのLLM設定
    """
    coders = load_coders()
    active_coder_id = get_active_coder_id()
    return coders.get(active_coder_id, {})
