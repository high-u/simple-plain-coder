"""
LLMクライアント関連のモジュール

このモジュールは、LLMクライアントの初期化と実行など、副作用を持つ操作を提供します。
"""
from typing import Dict, Any, List, Optional, Tuple, Generator
from qwen_agent.agents import Assistant
import config_io
import llm_core
import logging
import os

def initialize_llm_client() -> Assistant:
    """現在のアクティブなcoderに基づいてLLMクライアントを初期化する
    
    Returns:
        初期化されたAssistantインスタンス
    """
    # 設定ファイルからLLM設定を読み込む
    llm_config = config_io.get_llm_config()
    model_name = llm_config.get('model_name')
    if not model_name:
        raise ValueError("Model name is not configured. Please check your config file.")
    
    # LLM設定を準備
    llm_cfg = llm_core.prepare_llm_config(llm_config)
    
    # MCP対応ツール設定
    # YAMLファイルからMCPサーバー設定を読み込む
    mcp_config = config_io.load_mcp_servers()
    
    # MCPサーバー設定からツールリストを準備
    tools = llm_core.prepare_mcp_tools(mcp_config)
    
    # Assistant作成して返す
    return Assistant(llm=llm_cfg, function_list=tools)

def run_llm(bot: Assistant, messages: List[Dict[str, Any]]) -> Generator[str, None, None]:
    """LLMを実行し、レスポンスを生成する
    
    Args:
        bot: Assistantインスタンス
        messages: メッセージ履歴
        
    Yields:
        生成されたレスポンステキスト
    """
    response_text = ""
    for response in bot.run(messages=messages):
        if response and len(response) > 0:
            content = response[-1].get('content', '')
            if content and content != response_text:
                yield content[len(response_text):]
                response_text = content
    
    return response

def suppress_loggers() -> None:
    """ノイズの多いロガーを抑制する"""
    # ロギングシステムの設定
    logging.basicConfig(level=logging.CRITICAL, force=True)
    
    # ノイズの多いロガーを制御
    noisy_loggers = ['', 'mcp_manager', 'qwen_agent', 'qwen_agent_logger', 'stdio_client']
    
    # すべてのノイズの多いロガーを抑制
    for logger_name in noisy_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.CRITICAL)
        # 既存のハンドラーを削除
        if logger.handlers:
            for handler in logger.handlers:
                logger.removeHandler(handler)
        # 親ロガーへの伝播を停止
        logger.propagate = False
