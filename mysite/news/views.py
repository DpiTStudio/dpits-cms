# news/views.py
# Представления (контроллеры) для приложения news (новости)
from django.shortcuts import (
    render,
    get_object_or_404,
    reverse,
)
from django.core.paginator import Paginator
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from captcha.models import CaptchaStore
from .models import News, NewsCategory, NewsTag, Comment, NewsReaction
from .forms import CommentForm
from .utils import (
    get_cached_news_categories,
    get_cached_sidebar_news,
    get_cached_popular_news,
    get_cached_popular_tags,
    get_cached_news_stats,
)
from main.breadcrumbs import get_breadcrumbs


def news_list(request):
    """
    Отображение списка всех активных новостей.
    Оптимизировано с использованием select_related и кэширования.
    """
    query = request.GET.get("q", "")
    sort_by = request.GET.get("sort", "date_desc")

    # Маппинг сортировок (поддержка старых и новых форматов с сайта)
    sort_mapping = {
        "date_desc": "-published_at",
        "views_desc": "-views",
        "category": "category",
        "-created_at": "-published_at",
        "created_at": "published_at",
        "-views": "-views",
        "title": "title",
    }

    db_sort = sort_mapping.get(sort_by, "-published_at")

    category_slug = request.GET.get("category")
    tag_slug = request.GET.get("tag")
    date_filter = request.GET.get("date")

    # Фильтруем активные новости, дата публикации которых уже наступила
    news_queryset = News.objects.filter(
        is_active=True, published_at__lte=timezone.now()
    ).select_related("category").prefetch_related("tags")

    if query:
        news_queryset = news_queryset.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(content__icontains=query)
        )

    if category_slug:
        news_queryset = news_queryset.filter(category__slug=category_slug)

    if tag_slug:
        news_queryset = news_queryset.filter(tags__slug=tag_slug)

    # Фильтрация по дате публикации
    if date_filter:
        try:
            parts = date_filter.split("-")
            if len(parts) == 3:
                news_queryset = news_queryset.filter(
                    published_at__year=int(parts[0]),
                    published_at__month=int(parts[1]),
                    published_at__day=int(parts[2]),
                )
            elif len(parts) == 2:
                news_queryset = news_queryset.filter(
                    published_at__year=int(parts[0]), published_at__month=int(parts[1])
                )
            elif len(parts) == 1:
                news_queryset = news_queryset.filter(published_at__year=int(parts[0]))
        except ValueError:
            pass

    # Сортировка
    if db_sort == "category":
        news_queryset = news_queryset.order_by("category__name", "-published_at")
    else:
        news_queryset = news_queryset.order_by(db_sort)

    total_count = news_queryset.count()
    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Активный тег
    active_tag = None
    if tag_slug:
        try:
            active_tag = NewsTag.objects.get(slug=tag_slug)
        except NewsTag.DoesNotExist:
            pass

    context = {
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "popular_news": get_cached_popular_news(5),
        "popular_tags": get_cached_popular_tags(15),
        "news_stats": get_cached_news_stats(),
        "selected_category": category_slug or "",
        "current_sort": sort_by,
        "search_query": query,
        "selected_date": date_filter or "",
        "active_tag": active_tag,
        "total_count": total_count,
        "page_title": "Новости",
        "breadcrumbs": get_breadcrumbs(
            [
                ("Новости", reverse("news:list"), "fas fa-newspaper"),
            ]
        ),
    }
    return render(request, "news/list.html", context)


def news_detail(request, slug):
    """
    Отображение детальной страницы новости.
    Оптимизировано с использованием select_related и кэширования.
    """
    news = get_object_or_404(
        News.objects.select_related("category").prefetch_related("tags"),
        slug=slug,
        is_active=True,
        published_at__lte=timezone.now(),
    )

    news.increment_views()

    # Умный алгоритм рекомендаций
    news_tags = news.tags.all()
    if news_tags.exists():
        similar_news = (
            News.objects.filter(
                tags__in=news_tags, is_active=True, published_at__lte=timezone.now()
            )
            .exclude(id=news.id)
            .select_related("category")
            .distinct()
            .order_by("-published_at")[:4]
        )

        if len(similar_news) < 4:
            additional_news = (
                News.objects.filter(
                    category=news.category,
                    is_active=True,
                    published_at__lte=timezone.now(),
                )
                .exclude(id=news.id)
                .exclude(id__in=[n.id for n in similar_news])
                .select_related("category")
                .order_by("-published_at")[: 4 - len(similar_news)]
            )
            similar_news = list(similar_news) + list(additional_news)
    else:
        similar_news = (
            News.objects.filter(
                category=news.category, is_active=True, published_at__lte=timezone.now()
            )
            .exclude(id=news.id)
            .select_related("category")
            .order_by("-published_at")[:4]
        )

    # Связанные новости — из той же категории (кроме текущей)
    related_news = (
        News.objects.filter(
            category=news.category,
            is_active=True,
            published_at__lte=timezone.now(),
        )
        .exclude(id=news.id)
        .order_by("-published_at")[:10]
    )

    # Навигация prev/next по категории
    category_news = News.objects.filter(
        category=news.category,
        is_active=True,
        published_at__lte=timezone.now(),
    ).order_by("-published_at")

    ids = list(category_news.values_list("id", flat=True))
    current_idx = ids.index(news.id) if news.id in ids else -1
    prev_news = None
    next_news = None
    if current_idx > 0:
        try:
            prev_news = category_news[current_idx - 1]
        except IndexError:
            pass
    if current_idx >= 0 and current_idx < len(ids) - 1:
        try:
            next_news = category_news[current_idx + 1]
        except IndexError:
            pass

    # Комментарии: получаем все корневые комментарии и префетчим ответы к ним
    replies_prefetch = Prefetch(
        "replies",
        queryset=Comment.objects.filter(is_approved=True).select_related("user", "user__profile").order_by("created_at")
    )
    approved_comments = (
        news.comments.filter(is_approved=True, parent=None)
        .select_related("user", "user__profile")
        .prefetch_related(replies_prefetch)
        .order_by("created_at")
    )
    comment_form = CommentForm(user=request.user)

    # Реакции
    reactions_data = news.reactions.values("reaction_type").annotate(count=Count("id"))
    valid_types = ["like", "love", "fire", "wow", "sad"]
    reactions = {r_type: 0 for r_type in valid_types}
    for r in reactions_data:
        if r["reaction_type"] in reactions:
            reactions[r["reaction_type"]] = r["count"]

    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    user_reaction = news.reactions.filter(session_key=session_key).values_list("reaction_type", flat=True).first()

    context = {
        "news": news,
        "related_news": related_news,
        "similar_news": similar_news,
        "prev_news": prev_news,
        "next_news": next_news,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "popular_news": get_cached_popular_news(5),
        "popular_tags": get_cached_popular_tags(15),
        "approved_comments": approved_comments,
        "comment_form": comment_form,
        "reactions": reactions,
        "user_reaction": user_reaction,
        "breadcrumbs": get_breadcrumbs(
            [
                ("Новости", reverse("news:list"), "fas fa-newspaper"),
                (news.category.name, news.category.get_absolute_url()),
                (news.title, reverse("news:detail", kwargs={"slug": news.slug})),
            ]
        ),
    }
    return render(request, "news/detail.html", context)


def news_by_category(request, slug):
    """
    Отображение новостей определённой категории с пагинацией.
    """
    category = get_object_or_404(NewsCategory, slug=slug, is_active=True)

    query = request.GET.get("q", "")
    sort_by = request.GET.get("sort", "-published_at")
    valid_sorts = {"published_at", "-published_at", "title", "-views"}
    if sort_by not in valid_sorts:
        sort_by = "-published_at"

    news_queryset = News.objects.filter(
        category=category, is_active=True, published_at__lte=timezone.now()
    ).select_related("category").prefetch_related("tags")

    if query:
        news_queryset = news_queryset.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(content__icontains=query)
        )

    news_queryset = news_queryset.order_by(sort_by)

    from django.db.models import QuerySet
    if not isinstance(news_queryset, QuerySet):
        news_queryset = News.objects.none()

    total_count = news_queryset.count()
    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "category": category,
        "selected_category": category.slug,
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "popular_news": get_cached_popular_news(5),
        "popular_tags": get_cached_popular_tags(15),
        "current_sort": sort_by,
        "search_query": query,
        "total_count": total_count,
        "breadcrumbs": get_breadcrumbs(
            [
                ("Новости", reverse("news:list"), "fas fa-newspaper"),
                (category.name, category.get_absolute_url()),
            ]
        ),
    }
    return render(request, "news/category.html", context)


def news_search(request):
    """
    Поиск новостей по запросу пользователя с пагинацией.
    """
    query = request.GET.get("q", "")

    if query:
        news_queryset = (
            News.objects.filter(
                Q(title__icontains=query)
                | Q(short_description__icontains=query)
                | Q(content__icontains=query),
                is_active=True,
                published_at__lte=timezone.now(),
            )
            .select_related("category")
            .prefetch_related("tags")
            .distinct()
            .order_by("-published_at")
        )
    else:
        news_queryset = (
            News.objects.filter(is_active=True, published_at__lte=timezone.now())
            .select_related("category")
            .order_by("-published_at")
        )

    total_count = news_queryset.count()
    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "popular_tags": get_cached_popular_tags(15),
        "query": query,
        "total_count": total_count,
        "breadcrumbs": get_breadcrumbs(
            [
                ("Новости", reverse("news:list"), "fas fa-newspaper"),
                (f"Поиск: {query}" if query else "Поиск", request.path),
            ]
        ),
    }
    return render(request, "news/search.html", context)


def news_by_tag(request, slug):
    """
    Отображение новостей с определённым тегом.
    """
    tag = get_object_or_404(NewsTag, slug=slug)

    sort_by = request.GET.get("sort", "-published_at")
    valid_sorts = {"published_at", "-published_at", "-views", "title"}
    if sort_by not in valid_sorts:
        sort_by = "-published_at"

    news_queryset = (
        News.objects.filter(tags=tag, is_active=True, published_at__lte=timezone.now())
        .select_related("category")
        .prefetch_related("tags")
        .order_by(sort_by)
    )

    total_count = news_queryset.count()
    paginator = Paginator(news_queryset, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Похожие теги (теги, которые часто встречаются вместе с этим)
    related_tags = (
        NewsTag.objects.filter(news__in=news_queryset)
        .exclude(pk=tag.pk)
        .annotate(cnt=Count("id"))
        .order_by("-cnt")[:10]
    )

    context = {
        "tag": tag,
        "news_list": page_obj,
        "categories": get_cached_news_categories(),
        "sidebar_news": get_cached_sidebar_news(),
        "popular_tags": get_cached_popular_tags(15),
        "related_tags": related_tags,
        "current_sort": sort_by,
        "total_count": total_count,
        "breadcrumbs": get_breadcrumbs(
            [
                ("Новости", reverse("news:list"), "fas fa-newspaper"),
                (f"#{tag.name}", request.path),
            ]
        ),
    }
    return render(request, "news/list.html", context)


def get_category_image(request, category_id):
    """
    API endpoint для получения URL изображения категории.
    Используется в админке для автоматической подстановки картинки.
    """
    category = get_object_or_404(NewsCategory, pk=category_id)
    return JsonResponse(
        {
            "image_url": category.image.url if category.image else None,
            "hero_image_url": category.hero_image.url if category.hero_image else None,
        }
    )


def news_live_search(request):
    """
    AJAX endpoint для живого поиска новостей (autocomplete).
    Возвращает JSON с результатами.
    """
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"results": []})

    results = (
        News.objects.filter(
            Q(title__icontains=query) | Q(short_description__icontains=query),
            is_active=True,
            published_at__lte=timezone.now(),
        )
        .select_related("category")
        .order_by("-published_at")[:8]
    )

    data = [
        {
            "id": n.id,
            "title": n.title,
            "url": n.get_absolute_url(),
            "category": n.category.name if n.category else "",
            "image": n.image.url if n.image else "",
            "date": timezone.localtime(n.published_at).strftime("%d.%m.%Y"),
            "views": n.views,
        }
        for n in results
    ]
    return JsonResponse({"results": data, "query": query})


def news_api_stats(request):
    """
    API endpoint для получения статистики новостей.
    """
    stats = get_cached_news_stats()
    return JsonResponse(stats)


@require_POST
def post_comment(request, news_id):
    """
    AJAX представление для добавления нового комментария (включая ответы).
    """
    news_obj = get_object_or_404(News, id=news_id, is_active=True, published_at__lte=timezone.now())
    form = CommentForm(request.POST, user=request.user)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.news = news_obj
        if request.user.is_authenticated:
            comment.user = request.user
        
        parent_id = request.POST.get("parent_id")
        if parent_id:
            try:
                comment.parent = Comment.objects.get(id=parent_id, news=news_obj)
            except Comment.DoesNotExist:
                pass
                
        comment.save()

        # Формируем ответ для AJAX
        avatar_url = ""
        author_name = ""
        if comment.user:
            author_name = comment.user.username
            if hasattr(comment.user, "profile"):
                avatar_url = comment.user.profile.get_avatar_url
            else:
                avatar_url = "/static/accounts/images/default-avatar.png"
        else:
            author_name = comment.name
            avatar_url = "/static/accounts/images/default-avatar.png"

        return JsonResponse({
            "status": "success",
            "comment": {
                "id": comment.id,
                "author": author_name,
                "avatar_url": avatar_url,
                "content": comment.content,
                "created_at": timezone.localtime(comment.created_at).strftime("%d.%m.%Y %H:%M"),
                "parent_id": comment.parent_id if comment.parent else None
            }
        })
    else:
        # Если форма невалидна (например, неверная капча для гостя)
        # Генерируем новую капчу для обновления без перезагрузки
        new_key = CaptchaStore.generate_key()
        new_image = reverse("captcha-image", args=[new_key])
        
        errors = {field: errors_list[0] for field, errors_list in form.errors.items()}
        return JsonResponse({
            "status": "error",
            "errors": errors,
            "new_captcha_key": new_key,
            "new_captcha_image": new_image
        }, status=400)


@require_POST
def toggle_reaction(request, news_id):
    """
    AJAX представление для переключения эмодзи-реакции на новость.
    """
    news_obj = get_object_or_404(News, id=news_id, is_active=True, published_at__lte=timezone.now())
    reaction_type = request.POST.get("reaction_type", "").strip()

    valid_types = ["like", "love", "fire", "wow", "sad"]
    if reaction_type not in valid_types:
        return JsonResponse({"status": "error", "message": "Недопустимый тип реакции"}, status=400)

    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # Получаем IP-адрес клиента
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(",")[0]
    else:
        ip_address = request.META.get("REMOTE_ADDR")

    # Проверяем, есть ли уже реакция этого пользователя на эту новость
    existing_reaction = NewsReaction.objects.filter(
        news=news_obj,
        session_key=session_key
    ).first()

    active_type = None
    if existing_reaction:
        if existing_reaction.reaction_type == reaction_type:
            # Если кликнули на ту же реакцию — удаляем её (toggle off)
            existing_reaction.delete()
        else:
            # Меняем тип реакции
            existing_reaction.reaction_type = reaction_type
            existing_reaction.ip_address = ip_address
            existing_reaction.save()
            active_type = reaction_type
    else:
        # Создаем новую реакцию
        NewsReaction.objects.create(
            news=news_obj,
            reaction_type=reaction_type,
            session_key=session_key,
            ip_address=ip_address
        )
        active_type = reaction_type

    # Получаем обновленные счетчики для всех реакций
    reactions_data = news_obj.reactions.values("reaction_type").annotate(count=Count("id"))
    reactions = {r_type: 0 for r_type in valid_types}
    for r in reactions_data:
        if r["reaction_type"] in reactions:
            reactions[r["reaction_type"]] = r["count"]

    return JsonResponse({
        "status": "success",
        "reactions": reactions,
        "user_reaction": active_type
    })
