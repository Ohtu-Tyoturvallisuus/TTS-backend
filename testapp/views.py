from django.http import HttpResponse


def index(request):
    return HttpResponse("Tämä on työturvallisuus-sovelluksen django app")