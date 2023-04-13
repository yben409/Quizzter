from django.urls import path
from quizzApp import views

urlpatterns = [
    path('api/text/<str:func>', views.modify),
    path('api/pdftotext' , views.pdf_to_text),
    path('api/linktotext' , views.link_to_text)

]