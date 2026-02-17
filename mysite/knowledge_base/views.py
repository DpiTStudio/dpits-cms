from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Category, Article

class CategoryListView(ListView):
    model = Category
    template_name = "knowledge_base/category_list.html"
    context_object_name = "categories"
    queryset = Category.objects.all().order_by("order")

class ArticleListView(DetailView):
    model = Category
    template_name = "knowledge_base/article_list.html"
    context_object_name = "category"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["articles"] = self.object.articles.filter(is_published=True)
        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = "knowledge_base/article_detail.html"
    context_object_name = "article"
    slug_url_kwarg = "slug"

    def get_object(self):
        obj = super().get_object()
        # Simple view counter
        obj.views_count += 1
        obj.save(update_fields=["views_count"])
        return obj

class SearchResultsView(ListView):
    model = Article
    template_name = "knowledge_base/search_results.html"
    context_object_name = "articles"

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return Article.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query),
                is_published=True
            )
        return Article.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context
