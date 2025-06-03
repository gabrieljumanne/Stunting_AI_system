import requests

API_KEY = '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'

headers = {
    'Content-type':'application/json',
    'Authorization':f"Bearer {API_KEY}"
}

data = {
    'model':'deepseek/deepseek-chat-v3-0324:free',
    'messages':[
        {'role':'system', 'content':'You are helpfull assistance'},
        {'role':'system', 'content': 'speack swahili for me, Niambie kuhusu tatizo la udumavu la watoto  ?  '}
    ], 
    'stream':False,
}

response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
response_data = response.json()

try:
    print(response_data['choices'][0]['message']['content'])
except KeyError as e:
    print(f'Error:Missing key {e} in response')
    print(f'Response structure: {response_data}')
    
