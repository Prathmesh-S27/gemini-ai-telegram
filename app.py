from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure Gemini AI
API_KEY = os.environ.get('API_KEY', 'your-api-key-here')
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'web_user')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Generate response using Gemini
        chat = model.start_chat()
        response = chat.send_message(message)
        
        return jsonify({
            'response': response.text,
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Gemini AI Web App'})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
