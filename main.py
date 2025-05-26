from qwen_agent.agents import Assistant
import config_utils

def main():
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
    system_prompt_path = llm_config.get('system_prompt')
    template_path = llm_config.get('template')
    
    # ファイルからシステムプロンプトとテンプレートを読み込む
    system_prompt_content = config_utils.load_file_content(system_prompt_path)
    template_content = config_utils.load_file_content(template_path)
    
    # ファイルから読み込んだ内容があれば追加
    if system_prompt_content:
        llm_cfg['system'] = system_prompt_content
    
    if template_content:
        llm_cfg['template'] = template_content
    
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
    
    # Assistant作成
    bot = Assistant(llm=llm_cfg, function_list=tools)
    
    messages = []
    
    while True:
        try:
            user_input = input("> ")
        except KeyboardInterrupt:
            print("\nBye!")
            break
        if user_input.lower() in ['quit', 'exit']:
            break
            
        messages.append({'role': 'user', 'content': user_input})
        
        # print("Assistant: ", end="", flush=True)
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
