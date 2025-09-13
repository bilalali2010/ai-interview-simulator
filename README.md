# AI Interview Simulator 🤖🎤

A free, open-source AI interview simulator built with Streamlit. Practice your interview skills without any API keys or costs.

## Important Note

This app uses Hugging Face transformers which require significant resources. If deployment fails due to memory issues, the app will gracefully fall back to simplified analysis without the AI components.

## Features

- **Multiple Question Types**: Behavioral, technical, and general questions
- **Smart Feedback**: Get analysis on your answers with performance scoring
- **Follow-up Questions**: Context-aware follow-up questions
- **Streamlit Deployment**: Ready to deploy on Streamlit Cloud
- **Graceful Fallbacks**: Works even if AI models can't load

## Deployment on Streamlit

1. Fork this repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select your repository
5. Set the main file path to `app.py`
6. Click "Deploy"

## Local Development

```bash
git clone https://github.com/your-username/ai-interview-simulator.git
cd ai-interview-simulator
pip install -r requirements.txt
streamlit run app.py
