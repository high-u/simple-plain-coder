#!/usr/bin/env python3

from qwen_agent.agents import Assistant

def main():
    # LLM設定
    llm_cfg = {
        'model': 'qwen3:8b-q4_K_M',
        'model_server': 'http://localhost:11434/v1',
        'api_key': 'EMPTY'
    }
    
    # MCP対応ツール設定
    tools = [
        {
            'mcpServers': {
                'filesystem': {
                    'command': 'npx',
                    'args': ['-y', '@modelcontextprotocol/server-filesystem', '.']
                }
            }
        }
    ]
    
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

