from flask import Flask, request, jsonify
from flask_cors import CORS                      # <== NEW
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)                                         # <== NEW

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

@app.route('/detect-prereqs', methods=['POST'])
def detect_prereqs():
    data = request.json
    question = data.get('question', '')
    correct = data.get('correct_answer', '')
    wrong = data.get('wrong_answer', '')

    if not (question and correct and wrong):
        return jsonify({"error": "Missing fields in request"}), 400

    try:
        prompt1 = f"""Question: {question}
Correct Answer: {correct}
List all prerequisite concepts required to solve this question."""
        resp1 = model.generate_content(prompt1)

        prompt2 = f"""Question: {question}
Correct Answer: {correct}
Wrong Answer: {wrong}
Which concept(s) seem missing or misunderstood in the wrong answer?"""
        resp2 = model.generate_content(prompt2)

        return jsonify({
            "all_prerequisites": resp1.text.strip(),
            "missing_prerequisites": resp2.text.strip()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "Gemini Prerequisite Detection API is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
