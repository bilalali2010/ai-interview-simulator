import streamlit as st
import random
import re
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import numpy as np
from datetime import datetime
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Interview Simulator",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.3rem;
        margin-top: 1.5rem;
    }
    .score-card {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .positive {
        color: #2ecc71;
    }
    .negative {
        color: #e74c3c;
    }
    .stButton button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# App header
st.markdown('<h1 class="main-header">🎤 AI Interview Simulator</h1>', unsafe_allow_html=True)
st.markdown("### Practice your interview skills with AI - No API keys required!")

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'scores' not in st.session_state:
    st.session_state.scores = []
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'waiting_for_answer' not in st.session_state:
    st.session_state.waiting_for_answer = False

# Initialize the free models (no API key needed)
@st.cache_resource
def load_models():
    try:
        # For question generation
        qa_generator = pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-question-generation-ap")
    except:
        qa_generator = None
    
    try:
        # For sentiment analysis of answers
        sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    except:
        sentiment_analyzer = None
    
    return qa_generator, sentiment_analyzer

qa_generator, sentiment_analyzer = load_models()

# Interview questions database
interview_questions = {
    "behavioral": [
        "Tell me about a time you had to overcome a challenge.",
        "Describe a situation where you had to work with a difficult team member.",
        "Tell me about a time you failed and what you learned from it.",
        "Describe a project where you had to take initiative.",
        "Tell me about a time you had to meet a tight deadline."
    ],
    "technical": [
        "What programming languages are you most comfortable with?",
        "How do you approach debugging a complex problem?",
        "Describe your experience with version control systems.",
        "What development methodologies are you familiar with?",
        "How do you stay updated with the latest technology trends?"
    ],
    "general": [
        "Tell me about yourself.",
        "What are your strengths and weaknesses?",
        "Where do you see yourself in 5 years?",
        "Why do you want to work at our company?",
        "What motivates you at work?"
    ]
}

# Feedback phrases
positive_feedback = [
    "Great answer! You provided specific examples which really strengthen your response.",
    "Excellent! You demonstrated relevant skills and experience.",
    "Well done! You structured your answer clearly and concisely.",
    "Good response! You showed self-awareness and growth mindset.",
    "Nice job! You connected your experience directly to the role."
]

improvement_feedback = [
    "Consider providing a more specific example to illustrate your point.",
    "Try to structure your answer using the STAR method (Situation, Task, Action, Result).",
    "You might want to focus more on your role and contributions in that situation.",
    "Consider connecting your answer more directly to the job requirements.",
    "Try to be more concise while still providing enough detail."
]

# Function to generate follow-up questions
def generate_followup_question(answer, question_type):
    if not qa_generator or not answer.strip():
        return None
    
    try:
        # Create context from answer
        context = answer[:500]  # Limit context length
        
        # Generate follow-up question
        follow_up = qa_generator(
            f"generate question: {context}",
            max_length=100,
            num_return_sequences=1,
            do_sample=True
        )
        
        if follow_up and len(follow_up) > 0:
            return follow_up[0]['generated_text'].strip()
    except:
        pass
    
    # Fallback questions if generation fails
    fallback_questions = {
        "behavioral": "Can you tell me more about what you learned from that experience?",
        "technical": "Could you elaborate on your technical approach to that problem?",
        "general": "How did that experience prepare you for this role?"
    }
    
    return fallback_questions.get(question_type, "Can you tell me more about that?")

# Function to analyze answer quality
def analyze_answer(question, answer):
    if not answer.strip():
        return "Please provide a more detailed answer.", 0
    
    # Calculate basic metrics
    word_count = len(answer.split())
    sentence_count = len(re.findall(r'[.!?]+', answer))
    
    # Simple content analysis
    has_example = bool(re.search(r'(example|for instance|such as|experience|project)', answer.lower()))
    has_action = bool(re.search(r'(i did|i implemented|i created|i developed|i led)', answer.lower()))
    has_result = bool(re.search(r'(result|outcome|achieved|accomplished|succeeded)', answer.lower()))
    
    # Score calculation
    score = 0
    feedback = ""
    
    if word_count < 20:
        feedback += "Your answer is quite brief. Try to provide more detail. "
        score += 2
    elif word_count > 150:
        feedback += "Your answer is quite long. Try to be more concise while still providing key details. "
        score += 3
    else:
        feedback += "Good length for your answer. "
        score += 4
    
    if has_example:
        feedback += "Good job providing examples. "
        score += 3
    
    if has_action:
        feedback += "You clearly described your actions. "
        score += 3
    
    if has_result:
        feedback += "You effectively discussed results. "
        score += 3
    
    # Sentiment analysis if available
    if sentiment_analyzer:
        try:
            sentiment = sentiment_analyzer(answer[:512])[0]
            if sentiment['label'] == 'positive':
                score += 2
                feedback += "You maintained a positive tone. "
            elif sentiment['label'] == 'negative':
                score -= 1
                feedback += "Try to maintain a more positive tone. "
        except:
            pass
    
    # Convert to percentage (max score 15 -> convert to 100 scale)
    score_percent = min(100, int((score / 15) * 100))
    
    # Add encouragement
    if score_percent < 50:
        feedback += "Keep practicing - you'll improve with each interview!"
    elif score_percent < 80:
        feedback += "Good effort! With a bit more practice, you'll be interview-ready."
    else:
        feedback += "Excellent! You're demonstrating strong interview skills."
    
    return feedback, score_percent

# Function to get next question
def get_next_question(category, user_answer=None):
    if user_answer and st.session_state.question_count > 0:
        # Generate follow-up question based on previous answer
        follow_up = generate_followup_question(user_answer, category)
        if follow_up:
            return follow_up
    
    # Return a random question from the selected category
    return random.choice(interview_questions[category])

# Function to handle interview process
def conduct_interview(category, user_answer=None):
    if not st.session_state.interview_started:
        st.session_state.interview_started = True
        st.session_state.question_count = 0
        st.session_state.scores = []
        st.session_state.conversation = []
    
    if user_answer:
        # Analyze the user's answer
        feedback, score = analyze_answer(st.session_state.current_question, user_answer)
        st.session_state.scores.append(score)
        st.session_state.conversation.append(("user", user_answer))
        st.session_state.conversation.append(("ai", f"Feedback: {feedback} (Score: {score}%)"))
    
    # Check if interview should end
    if st.session_state.question_count >= 5:
        avg_score = sum(st.session_state.scores) / len(st.session_state.scores)
        st.session_state.conversation.append(("ai", f"Interview completed! Your average score: {avg_score:.1f}%"))
        return
    
    # Get next question
    next_question = get_next_question(category, user_answer)
    st.session_state.current_question = next_question
    st.session_state.conversation.append(("ai", f"Question {st.session_state.question_count + 1}: {next_question}"))
    st.session_state.question_count += 1
    st.session_state.waiting_for_answer = True

# Sidebar for configuration
with st.sidebar:
    st.header("Interview Settings")
    
    category = st.selectbox(
        "Select Question Category",
        options=["behavioral", "technical", "general"],
        index=0
    )
    
    st.header("Instructions")
    st.info("""
    1. Select a question category
    2. Click 'Start Interview' to begin
    3. Answer each question as you would in a real interview
    4. Receive immediate feedback and scores
    5. Complete all 5 questions to finish
    """)
    
    st.header("Tips for Success")
    st.markdown("""
    - Use the STAR method (Situation, Task, Action, Result)
    - Be specific with examples from your experience
    - Keep answers concise but detailed
    - Connect your skills to job requirements
    - Practice speaking aloud for real interviews
    """)
    
    if st.button("Reset Interview", type="secondary"):
        st.session_state.interview_started = False
        st.session_state.conversation = []
        st.session_state.question_count = 0
        st.session_state.scores = []
        st.session_state.waiting_for_answer = False
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h2 class="section-header">Interview Practice</h2>', unsafe_allow_html=True)
    
    # Display conversation
    if st.session_state.conversation:
        for speaker, message in st.session_state.conversation:
            if speaker == "ai":
                st.chat_message("assistant").markdown(f"**Interviewer**: {message}")
            else:
                st.chat_message("user").markdown(f"**You**: {message}")
    
    # Start interview or get next answer
    if not st.session_state.interview_started:
        if st.button("Start Interview", type="primary"):
            conduct_interview(category)
            st.rerun()
    elif st.session_state.waiting_for_answer:
        user_input = st.chat_input("Type your answer here...")
        if user_input:
            st.session_state.waiting_for_answer = False
            conduct_interview(category, user_input)
            st.rerun()

with col2:
    st.markdown('<h2 class="section-header">Performance</h2>', unsafe_allow_html=True)
    
    if st.session_state.scores:
        # Display current score
        current_score = st.session_state.scores[-1] if st.session_state.scores else 0
        st.metric("Latest Score", f"{current_score}%")
        
        # Display average score
        if len(st.session_state.scores) > 1:
            avg_score = sum(st.session_state.scores) / len(st.session_state.scores)
            st.metric("Average Score", f"{avg_score:.1f}%")
        
        # Progress
        st.progress(st.session_state.question_count / 5, text=f"Question {st.session_state.question_count} of 5")
        
        # Score history chart
        if len(st.session_state.scores) > 1:
            st.line_chart(st.session_state.scores)
    else:
        st.info("Complete your first question to see performance metrics")

# Footer
st.markdown("---")
st.markdown("### 🚀 Practice makes perfect! Keep honing your interview skills.")
