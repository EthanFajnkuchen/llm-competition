from gpt4all import GPT4All

# gpt4all-falcon-q4_0.gguf
# mistral-7b-openorca.Q4_0.gguf
model = GPT4All("gpt4all-falcon-q4_0.gguf")
output = model.generate(prompt="The capital of france is")
print(output)