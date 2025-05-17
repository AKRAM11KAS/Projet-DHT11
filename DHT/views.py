from django.shortcuts import render
from .models import Dht11  # Assurez-vous d'importer le modèle Dht11
from django.utils import timezone
import csv
from django.http import HttpResponse
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import logout

from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout



# Page d'accueil
def home(request):
    return render(request, 'home.html')


# Dernière valeur dans value.html
def table(request):
    derniere_ligne = Dht11.objects.last()
    if not derniere_ligne:
        return HttpResponse("Aucune donnée disponible.")

    delta_temps = timezone.now() - derniere_ligne.dt
    minutes = delta_temps.seconds // 60
    temps_ecoule = f"il y a {minutes} min"
    if minutes > 60:
        temps_ecoule = f"il y a {minutes // 60}h{minutes % 60}min"

    valeurs = {
        'date': temps_ecoule,
        'id': derniere_ligne.id,
        'temp': derniere_ligne.temp,
        'hum': derniere_ligne.hum
    }
    return render(request, 'value.html', {'valeurs': valeurs})


# Téléchargement CSV
def download_csv(request):
    data = Dht11.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dht.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'temp', 'hum', 'dt'])
    for row in data.values_list('id', 'temp', 'hum', 'dt'):
        writer.writerow(row)
    return response


# Pages graphiques
def graphiqueTemp(request):
    return render(request, 'ChartTemp.html')


def graphiqueHum(request):
    return render(request, 'ChartHum.html')


# Données JSON - toutes
def chart_data(request):
    qs = Dht11.objects.all()
    data = {
        'temps': [d.dt.isoformat() for d in qs],
        'temperature': [d.temp for d in qs],
        'humidity': [d.hum for d in qs],
    }
    return JsonResponse(data)

def chart_data_jour(request):
    now = timezone.now()
    start = now - datetime.timedelta(hours=24)
    qs = Dht11.objects.filter(dt__range=(start, now))
    data = {
        'temps': [d.dt.isoformat() for d in qs],
        'temperature': [d.temp for d in qs],
        'humidity': [d.hum for d in qs],
    }
    return JsonResponse(data)

def chart_data_semaine(request):
    start = timezone.now() - datetime.timedelta(days=7)
    qs = Dht11.objects.filter(dt__gte=start)
    data = {
        'temps': [d.dt.isoformat() for d in qs],
        'temperature': [d.temp for d in qs],
        'humidity': [d.hum for d in qs],
    }
    return JsonResponse(data)

def chart_data_mois(request):
    start = timezone.now() - datetime.timedelta(days=30)
    qs = Dht11.objects.filter(dt__gte=start)
    data = {
        'temps': [d.dt.isoformat() for d in qs],
        'temperature': [d.temp for d in qs],
        'humidity': [d.hum for d in qs],
    }
    return JsonResponse(data)

def chart_data_date_temp(request):
    date_str = request.GET.get('date')
    try:
        # Convertir la chaîne en objet date
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return JsonResponse({'temps': [], 'temperature': [], 'humidity': []})

    # Créer un datetime pour le début (minuit) et la fin (minuit suivant) de la date sélectionnée
    start_datetime = datetime.datetime.combine(date_obj, datetime.time.min)
    start_datetime = timezone.make_aware(start_datetime)
    end_datetime = start_datetime + datetime.timedelta(days=1)

    # Filtrer les données entre start_datetime et end_datetime
    queryset = Dht11.objects.filter(dt__gte=start_datetime, dt__lt=end_datetime).order_by('dt')

    # Préparer les données avec les temps en format ISO
    data = {
        'temps': [obj.dt.isoformat() for obj in queryset],
        'temperature': [obj.temp for obj in queryset],
        'humidity': [obj.hum for obj in queryset],
    }
    return JsonResponse(data)

def chart_data_date_hum(request):
    date_str = request.GET.get('date')
    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return JsonResponse({'temps': [], 'temperature': [], 'humidity': []})

    start_datetime = datetime.datetime.combine(date_obj, datetime.time.min)
    start_datetime = timezone.make_aware(start_datetime)
    end_datetime = start_datetime + datetime.timedelta(days=1)

    queryset = Dht11.objects.filter(dt__gte=start_datetime, dt__lt=end_datetime).order_by('dt')

    data = {
        'temps': [obj.dt.isoformat() for obj in queryset],
        'temperature': [obj.temp for obj in queryset],
        'humidity': [obj.hum for obj in queryset],
    }
    return JsonResponse(data)


# Inscription utilisateur
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# Déconnexion
def user_logout(request):
    logout(request)
    return redirect('home')


