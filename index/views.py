import random
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import datetime
from . import models
from django.contrib.auth.decorators import login_required
from index.utils import flash_all, faker_one_point, collection, collect_day
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.contrib import auth
from django.contrib.auth.models import User


# Create your views here.

def user(request, id):
    """
    用户投放垃圾
    :param request:
    :param id:垃圾点位ID
    :return:致谢用户,有输入积分凭证则返回总积分
    """
    if request.method == 'POST':
        garbage_obj = models.Garbage.objects.get(id=id)
        count = request.POST.get('count')  # 袋数
        size = request.POST.get('size')  # 规格
        _class = request.POST.get('_class')  # 类别
        username = request.POST.get('username')
        if _class == 'class_1':  # 可回收垃圾
            weight = int(count) * float(size) * 0.1  # 总质量
            old_weight = garbage_obj.class_1
            garbage_obj.class_1 = weight + old_weight
            garbage_obj.totle += weight
        elif _class == 'class_2':  # 有害垃圾
            weight = int(count) * float(size) * 0.2  # 总质量
            old_weight = garbage_obj.class_2
            garbage_obj.class_2 = weight + old_weight
            garbage_obj.totle += weight
        elif _class == 'class_3':  # 餐厨垃圾
            weight = int(count) * float(size) * 0.35  # 总质量
            old_weight = garbage_obj.class_3
            garbage_obj.class_3 = weight + old_weight
            garbage_obj.totle += weight
        elif _class == 'class_4':  # 其他垃圾
            weight = int(count) * float(size) * 0.2  # 总质量
            old_weight = garbage_obj.class_4
            garbage_obj.class_4 = weight + old_weight
            garbage_obj.totle += weight
        garbage_obj.save()
        try:
            user_obj = models.UserGrade.objects.get(username=username)
            old_grade = user_obj.grade
            new_grade = int(_class) + old_grade
            user_obj.grade = new_grade
            user_obj.save()
        except Exception as e:
            return render(request, 'ok.html', {'username': username, 'grade': None})
        return render(request, 'ok.html', {'username': username, 'grade': new_grade})
    return render(request, 'user.html')


@login_required
def add_place(request):
    """
    地图选点后添加地点
    :param request:
    :return:
    """
    if request.method == 'GET':
        place = request.GET.get('place')
        la = round(float(request.GET.get('la')), 6)
        lo = round(float(request.GET.get('lo')), 6)
        # print(place, la, lo)
        models.Garbage.objects.create(longitude=lo, latitude=la, place=place)
        # return redirect('/app_place')
        return JsonResponse({'status': 'ok'})


@login_required
def test(request):
    return HttpResponse('ok')


@login_required
def set_max(request, id, num):
    """
    设置点位阈值
    :param request:
    :param id:垃圾点位ID
    :param num:点位的阈值
    :return:返回管理员页面
    """
    if id == '0':
        garbage_objs = models.Garbage.objects.all()
        for garbage_obj in garbage_objs:
            garbage_obj.max_size = num
            garbage_obj.save()
        return redirect('/app_admin')
    else:
        garbage_obj = models.Garbage.objects.get(id=id)
        garbage_obj.max_size = num
        garbage_obj.save()
        return redirect('/app_admin')


@login_required
def delete_place(request, id):
    """
    删除点位
    :param request:
    :param id:点位ID
    :return:返回点位管理页面
    """
    models.Garbage.objects.get(id=id).delete()
    return redirect('/app_place')


@login_required
def flash(request, id):
    """
    清理垃圾
    :param request:
    :param id:点位ID
    :return:返回点位详情页
    """
    garbage_obj = models.Garbage.objects.get(id=id)
    try:
        onepoint_obj = models.OneStatictics.objects.get(garbage_id=id, date=datetime.datetime.now().date())
    except Exception as e:
        onepoint_obj = models.OneStatictics.objects.create(garbage_id=id, date=datetime.datetime.now().date())
    old_class_1, old_class_2, old_class_3, old_class_4 = float(onepoint_obj.class_1), float(
        onepoint_obj.class_2), float(onepoint_obj.class_3), float(onepoint_obj.class_4)
    class_1, class_2, class_3, class_4 = float(garbage_obj.class_1), float(garbage_obj.class_2), float(
        garbage_obj.class_3), float(garbage_obj.class_4)
    onepoint_obj.class_1, onepoint_obj.class_2, onepoint_obj.class_3, onepoint_obj.class_4 = old_class_1 + class_1, old_class_2 + class_2, old_class_3 + class_3, old_class_4 + class_4
    garbage_obj.class_1, garbage_obj.class_2, garbage_obj.class_3, garbage_obj.class_4, garbage_obj.totle = 0, 0, 0, 0, 0
    garbage_obj.save()
    onepoint_obj.save()
    return redirect('/app_admin')


@csrf_exempt
def app_map(request):
    """
    地图,查看点位,正常点位及阈值报警
    :param request:
    :return:
    """
    if request.method == 'GET':
        garbages = models.Garbage.objects.all()
        return render(request, 'app_map.html', {'garbages': garbages})
    elif request.method == 'POST':
        garbage_list = []
        garbages = models.Garbage.objects.all()
        for garbage in garbages:
            if float(garbage.totle) > float(garbage.max_size):
                status = 'no'
            else:
                status = 'ok'
            garbage_list.append(
                {'id': garbage.id, 'place': garbage.place, 'longitude': float(garbage.longitude),
                 'latitude': float(garbage.latitude), 'status': status})
        return JsonResponse(garbage_list, safe=False)


def app_place(request):
    """
    点位管理
    :param request:
    :return:
    """
    garbages = models.Garbage.objects.all()
    return render(request, 'app_place.html', {'garbages': garbages})


@login_required
def app_addplace(request):
    """
    添加点位
    :param request:
    :return:
    """
    return render(request, 'addplace.html')


def index(request):
    """
    首页轮播图
    :param request:
    :return:
    """
    return render(request, 'index.html')


def app_history(request, start, end, _type, id):
    """
    历史记录查看
    :param request:
    :param start:
    :param end:
    :param _type:
    :param id:
    :return:
    """
    start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    end = datetime.datetime.strptime(end, '%Y-%m-%d').date()
    if id == '0':
        history_obj = models.Statictics.objects.filter(date__gte=start, date__lte=end)
    else:
        history_obj = models.OneStatictics.objects.filter(garbage_id=id, date__gte=start, date__lte=end)
    date_list = []
    class_1, class_2, class_3, class_4 = [], [], [], []
    for history in history_obj:
        # print(history.date.day)
        date_list.append(float(str(history.date.month) + '.' + str(history.date.day)))
        class_1.append(history.class_1)
        class_2.append(history.class_2)
        class_3.append(history.class_3)
        class_4.append(history.class_4)
    if _type == 'bar' or _type == 'line':
        class_all = [{'name': '可回收垃圾', 'class': class_1}, {'name': '有害垃圾', 'class': class_2},
                     {'name': '餐厨垃圾', 'class': class_3}, {'name': '其他垃圾', 'class': class_4}]
        garbage_points = models.Garbage.objects.all()
        data = {'class_all': class_all, 'date_list': date_list, 'type': _type, 'garbage_points': garbage_points,
                'startdate': str(start), 'enddate': str(end), 'id': id}
    elif _type == 'pie':
        garbage_points = models.Garbage.objects.all()
        class_all = {'class_1': sum(class_1), 'class_2': sum(class_2), 'class_3': sum(class_3), 'class_4': sum(class_4)}
        data = {'class_all': class_all, 'startdate': str(start), 'enddate': str(end), 'type': _type, 'id': id,
                'garbage_points': garbage_points, 'date_list': date_list}
    return render(request, 'app_history.html', data)


def app_manager(request, id):
    """
    点位实时数据查看
    :param request:
    :param id:
    :return:
    """
    garbage = models.Garbage.objects.get(id=id)
    garbage_objs = models.Garbage.objects.values('id', 'place')
    return render(request, 'app_manager.html', {'garbage': garbage, 'garbage_objs': garbage_objs})


def app_admin(request):
    """
    管理员页面
    :param request:
    :return:
    """
    if request.user.is_authenticated == True:
        is_auth = True
    else:
        is_auth = False
    garbage_objs = models.Garbage.objects.values('place', 'id', 'totle', 'max_size').order_by('-totle')
    return render(request, 'app_admin.html', {'garbage_objs': garbage_objs, 'is_auth': is_auth})


def login(request):
    """
    登录视图函数,通过后端来判断用户登录数据,错误则返回info
    :param request:
    :return: 登录用户cookie
    """
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'info': '用户名或密码错误'})


def register(request):
    """
    注册用户函数,通过后端来判断用户注册数据,错误则返回info
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        if password == repassword:
            try:
                User.objects.create_user(username=username, password=password)
            except Exception as e:
                return render(request, 'register.html', {'info': '用户已存在'})
        else:
            return render(request, 'register.html', {'info': '两次密码不一致'})
        return redirect('/login')


def logout(request):
    """
    注销登录
    :param request:
    :return:
    """
    auth.logout(request)
    return redirect('/')


# 开启定时工作
try:
    # 实例化调度器
    scheduler = BackgroundScheduler()
    # 调度器使用DjangoJobStore()
    scheduler.add_jobstore(DjangoJobStore(), "default")


    # 设置定时任务，选择方式为interval，时间间隔为10s
    # @register_job(scheduler, "interval", seconds=10)
    # def my_job():
    #   print('do it!')
    # 另一种方式为每天固定时间执行任务，对应代码为：
    # @register_job(scheduler, 'cron', day_of_week='mon-sun', hour='23', minute='59', second='10', id='task_time')
    # def my_job():
    #   print('do it!')
    @register_job(scheduler, 'cron', day_of_week='mon-sun', hour='6', minute='30', second='00', id='flash1')
    def flash1():
        flash_all()


    @register_job(scheduler, 'cron', day_of_week='mon-sun', hour='7', minute='30', second='00', id='faker1')
    def faker1():
        faker_one_point()


    @register_job(scheduler, 'cron', day_of_week='mon-sun', hour='11', minute='30', second='00', id='flash2')
    def flash2():
        flash_all()


    @register_job(scheduler, 'cron', day_of_week='mon-sun', hour='14', minute='00', second='00', id='faker2')
    def faker2():
        faker_one_point()


    @register_job(scheduler, 'cron', day_of_week='mon-sun', hour='16', minute='30', second='00', id='flash3')
    def flash3():
        flash_all()


    @register_job(scheduler, 'cron', day_of_week='mon-sun', hour='18', minute='30', second='00', id='faker3')
    def faker3():
        faker_one_point()


    @register_job(scheduler, 'cron', day_of_week='mon-sun', hour='23', minute='59', second='00', id='collection')
    def collect():
        collect_day()


    # 下面这种定时任务并不管用,所以也就改为上面的了
    # scheduler.add_job(flash_all, 'cron', day_of_week='mon-sun', hour='6', minute='30', second='00', id='flash1')
    # scheduler.add_job(faker_one_point, 'cron', day_of_week='mon-sun', hour='7', minute='30', second='00', id='faker1')
    # scheduler.add_job(flash_all, 'cron', day_of_week='mon-sun', hour='11', minute='30', second='00', id='flash2')
    # scheduler.add_job(faker_one_point, 'cron', day_of_week='mon-sun', hour='14', minute='00', second='00', id='faker2')
    # scheduler.add_job(flash_all, 'cron', day_of_week='mon-sun', hour='16', minute='30', second='00', id='flash3')
    # scheduler.add_job(faker_one_point, 'cron', day_of_week='mon-sun', hour='18', minute='30', second='00', id='faker3')
    # scheduler.add_job(collection, 'cron', day_of_week='mon-sun', hour='23', minute='59', second='00', id='collection')
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started!")
except Exception as e:
    pass
