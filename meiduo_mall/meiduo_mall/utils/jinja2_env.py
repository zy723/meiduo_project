from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from jinja2 import Environment


def jinja2_environment(**options):
    """

    jinja2 环境
    :param options:
    :return:
    """
    # 创建环境对象
    env = Environment(**options)

    # 创建自定义语法
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
    })
    # 返回环境对象
    return env
