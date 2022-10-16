from django.urls import path
from api import views, views_v2

urlpatterns = [
    path("cart/", views.GetCartView),
    path("cart/delete/", views.RemoveFromCartView),
    path("cart/add/", views_v2.AddToCartView),
    path("products/", views.GetProducts),
    path("user/shipping/", views.ShippingView),
    path("", views.index),
    path("charge/", views.app_charge),
    path("payment/complete/", views.get_pay_data),
    path("payment/failed/", views.get_pay_data),
    path("products/filter/", views_v2.GetProductsView),
    path("products/add/", views_v2.AddProductView),
]
