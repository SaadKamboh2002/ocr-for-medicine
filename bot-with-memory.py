from huggingface_hub import InferenceClient

client = InferenceClient("Qwen/Qwen3-8B")
response = client.chat_completion(messages=[
    {"role": "user", "content": "Hello, what do you know about quantum mechanics?"}
], max_tokens=1000)
print(response.choices[0].message.content)