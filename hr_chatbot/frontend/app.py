from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests

RASA_API_URL = "http://localhost:5005/webhooks/rest/webhook"

app = Flask(__name__, 
            static_folder='static', 
            template_folder='templates')
CORS(app)

@app.route('/')
def index():
    """Render the main page with chatbot"""
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Correct way to get JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400
            
        user_message = data.get('message', '')
        print("Received message:", user_message)

        # Forward to Rasa
        rasa_response = requests.post(
            RASA_API_URL,
            json={"sender": "user", "message": user_message}
        )
        rasa_response.raise_for_status()
        
        rasa_response_json = rasa_response.json()
        print("Rasa response:", rasa_response_json)

        # Process all responses from Rasa
        responses = []
        for message in rasa_response_json:
            if 'text' in message:
                responses.append({
                    "type": "text",
                    "content": message['text']
                })
            if 'buttons' in message:
                responses.append({
                    "type": "buttons",
                    "content": message['buttons']
                })
        
        return jsonify({'responses': responses})

    except requests.exceptions.RequestException as e:
        print("Request error:", str(e))
        return jsonify({
            'responses': [{
                'type': 'text',
                'content': "Sorry, I'm having trouble connecting to the chatbot service."
            }]
        }), 502
    except Exception as e:
        print("Unexpected error:", str(e))
        return jsonify({
            'responses': [{
                'type': 'text',
                'content': "Sorry, an unexpected error occurred."
            }]
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)