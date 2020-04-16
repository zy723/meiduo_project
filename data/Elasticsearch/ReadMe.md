
# 

- 重建搜索引擎 索引
python manage.py rebuild_index

```text
1.Haystack介绍

Haystack 是在Django中对接搜索引擎的框架，搭建了用户和搜索引擎之间的沟通桥梁。
我们在Django中可以通过使用 Haystack 来调用 Elasticsearch 搜索引擎。
Haystack 可以在不修改代码的情况下使用不同的搜索后端（比如 Elasticsearch、Whoosh、Solr等等）。
2.Haystack安装


$ pip install django-haystack
$ pip install elasticsearch==2.4.1
3.Haystack注册应用和路由

INSTALLED_APPS = [
    'haystack', # 全文检索
]
url(r'^search/', include('haystack.urls')),
4.Haystack配置

在配置文件中配置Haystack为搜索引擎后端
# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://192.168.103.158:9200/', # Elasticsearch服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'meiduo_mall', # Elasticsearch建立的索引库的名称
    },
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
重要提示：

HAYSTACK_SIGNAL_PROCESSOR 配置项保证了在Django运行起来后，有新的数据产生时，Haystack仍然可以让Elasticsearch实时生成新数据的索引

```


