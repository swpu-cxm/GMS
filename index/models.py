from django.db import models


# Create your models here.


class Garbage(models.Model):
    """点位数据"""
    id = models.AutoField(primary_key=True, verbose_name='垃圾桶编号')
    place = models.CharField(max_length=64, verbose_name='垃圾桶地址')
    class_1 = models.FloatField(verbose_name='可回收垃圾', default=0)
    class_2 = models.FloatField(verbose_name='有害垃圾', default=0)
    class_3 = models.FloatField(verbose_name='餐厨垃圾', default=0)
    class_4 = models.FloatField(verbose_name='其他垃圾', default=0)
    totle = models.FloatField(verbose_name='当前总量', default=0)
    max_size = models.FloatField(verbose_name='阈值', default=50)
    longitude = models.CharField(max_length=32, verbose_name='经度', default='0')
    latitude = models.CharField(max_length=32, verbose_name='纬度', default='0')

    class Meta:
        unique_together = ('longitude', 'latitude')


class UserGrade(models.Model):
    """用户积分"""
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64, verbose_name='用户名')
    grade = models.IntegerField(verbose_name='积分')


class Statictics(models.Model):
    """所有点位统计数据"""
    id = models.AutoField(primary_key=True)
    date = models.DateField(verbose_name='日期', unique=True)
    class_1 = models.FloatField(verbose_name='可回收垃圾', default=0)
    class_2 = models.FloatField(verbose_name='有害垃圾', default=0)
    class_3 = models.FloatField(verbose_name='餐厨垃圾', default=0)
    class_4 = models.FloatField(verbose_name='其他垃圾', default=0)


class OneStatictics(models.Model):
    """单个点位历史统计数据"""
    id = models.AutoField(primary_key=True)
    garbage = models.ForeignKey(Garbage, verbose_name='ID', on_delete=True, default='2')
    date = models.DateField(verbose_name='日期')
    class_1 = models.FloatField(verbose_name='可回收垃圾', default=0)
    class_2 = models.FloatField(verbose_name='有害垃圾', default=0)
    class_3 = models.FloatField(verbose_name='餐厨垃圾', default=0)
    class_4 = models.FloatField(verbose_name='其他垃圾', default=0)

    class Meta:
        unique_together = ('garbage', 'date',)
