from openai import OpenAI, AsyncOpenAI

DEFAULT_GEN_KWARGS = {
    "max_tokens": 2048,
    "stream": False,
    "top_p": 0.95,
    "temperature": 1.0
}

client = OpenAI(
    base_url="http://10.32.15.4:31265/qwen25-32b/v1",
    api_key="token-abc123"
)


messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {
        "role": "user",
        "content": "Hello. Who are you?"
    },
    {
        "role": "assistant",
        "content": "Hello! I'm an AI assistant created by Alibaba Cloud to help users like you. I can answer questions, provide information, and assist with a variety of tasks. How can I help you today?"
    },
    {
        "role": "user",
        "content": "What can you do?"
    }
]


chat_response = client.chat.completions.create(
    model="/model",
    messages=messages,
    **DEFAULT_GEN_KWARGS
)

content = chat_response.choices[0].message.content

print(content)
