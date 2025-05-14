import json
import os
import requests
import tempfile
from flask import Flask, request, jsonify
from google.oauth2 import service_account
import google.auth.transport.requests

app = Flask(__name__)


# Écrire le JSON dans un fichier temporaire
credentials_dict = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'])
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
temp_file.write(json.dumps(credentials_dict).encode())
temp_file.close()

# Chemin vers le fichier de compte de service (tu peux aussi utiliser une variable d'environnement)
SERVICE_ACCOUNT_FILE = temp_file.name
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
        google_request = google.auth.transport.requests.Request()
        credentials.refresh(google_request)
        
        # Jeton d'accès
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
