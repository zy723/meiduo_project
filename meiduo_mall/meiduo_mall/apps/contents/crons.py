import os

from django.conf import settings
from django.template import loader

from contents.models import ContentCategory
from contents.utils import get_categories


# 定时任务

def generate_static_html():
    """
    生成静态的主页html文件
    :return:
    """
    # 获取商品分类
    categories = get_categories()
    # 广告内容
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 渲染模板
    context = {
        'categories': categories,
        'contents': contents
    }

    # 获取首页模板文件
    template = loader.get_template('index.html')
    # 渲染模板
    html_text = template.render(context)
    # 写入本地
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
