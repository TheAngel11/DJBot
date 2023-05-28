from django.shortcuts import render
import uuid
from google.cloud import dialogflow_v2beta1 as dialogflow
from google.protobuf.json_format import MessageToJson

# Create your views here.

def index(request):
    session_client = dialogflow.SessionsClient()

    session_path = session_client.session_path("djbot-388016", str(uuid.uuid4()))
    print("Session path: {}\n".format(session_path))

    texts = ["Hey, how are you?"]

    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code="en-US")

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(session=session_path, query_input=query_input)

        json_response = MessageToJson(response._pb)
        print(json_response)

        print(response.query_result.fulfillment_text)

    


    return render(request, 'index.html')
