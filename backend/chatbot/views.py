from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import ChatMessage
import requests
import os

# Load API key and model from env variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot_query(request):
    user_message = request.data.get('message', '').strip()
    if not user_message:
        return Response({"error": "No message provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Save user message
    ChatMessage.objects.create(user_message=user_message)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Base system prompt instructing the model
    system_prompt = (
       "You are a helpful Barangay Official of Barangay Sindalan. "
        "If asked about a person or topic you don't have information on, "
        "please respond politely that you don't have that information instead of guessing."
        "Answer only about government services, complaints, permits, announcements, and community events."
    )

    # Build messages payload for the chat completion API
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    # Optionally, to add conversation history uncomment below and implement session history retrieval
    # conversation_history = get_conversation_history_for_session(request)  # Your method here
    # messages = [ {"role": "system", "content": system_prompt} ] + conversation_history + [ {"role": "user", "content": user_message} ]

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        reply = data['choices'][0]['message']['content'].strip()

        # Save bot reply
        ChatMessage.objects.create(user_message=user_message, bot_reply=reply)

        return Response({"reply": reply})

    except requests.exceptions.RequestException as e:
        # Log error (add your logging here)
        error_msg = f"Error calling Groq API: {str(e)}"
        return Response({"error": error_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
