from django.template.loader import render_to_string
from django.core.urlresolvers import resolve

from rest_framework.response import Response
from rest_framework.decorators import (api_view)

from .forms import RelatedArticlesForm
from .utils import populate_urls

@api_view(['GET'])
def related_articles(request):
    '''
    '''
    related_form = RelatedArticlesForm(request.GET)
    if related_form.is_valid() is True:
        match = resolve(related_form.cleaned_data["current_article"])
        article_array = []
        urlpatterns = populate_urls()
        for item in urlpatterns:
            try:
                if(related_form.cleaned_data["category"] ==
                       item.default_args["category"]):
                    article_array.append({"title":
                                              item.default_args["title"],
                                          "name": item.name})
            except KeyError:
                pass

        html = render_to_string('related_articles.html',
                                {"articles": article_array,
                                 "current_name": match.url_name})

        return Response({'html': html}, status=200)
    else:
        return Response({'html': "<div></div>"}, status=400)
