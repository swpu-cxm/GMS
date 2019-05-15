from index.models import OneStatictics, Statictics, Garbage
import random
import datetime


def faker_all(days, min_limit, max_limit, start_date='2019-5-1'):
    """
    每个点位从 start_date 生成 days 天的虚拟数据,范围为 (min_limit, max_limit)

    :param days: 多少天
    :param min_limit: 设置数据最小值
    :param max_limit: 设置数据最大值
    :param start_date: 开始日期
    :return:
    """
    garbage_obj = Garbage.objects.all()
    for garbage in garbage_obj:
        now = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        for i in range(int(days)):
            OneStatictics.objects.create(garbage_id=garbage.id,
                                         class_1=round(random.uniform(min_limit, max_limit), 2) * 0.5,
                                         class_2=round(random.uniform(min_limit, max_limit), 2) * 0.3,
                                         class_3=round(random.uniform(min_limit, max_limit), 2),
                                         class_4=round(random.uniform(min_limit, max_limit), 2) * 1.5, date=now)
            add = datetime.timedelta(days=1)
            now += add


def collection(days, start_date='2019-5-1'):
    """
    从 start_date 收集所有点 days 天数的数据汇总到当天的总数据
    :param days:
    :param start_date:
    :return:
    """
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    for i in range(int(days)):
        garbage_objs = OneStatictics.objects.filter(date=start)
        class_1, class_2, class_3, class_4 = 0, 0, 0, 0
        for garbage_obj in garbage_objs:
            class_1, class_2, class_3, class_4 = class_1 + float(garbage_obj.class_1), class_2 + float(
                garbage_obj.class_2), class_3 + float(garbage_obj.class_3), class_4 + float(garbage_obj.class_4)
        Statictics.objects.create(date=start, class_1=class_1, class_2=class_2, class_3=class_3, class_4=class_4)
        add = datetime.timedelta(days=1)
        start += add


def collect_day():
    now = datetime.datetime.now().date()
    garbage_objs = OneStatictics.objects.filter(date=now)
    class_1, class_2, class_3, class_4 = 0, 0, 0, 0
    for garbage_obj in garbage_objs:
        class_1, class_2, class_3, class_4 = class_1 + float(garbage_obj.class_1), class_2 + float(
            garbage_obj.class_2), class_3 + float(garbage_obj.class_3), class_4 + float(garbage_obj.class_4)
    Statictics.objects.create(date=now, class_1=class_1, class_2=class_2, class_3=class_3, class_4=class_4)




def faker_one_point():
    """
    随机选择11个点位生成每个点位的垃圾数据,模拟丢垃圾
    :return:
    """
    garbage_objs = Garbage.objects.order_by('?')[:11]
    for garbage_obj in garbage_objs:
        garbage_obj.class_1 = garbage_obj.class_1 + round(random.uniform(7, 15), 2) * 0.5
        garbage_obj.class_2 = garbage_obj.class_2 + round(random.uniform(7, 15), 2) * 0.3
        garbage_obj.class_3 = garbage_obj.class_3 + round(random.uniform(7, 15), 2)
        garbage_obj.class_4 = garbage_obj.class_4 + round(random.uniform(7, 15), 2) * 1.5
        garbage_obj.totle = garbage_obj.class_1 + garbage_obj.class_2 + garbage_obj.class_3 + garbage_obj.class_4
        garbage_obj.save()


def flash_all():
    """
    清理垃圾,汇总到当天该点位的总数据
    :return:
    """
    garbage_objs = Garbage.objects.all()
    for garbage_obj in garbage_objs:
        try:
            onepoint_obj = OneStatictics.objects.get(garbage_id=garbage_obj.id, date=datetime.datetime.now().date())
        except Exception as e:
            onepoint_obj = OneStatictics.objects.create(garbage_id=garbage_obj.id, date=datetime.datetime.now().date())
        old_class_1, old_class_2, old_class_3, old_class_4 = float(onepoint_obj.class_1), float(
            onepoint_obj.class_2), float(onepoint_obj.class_3), float(onepoint_obj.class_4)
        class_1, class_2, class_3, class_4 = float(garbage_obj.class_1), float(garbage_obj.class_2), float(
            garbage_obj.class_3), float(garbage_obj.class_4)
        onepoint_obj.class_1, onepoint_obj.class_2, onepoint_obj.class_3, onepoint_obj.class_4 = old_class_1 + class_1, old_class_2 + class_2, old_class_3 + class_3, old_class_4 + class_4
        garbage_obj.class_1, garbage_obj.class_2, garbage_obj.class_3, garbage_obj.class_4, garbage_obj.totle = 0, 0, 0, 0, 0
        garbage_obj.save()
        onepoint_obj.save()
