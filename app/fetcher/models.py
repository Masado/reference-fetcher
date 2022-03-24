from django.db import models

# Create your models here.


class Fetch(models.Model):
    id = models.BigAutoField(primary_key=True)
    fetch_id = models.CharField(max_length=50)
    species = models.CharField(max_length=80)
    ensembl_version = models.CharField(max_length=50)
    reference = models.CharField(max_length=50)

    def __str__(self):
        return self.fetch_id
