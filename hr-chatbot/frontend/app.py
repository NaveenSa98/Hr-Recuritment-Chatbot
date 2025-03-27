# frontend/app.py
from flask import Flask, render_template,jsonify
from flask_cors import CORS

app = Flask(__name__, 
            static_folder='static', 
            template_folder='templates')
CORS(app)

@app.route('/')
def index():
    """Render the main page with chatbot"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def handle_chat():
    """
    Endpoint to handle chat interactions
    TODO: Integrate with Rasa backend
    """
    return jsonify({"response": "Chatbot response placeholder"})

if __name__ == '__main__':
    app.run(debug=True, port=3000)