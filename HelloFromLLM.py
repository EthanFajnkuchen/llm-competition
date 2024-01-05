from gpt4all import GPT4All

# gpt4all-falcon-q4_0.gguf
# mpt-7b-chat-merges-q4_0.gguf
# orca-2-7b.Q4_0.gguf
model = GPT4All("mpt-7b-chat-merges-q4_0.gguf")
output = model.generate(prompt="Who was the first President of the United States?")
print(output)

#For responses that are very similar but not identical, assign a score close to 1, like 0.8. For moderately similar responses, use a score around 0.5. For answer with no connection, use a score around 0 like 0.1 .