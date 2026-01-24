from django.contrib import admin
from .models import Restaurant, MenuGroup, MenuCategory, MenuItem

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1

class MenuCategoryInline(admin.TabularInline):
    model = MenuCategory
    extra = 1
    inlines = [MenuItemInline]

class MenuGroupInline(admin.TabularInline):
    model = MenuGroup
    extra = 1
    inlines = [MenuCategoryInline]

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone')
    inlines = [MenuGroupInline]

@admin.register(MenuGroup)
class MenuGroupAdmin(admin.ModelAdmin):
    list_display = ('type', 'restaurant', 'group_order')
    list_filter = ('restaurant',)
    inlines = [MenuCategoryInline]

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'menu_group', 'cat_order')
    list_filter = ('menu_group__restaurant', 'menu_group')
    inlines = [MenuItemInline]

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'item_order')
    list_filter = ('category__menu_group__restaurant', 'category__menu_group', 'category')
