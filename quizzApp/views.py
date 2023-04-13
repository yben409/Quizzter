from django.shortcuts import render
from django.http.response import HttpResponse 
from rest_framework.decorators import api_view
from quizzApp.utils.summarize import generate_summary



# Create your views here.

@api_view(['POST'])
def text(request):
    sum_text = generate_summary(request.data['text'])
    return HttpResponse(sum_text)
