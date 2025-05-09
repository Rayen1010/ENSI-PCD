from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
import pymysql
from langchain_experimental.sql import SQLDatabaseChain
from langchain_groq import ChatGroq
from langchain.prompts import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.sql_database.prompt import PROMPT_SUFFIX, _mysql_prompt
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import SemanticSimilarityExampleSelector
from sqlalchemy import text
import random

from starlette.responses import HTMLResponse

# LLM initialization
llm = ChatGroq(
    temperature=0,
    groq_api_key='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',
    model_name="llama3-70b-8192"
)

# Database connection
password = "95369727aA@"
DATABASE_URL = URL.create(
    "mysql+pymysql",
    host="localhost",
    username="root",
    password=password,
    database="products"
)

engine = create_engine(DATABASE_URL)
db = SQLDatabase(engine)

examples = [
    {
        "Question": "What are the top 5 products by price?",
        "SQLQuery": "SELECT `reference`, `product_name`, `prix` FROM products ORDER BY `prix` DESC LIMIT 5;",
        "SQLResult": "[('REF005', 'Savon liquide pour mains 500ml', Decimal('4.20')), ('REF004', 'Jus d'orange 1L', Decimal('3.50')), ('REF001', 'Lait demi-écrémé 1L', Decimal('2.00')), ('REF003', 'Yaourt à la fraise (x4)', Decimal('1.80')), ('REF002', 'Eau minérale 1.5L', Decimal('1.20'))]",
        "Answer": "The top 5 products by price are:\n1. Savon liquide pour mains 500ml - 4.20\n2. Jus d'orange 1L - 3.50\n3. Lait demi-écrémé 1L - 2.00\n4. Yaourt à la fraise (x4) - 1.80\n5. Eau minérale 1.5L - 1.20"
    },
    {
        "Question": "What are the most sold products?",
        "SQLQuery": "SELECT `product_name`, SUM(`quantity`) FROM sales GROUP BY `product_name` ORDER BY SUM(`quantity`) DESC;",
        "SQLResult": "[('Savon liquide pour mains 500ml', Decimal('150.00')), ('Jus d'orange 1L', Decimal('120.00')), ('Lait demi-écrémé 1L', Decimal('100.00'))]",
        "Answer": "The most sold products are:\n1. Savon liquide pour mains 500ml - 150 units sold\n2. Jus d'orange 1L - 120 units sold\n3. Lait demi-écrémé 1L - 100 units sold"
    },
    {
        "Question": "What's the price of milk?",
        "SQLQuery": "SELECT `product_name`, `prix` FROM products WHERE `product_name` LIKE '%lait%';",
        "SQLResult": "[('Lait demi-écrémé 1L', Decimal('2.00'))]",
        "Answer": "The price of Lait demi-écrémé 1L is 2.00."
    }
]

embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

to_vectorize = [" ".join(example.values()) for example in examples]
vectorstore = Chroma.from_texts(to_vectorize, embeddings, metadatas=examples)

_mysql_prompt = """
You are a helpful chatbot for an online store. Your role is to assist clients by answering their questions about products, inventory, and prices.
The final result and the answer should be based only on the SQLResult. You just see the sql result and form a phrase based on the question that's it. 
""" + _mysql_prompt

example_selector = SemanticSimilarityExampleSelector(
    vectorstore=vectorstore,
    k=2,
)

example_prompt = PromptTemplate(
    input_variables=["Question", "SQLQuery", "SQLResult", "Answer"],
    template="\nQuestion: {Question}\nSQLQuery: {SQLQuery}\nSQLResult: {SQLResult}\nAnswer: {Answer}",
)

few_shot_prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix=_mysql_prompt,
    suffix=PROMPT_SUFFIX,
    input_variables=["input", "table_info", "top_k"],
)

db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True, prompt=few_shot_prompt)

# Assuming your db_chain, engine, etc. are imported or in the same file
app = FastAPI()

# Enable CORS (if you want to connect a frontend like React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str



# Add this before your other endpoints
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
   <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Magazine Store Assistant</title>
    <style>
        :root {
            --primary-color: #4a6fa5;
            --secondary-color: #166088;
            --background-color: #f5f7fa;
            --bot-bubble: #e9ecef;
            --user-bubble: #4a6fa5;
            --text-dark: #333;
            --text-light: #fff;
            --shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: var(--background-color);
            color: var(--text-dark);
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: var(--shadow);
            overflow: hidden;
        }

        header {
            background-color: var(--primary-color);
            color: var(--text-light);
            padding: 20px;
            text-align: center;
        }

        h1 {
            font-size: 1.8rem;
            margin-bottom: 5px;
        }

        .subtitle {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .chat-container {
            height: 500px;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }

        .message {
            max-width: 80%;
            padding: 12px 16px;
            margin-bottom: 15px;
            border-radius: 18px;
            position: relative;
            word-wrap: break-word;
        }

        .bot-message {
            background-color: var(--bot-bubble);
            align-self: flex-start;
            border-bottom-left-radius: 5px;
        }

        .user-message {
            background-color: var(--user-bubble);
            color: var(--text-light);
            align-self: flex-end;
            border-bottom-right-radius: 5px;
        }

        .typing-indicator {
            display: inline-flex;
            padding: 12px 16px;
            background-color: var(--bot-bubble);
            border-radius: 18px;
            align-self: flex-start;
            margin-bottom: 15px;
            border-bottom-left-radius: 5px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background-color: #666;
            border-radius: 50%;
            margin: 0 3px;
            animation: typingAnimation 1.4s infinite ease-in-out;
        }

        .typing-dot:nth-child(1) {
            animation-delay: 0s;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typingAnimation {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-5px);
            }
        }

        .input-area {
            display: flex;
            padding: 15px;
            background-color: #fff;
            border-top: 1px solid #eee;
        }

        #question {
            flex: 1;
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
            font-size: 1rem;
            transition: border 0.3s;
        }

        #question:focus {
            border-color: var(--primary-color);
        }

        #ask-btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0 20px;
            margin-left: 10px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s;
        }

        #ask-btn:hover {
            background-color: var(--secondary-color);
        }

        .error-message {
            color: #d9534f;
            background-color: #f8d7da;
            padding: 12px 16px;
            border-radius: 18px;
            margin-bottom: 15px;
            align-self: flex-start;
            border-bottom-left-radius: 5px;
        }

        .suggestions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }

        .suggestion-btn {
            background-color: #e9ecef;
            border: none;
            border-radius: 15px;
            padding: 8px 12px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
        }

        .suggestion-btn:hover {
            background-color: #d1d7dc;
        }

        .welcome-message {
            text-align: center;
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }

        @media (max-width: 600px) {
            .container {
                border-radius: 0;
            }
            
            .chat-container {
                height: 70vh;
            }
            
            .message {
                max-width: 90%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Store Assistant</h1>
            <p class="subtitle">Ask me anything about our products and services</p>
        </header>

        <div class="chat-container" id="chat-container">
            <div class="welcome-message">
                <p>Hello! I'm your  Store Assistant. How can I help you today?</p>
                <div class="suggestions">
                    <button class="suggestion-btn" onclick="insertSuggestion('Any current offers?')">Any current offers?</button>
                    <button class="suggestion-btn" onclick="insertSuggestion('Do you offer subscriptions?')">Do you offer subscriptions?</button>
                    <button class="suggestion-btn" onclick="insertSuggestion('What are your opening hours?')">Opening hours?</button>
                </div>
            </div>
            <!-- Chat messages will appear here -->
        </div>

        <div class="input-area">
            <input type="text" id="question" placeholder="Type your question here..." autocomplete="off">
            <button id="ask-btn" onclick="ask()">Send</button>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const questionInput = document.getElementById('question');
        const askBtn = document.getElementById('ask-btn');

        // Allow pressing Enter to send message
        questionInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                ask();
            }
        });

        function insertSuggestion(text) {
            questionInput.value = text;
            questionInput.focus();
        }

        async function ask() {
            const question = questionInput.value.trim();
            
            if (!question) return;
            
            // Add user message to chat
            addMessageToChat(question, 'user');
            questionInput.value = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            try {
                const response = await fetch("http://127.0.0.1:8000/ask", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question }),
                });
                
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                
                const data = await response.json();
                
                // Remove typing indicator
                removeTypingIndicator();
                
                // Add bot response to chat
                if (data.response) {
                    addMessageToChat(data.response, 'bot');
                } else if (data.error) {
                    addErrorMessage(data.error);
                } else {
                    addErrorMessage("Sorry, I couldn't understand that. Could you try rephrasing your question?");
                }
                
            } catch (error) {
                removeTypingIndicator();
                addErrorMessage("Sorry, I'm having trouble connecting right now. Please try again later.");
                console.error('Error:', error);
            }
        }

        function addMessageToChat(message, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
            messageDiv.classList.add(sender === 'bot' ? 'bot-message' : 'user-message');
            messageDiv.textContent = message;
            chatContainer.appendChild(messageDiv);
            scrollToBottom();
        }

        function addErrorMessage(message) {
            const errorDiv = document.createElement('div');
            errorDiv.classList.add('error-message');
            errorDiv.textContent = message;
            chatContainer.appendChild(errorDiv);
            scrollToBottom();
        }

        function showTypingIndicator() {
            const typingDiv = document.createElement('div');
            typingDiv.classList.add('typing-indicator');
            typingDiv.id = 'typing-indicator';
            typingDiv.innerHTML = `
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            `;
            chatContainer.appendChild(typingDiv);
            scrollToBottom();
        }

        function removeTypingIndicator() {
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }

        function scrollToBottom() {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Initial greeting from bot
        setTimeout(() => {
            addMessageToChat("Hi there! I can help you with information about our collection, subscriptions, store hours, and more. What would you like to know?", 'bot');
        }, 1000);
    </script>
</body>
</html>

    """


@app.post("/ask")
def ask_question(query: Query):
    try:
        question = query.question.lower().strip()

        # Handle thanks/gratitude
        if any(word in question for word in ["thank", "thanks", "appreciate"]):
            return {
                "response": "You're welcome! We're always happy to help at our store. "
                           "Let us know if you have any other questions."
            }

        # Handle specific calculation

        # Handle specific questions directly
        if "subscription" in question or "subscribe" in question:
            return {
                "response": "Yes! We offer monthly and yearly subscriptions. "
                           "Monthly: $10/month (10% discount)\n"
                           "Yearly: $100/year (20% discount)\n"
                           "You can subscribe in-store or on our website."
            }

        elif "opening hour" in question or "open" in question or "close" in question or "hour" in question:
            return {
                "response": "Our store hours are:\n\n"
                           "Monday-Friday: 9:00 AM - 7:00 PM\n"
                           "Saturday: 10:00 AM - 6:00 PM\n"
                           "Sunday: 11:00 AM - 5:00 PM"
            }

        # For all other questions, use your existing db_chain
        response = db_chain.run(query.question)
        return {"response": response}

    except Exception as e:
        return {"error": str(e)}