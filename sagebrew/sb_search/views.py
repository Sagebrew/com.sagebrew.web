from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required()
def search_result_view(request):
    return render(request, 'search.html')
