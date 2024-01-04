from gpt4all import GPT4All
from dotenv import load_dotenv
import wolframalpha as wf
import os

load_dotenv()

client = wf.Client(app_id=os.getenv('APP_ID'))
try :
    res = client.query("Where is Paris?")
    print(next(res.results).text)
except Exception as e:
    raise e

