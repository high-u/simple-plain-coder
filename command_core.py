"""
コマンド処理の純粋関数モジュール

このモジュールは、コマンドの解析、マッチング、検証などの純粋関数を提供します。
すべての関数は副作用を持たず、入力に基づいて結果を返します。
"""
from typing import Dict, List, Tuple, Any, Optional, Callable

# コマンドハンドラーの型定義
CommandHandler = Callable[[str, Dict[str, Any]], bool]

def parse_command(input_text: str) -> Tuple[str, str]:
    """ユーザー入力からコマンドと引数を解析する
    
    Args:
        input_text: ユーザー入力テキスト
        
    Returns:
        (command, args): コマンドと引数のタプル
        
    >>> parse_command('/help')
    ('/help', '')
    >>> parse_command('/list available')
    ('/list', 'available')
    >>> parse_command('not a command')
    ('', 'not a command')
    """
    if not input_text.startswith('/'):
        return ('', input_text)
        
    # コマンド部分を取得（空白で区切られた最初の部分）
    parts = input_text.split(maxsplit=1)
    command = parts[0]
    
    # 引数部分を取得（ある場合）
    args = parts[1] if len(parts) > 1 else ""
    
    return (command, args)

def is_command(input_text: str) -> bool:
    """入力テキストがコマンドかどうかを判定する
    
    Args:
        input_text: 判定するテキスト
        
    Returns:
        コマンドの場合はTrue、そうでない場合はFalse
        
    >>> is_command('/help')
    True
    >>> is_command('hello')
    False
    >>> is_command('')
    False
    """
    return input_text.startswith('/')

def match_command(command: str, registry: Dict[str, CommandHandler]) -> Optional[CommandHandler]:
    """コマンドをレジストリから検索する
    
    Args:
        command: 検索するコマンド
        registry: コマンドレジストリ
        
    Returns:
        コマンドハンドラー、見つからない場合はNone
        
    >>> def dummy_handler(args, context): return True
    >>> registry = {'/help': dummy_handler}
    >>> handler = match_command('/help', registry)
    >>> handler is not None
    True
    >>> match_command('/unknown', registry) is None
    True
    """
    return registry.get(command)

def format_command_help(commands: Dict[str, str]) -> str:
    """コマンドヘルプテキストをフォーマットする
    
    Args:
        commands: コマンドと説明の辞書
        
    Returns:
        フォーマットされたヘルプテキスト
        
    >>> help_text = format_command_help({'/help': 'ヘルプを表示', '/bye': '終了'})
    >>> print(help_text)
    Available commands:
      /help - ヘルプを表示
      /bye - 終了
    """
    lines = ["Available commands:"]
    for cmd, desc in commands.items():
        lines.append(f"  {cmd} - {desc}")
    return "\n".join(lines)

def prepare_command_list(commands: Dict[str, str]) -> List[Tuple[str, str]]:
    """コマンドリストをタプルリストに変換する
    
    Args:
        commands: コマンドと説明の辞書
        
    Returns:
        コマンドと説明のタプルリスト
        
    >>> prepare_command_list({'/help': 'ヘルプを表示', '/bye': '終了'})
    [('/help', 'ヘルプを表示'), ('/bye', '終了')]
    """
    return [(cmd, desc) for cmd, desc in commands.items()]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
