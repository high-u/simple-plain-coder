from qwen_agent.agents import Assistant
import config_utils
import commands
from prompt_utils import create_prompt_session, get_user_input
from typing import Dict, Any, List, Tuple, Optional
import logging
import os

# ログ出力を抹制する環境変数を設定
os.environ['QWEN_AGENT_LOG_LEVEL'] = 'CRITICAL'
os.environ['PYTHONUNBUFFERED'] = '1'

# ロギングシステムの設定
logging.basicConfig(level=logging.CRITICAL, force=True)

# ノイズの多いロガーを制御
noisy_loggers = ['', 'mcp_manager', 'qwen_agent', 'qwen_agent_logger', 'stdio_client']

# ロガーのレベルを設定する関数
def suppress_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.CRITICAL)
    # 既存のハンドラーを削除
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    # 親ロガーへの伝播を停止
    logger.propagate = False

# すべてのノイズの多いロガーを抹制
for logger_name in noisy_loggers:
    suppress_logger(logger_name)

def initialize_llm_client():
    """現在のアクティブなcoderに基づいてLLMクライアントを初期化する
    
    Returns:
        初期化されたAssistantインスタンス
    """
    
    # 設定ファイルからLLM設定を読み込む
    llm_config = config_utils.get_llm_config()
    model_name = llm_config.get('model_name')
    if not model_name:
        raise ValueError("Model name is not configured. Please check your config file.")
    
    # LLM基本設定
    llm_cfg = {
        'model': model_name,
        'model_server': llm_config.get('model_server', 'http://localhost:11434/v1'),
        'api_key': llm_config.get('api_key', 'EMPTY')
    }
    
    # 生成設定をオプションとして追加
    options = {}
    
    # 空でない値のみ追加
    for key in ['temperature', 'top_p', 'top_k', 'num_predict', 'max_tokens',
               'repeat_penalty', 'presence_penalty', 'frequency_penalty']:
        if key in llm_config and llm_config[key] != "":
            options[key] = llm_config[key]
    
    # システムプロンプトとテンプレートの処理
    system_prompt = llm_config.get('system_prompt')
    template = llm_config.get('template')
    
    # 設定値があれば直接使用
    if system_prompt:
        llm_cfg['system'] = system_prompt
    
    if template:
        llm_cfg['template'] = template
    
    # ストリーミング設定
    stream = llm_config.get('stream', True)
    
    # オプションが空でなければ追加
    if options:
        llm_cfg['options'] = options
    
    # MCP対応ツール設定
    # YAMLファイルからMCPサーバー設定を読み込む
    mcp_config = config_utils.load_mcp_servers()
    
    # MCPサーバー設定がある場合はそれを使用
    if mcp_config and 'mcpServers' in mcp_config:
        tools = [mcp_config]
    else:
        # MCPサーバー設定がない場合は空のツールリストを使用
        tools = []
    
    # Assistant作成して返す
    return Assistant(llm=llm_cfg, function_list=tools)

def main():
    """メイン関数
    """
    # ロガーを再設定して確実にログを抹制
    logging.getLogger().setLevel(logging.CRITICAL)
    logging.getLogger('mcp_manager').setLevel(logging.CRITICAL)
    logging.getLogger('qwen_agent').setLevel(logging.CRITICAL)
    logging.getLogger('stdio_client').setLevel(logging.CRITICAL)
    
    # 初期化時にLLMクライアントを作成
    bot = initialize_llm_client()
    
    # 会話履歴
    messages = []
    
    # コンテキスト辞書（コマンド間で共有する状態）
    context: Dict[str, Any] = {
        'exit_flag': False,
        'bot': bot,
        'messages': messages
    }
    
    # 利用可能なcoderを取得
    coders = config_utils.get_available_coders()
    
    # プロンプトセッションの作成
    session = create_prompt_session(commands.get_commands(), coders)
    
    # メインループ
    while not context['exit_flag']:
        # 現在のcoder名を取得
        current_coder_id = config_utils.get_active_coder_id()
        coder_name = next((name for key, name in coders if key == current_coder_id), current_coder_id)
        
        # ユーザー入力を取得
        user_input = get_user_input(session, profile_name=coder_name)
        
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
                    config_utils.set_active_coder_id(selected_key)
                    print(f"Changing coder to: {coder_input}...")
                    
                    # LLMクライアントを即時再初期化
                    context['bot'] = initialize_llm_client()
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
        if commands.handle_command(user_input, context):
            continue
        
        # 通常の会話処理
        messages.append({'role': 'user', 'content': user_input})
        
        # レスポンスの処理
        response_text = ""
        for response in bot.run(messages=messages):
            if response and len(response) > 0:
                content = response[-1].get('content', '')
                if content and content != response_text:
                    print(content[len(response_text):], end="", flush=True)
                    response_text = content
        print()
        
        messages.extend(response)

if __name__ == "__main__":
    main()
