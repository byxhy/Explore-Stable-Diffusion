import tomllib
import toml
import os
import datetime
import requests
import json

def generate_script(prompt, temperature: float, max_tokens:int=2048) -> dict:
    openai_api_key = 'sk-xxx'

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}",
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": f"{prompt}"
            },
        ]
    }
    
    completion = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(data))
    response = completion.json()['choices'][0]['message']["content"].strip()

    try:
        parsed_data = tomllib.loads(response)

        # 获取当前日期和时间
        now = datetime.datetime.now()
        # 格式化日期和时间为字符串，作为文件名
        script_filename = now.strftime("%Y-%m-%d-%H-%M-%S.toml")
        # # 创建文件，并写入内容
        with open(f'./out/script_{script_filename}', "w") as file:
            toml.dump(parsed_data, file)
    except tomllib.TOMLDecodeError:
        try:
            parsed_data = tomllib.loads(response + '"')
        except tomllib.TOMLDecodeError:
            raise tomllib.TOMLDecodeError("ChatGPT output was cut off midway through generation.", response)

    return parsed_data