from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View


class IndexView(View):
    """
    首页
    """

    def get(self, request):
        return render(request, 'index.html')

    def post(self):
        pass
