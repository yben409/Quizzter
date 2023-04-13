from django.shortcuts import render
from django.http.response import HttpResponse ,Http404
from rest_framework.decorators import api_view
from quizzApp.utils.summarize import generate_summary
from quizzApp.utils.MCQ import MCQ_output
from quizzApp.utils.fill_in_blanks import fill_in_blanks
from quizzApp.utils.paraphrase import generate_paraphrase




# Create your views here.
@api_view(['POST'])
def modify(request , func):
    text = request.data['text']
    if(text!=""):
        if func == "summarize":
            sum_text = generate_summary(text)
        elif func == "rephrased":
            sum_text = generate_paraphrase(text)
        elif func ==  "quiz":
            sum_text = MCQ_output(text)
            sum_text += '\n' 
            sum_text +=  fill_in_blanks(text)

        else:
            return HttpResponse("Not found" , status_code=404)
        return HttpResponse(sum_text)
    else:
        return HttpResponse("Nul value" , status_code=400)

@api_view(['POST'])
def pdf_to_text(request):
    return HttpResponse('text pdf here')

@api_view(['POST'])
def link_to_text(request):
    return HttpResponse('link pdf here')