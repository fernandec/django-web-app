from django.contrib import admin

# Register your models here.
from django.contrib import admin
from listings.models import Repertoire
from listings.models import Photo

admin.site.register(Repertoire)
admin.site.register(Photo)
