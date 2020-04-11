from collections import OrderedDict
from django.shortcuts import render
# Create your views here.
from django.views.generic.base import View

from goods.models import GoodsChannel


class IndexView(View):
    """
    首页广告提供
    """

    def get(self, request):
        categories = OrderedDict()
        # channels = GoodsChannel().objects.order_by('group_id', 'sequence')
        channels = GoodsChannel.objects.order_by('group_id', 'sequence')
        for channel in channels:
            group_id = channel.group_id  # 当前组
            if group_id not in categories:
                categories[group_id] = {'channels': [], 'sub_cats': []}

            cat1 = channel.category  # 当前频道类别

            # 最加当前频道
            categories[group_id]['channels'].append({
                'id': cat1.id,
                'name': cat1.name,
                'url': channel.url
            })

            # 构建当前类别的子类别
            for cat2 in cat1.subs.all():
                cat2.sub_cats = []
                for cat3 in cat2.subs.all():
                    cat2.sub_cats.append(cat3)
                categories[group_id]['sub_cats'].append(cat2)

        context = {
            'categories': categories
        }

        return render(request, 'index.html', context)
