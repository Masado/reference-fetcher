from django.contrib import admin

from .models import Fetch

# Register your models here.


class FetchAdmin(admin.ModelAdmin):
    list_display = ['id', 'fetch_id', 'species', 'ensembl_version', 'reference']
    list_filter = ['species', 'ensembl_version', 'reference']
    search_fields = ['species', 'ensembl_version', 'reference']

admin.site.register(Fetch, FetchAdmin)
