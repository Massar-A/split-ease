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
    path("splitease/admin/", admin.site.urls),
    path("splitease/", views.index, name="index"),
    path("splitease/participant/create/", views.add_participant_to_bill, name="create_participant"),
    path("splitease/participant/<int:participant_id>/", views.update_participant, name="update_participant"),
    path("splitease/participant/<int:participant_id>/", views.delete_participant, name="delete_participant"),
    path("splitease/bill/<int:bill_id>/participants/", views.get_participants, name="get_participants"),
    path("splitease/bill/<int:bill_id>/participant/<int:participant_id>/update-contribution/", views.participant_contribution, name="participant_contribution"),
    path("splitease/bill/<int:bill_id>/participants/total/", views.get_participants_total_cost, name="get_participant_total_cost"),
    path("splitease/bill/<int:bill_id>/", views.get_bill, name="get_bill"),
    path("splitease/bill/<int:bill_id>/view/", views.bill_details, name="view_bill"),
    path("splitease/bill/<int:bill_id>/price-per-person/", views.get_price_per_person, name="get_price_per_person"),
    path("splitease/bill/<int:bill_id>/product/", views.create_product, name="create_product"),
    path("splitease/bill/<int:bill_id>/product/<int:product_id>/update/", views.update_product, name="update_product"),
    path("splitease/bill/create/", views.create_new_bill, name="create_bill"),
    path("splitease/bill/<int:bill_id>/set-payer/", views.set_bill_payer, name="set_bill_payer"),
    path("splitease/product/<int:product_id>/delete/", views.delete_product, name="delete_product"),
    path("splitease/file/", views.upload_file, name="upload_file"),
    path("splitease/file/test/", views.upload_file_test, name="upload_file_test"),
    path("splitease/file/text/", views.read_test, name="read_test"),
]
