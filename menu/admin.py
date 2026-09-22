from django.contrib import admin
from .models import Category, MenuItem

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','restaurant')
    list_filter = ('restaurant',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price','category', 'is_available')
    list_filter = ('category','is_available')
    search_fields = ('name',)