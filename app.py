import os

from langchain.vectorstores.matching_engine import MatchingEngine
from google.cloud import aiplatform
from langchain_google_vertexai import VertexAIEmbeddings
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig

from google.cloud import secretmanager

import logging
logging.basicConfig(level=logging.INFO)

from config import PROJECT_ID, REGION, INDEX, ENDPOINT, DOCS_BUCKET, SECRET_ID

def access_secret_version(secret_version_id):
  client = secretmanager.SecretManagerServiceClient()
  response = client.access_secret_version(name=secret_version_id)
  return response.payload.data.decode('UTF-8')

secret_version_id = f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/latest"

key=access_secret_version(secret_version_id)
os.getenv(key)

aiplatform.init(project=PROJECT_ID, location=REGION)

embeddings = VertexAIEmbeddings('text-embedding-004')

#source: https://python.langchain.com/v0.1/docs/integrations/vectorstores/google_vertex_ai_vector_search/
def matching_engine_search(question):
    try:
        vector_store = MatchingEngine.from_components(
                            index_id=INDEX,
                            region=REGION,
                            embedding=embeddings,
                            project_id=PROJECT_ID,
                            endpoint_id=ENDPOINT,
                            gcs_bucket_name=DOCS_BUCKET)

        relevant_documentation=vector_store.similarity_search(question, k=8)
        context = str("\n".join([doc.page_content for doc in relevant_documentation])[:10000])
        logging.info(f"Context provided by matching engine search: ${context}")
        return str(context)
    
    except Exception as e:
        logging.error(f"An error occurred in matching_engine_search: {e}")
        return None
    

def get_response_from_llm(question):
    try:
        matching_engine_response = matching_engine_search(question)

        prompt = f"""
            Follow these guidelines and steps:
            1. Read the following context and summarize it: {matching_engine_response}
            2. Use the summarized context to respond to the user's question: {question}
            - The response must be directly supported by the provided sources
            - Be concise and short
            3. If you do not have the context to provide an answer, say so
            4. Cite the source url used to provide your answer
        """

        model = GenerativeModel("gemini-pro")
        generation_config = GenerationConfig(
            temperature=0.5,
            top_p=0.8,
            top_k=40,
            candidate_count=1,
            max_output_tokens=1024,
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
        )

        logging.info(f"Response from LLM: {response.text}")
        return(response.text)
    
    except Exception as e:
        logging.error(f"An error occurred in get_response_from_llm: {e}")
        return None


# Flask App
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import app 

app = Flask(__name__)

CORS(app) #allows for cross origin requests

@app.route('/getresponse', methods= ['POST'])
def get_response():
    if request.get_json(): #check if it's a response object
        dialogflow_payload = request.get_json()
    else:
        dialogflow_payload={}
    
    question = dialogflow_payload["text"]
    llm_response = get_response_from_llm(question)

    jsonified_llm_response = jsonify({
        "fulfillment_response": {
            "messages": [{
                "text": {
                    "text": [
                        llm_response
                    ]
                }   
            }]
        }
    })

    jsonified_llm_response.headers['Access-Control-Allow-Origin'] = '*' #indicate which domains (origins) are allowed to access the data

    logging.info(f"Response to be returned to dialogflow: {jsonified_llm_response.get_json()}")
    return jsonified_llm_response

if __name__ == "__main__":
    app.run(port=8080, host='0.0.0.0', debug=True)

