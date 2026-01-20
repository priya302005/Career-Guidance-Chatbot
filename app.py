from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# API Configuration
API_CONFIG = {
    "url": "https://openrouter.ai/api/v1/chat/completions",
    "apiKey": "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",
    "model": "deepseek/deepseek-chat",
    "siteUrl": "https://career-guidance-chatbot.com",
    "siteName": "Career Guidance Assistant for 10th & 12th Students"
}

# Conversation memory
conversation_history = [
    {
        "role": "system",
        "content": """You are a Career Guidance Assistant for 10th and 12th grade students in India.

Your role is to help students choose the right career path based on:
- Their class (10th or 12th)
- Stream (Science, Commerce, Arts)
- Interests and strengths
- Entrance exams and eligibility
- Courses, colleges, and career opportunities

You provide guidance on:
- Career options after 10th (Diploma, ITI, Science, Commerce, Arts)
- Career options after 12th (Engineering, Medical, Commerce, Arts, Government exams)
- Competitive exams (JEE, NEET, CUET, NDA, CLAT, etc.)
- Skill-based and vocational courses
- Government vs private career paths

Always explain in simple, student-friendly language.
Be motivating, clear, and practical.
Focus on the Indian education system."""
    }
]

def get_current_time():
    return datetime.now().strftime("%H:%M")

def generate_fallback_response(user_message):
    message = user_message.lower()

    # After 10th
    if '10th' in message:
        return """Career Options After 10th:

🔹 Science Stream
- MPC / PCMB
- Leads to Engineering, Medical, Data Science, Research

🔹 Commerce Stream
- Accountancy, Business Studies, Economics
- Leads to CA, CMA, Finance, MBA

🔹 Arts / Humanities
- History, Geography, Psychology, Political Science
- Leads to UPSC, Teaching, Journalism, Design

🔹 Diploma / ITI
- Polytechnic Diploma (Mechanical, Electrical, Civil, CS)
- ITI Trades (Electrician, Fitter, Welder)

👉 Choose based on interest, marks, and future goals.
Tell me your interest for better guidance."""

    # After 12th
    if '12th' in message:
        return """Career Options After 12th:

🔹 Science Students
- Engineering (B.E / B.Tech)
- Medical (MBBS, BDS, Nursing)
- AI, Data Science, Biotechnology

🔹 Commerce Students
- B.Com, CA, CMA, CS
- MBA, Banking, Business Analytics

🔹 Arts Students
- BA, LLB, B.Ed
- UPSC, Journalism, Psychology

🔹 Skill-Based Courses
- Digital Marketing
- UI/UX Design
- Web Development

Tell me your stream and interest."""

    # Entrance exams
    if any(word in message for word in ['exam', 'entrance', 'competitive']):
        return """Important Entrance Exams in India:

📘 Engineering
- JEE Main & Advanced
- State CET Exams

📘 Medical
- NEET

📘 Arts & Commerce
- CUET
- CLAT (Law)
- NIFT / NID (Design)

📘 Defense
- NDA

I can explain eligibility and preparation tips."""

    # Stream-specific
    if 'science' in message:
        return """Science Stream Career Options:
- Engineering (CSE, AI, ECE, Mechanical)
- Medical & Allied Health
- Research & Data Science
- Government Exams (UPSC, GATE)

Strong foundation in Maths & Science required."""

    if 'commerce' in message:
        return """Commerce Stream Career Options:
- CA, CMA, CS
- Banking & Finance
- Business Analyst
- MBA

Ideal for students interested in business and finance."""

    if 'arts' in message:
        return """Arts / Humanities Career Options:
- Civil Services (UPSC)
- Law
- Teaching
- Journalism
- Psychology
- Design

Best for creative and analytical minds."""

    # Greetings
    if any(word in message for word in ['hi', 'hello', 'hey']):
        return """Hello 👋  
I am your Career Guidance Assistant.

I can help you with:
✔ Career options after 10th & 12th
✔ Stream selection
✔ Entrance exams
✔ Courses & careers

Tell me your class and interest 😊"""

    # Thanks
   # Thanks
   # Thanks
    if 'thank' in message:
         return "You're welcome 😊 I’m here to help you plan your future. Ask anytime!"

    # Help
    if 'help' in message:
        return """I can help you with:
- Career guidance after 10th
- Career options after 12th
- Entrance exams
- Skill-based courses

Tell me your class and interest."""

    # Default
    return """I can guide you in choosing the right career.

Please tell me:
• Your class (10th / 12th)
• Your stream or interest

I will help you step by step 😊"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get('message', '')

    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    try:
        request_body = {
            "model": API_CONFIG["model"],
            "messages": conversation_history,
            "max_tokens": 1000,
            "temperature": 0.7
        }

        response = requests.post(
            API_CONFIG["url"],
            headers={
                "Authorization": f"Bearer {API_CONFIG['apiKey']}",
                "HTTP-Referer": API_CONFIG["siteUrl"],
                "X-Title": API_CONFIG["siteName"],
                "Content-Type": "application/json"
            },
            json=request_body
        )

        if response.status_code == 200:
            data = response.json()
            ai_response = data["choices"][0]["message"]["content"]
        else:
            raise Exception("API Error")

    except Exception as e:
        print("API failed, using fallback:", e)
        ai_response = generate_fallback_response(user_message)

    conversation_history.append({
        "role": "assistant",
        "content": ai_response
    })

    return jsonify({
        "response": ai_response,
        "timestamp": get_current_time()
    })

if __name__ == '__main__':
    app.run(debug=True)
