from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .models import conversations, Message, AIModel

from .serializers import (
    ConversationSerializer, MessageSerializer, ChatRequestSerializer, 
    ChatResponseSerializer, AIModelSerializer
)

from .services import OpenAIService
import uuid
# Create your views here.

@api_view(['POST'])
def chat(request):
     """
    Main chat endpoint.
    Handles user messages and returns AI responses.
    
    Educational Note: This demonstrates how to:
    1. Validate incoming data
    2. Manage conversation context
    3. Integrate with external AI services
    4. Handle errors gracefully
    """
     serializer = ChatRequestSerializer(data=request.data)
     if not serializer.is_valid():
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
     data = serializer.validated_data
     user_message = data['message']
     conversation_id = data.get('conversation_id')
     model_name = data.get('model_name','gpt-3.5-turbo')
     temperature = data.get('temperature', 0.7)
     max_tokens = data.get('max_tokens', 150)

     # Get or create Conversation

     if conversation_id:
          try:
               conversation = get_object_or_404(conversation, id=conversation_id)
          except:
               return Response(
                    {'error':'Conversation Not Found'}
                    status=HTTP_400_BAD_REQUEST
               )
     else:
           conversation = conversation.objects.create(
                title = user_message[:50] + ".." if len(user_message) > 50 else user_message
           )
     
     # Save User Message
     user_msg = Message.objects.create(
          conversation = conversation,
          role='user',
          content = user_message
     )
     
     #Initialize OpenAI Service 

     openai_service = OpenAIService()

     messages = conversation.messages.all()
     context = openai_service.prepare_conversation_context(
          messages,
          system_prompt = openai_service.get_educational_prompt()['default']
     )

     #Get AI Response
     ai_response = openai_service.get_response(
          context,
          model = model_name,
          temperature = temperature,
          max_tokens = max_tokens
     )

     if not ai_response['success']:
          return Response(
                    {'error': ai_response['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
               )
     
     # Save AI Response
     ai_msg = Message.objects.create(
          conversation = conversation,
          role = 'assistant',
          content = ai_response['response'],
          token_count = ai_response.get('usage', {}).get('total_tokens', 0)
     )

     # Update Conversation Timestamp
     conversation.save()

     response_data = {
          'conversation_id': conversation.id,
          'response': ai_response['response'],
          'message_id': ai_msg.id,
          'token_usage': ai_response.get('usage', {}),
          'model_used': ai_response.get('model', model_name)
     }

     return Response(response_data, status=status.HTTP_200_OK)


     
