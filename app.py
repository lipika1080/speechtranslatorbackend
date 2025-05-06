import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv

# Load config
dotenv_path = load_dotenv()
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')
AZURE_KEY      = os.getenv('AZURE_KEY')

app = Flask(__name__)
CORS(app)

@app.route('/translate', methods=['POST'])
def translate():
    payload = request.get_json() or {}
    text   = payload.get('text', '').strip()
    target = payload.get('target_language', 'English').strip()

    if not text:
        return jsonify({'error': 'No text provided.'}), 400

    # Build LLM prompt
    headers = {
        'Content-Type': 'application/json',
        'api-key': AZURE_KEY
    }
    body = {
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant that translates text preserving meaning.'},
            {'role': 'user',   'content': f"Translate the following text into {target}:\n\n{text}"}
        ]
    }

    resp = requests.post(AZURE_ENDPOINT, headers=headers, json=body)
    result = resp.json()

    try:
        translated = result['choices'][0]['message']['content']
    except Exception:
        return jsonify({'error': 'Failed to parse translation.', 'details': result}), 500

    return jsonify({'translated': translated})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)