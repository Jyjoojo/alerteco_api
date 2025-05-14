import json
import requests
from flask import Flask, request, jsonify
from google.oauth2 import service_account
import google.auth.transport.requests

app = Flask(__name__)

# Chemin vers le fichier de compte de service (tu peux aussi utiliser une variable d'environnement)
SERVICE_ACCOUNT_FILE = 'alerteco-firebase-adminsdk-fbsvc-f454679d70.json'
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

@app.route('/')
def home():
    return "API FCM prête à l'emploi"

@app.route('/send-notification', methods=['POST'])
def send_notification():
    try:
        data = request.get_json()
        device_token = data['token']
        title = data.get('title', 'Notification')
        body = data.get('body', 'Contenu vide')
        custom_data = data.get('data', {})

        # Authentification
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        request_auth = google.auth.transport.requests.Request()
        credentials.refresh(request_auth)
        access_token = credentials.token

        # Message
        message = {
            "message": {
                "token": device_token,
                "notification": {
                    "title": title,
                    "body": body
                },
                "data": custom_data
            }
        }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8',
        }

        response = requests.post(
            'https://fcm.googleapis.com/v1/projects/alerteco/messages:send',
            headers=headers,
            data=json.dumps(message)
        )

        return jsonify({
            "status": response.status_code,
            "response": response.json()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
