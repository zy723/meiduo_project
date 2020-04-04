import logging

from django import http
from django.core.cache import cache
from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View

from . import constants
from meiduo_mall.utils.response_code import RETCODE
from .models import Area

logger = logging.getLogger('django')


class AreasView(View):
    """
    省市区三级联动
    """

    def get(self, request):
        area_id = request.GET.get('area_id')

        if not area_id:
            # 获取并判断是否有缓存
            province_list = cache.get('province_list')
            if not province_list:
                # 查询省级数据
                try:
                    province_model_list = Area.objects.filter(parent__isnull=True)
                    # 将获取的模型类转换成字典列表
                    province_list = []
                    for province_model in province_model_list:
                        province_dict = {
                            'id': province_model.id,
                            'name': province_model.name
                        }
                        province_list.append(province_dict)

                    # 缓存省份字典数据; 默认存储到别名位为 default 的配置中
                    cache.set('province_list', province_list, constants.CACHE_TOKEN_EXPIRES)

                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '查询省份数据错误'})

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'province_list': province_list})

        else:
            # 判断是否有缓存数据
            sub_data = cache.get('sub_area_' + area_id)
            if not sub_data:
                try:
                    # 查询城市或区县数据
                    parent_model = Area.objects.get(id=area_id)
                    sub_model_list = parent_model.subs.all()

                    # 将子模型列表转换成字典列表
                    subs = []
                    for sub_model in sub_model_list:
                        sub_dict = {
                            'id': sub_model.id,
                            'name': sub_model.name
                        }
                        subs.append(sub_dict)
                    # 构造子集json数据
                    sub_data = {
                        'id': parent_model.id,
                        'name': parent_model.name,
                        'subs': subs
                    }
                    # 缓存城市或者区县
                    cache.set('sub_area_' + area_id, sub_data, constants.CACHE_TOKEN_EXPIRES)
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': "查询城市或区县错误"})

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'sub_data': sub_data})
