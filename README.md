# Dialogflow Chatbot powered by Retrieval Augmented Generation with Vertex AI Vector Search and Gemini

This Python Flask application demonstrates a Retrieval-Augmented Generated system leveraging Google's Gemini and Vertex AI Vector Search for document search. The system retrieves relevant documents from the created Vector Search Index based on the user's question and feeds the retrieved context to the Gemini to return a comprehensive and informative response.The application is deployed on Cloud Run, and Dialogflow can interact with the endpoint with the use of webhooks (a feature within Dialogflow), allowing a chatbot created with Dialogflow to serve as the interaction point between the user and the application.
<img src=https://github.com/dannyang30/gemini-dialogflow-app/blob/main/img/architecture.png>


## Key Features:

* Integration with Google's Vertex AI Vector Search: Utilizes Vertex AI's Text Embedding service for efficient document search.
* Contextual Gemini Responses: Gemini provides a response using retrieved documents to provide insightful and grounded answers.
* Error Handling and Logging: Robust error handling with informative logging for improved debugging and monitoring.



## Getting Started

<b>1. Prerequisites:</b>
- All libraries listed in requirements.txt and python 3.11.2
- A project created on Google Cloud Platform (GCP) with billing enabled
    - For deployment to work in Cloud Run later, a service account has to be created with the following permissions: AI Platform Viewer, Dialogflow API Client, Secret Manager Secret Accessor, Service Usage Consumer, Storage Admin, Vertex AI user
    - Add the JSON key from the service account created into a Secret in Secrets Manager. Name the Secret ID "GOOGLE_APPLICATION_CREDENTIALS"
    - All relevant APIs has to be enabled
- A Vector Search Endpoint & Index has to be created using your datasource. Endpoint & Index ID will be used in the application. Find out how to create one [here](https://cloud.google.com/vertex-ai/docs/vector-search/quickstart)
- To interact with the GCP CLI, [install the gcloud CLI](https://cloud.google.com/sdk/docs/install?authuser=0). You would have to also authenticate yourself by running the following in your terminal: 
```gcloud auth application-default login```


<b>2. Test locally:</b>
- Setup python virtual environment by running the following in your terminal: 
```
python3 -m venv rag-app
source rag-app/bin/activate
```
- Install required libraries: 
```
pip install -r requirements.txt
```
- Replace placeholders like PROJECT_ID, REGION, INDEX, ENDPOINT, DOCS_BUCKET and SECRET_ID with your specific GCP project details in the config.py file
- Run the Flask app by running the following in your terminal: ```python3 app.py```
- Test calling the app by running the following in your terminal: ```python3 test_app.py```


<b>3. Build a Docker image for deployment in Cloud Run by running:</b>
```
AR_REPO='artifact-registry-name-of-your-choice'
SERVICE_NAME='service-name-of-your-choice' 
gcloud artifacts repositories create "$AR_REPO" --location="$GCP_REGION" --repository-format=Docker
gcloud builds submit --tag "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME"
```


<b>4. Deploy in Cloud Run by running:</b>
``` 
gcloud run deploy "$SERVICE_NAME"   --port=8080   --image="$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME"   --allow-unauthenticated   --region=$GCP_REGION   --platform=managed    --project=$GCP_PROJECT   --set-env-vars=GCP_PROJECT=$GCP_PROJECT,GCP_REGION=$GCP_REGION --service-account [Email Address of GCP Service Account]
```
- After deploying in Cloud Run, you will have a public URL for the application 


<b>5. Create webhook in Dialogflow and add under an event handler:</b>
<img src=https://github.com/dannyang30/gemini-dialogflow-app/blob/main/img/create_webhook.png>
<img src=https://github.com/dannyang30/gemini-dialogflow-app/blob/main/img/event_handler_webhook.png>


## Example of Dialogflow chatbot in action:

<b>1. Question asked with response received in Dialogflow:</b>

<img src=https://github.com/dannyang30/gemini-dialogflow-app/blob/main/img/example_1of3.png>
<img src=https://github.com/dannyang30/gemini-dialogflow-app/blob/main/img/example_2of3.png>
<img src=https://github.com/dannyang30/gemini-dialogflow-app/blob/main/img/example_3of3.png>


<b>2. Cloud Run logs reflecting that the application ran:</b>
<img src=https://github.com/dannyang30/gemini-dialogflow-app/blob/main/img/cloud_run_logs.png>

