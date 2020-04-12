from collections import OrderedDict
from django.shortcuts import render
# Create your views here.
from django.views.generic.base import View

from contents.models import ContentCategory
from contents.utils import get_categories
from goods.models import GoodsChannel


class IndexView(View):
    """
    首页广告提供
    """

    def get(self, request):
        # --------------------------渲染首页商品频道分类---------------------------------------
        categories = get_categories()
        # --------------------------广告数据---------------------------------------
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': categories,
            'contents': contents,
        }

        return render(request, 'index.html', context)
