from django.urls import path
from .views import agent_chat

urlpatterns = [
    path('api/agent-chat/', agent_chat, name='agent_chat'),
] 