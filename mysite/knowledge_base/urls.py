from django.urls import path
from . import views

app_name = "knowledge_base"

urlpatterns = [
    path("", views.CategoryListView.as_view(), name="category_list"),
    path("category/<slug:slug>/", views.ArticleListView.as_view(), name="category_detail"),
    path("article/<slug:slug>/", views.ArticleDetailView.as_view(), name="article_detail"),
    path("search/", views.SearchResultsView.as_view(), name="search"),
]
