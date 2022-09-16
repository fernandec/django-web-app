"""
waitThe `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from listings import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('gallery/create/', views.db_create, name = 'db-create' ),
    path('show_gallery/', views.gallery, name = 'gallery'),
    path('show_gallery/next/', views.gallery_next, name = 'gallery_next'),
    path('show_gallery/previous/', views.gallery_previous, name = 'gallery-previous'),
    path('gallery/<int:id>/',views.gallery_detail, name='gallery-detail'),
    path('gallery/year/',views.gallery_year, name='gallery-year'),
    path('gallery/admin/',views.gallery_admin, name='gallery-admin'),
    path('gallery/migrate_tel_bruno/', views.migrate_tel_bruno, name='migrate-tel-bruno'),
    path('gallery/migrate_tel_marie/', views.migrate_tel_marie, name='migrate-tel-marie'),
    path('gallery/audit/', views.audit_db, name='audit'),
]
