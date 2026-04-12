import litellm

response = litellm.completion(
    model="ollama/llama3.1:8b",
    messages=[{"role": "user", "content": "Say hello"}],
    api_base="http://localhost:11434"
)

print(response.choices[0].message.content)
