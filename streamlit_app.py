import streamlit as st
import random

# Page configuration
st.set_page_config(
    page_title="AI Interview Simulator",
    page_icon="🎤",
    layout="wide"
)

# App header
st.title("🎤 AI Interview Simulator")
st.write("Practice your interview skills with this lightweight simulator!")

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""

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
feedback_phrases = [
    "Good answer! You provided specific examples.",
    "Well done! You demonstrated relevant skills.",
    "Nice job structuring your answer clearly.",
    "Good response showing self-awareness.",
    "You connected your experience to the role well."
]

# Function to analyze answer quality (simple version)
def analyze_answer(answer):
    if not answer.strip():
        return "Please provide a more detailed answer.", 50
    
    word_count = len(answer.split())
    
    if word_count < 20:
        return "Your answer is quite brief. Try to provide more detail.", 60
    elif word_count > 150:
        return "Your answer is quite long. Try to be more concise.", 70
    else:
        return random.choice(feedback_phrases), 80

# Function to get next question
def get_next_question(category):
    return random.choice(interview_questions[category])

# Function to handle interview process
def conduct_interview(category, user_answer=None):
    if not st.session_state.interview_started:
        st.session_state.interview_started = True
        st.session_state.question_count = 0
        st.session_state.conversation = []
    
    if user_answer:
        # Analyze the user's answer
        feedback, score = analyze_answer(user_answer)
        st.session_state.conversation.append(("user", user_answer))
        st.session_state.conversation.append(("ai", f"Feedback: {feedback} (Score: {score}%)"))
    
    # Check if interview should end
    if st.session_state.question_count >= 3:  # Reduced to 3 questions for simplicity
        st.session_state.conversation.append(("ai", "Interview completed! Great job practicing!"))
        return
    
    # Get next question
    next_question = get_next_question(category)
    st.session_state.current_question = next_question
    st.session_state.conversation.append(("ai", f"Question {st.session_state.question_count + 1}: {next_question}"))
    st.session_state.question_count += 1

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
    3. Answer each question
    4. Receive feedback
    5. Complete all 3 questions to finish
    """)
    
    if st.button("Reset Interview"):
        st.session_state.interview_started = False
        st.session_state.conversation = []
        st.session_state.question_count = 0
        st.rerun()

# Main content area
st.header("Interview Practice")

# Display conversation
if st.session_state.conversation:
    for speaker, message in st.session_state.conversation:
        if speaker == "ai":
            st.write(f"**Interviewer**: {message}")
        else:
            st.write(f"**You**: {message}")

# Start interview or get next answer
if not st.session_state.interview_started:
    if st.button("Start Interview"):
        conduct_interview(category)
        st.rerun()
elif st.session_state.question_count < 3:
    user_input = st.text_input("Type your answer here:", key="answer_input")
    if user_input:
        conduct_interview(category, user_input)
        st.rerun()

# Progress indicator
if st.session_state.interview_started:
    st.progress(st.session_state.question_count / 3)
    st.write(f"Question {st.session_state.question_count} of 3 completed")

# Footer
st.write("---")
st.write("### Keep practicing to improve your interview skills!")
