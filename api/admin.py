from django.contrib import admin
from api.models import *

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'brands', 'color_name']
    list_filter = []
    search_fields = []

admin.site.register(Product, ProductAdmin)
admin.site.register(Categories)
admin.site.register(Brands)
admin.site.register(Pictures)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Shipping)