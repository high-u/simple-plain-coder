"""
LLM関連の純粋関数モジュール

このモジュールは、LLM設定の準備、メッセージ処理などの純粋関数を提供します。
すべての関数は副作用を持たず、入力に基づいて結果を返します。
"""
from typing import Dict, Any, List, Optional, Tuple

def prepare_llm_config(coder_config: Dict[str, Any]) -> Dict[str, Any]:
    """コーダー設定からLLM設定を準備する
    
    Args:
        coder_config: コーダー設定
        
    Returns:
        LLM設定辞書
        
    >>> prepare_llm_config({'model_name': 'gpt-4'})
    {'model': 'gpt-4', 'model_server': 'http://localhost:11434/v1', 'api_key': 'EMPTY'}
    >>> result = prepare_llm_config({'model_name': 'gpt-4', 'temperature': 0.7})
    >>> result['model']
    'gpt-4'
    >>> result['options']['temperature']
    0.7
    """
    model_name = coder_config.get('model_name')
    if not model_name:
        raise ValueError("Model name is not configured")
    
    # LLM基本設定
    llm_cfg = {
        'model': model_name,
        'model_server': coder_config.get('model_server', 'http://localhost:11434/v1'),
        'api_key': coder_config.get('api_key', 'EMPTY')
    }
    
    # 生成設定をオプションとして追加
    options = {}
    
    # 空でない値のみ追加
    for key in ['temperature', 'top_p', 'top_k', 'num_predict', 'max_tokens',
               'repeat_penalty', 'presence_penalty', 'frequency_penalty']:
        if key in coder_config and coder_config[key] != "":
            options[key] = coder_config[key]
    
    # システムプロンプトとテンプレートの処理
    system_prompt = coder_config.get('system_prompt')
    template = coder_config.get('template')
    
    # 設定値があれば直接使用
    if system_prompt:
        llm_cfg['system'] = system_prompt
    
    if template:
        llm_cfg['template'] = template
    
    # オプションが空でなければ追加
    if options:
        llm_cfg['options'] = options
    
    return llm_cfg

def prepare_messages(history: List[Dict[str, Any]], new_message: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """メッセージ履歴に新しいメッセージを追加する
    
    Args:
        history: メッセージ履歴
        new_message: 追加する新しいメッセージ（オプション）
        
    Returns:
        更新されたメッセージ履歴
        
    >>> history = [{'role': 'user', 'content': 'こんにちは'}]
    >>> prepare_messages(history, {'role': 'user', 'content': '元気？'})
    [{'role': 'user', 'content': 'こんにちは'}, {'role': 'user', 'content': '元気？'}]
    >>> prepare_messages(history)
    [{'role': 'user', 'content': 'こんにちは'}]
    """
    if new_message is None:
        return history.copy()
    
    # 不変性を保持した新しいリストを返す
    return history + [new_message]

def extract_response_content(response: List[Dict[str, Any]]) -> str:
    """LLMレスポンスからコンテンツを抽出する
    
    Args:
        response: LLMレスポンス
        
    Returns:
        抽出されたコンテンツ
        
    >>> extract_response_content([{'role': 'assistant', 'content': 'こんにちは'}, {'role': 'assistant', 'content': '元気です'}])
    '元気です'
    >>> extract_response_content([])
    ''
    """
    if not response:
        return ""
    
    # 最後のメッセージのコンテンツを取得
    return response[-1].get('content', '')

def prepare_mcp_tools(mcp_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """MCP設定からツールリストを準備する
    
    Args:
        mcp_config: MCP設定データ
        
    Returns:
        ツールリスト
        
    >>> prepare_mcp_tools({})
    []
    >>> prepare_mcp_tools({'mcpServers': [{'name': 'test'}]})
    [{'mcpServers': [{'name': 'test'}]}]
    """
    if not mcp_config or 'mcpServers' not in mcp_config:
        return []
    
    return [mcp_config]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
