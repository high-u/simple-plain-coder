"""
設定関連の純粋関数モジュール

このモジュールは、設定データの変換、検証、準備などの純粋関数を提供します。
すべての関数は副作用を持たず、入力に基づいて結果を返します。
"""
from typing import Dict, Any, List, Tuple, Optional, Union

def validate_config(config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """設定データを検証し、有効かどうかを返す
    
    Args:
        config_data: 検証する設定データ
        
    Returns:
        (is_valid, errors): 検証結果と、エラーがあればそのリスト
        
    >>> validate_config({})
    (False, ['設定が空です'])
    >>> validate_config({'default': {'model_name': 'gpt-4'}})
    (True, [])
    """
    errors = []
    if not config_data:
        errors.append('設定が空です')
        return (False, errors)
    
    # 少なくとも1つのcoderセクションがあることを確認
    has_valid_coder = False
    for coder_id, coder_config in config_data.items():
        if isinstance(coder_config, dict) and 'model_name' in coder_config:
            has_valid_coder = True
            break
    
    if not has_valid_coder:
        errors.append('有効なcoderセクションが見つかりません')
    
    return (len(errors) == 0, errors)

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

def get_coder_display_info(coders_data: Dict[str, Any], coder_id: str) -> Tuple[str, str]:
    """コーダーIDから表示名と説明を取得する
    
    Args:
        coders_data: コーダー設定データ
        coder_id: コーダーID
        
    Returns:
        (name, description): コーダー名と説明のタプル
        
    >>> get_coder_display_info({'test': {'name': 'テスト', 'description': '説明'}}, 'test')
    ('テスト', '説明')
    >>> get_coder_display_info({'test': {}}, 'test')
    ('test', '')
    >>> get_coder_display_info({}, 'unknown')
    ('unknown', '')
    """
    coder_config = coders_data.get(coder_id, {})
    name = coder_config.get('name', coder_id)
    description = coder_config.get('description', '')
    return (name, description)

def extract_available_coders(coders_data: Dict[str, Any]) -> List[Tuple[str, str]]:
    """設定データから利用可能なコーダーのリストを抽出する
    
    Args:
        coders_data: コーダー設定データ
        
    Returns:
        コーダーのリスト [(コーダーID, コーダー名)]
        
    >>> extract_available_coders({'test1': {'name': 'テスト1'}, 'test2': {'name': 'テスト2'}})
    [('test1', 'テスト1'), ('test2', 'テスト2')]
    >>> extract_available_coders({})
    []
    """
    coder_list = []
    
    for key, value in coders_data.items():
        # 各セクションからname属性を取得
        name = value.get('name', key)
        coder_list.append((key, name))
    
    return coder_list

def find_default_coder_id(coders_data: Dict[str, Any]) -> Optional[str]:
    """設定データからデフォルトのコーダーIDを見つける
    
    Args:
        coders_data: コーダー設定データ
        
    Returns:
        デフォルトのコーダーID、または設定が空の場合はNone
        
    >>> find_default_coder_id({'test1': {}, 'test2': {}})
    'test1'
    >>> print(find_default_coder_id({}))
    None
    """
    if not coders_data:
        return None
    
    # 最初のコーダーIDを返す
    return next(iter(coders_data.keys()))

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
