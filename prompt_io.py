"""
プロンプト関連のI/O操作モジュール

このモジュールは、ユーザー入力の取得、表示、対話的な選択などの副作用を持つI/O操作を提供します。
"""
from typing import List, Optional, Callable, Tuple, Any, Dict
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter, Completer, Completion
from prompt_toolkit.shortcuts import radiolist_dialog, CompleteStyle
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
import prompt_core

class CoderCommandCompleter(Completer):
    """coder選択とコマンド入力のためのコンプリーター
    
    coder選択は '@' で始まり、コマンドは '/' で始まる
    """
    
    def __init__(self, commands: List[Tuple[str, str]], coders: List[Tuple[str, str]]):
        """初期化
        
        Args:
            commands: コマンドのリスト [(コマンド名, 説明)]
            coders: coderのリスト [(coder ID, coder名)]
        """
        self.commands = commands
        self.coders = coders
        
        # コマンドのコンプリーター
        self.command_completer = FuzzyCompleter(
            WordCompleter([cmd for cmd, _ in commands], sentence=True)
        )
        
        # coderのコンプリーター
        self.coder_completer = FuzzyCompleter(
            WordCompleter([name for _, name in coders], sentence=True)
        )
    
    def get_completions(self, document, complete_event):
        """補完候補を生成する
        
        Args:
            document: 現在の入力ドキュメント
            complete_event: 補完イベント
            
        Yields:
            補完候補
        """
        text = document.text
        
        # 空の場合は何も提供しない
        if not text:
            return
        
        # @ で始まる場合はcoder名を補完
        if text.startswith('@'):
            prefix = text[1:]  # @ を除去
            for _, coder_name in self.coders:
                # 現在の入力に一致する場合のみ候補を提供
                if not prefix or prefix.lower() in coder_name.lower():
                    yield Completion(
                        coder_name, 
                        start_position=-len(prefix),
                        display=coder_name
                    )
        
        # / で始まる場合はコマンドを補完
        elif text.startswith('/'):
            prefix = text[1:]  # / を除去
            for command, _ in self.commands:
                # 現在の入力に一致する場合のみ候補を提供
                if not prefix or prefix.lower() in command.lower():
                    yield Completion(
                        command, 
                        start_position=-len(prefix) - 1,  # / も含めて置き換える
                        display=command
                    )

def create_prompt_session(commands: List[Tuple[str, str]], coders: List[Tuple[str, str]]) -> PromptSession:
    """プロンプトセッションを作成する
    
    Args:
        commands: コマンドのリスト [(コマンド名, 説明)]
        coders: coderのリスト [(coder ID, coder名)]
        
    Returns:
        プロンプトセッション
    """
    # coderとコマンドのコンプリーターを作成
    completer = CoderCommandCompleter(commands, coders)
    # ファジー検索機能を追加
    completer = FuzzyCompleter(completer)
    
    # プロンプトセッションの作成
    return PromptSession(
        completer=completer,
        complete_style=CompleteStyle.MULTI_COLUMN,
        complete_while_typing=True
    )



def get_user_input(session: PromptSession, profile_name: str = None) -> Optional[str]:
    """ユーザーからの入力を取得する
    
    Args:
        session: プロンプトセッション
        profile_name: 表示するcoder名
        
    Returns:
        ユーザー入力、中断された場合はNone
    """
    try:
        # プロンプト文字列をフォーマット
        prompt = prompt_core.format_prompt(profile_name)
        
        # prompt_toolkitを使用したインタラクティブな入力
        user_input = session.prompt(prompt, complete_in_thread=True)
        
        return user_input.strip()
    except KeyboardInterrupt:
        print("\nBye!")
        return None
    except EOFError:
        print("\nBye!")
        return None

def select_from_list(title: str, values: List[Tuple[str, str]], default_value: Optional[str] = None) -> Optional[str]:
    """リストから項目を選択するダイアログを表示する
    
    Args:
        title: ダイアログのタイトル
        values: 選択肢のリスト [(値, 表示名)]
        default_value: デフォルトで選択される値
        
    Returns:
        選択された値、キャンセルされた場合はNone
    """
    # 選択肢のデータを作成
    values_dict = [(value, HTML(f"<b>{display}</b>")) for value, display in values]
    
    # ダイアログを表示して選択結果を取得
    result = radiolist_dialog(
        title=title,
        text="Please select an option:",
        values=values_dict,
        default=default_value
    ).run()
    
    return result

def fuzzy_select_from_list(prompt_text: str, values: List[Tuple[str, str]], default_value: Optional[str] = None) -> Optional[str]:
    """ファジー検索を使用してリストから項目を選択する
    
    Args:
        prompt_text: プロンプトのテキスト
        values: 選択肢のリスト [(値, 表示名)]
        default_value: デフォルトで選択される値
        
    Returns:
        選択された値のキー、キャンセルされた場合はNone
    """
    # 表示用のスタイルを定義
    style = Style.from_dict({
        'completion-menu': 'bg:#333333 #ffffff',
        'completion-menu.completion': 'bg:#333333 #ffffff',
        'completion-menu.completion.current': 'bg:#00aaaa #000000',
        'scrollbar.background': 'bg:#88aaaa',
        'scrollbar.button': 'bg:#222222',
    })
    
    # 選択肢を表示用に整形
    choices = prompt_core.prepare_display_choices(values)
    key_map = {choice: prompt_core.extract_key_from_display(choice) for choice in choices}
    
    # デフォルト値が指定されている場合は、表示用に変換
    default_text = ""
    if default_value:
        default_index = prompt_core.find_default_choice_index(choices, default_value)
        if 0 <= default_index < len(choices):
            default_text = choices[default_index]
    
    # ファジー表示用のコンプリータを作成
    completer = FuzzyCompleter(WordCompleter(choices))
    
    # 利用可能な選択肢を表示
    print("Available profiles:")
    for key, display in values:
        print(f"  {key}: {display}")
    
    # ユーザーからの入力を取得
    try:
        print("Type to search, use arrow keys to navigate, and Enter to select")
        
        # 初期状態で補完メニューを表示するための関数
        def show_completions():
            # 補完メニューを表示
            session.default_buffer.start_completion(select_first=False)
        
        # プロンプトセッションを作成して実行
        session = PromptSession(
            completer=completer,
            style=style,
            complete_while_typing=True,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        
        # デフォルト値があれば初期テキストとして設定
        initial_text = default_text if default_value else ""
        
        # プロンプトを表示し、初期状態で補完メニューを表示
        result = session.prompt(
            f"{prompt_text}: ", 
            pre_run=show_completions,
            default=initial_text
        )
        
        # 選択された値が選択肢に含まれているか確認
        if result in key_map:
            return key_map[result]
        elif result.strip() == "":
            return None
        else:
            # 完全一致しない場合は、最も近い候補を探す
            best_match = prompt_core.find_best_match(result, choices)
            if best_match:
                return key_map[best_match]
            return None
    except (KeyboardInterrupt, EOFError):
        print("\nSelection cancelled")
        return None
