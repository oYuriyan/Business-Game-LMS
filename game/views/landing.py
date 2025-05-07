from django.shortcuts import render

def landing_page_view(request):
    #Exibe a página institucional de entrada com apresentação do projeto e chamada para ação.
    
    return render(request, 'landing.html')