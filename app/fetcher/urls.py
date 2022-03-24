from django.urls import path

from . import views

app_name = "fetcher"

urlpatterns = [
    path('', views.reference_fetcher_view, name='fetcher'),
    path('species_list/', views.ensembl_list_view, name='species_list'),
    path('version_list/', views.version_list_view, name='version_list'),
    path('missing/', views.missing_species_view, name='missing'),
]