from django.urls import path
from . import views

app_name = "chatbot_app"

urlpatterns = [
    #Main Chat endpoint

    path('chat/', views.chat, name='chat'),

    #Conversation Management 
    path('conversations/', views.get_conversation, name='get_conversation'),
    path('conversations/create', views.create_conversation, name='create_conversation'),
    path('conversations/<uuid:conversation_id>/', views.get_conversation, name='get_conversation'),
    path('conversations/<uuid:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),

    #AI Models
    path('models/', views.get_ai_models, name='get_ai_models'),

    # Educational Contents
    path('examples/', views.get_educational_examples, name='get_educational_examples'),

]