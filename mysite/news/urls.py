from django.urls import path
from . import views

app_name = "news"

urlpatterns = [
    path("", views.news_list, name="list"),  # news:list
    path("category/<slug:category_slug>/", views.news_by_category, name="by_category"),
    path("<slug:slug>/", views.news_detail, name="detail"),
]
