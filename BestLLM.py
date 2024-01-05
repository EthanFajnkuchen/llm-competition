from gpt4all import GPT4All
from dotenv import load_dotenv
import wolframalpha as wf
import os
import csv
import time

load_dotenv()

def read_csv(file_path):
    questions = []
    with open(file_path, newline='', encoding='utf-8') as csvfile :
        csvreader = csv.reader(csvfile)
        next(csvreader, None)
        for row in csvreader:
            if len(row) > 1:
                questions.append(row[1])
    return questions

def ask_wolfram(client, question):
    try :
        start_time = time.time()  # Record start time
        res = client.query(question)
        if not res.results:
            return "No results found."
        end_time = time.time()  # Record end time
        response_time = (end_time - start_time) * 1000 
        return next(res.results).text, response_time
    except StopIteration:
        return "No results available for this query.", 0
    except Exception as e:
        return f"An error occurred: {e}", 0

    
def ask_modelGPT4All(model, question):
    try :
        start_time = time.time()  # Record start time in seconds
        response = model.generate(question)
        end_time = time.time()  # Record end time in seconds
        response_time = (end_time - start_time) * 1000  # Convert duration to milliseconds
        return response, response_time    
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
    '''    questions = read_csv('./General_Knowledge_Questions.csv')
    client_wf = wf.Client(app_id=os.getenv('APP_ID'))
    model_llm1_questions = GPT4All("gpt4all-falcon-q4_0.gguf")
    model_llm2_questions = GPT4All('orca-2-7b.Q4_0.gguf')
    model_llm_checker = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
    name_modellm1 = model_llm1_questions.config['name']
    name_modellm2 = model_llm2_questions.config['name']


    for question in questions:
        answer_wf, time_wf = ask_wolfram(client_wf, question)
        if answer_wf == "No results available for this query." :
            continue
        answer_llm1, time_llm1 = ask_modelGPT4All(model_llm1_questions, question)
        mesure_llm1 = check_similarity(model_llm_checker, question, answer_wf, answer_llm1)
        llm1_stats = (question, model_llm1_questions.config['name'], answer_llm1, time_llm1, mesure_llm1)
        answer_llm2, time_llm2 = ask_modelGPT4All(model_llm2_questions, question)
        mesure_llm2 = check_similarity(model_llm_checker, question, answer_wf, answer_llm2)
        llm2_stats = (question, model_llm2_questions.config['name'], answer_llm2, time_llm2, mesure_llm2)'''
    '''    questions = read_csv('./General_Knowledge_Questions.csv')
    print("Read CSV : DONE")
    client_wf = wf.Client(app_id=os.getenv('APP_ID'))
    model_llm1_questions = GPT4All("gpt4all-falcon-q4_0.gguf")
    name_modellm1 = model_llm1_questions.config['name']
    model_llm2_questions = GPT4All('orca-2-7b.Q4_0.gguf')
    name_modellm2 = model_llm2_questions.config['name']
    model_llm_checker = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
    print("Create all models : DONE")
    answer_wf, time_wf = ask_wolfram(client_wf, questions[1])
    print("Wolfram Alpha Answered!")
    answer_llm1, time_llm1 = ask_modelGPT4All(model_llm1_questions, questions[1])
    print("Model 1 : Answered")
    mesure_llm1 = check_similarity(model_llm_checker, questions[1], answer_wf, answer_llm1)
    print("Check Similiarity w/ model 1 : DONE")
    llm1_stats = (questions[1], name_modellm1, answer_llm1, time_llm1, mesure_llm1)
    answer_llm2, time_llm2 = ask_modelGPT4All(model_llm2_questions, questions[1])
    print("Model 2 : Answered")
    mesure_llm2 = check_similarity(model_llm_checker, questions[1], answer_wf, answer_llm2)
    print("Check Similiarity w/ model 2 : DONE")
    llm2_stats = (questions[1], name_modellm2, answer_llm2, time_llm2, mesure_llm2)
    print(llm1_stats)
    print(llm2_stats)

    answer_wf, time_wf = ask_wolfram(client_wf, questions[2])
    print("Wolfram Alpha Answered!")
    answer_llm1, time_llm1 = ask_modelGPT4All(model_llm1_questions, questions[2])
    print("Model 1 : Answered")
    mesure_llm1 = check_similarity(model_llm_checker, questions[2], answer_wf, answer_llm1)
    print("Check Similiarity w/ model 1 : DONE")
    llm1_stats = (questions[2], name_modellm1, answer_llm1, time_llm1, mesure_llm1)
    answer_llm2, time_llm2 = ask_modelGPT4All(model_llm2_questions, questions[2])
    print("Model 2 : Answered")
    mesure_llm2 = check_similarity(model_llm_checker, questions[2], answer_wf, answer_llm2)
    print("Check Similiarity w/ model 2 : DONE")
    llm2_stats = (questions[2], name_modellm2, answer_llm2, time_llm2, mesure_llm2)
    print(llm1_stats)
    print(llm2_stats)'''
    questions = read_csv('./General_Knowledge_Questions.csv')
    client_wf = wf.Client(app_id=os.getenv('APP_ID'))
    counter = 0
    for question in questions:
            wolfram_result, time_wf = ask_wolfram(client_wf, question)
            if wolfram_result == "No results available for this query.":
                continue

            print(question + " -> " + wolfram_result)
            counter += 1
    print('WolframAlpha answered ' + str(counter) + " / 50 questions")
            





    



