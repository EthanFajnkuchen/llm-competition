from gpt4all import GPT4All
from dotenv import load_dotenv
import wolframalpha as wf
import os
import csv
import time
import redis

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

def ask_wolfram(redis_client, client_wf , question):
    try :
        #check if question already in Redis
        cached_answer = redis_client.get(question)
        if cached_answer:
            print('Redis Answered')
            return cached_answer.decode()
        
        #If not, ask WA
        res = client_wf.query(question)
        if not res.results:
            return "No results found."
        
        #Save to redis and return
        answer = next(res.results).text
        save_to_redis(redis_client, question, answer)
        print('Wolfram answered')
        return answer
    except StopIteration:
        return "No results available for this query."
    except Exception as e:
        return f"An error occurred: {e}"
    

def save_to_redis(redis_client, question, answer):
    try :
        redis_client.setex(question, 14400, answer)
    except Exception as e:
        print(f"Error saving to Redis : {e}")
        


    
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

def compute_stats(model_stats, model_llm1_name, model_llm2_name):
    llm1_data = [item for item in model_stats if item[1] == model_llm1_name]
    llm2_data = [item for item in model_stats if item[1] ==  model_llm2_name]

    #Compute number of questions answered
    nb_question_answered = len(model_stats) / 2

    #Compute average ratings
    avg_rating_llm1 = sum([float(item[4]) for item in llm1_data]) / len(llm1_data)
    avg_rating_llm2 = sum([float(item[4]) for item in llm2_data]) / len(llm2_data)

    #Finding lowest rating question and answer for each model
    lowest_rating_llm1 = min(llm1_data, key=lambda x: float(x[4]))
    lowest_rating_llm2 = min(llm2_data, key=lambda x: float(x[4]))

    return nb_question_answered, avg_rating_llm1, avg_rating_llm2, lowest_rating_llm1, lowest_rating_llm2





if __name__ == '__main__':


    #Read CSV
    questions = read_csv('./General_Knowledge_Questions.csv')
    print('Read CSV : Done')

    #Open Redis Client
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    print('Open Redis Client: Done')
    
    #Open Client with Wolfram + 3 Local LLMs
    print('Try to open to client to the 4 LLMs')
    client_wf = wf.Client(app_id=os.getenv('APP_ID'))
    model_llm1_questions = GPT4All("gpt4all-falcon-q4_0.gguf")
    name_model_llm1 = model_llm1_questions.config['name']
    model_llm2_questions = GPT4All('orca-2-7b.Q4_0.gguf')
    name_model_llm2 = model_llm1_questions.config['name']

    model_llm_checker = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
    print('Open Client to the 4 LLMs : Done')



    #Initialize list DS
    all_answers = []


    counter = 0
    for question in questions:
        answer_wf = ask_wolfram(redis_client, client_wf, question)
        if answer_wf == "No results available for this query.":
            continue
        
        print('Ask to LLM 1')
        answer_llm1, time_llm1 = ask_modelGPT4All(model_llm1_questions, question)
        print('LLM1: DONE')

        mesure_llm1 = check_similarity(model_llm_checker, question, answer_wf, answer_llm1)
        print("Check Similiarity w/ model 1 : DONE")

        llm1_stats = (question, name_model_llm1, answer_llm1, time_llm1, mesure_llm1)
        print(llm1_stats)
        
        all_answers.append(llm1_stats)
        
        print('Ask to LLM 2')
        answer_llm2, time_llm2 = ask_modelGPT4All(model_llm2_questions, question)
        print('LLM2: DONE')

        mesure_llm2 = check_similarity(model_llm_checker, question, answer_wf, answer_llm2)
        print("Check Similiarity w/ model 2 : DONE")

        llm2_stats = (question, name_model_llm2, answer_llm2, time_llm2, mesure_llm2)
        print(llm2_stats)

        all_answers.append(llm2_stats)
        counter += 1
        if counter == 1:
            break

    
    #Compute stats and print final answers
    nb_question_answered, avg_rating_llm1, avg_rating_llm2, lowest_rating_llm1, lowest_rating_llm2 = compute_stats(all_answers, name_model_llm1, name_model_llm2)
    print(f'Number of questions answered : {nb_question_answered}')
    print(f'Average rating for {name_model_llm1}: {avg_rating_llm1}')
    print(f'Average rating for {name_model_llm2}: {avg_rating_llm2}')
    print(f'Lowest rating question and answer of {name_model_llm1} : {lowest_rating_llm1[0]} {lowest_rating_llm1[2]}')
    print(f'Lowest rating question and answer of {name_model_llm2} : {lowest_rating_llm2[0]} {lowest_rating_llm2[2]}')


    '''

    questions = read_csv('./General_Knowledge_Questions.csv')
    print("Read CSV : DONE")

    #Open Redis Client
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    print('Redis Client opened : DONE')

    #Open WF + 3 LLMs
    client_wf = wf.Client(app_id=os.getenv('APP_ID'))
    model_llm1_questions = GPT4All("gpt4all-falcon-q4_0.gguf")
    name_modellm1 = model_llm1_questions.config['name']
    model_llm2_questions = GPT4All('orca-2-7b.Q4_0.gguf')
    name_modellm2 = model_llm2_questions.config['name']
    model_llm_checker = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
    print("Create all models : DONE")

    #Ask Wolfram or check Redis
    answer_wf = ask_wolfram(redis_client, client_wf, questions[1])

    #Ask LLMs
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

    #Print Stats
    print(llm1_stats)
    print(llm2_stats)


    #Ask Wolfram or check Redis
    answer_wf = ask_wolfram(redis_client, client_wf, questions[1])

    #Ask LLMs
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


    
    #Print Stats
    print(llm1_stats)
    print(llm2_stats)

        '''
    '''

    questions = read_csv('./General_Knowledge_Questions.csv')
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    client_wf = wf.Client(app_id=os.getenv('APP_ID'))
    counter = 0
    for question in questions:
            wolfram_result = ask_wolfram(redis_client, client_wf, question)
            if wolfram_result == "No results available for this query.":
                continue
            print(question + " -> " + wolfram_result)
            counter += 1
    print('WolframAlpha answered ' + str(counter) + " / 50 questions")
            '''





    



