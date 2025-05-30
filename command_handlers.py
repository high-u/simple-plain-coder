"""
コマンドハンドラーモジュール

このモジュールは、各コマンドの実際の処理を行うハンドラー関数を提供します。
これらの関数は副作用（出力、状態変更など）を持ちます。
"""
from typing import Dict, List, Tuple, Any, Optional, Callable
import config_io
from prompt_io import select_from_list, fuzzy_select_from_list
import command_core

# コマンドハンドラーの型定義
CommandHandler = Callable[[str, Dict[str, Any]], bool]

# コマンドレジストリ
_commands: Dict[str, CommandHandler] = {}
_descriptions: Dict[str, str] = {}

def register_command(command: str, handler: CommandHandler, description: str = "") -> None:
    """コマンドを登録する
    
    Args:
        command: コマンド名（先頭の/は含む）
        handler: コマンドハンドラー関数
        description: コマンドの説明
    """
    _commands[command] = handler
    _descriptions[command] = description

def handle_command(user_input: str, context: Dict[str, Any]) -> bool:
    """ユーザー入力をコマンドとして処理する
    
    Args:
        user_input: ユーザー入力
        context: コマンド実行コンテキスト（状態や依存オブジェクトを含む辞書）
            
    Returns:
        コマンドが処理された場合はTrue、そうでない場合はFalse
    """
    # コマンドかどうかをチェック
    if not command_core.is_command(user_input):
        return False
    
    # コマンドと引数を解析
    command, args = command_core.parse_command(user_input)
    
    # コマンドが登録されているかチェック
    handler = command_core.match_command(command, _commands)
    if handler:
        # コマンドハンドラーを呼び出し
        return handler(args, context)
    
    # 登録されていないコマンドの場合
    print(f"Unknown command: {command}")
    return True

def get_commands() -> List[Tuple[str, str]]:
    """登録されているコマンドとその説明のタプルリストを取得する
    
    Returns:
        コマンドと説明のタプルリスト [(コマンド名, 説明)]
    """
    return command_core.prepare_command_list(_descriptions)

def get_command_descriptions() -> Dict[str, str]:
    """登録されているコマンドとその説明の辞書を取得する
    
    Returns:
        コマンドとその説明の辞書
    """
    return _descriptions.copy()

# 標準コマンドの実装
def handle_bye_command(args: str, context: Dict[str, Any]) -> bool:
    """byeコマンドのハンドラー
    
    Args:
        args: コマンド引数
        context: コンテキスト辞書
        
    Returns:
        常にTrue
    """
    if 'exit_flag' in context:
        context['exit_flag'] = True
    print("Goodbye!")
    return True

def handle_help_command(args: str, context: Dict[str, Any]) -> bool:
    """helpコマンドのハンドラー
    
    Args:
        args: コマンド引数
        context: コンテキスト辞書
        
    Returns:
        常にTrue
    """
    help_text = command_core.format_command_help(_descriptions)
    print(help_text.replace('\\n', '\n'))
    return True

def handle_list_command(args: str, context: Dict[str, Any]) -> bool:
    """listコマンドのハンドラー - 利用可能なcoderを表示し選択する
    
    Args:
        args: コマンド引数
        context: コンテキスト辞書
        
    Returns:
        常にTrue
    """
    # 利用可能なcoderを取得
    coders = config_io.get_available_coders()
    
    if not coders:
        print("No coders found in config file.")
        return True
    
    # 現在のアクティブなcoderを取得
    current_coder_id = config_io.get_active_coder_id()
    
    # 現在のcoder情報を表示
    current_coder_name = next((name for key, name in coders if key == current_coder_id), current_coder_id)
    print(f"Current coder: {current_coder_name}")
    
    # ファジー検索を使用したcoder選択を表示
    selected = fuzzy_select_from_list(
        "Select coder", 
        coders,
        default_value=current_coder_id
    )
    
    if selected is None:
        print("Coder selection cancelled.")
        return True
    
    # 選択されたcoderを設定
    if selected != current_coder_id:
        config_io.set_active_coder_id(selected)
        coder_name = next((name for key, name in coders if key == selected), selected)
        print(f"Coder changed to: {coder_name}")
        
        # ボットを再初期化する
        if 'bot' in context:
            # main.pyのinitialize_llm_client関数を呼び出す
            # この部分は後でmain.pyをリファクタリングする際に修正
            from main import initialize_llm_client
            context['bot'] = initialize_llm_client()
            print(f"Coder changed to: {coder_name}")
    else:
        coder_name = next((name for key, name in coders if key == selected), selected)
        print(f"Coder unchanged: {coder_name}")
    
    return True

# 標準コマンドの登録
register_command('/bye', handle_bye_command, "アプリケーションを終了します")
register_command('/help', handle_help_command, "利用可能なコマンドを表示します")
register_command('/list', handle_list_command, "利用可能なプロファイルを表示して選択します")
