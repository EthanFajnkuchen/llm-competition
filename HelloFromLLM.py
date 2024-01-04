from gpt4all import GPT4All

# gpt4all-falcon-q4_0.gguf
# mpt-7b-chat-merges-q4_0.gguf
model = GPT4All("mpt-7b-chat-merges-q4_0.gguf")
output = model.generate(prompt="Who was the first President of the United States?")
print(output)