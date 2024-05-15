"""
URL configuration for SplitEase project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("participant/create/", views.add_participant_to_bill, name="create_participant"),
    path("bill/<int:bill_id>/participant/<int:participant_id>/update-contribution/", views.participant_contribution,
         name="participant_contribution"),
    path("bill/<int:bill_id>/participants/total/", views.get_participants_total_cost,
         name="get_participant_total_cost"),
    path("bill/<int:bill_id>/", views.get_bill, name="get_bill"),
    path("bill/<int:bill_id>/view/", views.bill_details, name="view_bill"),
    path("bill/<int:bill_id>/product/", views.create_product, name="create_product"),
    path("bill/<int:bill_id>/product/<int:product_id>/update/", views.update_product, name="update_product"),
    path("bill/create/", views.create_new_bill, name="create_bill"),
    path("product/<int:product_id>/delete/", views.delete_product, name="delete_product"),
    path("file/", views.upload_file, name="upload_file"),
    path("file/test/", views.upload_file_test, name="read_test"),
    path("file/text/", views.read_test, name="read_test")
]
