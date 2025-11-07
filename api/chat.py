from flask import Flask, request, jsonify
import os
from openai import OpenAI
from datetime import datetime

app = Flask(__name__)

# Initialize OpenAI client
client = None

def init_openai():
    global client
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return False
    try:
        client = OpenAI(api_key=api_key)
        return True
    except Exception as e:
        print(f"Error initializing OpenAI: {str(e)}")
        return False

# Resume content for RAG
RESUME_CONTEXT = """
Deepak K V
Male, 35 years

Professional Summary:
Senior Data Science Architect and Leader with 12+ years of experience and love for mentoring and coaching driving AI/ML initiatives across banking, retail, and technology sectors. Proven track record of building high-performing teams, deploying production-ready models that improve business outcomes, and leading digital transformation initiatives. Expert in risk modeling, generative AI implementations, and end-to-end ML product development.

Professional Skills:
- Software: R, H20, MLR library (R), Python, Spark, SQL, SAS, Angoss Knowledge Studio, Tableau, MS Excel, Git
- Modelling Techniques: Regression, Decision Trees, Random Forest, GBM, XGBoost, ANN, RNN, CNN, LSTM, Ensemble Models
- Validation & Evaluation Techniques: Discrimination tests (KS, AR), Stability tests (CSI, PSI), Calibration tests (Normal, Binomial), Bootstrapping, Cross-validation, Information Value
- Deployment Techniques: On R via APIs, RShiny, At front end via Java & H2O, Using web/android applications
- GenAI: LLMs, ASR, TTS, Agentic frameworks (OpenAI Agents SDK / Crew / LangGraph, n8n), Hybrid RAG, GraphRAG, Triton Inferencing, vLLM, SGLang, MCP integrations, Workflow design and agentic orchestration, Prompt management, Edge deployment, LoRA finetuning, Observability and audit
- Cloud Services: GCP, Microsoft Azure
- Domain Experience:
  * Retail: Forecasting models (time series), NLP models, Computer vision models
  * Banking & Finance: Application, Multi-bureau, Behaviour and Collection scorecards for credit risk management; PD, LGD models for regulatory reporting; Forecasting models

Work Experience:

1. Reflections Info Systems – Head, Data Science (Apr 2024 – Present)
   - Managed end-to-end AI delivery cycle from proactive pitches to proposals, effort estimation, resource planning, and final delivery
   - Currently managing a direct AI team of 8 data scientists and guiding an extended team of 20–30 members
   - Lead the documentation and AI system revamp for adhering to ISO 42001 guideline and successfully acquired certification
   - Drove AI adoption across the full SDLC through workshops, training, mentoring, and LMS courses
   - LLM deployment on edge devices for SUV HUD real-time voice assistant
   - Advanced chatbot implementation on large contracts database (~1M documents) with graph-based RAG, user-level access controls, multiple retrieval workflows, Cypher query integration
   - End-to-end forecasting framework with agentic orchestration
   - Deployment of LLMs on-prem via vLLM, SGLang and Triton inferencing servers

2. Boston Institute of Analytics – Trainer, DS & AI (Jun 2025 – Present)
   - Empaneled as a trainer to deliver offline sessions on Data Science and AI
   - Conduct workshops and hands-on sessions for professionals and students

3. Upgrad – Trainer, DS & AI (Jan 2021 – May 2024)
   - Delivered 20+ Small Group Coaching batches in Data Science and Machine Learning
   - Trained students and working professionals, including senior management
   - Specialized in teaching Natural Language Processing and Deep Learning
   - Conducted large-scale masterclasses (200+ participants)
   - Designed and developed course content for ML and DL specializations

4. General Mills – Manager (Oct 2019 – Apr 2024)
   - Managed a team of five data scientists
   - Developed visualization bot for automatically generating insights from data and charts
   - Created scalable, AI-driven sales forecasting web application
   - Built AI-enabled Android app for food recipe suggestions based on images
   - Developed ontology framework for food trends using unsupervised NLP
   - Designed data-driven strategies achieving 2% top-line growth for American market

5. Capital First Limited (IDFC FIRST Bank) – Chief Manager (Sep 2018 – Oct 2019)
   - Developed statistical models for optimizing collections
   - Developed early warning and flow scorecards for multiple products
   - Developed acquisition scorecards using internal and bureau data
   - Deployed advanced models (GBM/XGBoost/ensembles) on R engine via APIs
   - Conducted NLP on unstructured text to predict probability of bounces

6. HDFC Bank Ltd. – Manager (May 2016 – Sep 2018)
   - Developed credit risk models using Decision Trees, Random Forests, and Logistic Regression
   - Validated retail and wholesale PD and LGD models
   - Developed multi-bureau models – 3× better discrimination compared to CIBIL score
   - Built LGD models on highly skewed data with 58% accuracy rate

7. Larsen & Toubro Limited – Senior Engineer (Jul 2012 – May 2014)
   - Oversaw railway signalling-related construction activities
   - Designed railway signalling plans using CAD
   - Project: Railway Construction Project at TATA Steel, Jamshedpur

Academic Qualification:
- PGDM, Finance – T. A. Pai Management Institute (2016)
- B.Tech. (Hons.) Applied Electronics & Instrumentation – Government Engineering College, Kozhikode (2012)

Achievements:
- 20+ Data Science certifications (SAS, Coursera, Pluralsight, One Fourth Labs – IIT Madras)
- Secured 1st Rank in B.Tech. (Applied Electronics & Instrumentation), Calicut University
- Selected for Govt. of Kerala tuition fee waiver (B.Tech.)

Contact:
- Email: d4deepakkv@gmail.com
- Phone: +91 944 6964 309
- LinkedIn: https://www.linkedin.com/in/deepak-k-v/
"""

SYSTEM_PROMPT = """You are an AI assistant helping visitors learn about Deepak K V's professional background, skills, and experience.
You have access to Deepak's complete resume and should answer questions accurately based on this information.

Be professional, friendly, and concise in your responses. If asked about something not in the resume, politely mention that you don't have that information.

Here is Deepak's complete resume:

{resume_context}

Answer questions about Deepak's:
- Professional experience and roles
- Technical skills and expertise
- Education and qualifications
- Achievements and certifications
- Contact information
- Projects and accomplishments
"""

# In-memory conversation storage (Note: Vercel serverless is stateless, so this resets between invocations)
conversations = {}

def handler(request):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405

    if not client:
        if not init_openai():
            return jsonify({
                'response': 'OpenAI API is not configured. Please set the OPENAI_API_KEY environment variable.'
            }), 500

    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id', datetime.now().strftime("%Y%m%d%H%M%S"))

        if not user_message:
            return jsonify({'response': 'Please provide a message.'}), 400

        # Get or create conversation history
        if conversation_id not in conversations:
            conversations[conversation_id] = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT.format(resume_context=RESUME_CONTEXT)
                }
            ]

        # Add user message to history
        conversations[conversation_id].append({
            "role": "user",
            "content": user_message
        })

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversations[conversation_id],
            temperature=0.7,
            max_tokens=500
        )

        assistant_message = response.choices[0].message.content

        # Add assistant response to history
        conversations[conversation_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        # Keep conversation history manageable
        if len(conversations[conversation_id]) > 21:
            conversations[conversation_id] = [conversations[conversation_id][0]] + conversations[conversation_id][-20:]

        return jsonify({
            'response': assistant_message,
            'conversation_id': conversation_id
        }), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'response': f'Sorry, I encountered an error: {str(e)}'
        }), 500

# For Vercel serverless
def main(request):
    with app.request_context(request.environ):
        try:
            return handler(request)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# For local testing
if __name__ == '__main__':
    init_openai()
    app.run(debug=True)
