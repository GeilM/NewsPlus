from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
#
# # Create your models here.
#
# class category(models.Model):
#     name = models.CharField(max_length=30, primary_key=True)
#     def  __str__(self):
#         return self.name
#
# class newsInfo(models.Model):
#     article_id = models.CharField(max_length=30, primary_key=True, blank=True)
#     title = models.CharField(max_length=30, null=True, blank=True)
#     article_path = models.CharField(max_length=100, null=True, blank=True)
#     keywords = models.CharField(max_length=100, null=True, blank=True)
#     category = models.ForeignKey(category, null=True, blank=True)
#     img_path = models.CharField(max_length=100, null=True, blank=True)
#     def __str__(self):
#         return self.article_id + "-" + self.title
#     class Meta:
#         ordering = ['-article_id']


#
# class history(models.Model):
#     username = models.ForeignKey(User)
#     keywords = models.CharField(max_length=100, null=True, blank=True)
#     category = models.CharField(max_length=10, null=True, blank=True)
#     def __str__(self):
#         return self.username.username + self.keywords
#
# class weights(models.Model):
#     article_id = models.ForeignKey(newsInfo)
#     keyword = models.CharField(max_length=10, null=True, blank=True)
#     weight = models.FloatField(null=True, blank=True)
#     def __str__(self):
#         return self.article_id.article_id
#
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.


class Categories(models.Model):
    name = models.CharField(primary_key=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'categories'

class History(models.Model):
    username = models.ForeignKey('Userinfo', models.DO_NOTHING, db_column='username', blank=True, null=True)
    category = models.CharField(max_length=10, blank=True, null=True)
    keywords = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'history'


class Menus(models.Model):
    name = models.ForeignKey(Categories, models.DO_NOTHING, db_column='name', blank=True, null=True)
    article = models.ForeignKey('Newsinfo', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'menus'


class Newsinfo(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    article_id = models.CharField(primary_key=True, max_length=200)
    keywords = models.TextField(blank=True, null=True)
    img_path = models.CharField(max_length=350, blank=True, null=True)
    url = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'newsinfo'


class Userinfo(models.Model):
    username = models.CharField(primary_key=True, max_length=10)
    psw = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'userinfo'


class Weights(models.Model):
    keyword = models.TextField(unique=True, max_length=300, blank=True, null=True)
    pairs = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'weights'

class Usercf(models.Model):
    username = models.CharField(max_length=20, blank=True, null=True)
    article_id = models.IntegerField(blank=True, null=True)
    rate = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usercf'

