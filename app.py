"""
アプリケーションのメインモジュール

このモジュールは、アプリケーションのメインループと全体的な制御フローを提供します。
"""
from typing import Dict, Any, List, Optional
import os
import logging
import config_io
import command_handlers
import prompt_io
import llm_client
import llm_core

def setup_environment() -> None:
    """環境設定を行う"""
    # ログ出力を抑制する環境変数を設定
    os.environ['QWEN_AGENT_LOG_LEVEL'] = 'CRITICAL'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # ロガーを抑制
    llm_client.suppress_loggers()

def run_application() -> None:
    """アプリケーションのメインループを実行する"""
    # 環境設定
    setup_environment()
    
    # ロガーを再設定して確実にログを抑制
    logging.getLogger().setLevel(logging.CRITICAL)
    logging.getLogger('mcp_manager').setLevel(logging.CRITICAL)
    logging.getLogger('qwen_agent').setLevel(logging.CRITICAL)
    logging.getLogger('stdio_client').setLevel(logging.CRITICAL)
    
    # 初期化時にLLMクライアントを作成
    bot = llm_client.initialize_llm_client()
    
    # 会話履歴
    messages = []
    
    # コンテキスト辞書（コマンド間で共有する状態）
    context: Dict[str, Any] = {
        'exit_flag': False,
        'bot': bot,
        'messages': messages
    }
    
    # 利用可能なcoderを取得
    coders = config_io.get_available_coders()
    
    # プロンプトセッションの作成
    session = prompt_io.create_prompt_session(command_handlers.get_commands(), coders)
    
    # メインループ
    while not context['exit_flag']:
        # 現在のcoder名を取得
        current_coder_id = config_io.get_active_coder_id()
        coder_name = next((name for key, name in coders if key == current_coder_id), current_coder_id)
        
        # ユーザー入力を取得
        user_input = prompt_io.get_user_input(session, profile_name=coder_name)
        
        # 入力がない場合（Ctrl+C/Ctrl+Dなど）は終了
        if user_input is None:
            break
            
        # 空入力の場合はスキップ
        if not user_input:
            continue
            
        # @ で始まる入力はcoder選択として処理
        if user_input.startswith('@'):
            coder_input = user_input[1:].strip()  # @ を除去
            
            # 入力されたcoder名からcoder IDを探す
            selected_key = None
            for key, name in coders:
                if coder_input.lower() == name.lower():
                    selected_key = key
                    break
            
            # 一致するcoderが見つかった場合
            if selected_key:
                if selected_key != current_coder_id:
                    # coderを変更
                    config_io.set_active_coder_id(selected_key)
                    print(f"Changing coder to: {coder_input}...")
                    
                    # LLMクライアントを即時再初期化
                    context['bot'] = llm_client.initialize_llm_client()
                    bot = context['bot']  # ローカル変数も更新
                    print(f"Coder changed to: {coder_input}")
                else:
                    print(f"Already using coder: {coder_input}")
                continue
            else:
                print(f"Unknown coder: {coder_input}")
                continue
            
        # 従来の終了コマンドの処理
        if user_input.lower() in ['quit', 'exit']:
            break
            
        # コマンド処理
        if command_handlers.handle_command(user_input, context):
            continue
        
        # 通常の会話処理
        messages.append({'role': 'user', 'content': user_input})
        
        # レスポンスの処理
        response_text = ""
        for chunk in llm_client.run_llm(bot, messages):
            print(chunk, end="", flush=True)
            response_text += chunk
        print()
        
        # 最後のレスポンスを会話履歴に追加
        if response_text:
            messages.append({'role': 'assistant', 'content': response_text})

if __name__ == "__main__":
    run_application()
