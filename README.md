# Deepak K V - Professional Resume Website

A modern, responsive resume showcase website with an AI-powered chatbot that answers questions about Deepak's professional background, skills, and experience.

## Features

- **Responsive Design**: Beautiful, mobile-friendly interface that works on all devices
- **Professional Resume Display**: Complete professional summary, work experience, skills, education, and achievements
- **AI-Powered Chatbot**: Interactive chatbot using OpenAI's GPT models with RAG (Retrieval Augmented Generation) to answer questions about Deepak's background
- **Modern UI/UX**: Clean, professional design with smooth animations and interactions
- **Contact Information**: Easy access to email, phone, and LinkedIn profile

## Technology Stack

### Frontend
- HTML5
- CSS3 (with custom animations and responsive design)
- Vanilla JavaScript
- Font Awesome icons

### Backend
- Python 3.11+
- Flask (web framework)
- OpenAI API (GPT-4o-mini for chatbot)
- Flask-CORS (for API access)

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- OpenAI API key (get one from https://platform.openai.com/api-keys)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mywebsite
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   PORT=5000
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the website**

   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Using the Chatbot

1. Click the blue floating chat button in the bottom-right corner
2. Type your question about Deepak's experience, skills, or background
3. Press Enter or click the send button
4. The AI assistant will respond based on the resume content

### Example Questions

- "What is Deepak's experience with GenAI?"
- "Tell me about Deepak's role at Reflections Info Systems"
- "What certifications does Deepak have?"
- "What are Deepak's technical skills?"
- "Where did Deepak study?"
- "How can I contact Deepak?"

## Project Structure

```
mywebsite/
├── index.html              # Main website HTML
├── styles.css              # Website styling
├── script.js               # Frontend JavaScript for chatbot
├── app.py                  # Flask backend with RAG system
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── Deepak Cv Aug2025_original.docx  # Original resume document
```

## Deployment

### Deploy to Production

For production deployment, you can use:

1. **Heroku**
   ```bash
   # Create Procfile
   echo "web: gunicorn app:app" > Procfile

   # Deploy
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your-key-here
   git push heroku main
   ```

2. **AWS, GCP, or Azure**
   - Use gunicorn as the WSGI server
   - Set environment variables in your platform's configuration
   - Ensure port 5000 is accessible (or configure PORT environment variable)

3. **Docker**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   ENV PORT=5000
   CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
   ```

## RAG System Architecture

The chatbot uses a simple but effective RAG (Retrieval Augmented Generation) approach:

1. **Context Loading**: The complete resume content is loaded into the system prompt
2. **Conversation Management**: Chat history is maintained for context-aware responses
3. **OpenAI Integration**: GPT-4o-mini processes queries with the resume context
4. **Response Generation**: AI generates accurate, contextual answers based on the resume

## Cost Considerations

- Using GPT-4o-mini for cost efficiency (~$0.15 per 1M input tokens, $0.60 per 1M output tokens)
- Conversation history limited to last 20 messages to control costs
- Average conversation costs approximately $0.001-0.005

## Security Notes

- Never commit `.env` file with actual API keys
- Use environment variables for sensitive configuration
- In production, implement rate limiting and authentication if needed
- Consider using a database for conversation history in production

## Customization

To customize this website for yourself:

1. Update `index.html` with your information
2. Replace resume content in `app.py` (RESUME_CONTEXT variable)
3. Modify colors in `styles.css` (CSS variables in `:root`)
4. Add your own resume document

## License

This project is open source and available for personal use.

## Contact

**Deepak K V**
- Email: d4deepakkv@gmail.com
- Phone: +91 944 6964 309
- LinkedIn: [https://www.linkedin.com/in/deepak-k-v/](https://www.linkedin.com/in/deepak-k-v/)

## Acknowledgments

- OpenAI for the GPT API
- Font Awesome for icons
- Flask framework for the backend
