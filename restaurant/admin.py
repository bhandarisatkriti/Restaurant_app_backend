from django.contrib import admin
from .models import Restaurant

@admin.register(Restaurant)
# Register your models here.
class RestaurantAdmin(admin.ModelAdmin):
    list_display= ('name', 'phone', 'opening_time', 'closing_time','is_active')
    list_filter=('is_active',)