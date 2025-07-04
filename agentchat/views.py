from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import re
from .utils import openai_chat, detect_intent
from .agent import news_summary_agent

# Create your views here.

@csrf_exempt
def agent_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            intent = detect_intent(user_message)
            if intent.get('intent') == 'news':
                country = intent.get('country', 'france')
                result = news_summary_agent(country)
                return JsonResponse({'response': result['summary'], 'trace': result['trace'], 'sources': result['sources']})
            else:
                agent_response = openai_chat(user_message)
                return JsonResponse({'response': agent_response, 'trace': []})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'POST request required'}, status=405)
