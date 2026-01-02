from django.contrib import admin

from .models import Category, Fact

admin.site.register(Fact)
admin.site.register(Category)
