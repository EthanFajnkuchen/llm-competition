from gpt4all import GPT4All


model_llm_checker = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
model_llm_checker_name = model_llm_checker.config['name']
print(model_llm_checker.config)
model_llm2_questions = GPT4All('orca-2-7b.Q4_0.gguf')
model_llm2_questions_name = model_llm2_questions.config['name']
print(model_llm2_questions.config)
print(model_llm_checker.config)

