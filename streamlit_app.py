import streamlit as st
import random
import re
import numpy as np
from datetime import datetime
import requests
import json

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
st.markdown("### Practice your interview skills - No heavy dependencies!")

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

# Interview questions database
interview_questions = {
    "behavioral": [
        "Tell me about a time you had to overcome a challenge.",
        "Describe a situation where you had to work with a difficult team member.",
        "Tell me about a time you failed and what you learned from it.",
        "Describe a project where you had to take initiative.",
        "Tell me about a time you had to meet a tight deadline.",
        "Describe a time you had to persuade someone to see things your way.",
        "Tell me about a time you had to adapt to a significant change at work.",
        "Describe a situation where you had to make a difficult decision.",
        "Tell me about a time you went above and beyond your job responsibilities.",
        "Describe a time you had to resolve a conflict within your team."
    ],
    "technical": [
        "What programming languages are you most comfortable with?",
        "How do you approach debugging a complex problem?",
        "Describe your experience with version control systems.",
        "What development methodologies are you familiar with?",
        "How do you stay updated with the latest technology trends?",
        "Describe your experience with database management systems.",
        "What testing frameworks have you worked with?",
        "How do you ensure code quality in your projects?",
        "Describe your experience with cloud platforms.",
        "What's your approach to learning new technologies?"
    ],
    "general": [
        "Tell me about yourself.",
        "What are your strengths and weaknesses?",
        "Where do you see yourself in 5 years?",
        "Why do you want to work at our company?",
        "What motivates you at work?",
        "How do you handle stress or pressure?",
        "What's your ideal work environment?",
        "Describe your leadership style.",
        "What are your salary expectations?",
        "Do you have any questions for me?"
    ]
}

# Feedback phrases
positive_feedback = [
    "Great answer! You provided specific examples which really strengthen your response.",
    "Excellent! You demonstrated relevant skills and experience.",
    "Well done! You structured your answer clearly and concisely.",
    "Good response! You showed self-awareness and growth mindset.",
    "Nice job! You connected your experience directly to the role.",
    "Impressive answer! You provided concrete examples that showcase your abilities.",
    "Strong response! You effectively highlighted your achievements.",
    "Well articulated! You communicated your thoughts clearly and effectively."
]

improvement_feedback = [
    "Consider providing a more specific example to illustrate your point.",
    "Try to structure your answer using the STAR method (Situation, Task, Action, Result).",
    "You might want to focus more on your role and contributions in that situation.",
    "Consider connecting your answer more directly to the job requirements.",
    "Try to be more concise while still providing enough detail.",
    "Consider quantifying your achievements with numbers or metrics.",
    "Try to focus more on the positive outcomes of the situation.",
    "You might want to elaborate more on what you learned from that experience."
]

# Follow-up questions database
follow_up_questions = {
    "behavioral": [
        "Can you tell me more about what you learned from that experience?",
        "How would you handle a similar situation differently today?",
        "What was the most challenging aspect of that situation?",
        "How did others respond to your actions?",
        "What feedback did you receive about your approach?"
    ],
    "technical": [
        "Could you elaborate on your technical approach to that problem?",
        "What alternative solutions did you consider?",
        "How did you validate that your solution was correct?",
        "What tools or technologies did you use in that situation?",
        "How would you improve that solution today?"
    ],
    "general": [
        "How did that experience prepare you for this role?",
        "Can you give me another example that demonstrates that skill?",
        "What specifically interests you about our company?",
        "How does that strength help you in your work?",
        "What steps are you taking to improve that weakness?"
    ]
}

# Function to generate follow-up questions (without transformers)
def generate_followup_question(answer, question_type):
    # Simple algorithm to generate follow-up questions based on answer content
    answer_lower = answer.lower()
    
    # Check for specific keywords to determine appropriate follow-up
    if any(word in answer_lower for word in ['learn', 'learned', 'realized', 'understand']):
        return "What was the most important lesson you learned from that experience?"
    
    if any(word in answer_lower for word in ['challenge', 'difficult', 'hard', 'struggle']):
        return "What made that situation particularly challenging for you?"
    
    if any(word in answer_lower for word in ['success', 'achieved', 'accomplished', 'result']):
        return "How did you measure the success of that outcome?"
    
    if any(word in answer_lower for word in ['team', 'colleague', ' coworker', 'partner']):
        return "How did your team members contribute to this outcome?"
    
    if any(word in answer_lower for word in ['time', 'schedule', 'deadline', 'timeline']):
        return "How did you manage your time to meet that deadline?"
    
    # Default to a random follow-up question from the database
    return random.choice(follow_up_questions[question_type])

# Function to analyze answer quality (without transformers)
def analyze_answer(question, answer):
    if not answer.strip():
        return "Please provide a more detailed answer.", 0
    
    # Calculate basic metrics
    word_count = len(answer.split())
    sentence_count = len(re.findall(r'[.!?]+', answer))
    
    # Simple content analysis using regex patterns
    has_example = bool(re.search(r'(example|for instance|such as|experience|project|when|time)', answer.lower()))
    has_action = bool(re.search(r'(i did|i implemented|i created|i developed|i led|i organized|i managed|my role|my responsibility)', answer.lower()))
    has_result = bool(re.search(r'(result|outcome|achieved|accomplished|succeeded|improved|increased|reduced|saved)', answer.lower()))
    has_positive = bool(re.search(r'(success|achievement|proud|happy|satisfied|learned|growth|improved|better)', answer.lower()))
    
    # Score calculation
    score = 0
    feedback = ""
    
    # Word count scoring
    if word_count < 20:
        feedback += "Your answer is quite brief. Try to provide more detail. "
        score += 2
    elif word_count > 200:
        feedback += "Your answer is quite long. Try to be more concise while still providing key details. "
        score += 3
    else:
        feedback += "Good length for your answer. "
        score += 4
    
    # Content scoring
    if has_example:
        feedback += "Good job providing specific examples. "
        score += 3
    
    if has_action:
        feedback += "You clearly described your actions and role. "
        score += 3
    
    if has_result:
        feedback += "You effectively discussed results and outcomes. "
        score += 3
    
    if has_positive:
        feedback += "You maintained a positive tone. "
        score += 2
    
    # Check for STAR method components
    star_components = 0
    if has_example:
        star_components += 1
    if has_action:
        star_components += 1
    if has_result:
        star_components += 1
    
    if star_components >= 2:
        feedback += "You're using elements of the STAR method effectively. "
        score += 2
    else:
        feedback += "Try using the STAR method (Situation, Task, Action, Result) to structure your answers. "
    
    # Convert to percentage
    score_percent = min(100, int((score / 20) * 100))
    
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
    if user_answer and st.session_state.question_count > 0 and random.random() < 0.6:
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
        st.session_state.waiting_for_answer = False
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
    - **Use the STAR method**: Situation, Task, Action, Result
    - **Be specific**: Provide concrete examples from your experience
    - **Be concise**: Keep answers focused but detailed
    - **Connect to the role**: Relate your skills to job requirements
    - **Practice aloud**: Simulate real interview conditions
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
        if st.button("Start Interview", type="primary", use_container_width=True):
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
            # Create a simple line chart using st.line_chart
            chart_data = {"Score": st.session_state.scores}
            st.line_chart(chart_data)
            
        # Tips based on performance
        if current_score < 60:
            st.info("💡 Tip: Try to provide more specific examples and use the STAR method.")
        elif current_score < 80:
            st.info("💡 Tip: Good job! Focus on connecting your answers to the job requirements.")
        else:
            st.success("💡 Tip: Excellent! You're demonstrating strong interview skills.")
    else:
        st.info("Complete your first question to see performance metrics")

# Footer
st.markdown("---")
st.markdown("### 🚀 Practice makes perfect! Keep honing your interview skills.")
