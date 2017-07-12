from django.contrib import admin
from django.db import models
from .models import *
#
# # Register your models here.
# admin.site.register(newsInfo)
# admin.site.register(history)
# admin.site.register(weights)
# admin.site.register(category)
admin.site.register(Categories)
admin.site.register(History)
admin.site.register(Newsinfo)
admin.site.register(Userinfo)
admin.site.register(Weights)
admin.site.register(Menus)
admin.site.register(Usercf)