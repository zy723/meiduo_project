import json
import re
import logging
from django import http
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.base import View

from celery_tasks.email.tasks import send_verify_email
from . import constants
from .utils import generate_verify_email_url, check_verify_email_token
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from .models import *

logger = logging.getLogger('django')


class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request):
        """
        修改密码
        :param request:
        :return:
        """
        return render(request, 'user_center_pass.html')

    def post(self, request):
        """
        实现修改密码逻辑
        :param request:
        :return:
        """
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')

        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^[0-9a-zA-Z]{8,20}$', new_password):
            return http.HttpResponseForbidden('新密码长度为8-20位')
        if new_password2 != new_password:
            return http.HttpResponseForbidden('两次输入密码不一致')
        if old_password == new_password:
            return render(request, 'user_center_pass.html', {'change_pwd_errmsg': '新老密码不能相同'})

        # 更改密码

        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_pwd_errmsg': '修改密码失败'})

        # 清理登录状态
        logout(request)
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')

        return response

        # return render(request, 'user_center_pass.html', {'change_pwd_errmsg': '修改密码成功'})


class UpdateTitleAddressView(LoginRequiredMixin, View):
    def put(self, request, address_id):
        """
        修改默认标题
        :param request:
        :param address_id:
        :return:
        """
        json_dict = json.loads(request.body.decode())

        title = json_dict.get('title')

        try:
            address = Address.objects.get(id=address_id)

            address.title = title
            address.save()
        except Exception as e:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '修改标题失败'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改标题成功'})


class DefaultAddressView(LoginRequiredMixin, View):
    def put(self, request, address_id):
        """
        设置成默认地址
        :param request:
        :param address_id:
        :return:
        """
        try:
            address = Address.objects.get(id=address_id)
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})


class UpdateDestroyAddressView(LoginRequiredMixin, View):
    def put(self, request, address_id):
        """
        修改收货地址

        2.请求参数：路径参数 和 JSON

        参数名	类型	是否必传	说明
        address_id	string	是	要修改的地址ID（路径参数）
        receiver	string	是	收货人
        province_id	string	是	省份ID
        city_id	string	是	城市ID
        district_id	string	是	区县ID
        place	string	是	收货地址
        mobile	string	是	手机号
        tel	string	否	固定电话
        email	string	否	邮箱

        3.响应结果：JSON

        字段	说明
        code	状态码
        errmsg	错误信息
        id	地址ID
        receiver	收货人
        province	省份名称
        city	城市名称
        district	区县名称
        place	收货地址
        mobile	手机号
        tel	固定电话
        email	邮箱

        :param request:
        :return:
        """
        json_dict = json.loads(request.body.decode())

        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([address_id, receiver, province_id, city_id, district_id, place, mobile]):
            http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^1[3-9]/d{9}$', mobile):
            http.HttpResponseForbidden('手机号校验失败')

        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', tel):
                http.HttpResponseForbidden('参数email有误')

        # 判断地址是否存在 并更新收货地址
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        # 响应并构造修改后的数据

        address = Address.objects.get(id=address_id)

        address_dict = {
            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email,
        }

        # 响应更新地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """
        删除地址
        :param request:
        :param address_id:
        :return:
        """

        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)
            # 逻辑删除
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})


class CreateAddressView(LoginRequiredMixin, View):
    """创建收获地址"""

    def get(self, request):
        pass

    def post(self, request):
        """
        新增地址

        1. 接收参数
        参数名	类型	是否必传	说明
        receiver	string	是	收货人
        province_id	string	是	省份ID
        city_id	string	是	城市ID
        district_id	string	是	区县ID
        place	string	是	收货地址
        mobile	string	是	手机号
        tel	string	否	固定电话
        email	string	否	邮箱

        2. 响应结果：JSON

        字段	说明
        code	状态码
        errmsg	错误信息
        id	地址ID
        receiver	收货人
        province	省份名称
        city	城市名称
        district	区县名称
        place	收货地址
        mobile	手机号
        tel	固定电话
        email	邮箱
        :param request:
        :return:
        """

        # 判断地址是否超出 上限
        # 原始查询方式
        # Address.objects.filter(user=request.user).count()
        # 一查多的方式
        count = request.user.addresses.count()

        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址上限'})

        # 接收传入参数
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            http.HttpResponseForbidden('参数mobile有误')
        if not re.match(r'^^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
            http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                http.HttpResponseForbidden('参数email有误')

        # 保存收获地址
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,  # 标题默认就是收货人
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )

            # 如果登录用户没有默认的地址，我们需要指定默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 新增地址展示给前端
        address_dict = {
            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email,
        }
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


class AddressView(LoginRequiredMixin, View):
    """
    用户收获地址
    """

    def get(self, request):
        """
        :param request:
        :return:
        """
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list,
        }

        return render(request, 'user_center_site.html', context)


class VerifyEmailView(View):
    """
    验证邮箱
    验证邮箱的核心：就是将用户的email_active字段设置为True
    """

    def get(self, request):
        token = request.GET.get('token')
        # 验证token
        if not token:
            return http.HttpResponseBadRequest('缺少token')
        user = check_verify_email_token(token)
        if not user:
            http.HttpResponseForbidden('无效的token')

        # 修改email_active = true

        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活失败')

        else:

            return redirect(reverse('users:info'))


class EmailView(LoginRequiredJSONMixin, View):
    """
    添加邮箱验证
    """

    def put(self, request):

        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')

        # 校验参数
        if not email:
            return http.HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email格式有误')

        # 保存邮箱
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})
        else:
            veriffy_url = generate_verify_email_url(request.user)
            # 发送邮件
            send_verify_email.delay(email, veriffy_url)

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


class UserInfoView(LoginRequiredMixin, View):
    """
    用户中心
    """

    def get(self, request):
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }

        return render(request, 'user_center_info.html', context)


class LogoutView(View):
    """
    退出登录
    """

    def get(self, request):
        """
        实现退出登录逻辑
        :param request:
        :return:
        """
        logout(request)

        # 退出后重定向到首页
        response = redirect(reverse('contents:index'))

        response.delete_cookie('username')

        return response


class LoginView(View):
    """
    登录页面
    """

    def get(self, request):
        """提供登录页面"""
        return render(request, 'login.html')

    def post(self, request):
        """
        实现登录逻辑
        :param request:
        :return:
        """
        # 获取参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        # 校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必要参数')

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')

        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.HttpResponseForbidden('密码最少为8位,最长为20位')

        # 用户登录
        user = authenticate(username=username, password=password)  # 重写该方法实现多用户登录

        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 状态保持

        login(request, user)

        if remembered != 'on':
            # 没有记住用户, 关闭浏览器会话即过期
            request.session.set_expiry(0)
        else:
            # None 表示两周后过期
            request.session.set_expiry(None)

        # 响应登录结果
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))
        # 写入cookie 有效期 15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response


class MobileCountView(View):
    """
    判断手机号是否存在重复
    """

    def get(self, request, mobile):
        """

        :param request:
        :param mobile: 手机号
        :return:
        """
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})

    def post(self, request):
        pass


class UsernameCountView(View):
    """
    判断用户名是否重复注册
    """

    def get(self, request, username):
        """

        :param request:
         :param username:
        :return:
        """
        # 实现主体业务逻辑：使用username查询对应的记录的条数(filter返回的是满足条件的结果集)
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class RegisterView(View):
    """
    注册页面
    """

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden("缺少必要参数")
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden("请输入5-20个字符的用户名")
        # 判断密码是否是8-20个数字
        if not re.match(r'^[a-zA-Z0-9]{8,20}', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password2 != password:
            return http.HttpResponseForbidden('两次输入密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')

        # 保存用户信息到数据库
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            # http.HttpResponseForbidden('注册失败')
            return render(request, 'register.html', {'register_errmsg': '注册失败'})
        # 登陆状态保持
        login(request, user)
        # 注册成功 重定向到首页
        # return http.HttpResponseForbidden('注册成功,重定向到首页')

        response = redirect(reverse('contents:index'))

        # 写入cookie 有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response
