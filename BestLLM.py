from gpt4all import GPT4All
from dotenv import load_dotenv
import wolframalpha as wf
import os

load_dotenv()


def ask_wolfram(client, question):
    try :
        res = client.query(question)
        return next(res.results).text
    except Exception as e:
        raise e
    
def ask_modelGPT4All(model, question):
    try :
        return model.generate(question)
    except Exception as e : 
        raise e

def check_similarity(model,question, answer1, answer2):
    prompt = f'''
            Assess the similarity between two responses to a specific question, quantifying their similarity on a scale from 0.0 (completely different) to 1.0 (exactly the same). The score should reflect how closely the responses align in meaning or content. For responses that are very similar but not identical, assign a score close to 1, like 0.8. For moderately similar responses, use a score around 0.5. For answer with no connection, use a score around 0 like 0.1 . IMPORTANT: Return only a floating-point number indicating the similarity score. Do not include any comments, explanations, introductions, or additional text. 

            Example:
            [Question] Who is the queen of Denmark?
            [Response 1] Margrethe II (1972-present).
            [Response 2] The queen of Denmark is King Charles III.

            [Your Output]: 0.1"

            Your task: 

            [Question] {question}
            [Response 1] {answer1}
            [Response 2] {answer2}
            [Your Output:] '''
    similarity_mesure = model.generate(prompt)
    return similarity_mesure


if __name__ == '__main__':
    #client_wf = wf.Client(app_id=os.getenv('APP_ID'))
    #model_llm_questions = GPT4All("gpt4all-falcon-q4_0.gguf")
    model_llm_checker = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
    #answer_wf = ask_wolfram(client_wf, 'Who is the president of the USA?') #Need to change the prompt to get questions from the list
    #print(answer_wf)

    #answer_llm = ask_modelGPT4All(model_llm_questions, 'Who is the president of the USA?')
    #print(answer_llm)
    mesure = check_similarity(model=model_llm_checker, question='Who is the president of the USA? ',answer1='Joe Biden (2021-present)', answer2='The president of the USA is Donald Trump')
    print(mesure)



