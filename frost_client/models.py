from django.db import models

from geospaas.catalog.models import Dataset as CatalogDataset

from frost_client.managers import FrostManager

class Dataset(CatalogDataset):
    class Meta:
        proxy = True
    objects = FrostManager()

