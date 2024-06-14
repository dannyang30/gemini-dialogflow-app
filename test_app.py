import requests
import time

test_url = 'http://127.0.0.1:8080/getresponse' 

r = requests.post(
    test_url, json={"text": "How can a marketing manager use Gemini?"}) # make a request to the local endpoint 

print(r.json())
time.sleep(8)