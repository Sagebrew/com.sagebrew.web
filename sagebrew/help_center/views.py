from django.template.loader import render_to_string
from django.core.urlresolvers import resolve
from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import (api_view, permission_classes)

from .forms import RelatedArticlesForm
from .utils import populate_urls


@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def related_articles(request):
    """

    :param request:
    :return:
    """
    related_form = RelatedArticlesForm(request.GET)
    if related_form.is_valid() is True:
        match = resolve(related_form.cleaned_data["current_article"])
        article_array = []
        urlpatterns = populate_urls()
        for item in urlpatterns:
            try:
                if(related_form.cleaned_data[
                        "category"] == item.default_args["category"]):
                    article_array.append(
                        {"title": item.default_args["title"],
                         "name": item.name})
            except KeyError:
                pass

        html = render_to_string('related_articles.html',
                                {"articles": article_array,
                                 "current_name": match.url_name})

        return Response({'html': html}, status=200)
    else:
        return Response({'html': "<div></div>"}, status=400)


def help_area(request):
    category_dict = {}
    urlpatterns = populate_urls()
    for item in urlpatterns:
        category = item.default_args["category"]
        category = category.replace("_", " ")
        try:
            category_dict[category].append(
                {"title": item.default_args["title"], "name": item.name})
        except KeyError:
            category_dict[category] = [{"title": item.default_args["title"],
                                        "name": item.name}]

    return render(request, 'help_center.html', {"categories": category_dict})
