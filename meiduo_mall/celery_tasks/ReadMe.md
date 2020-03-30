## 启动celery任务


```text

$ cd ~/projects/meiduo_project/meiduo_mall
$ celery -A celery_tasks.main worker -l info

```

## 协程方式 运行

```text

# 安装eventlet模块
$ pip install eventlet

# 启用 Eventlet 池
$ celery -A celery_tasks.main worker -l info -P eventlet -c 1000

```