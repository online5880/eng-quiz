from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from flask_login import login_required, current_user
from app.models.quiz import Quiz
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

bp = Blueprint('quiz', __name__, url_prefix='/quiz')
quiz = Quiz()

llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)
output_parser = StrOutputParser()
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """당신은 초등학생을 위한 영어 학습 도우미입니다. 
                      친절하고 이해하기 쉽게 설명해주세요.
                      답변은 한국어로 해주세요."""),
        ("human", "#Question:\n{question}")
    ]
)

load_dotenv()

chain = prompt | llm | output_parser

@bp.route('/')
@login_required
def index():
    question = quiz.get_random_question()
    progress = quiz.get_progress()
    stats = quiz.get_stats()
    return render_template('quiz.html', 
                         question=question, 
                         progress=progress, 
                         stats=stats,
                         user=current_user)

@bp.route('/check', methods=['POST'])
@login_required
def check_answer():
    answer = request.form.get('answer', '')
    is_correct = quiz.check_answer(answer)
    details = quiz.get_current_question_details()
    progress = quiz.get_progress()
    stats = quiz.get_stats()
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': details['correct_answer'],
        'example_en': details['example_en'],
        'example_ko': details['example_ko'],
        'progress': progress,
        'stats': stats
    })

@bp.route('/next')
@login_required
def next_question():
    question = quiz.get_random_question()
    progress = quiz.get_progress()
    stats = quiz.get_stats()
    return jsonify({
        'question': question,
        'progress': progress,
        'stats': stats
    })

@bp.route('/save_state', methods=['POST'])
def save_state():
    state = quiz.to_dict()
    return jsonify(state)

@bp.route('/load_state', methods=['POST'])
def load_state():
    state_data = request.json
    quiz.load_state(state_data)
    return jsonify({'success': True})

@bp.route('/chat', methods=['POST'])
@login_required
async def chat():
    if not session.get('openai_api_key'):
        return jsonify({'response': 'API 키가 설정되지 않았습니다. API 설정 메뉴에서 키를 입력해주세요.'})
    
    data = request.get_json()
    question = data.get('question', '')
    
    try:
        llm.openai_api_key = session['openai_api_key']
        response = chain.stream({"question": question})
        messages = ""
        for token in response:
            messages += token
        
        answer = messages
        return jsonify({'response': answer})
        
    except Exception as e:
        return jsonify({'response': f'오류가 발생했습니다: {str(e)}'})
