from .models import Brands, Cart, CartProduct, Categories, Product, Shipping
from accounts.models import User
from rest_framework import serializers

class CartSerializer(serializers.ModelSerializer):
    '''
        user
        product
    '''
    class Meta:
        model = Cart
        fields = '__all__'
        depth = 1

class CartProductSerializer(serializers.ModelSerializer):
    '''
        cart
        product
    '''
    class Meta:
        model = CartProduct
        fields = '__all__'
        depth = 1


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        depth = 1


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brands
        fields = '__all__'
        depth = 1


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'
        depth = 1
        