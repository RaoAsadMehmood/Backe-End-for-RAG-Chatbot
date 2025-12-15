#!/usr/bin/env python3
"""
Test script to verify that the RAG chatbot properly handles general questions
while maintaining focus on book content.
"""

import os
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
from agents import set_tracing_disabled, function_tool
import cohere
from qdrant_client import QdrantClient

# Load environment variables
load_dotenv()
set_tracing_disabled(disabled=True)

# Initialize OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

provider = AsyncOpenAI(api_key=openai_api_key)
model = OpenAIChatCompletionsModel(
    model="gpt-4o-mini",
    openai_client=provider
)

# Initialize Cohere and Qdrant
cohere_client = cohere.Client(os.getenv("COHERE_API_KEY"))
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

def get_embedding(text):
    """Get embedding vector from Cohere Embed v3"""
    response = cohere_client.embed(
        model=os.getenv("EMBED_MODEL", "embed-english-v3.0"),
        input_type="search_query",
        texts=[text],
    )
    return response.embeddings[0]

@function_tool
def retrieve(query):
    embedding = get_embedding(query)
    result = qdrant_client.query_points(
        collection_name=os.getenv("COLLECTION_NAME", "physical_ai_book"),
        query=embedding,
        limit=5
    )
    return [point.payload["text"] for point in result.points]

# Create agent with updated instructions
agent = Agent(
    name="Assistant for Physical AI & Humanoid Robotics",
    instructions="""
You are a concise AI tutor for Physical AI and Humanoid Robotics. Your primary role is to answer questions using retrieved textbook content about Physical AI and Humanoid Robotics.

**CRITICAL: Be CONCISE to minimize API costs:**
- Keep responses brief and direct - avoid unnecessary words
- Use bullet points instead of long paragraphs when possible
- Get straight to the answer without lengthy introductions
- Avoid repetition and redundant explanations
- Limit responses to 2-4 sentences for simple questions, max 1-2 paragraphs for complex ones

**Process:**
1. For questions about Physical AI, Humanoid Robotics, or related topics: Use `retrieve` tool first and base answers on retrieved content
2. For general questions like "who are you", "how are you", "what can you do": Respond briefly with your identity and redirect to book topics
3. For questions unrelated to the textbook: Briefly acknowledge and encourage questions about Physical AI & Humanoid Robotics
4. If textbook information unavailable for topic-specific questions, say: "Not found in textbook. Try rephrasing or ask about Physical AI/Humanoid Robotics concepts."

**Identity & Purpose:**
- You are an AI assistant specializing in Physical AI and Humanoid Robotics
- You were created to help users learn about Physical AI and Humanoid Robotics from the textbook
- You can only provide information that is in the textbook content

**Examples of appropriate responses to general questions:**
- "Who are you?": "I'm an AI tutor specializing in Physical AI and Humanoid Robotics. I can help you understand concepts from the textbook. What would you like to learn about Physical AI or Humanoid Robotics?"
- "How are you?": "I'm functioning well, thank you! I'm here to help you learn about Physical AI and Humanoid Robotics. Would you like to explore a concept from the textbook?"
- "What can you do?": "I can explain concepts about Physical AI and Humanoid Robotics based on the textbook. Ask me anything about these topics!"

**Style:**
- Direct and factual
- No fluff or filler words
- Essential information only
- Professional but brief
- Always redirect to book-related topics after brief general responses
""",
    model=model,
    tools=[retrieve]
)

# Test general questions
test_questions = [
    "Who are you?",
    "How are you?",
    "What can you do?",
    "Tell me about yourself",
    "What is your purpose?",
    "Explain quantum physics",
    "What's the weather like today?",
    # These should trigger textbook search
    "What is Physical AI?",
    "Explain humanoid robotics",
    "How do robots learn?"
]

print("Testing the RAG chatbot's response to general questions...\n")

for question in test_questions:
    print(f"Question: {question}")
    try:
        result = Runner.run_sync(
            agent,
            input=question
        )
        print(f"Response: {result.final_output}")
    except Exception as e:
        print(f"Error: {str(e)}")
    print("-" * 80)