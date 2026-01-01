from django.contrib import admin

from .models import Fact, Category

admin.site.register(Fact)
admin.site.register(Category)
