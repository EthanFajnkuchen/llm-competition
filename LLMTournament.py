from gpt4all import GPT4All
from dotenv import load_dotenv
import os
import csv
import time
import redis
import requests
import datetime

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

def ask_wolfram(redis_client, question, app_id=os.getenv('APP_ID')):
    try:
        # Check if question already in Redis
        cached_answer = redis_client.get(question)
        if cached_answer:
            print('Redis Answered')
            return cached_answer.decode()

        # If not, make API call to Wolfram Alpha
        encoded_question = requests.utils.quote(question)
        url = f"https://api.wolframalpha.com/v1/result?i={encoded_question}&appid={app_id}"
        response = requests.get(url)

        if response.status_code != 200:
            return "No results found."

        # Save to redis and return
        answer = response.text
        save_to_redis(redis_client, question, answer)
        print('Wolfram answered')
        return answer

    except Exception as e:
        return f"An error occurred: {e}"
    

def save_to_redis(redis_client, question, answer):
    try :
        redis_client.setex(question, 14400, answer)
    except Exception as e:
        print(f"Error saving to Redis : {e}")
        
    
def ask_all_wf(redis_client, questions, wf_answers):
    counter = 0
    for question in questions:
        answer = ask_wolfram(redis_client, question)
        if answer == "No results found.":
            continue
        wf_answers.append((question,answer))
        counter += 1
        if counter == 5:
            break


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
    """prompt = f'''
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
            [Your Output:] 
            '''"""
    while True:
        try:

            prompt = f'''
                    Assess the similarity between two sentances, quantifying their similarity on a scale from 0.0 to 1.0. That is, if the two sentances are similar, rate them as 0.8 or 0.9, if they are very different, rate them as 0.1 or 0.2. Only output this similarity score, a float. Do not include any comments, explanations, introductions, or any additional text.
                    1. {answer1} 2. {answer2}. Your output:
                    '''
            similarity_mesure = model.generate(prompt)
            similarity_mesure = float(similarity_mesure)
            return similarity_mesure
        except ValueError:
            print("Model did not answer a single float, we ask again!")
            continue




def execute_model(model_llm, list_questions_wf, llm_answers):
    name_model = model_llm.config['name']
    counter = 0
    for question, answer_wf in list_questions_wf:
        answer, response_time = ask_modelGPT4All(model_llm, question)
        counter += 1
        print("Question " + str(counter) + " : answered!")
        llm_answers.append({
            "Name": name_model,
            "Question": question,
            "Answer": answer,
            "Time": response_time,
            "Correctness": 'No value yet'
        })


def test_models(model_checker, llms_answers, wf_answers):
    for question, answer_wf in wf_answers:
        for index, element in enumerate(llms_answers):
            if element["Question"] == question:
                print("Checking similarity for question '" + question + " ' with model " + element["Name"] + "...")
                similarity = check_similarity(model_checker, question, answer_wf, element["Answer"])
                llms_answers[index]["Correctness"] = similarity 




def compute_stats(llm_answers, name_llm1, name_llm2):

    llm1_answers = [x for x in llm_answers if x["Name"] == name_llm1]
    llm2_answers = [x for x in llm_answers if x["Name"] == name_llm2]

    # Count the number of answered questions
    nb_question_answered =  len(llm1_answers)

    # Compute average correctness for each list
    avg_correctness_llm1 = sum(d['Correctness'] for d in llm1_answers) / len(llm1_answers) if llm1_answers else 0
    avg_correctness_llm2 = sum(d['Correctness'] for d in llm2_answers) / len(llm2_answers) if llm2_answers else 0

    # Find the minimum correctness and its corresponding element
    min_correctness_llm1 = min(llm1_answers, key=lambda d: d['Correctness']) if llm1_answers else None
    min_correctness_llm2 = min(llm2_answers, key=lambda d: d['Correctness']) if llm2_answers else None

    print(f"Number of questions answered: {nb_question_answered}")
    print(f"Average rating for {name_llm1}: {avg_correctness_llm1}")
    print(f"Average rating for {name_llm2}: {avg_correctness_llm2}")
    print(f"Lowest rating question and answer of {name_llm1}: {min_correctness_llm1['Question']} {min_correctness_llm1['Answer']}")
    print(f"Lowest rating question and answer of {name_llm2}: {min_correctness_llm2['Question']} {min_correctness_llm2['Answer']}")



if __name__ == '__main__':


    #start_time = datetime.datetime.now()  # Start time
    
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    try : 
        redis_client.get('test') #Dummy get to check if the client is open!
    except Exception as e:
        print(f"Error connecting to Redis : {e}")
        exit(1)
    

    questions = read_csv('./General_Knowledge_Questions.csv')
    wf_answers = []
    llm_answers = []

    ask_all_wf(redis_client, questions, wf_answers)
    
    
    print('Open Client for LLM1')
    llm_model = GPT4All("gpt4all-falcon-q4_0.gguf")
    llm1_name = llm_model.config['name']
    print('Client opened')
    execute_model(llm_model, wf_answers, llm_answers)
    
    print('Open Client for LLM2')
    llm_model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
    llm2_name = llm_model.config['name']
    print('Client opened')
    execute_model(llm_model, wf_answers, llm_answers)

    test_models(llm_model, llm_answers, wf_answers)

    compute_stats(llm_answers, llm1_name, llm2_name)

    """for element in llm_answers:
        print(element)"""

    """end_time = datetime.datetime.now()  # End time
    duration = end_time - start_time
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"
    print(f"Total execution time: {formatted_time}")"""

