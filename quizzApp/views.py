from django.shortcuts import render
from django.http.response import HttpResponse ,HttpResponseNotFound
from rest_framework.decorators import api_view
from quizzApp.utils.summarize import generate_summary
from quizzApp.utils.MCQ import MCQ_output
from quizzApp.utils.fill_in_blanks import fill_in_blanks
from quizzApp.utils.paraphrase import generate_paraphrase
from quizzApp.utils.pdf_to_text import read_pdf
from quizzApp.utils.link_scraper import link_scraper



# Create your views here.
@api_view(['POST'])
def modify(request , func):
    text = request.data['text']
    if(text!=""):
        if func == "summarize":
            sum_text = generate_summary(text.replace('\n',''))
        elif func == "rephrase":
            sum_text = generate_paraphrase(text.replace('\n',''))
        elif func ==  "quiz":
            sum_text =  "Fill in the blanks :\n" + fill_in_blanks(text)+ "\nMCQ :\n"+ MCQ_output(text)
             ##sum_text = sum_text + fill_in_blanks(text)

        else:
            return HttpResponseNotFound("Not found")
        return HttpResponse(sum_text)
    else:
        return HttpResponse("Nul value").status_code(400)

@api_view(['PUT'])
def pdf_to_text(request):
    pdf = request.FILES.get('pdfFile')
    if pdf :
        text = read_pdf(pdf)
        return HttpResponse(text)
    else:
       return  HttpResponse("Nul value").status_code(400)

@api_view(['POST'])
def link_to_text(request):
    link = request.data['link']
    if link :
        text = link_scraper(link)
        return HttpResponse(text)
    else:
       return  HttpResponse("Nul value").status_code(400)