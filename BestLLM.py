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

    

if __name__ == '__main__':
    client_wf = wf.Client(app_id=os.getenv('APP_ID'))
    model_llm = GPT4All('gpt4all-falcon-q4_0.gguf')
    answer_wf = ask_wolfram(client_wf, 'Who is the president of the USA?') #Need to change the prompt to get questions from the list
    answer_llm = ask_modelGPT4All(model_llm, 'Who is the president of the USA?')
    print(answer_wf)
    print(answer_llm)
