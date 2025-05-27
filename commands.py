"""
コマンド管理モジュール - 関数型アプローチ
"""
from typing import Dict, Callable, List, Tuple, Any
import config_utils
from prompt_utils import select_from_list, fuzzy_select_from_list

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
    # コマンドかどうかをチェック（/で始まるか）
    if not user_input.startswith('/'):
        return False
        
    # コマンド部分を取得（空白で区切られた最初の部分）
    parts = user_input.split(maxsplit=1)
    command = parts[0]
    
    # 引数部分を取得（ある場合）
    args = parts[1] if len(parts) > 1 else ""
    
    # コマンドが登録されているかチェック
    if command in _commands:
        # コマンドハンドラーを呼び出し
        return _commands[command](args, context)
        
    # 登録されていないコマンドの場合
    print(f"Unknown command: {command}")
    return True

def get_commands() -> List[Tuple[str, str]]:
    """登録されているコマンドとその説明のタプルリストを取得する
    
    Returns:
        コマンドと説明のタプルリスト [(コマンド名, 説明)]
    """
    return [(cmd, _descriptions.get(cmd, "")) for cmd in _commands.keys()]

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
    descriptions = get_command_descriptions()
    print("Available commands:")
    for cmd, desc in descriptions.items():
        print(f"  {cmd} - {desc}")
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
    coders = config_utils.get_available_coders()
    
    if not coders:
        print("No coders found in config file.")
        return True
    
    # 現在のアクティブなcoderを取得
    current_coder_id = config_utils.get_active_coder_id()
    
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
        config_utils.set_active_coder_id(selected)
        coder_name = next((name for key, name in coders if key == selected), selected)
        print(f"Coder changed to: {coder_name}")
        
        # ボットを再初期化する必要があることを通知
        if 'bot' in context:
            print("Please restart the application to apply the new coder.")
    else:
        coder_name = next((name for key, name in coders if key == selected), selected)
        print(f"Coder unchanged: {coder_name}")
    
    return True

# 標準コマンドの登録
register_command('/bye', handle_bye_command, "アプリケーションを終了します")
register_command('/help', handle_help_command, "利用可能なコマンドを表示します")
register_command('/list', handle_list_command, "利用可能なプロファイルを表示して選択します")
