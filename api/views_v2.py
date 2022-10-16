from datetime import datetime
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import *
from mysite import settings
from accounts.models import User
from rest_framework import generics
from .serailizers import BrandSerializer, CartSerializer, CartProductSerializer, CategorySerializer, ProductSerializer, ShippingSerializer
from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from django.shortcuts import render
import json, jwt, razorpay
from django.conf import settings
from api.utils import *


@api_view(['POST'])
def AddToCartView(request):
    '''
    Adds CartProduct to cart
    Required data: reality
        {
            "cart_product": {
                "product_id": Product ID,
                "qty": Quantity
            }
        }
    Response: Cart object
    expectatiuons
    {
        cart: [
            {
                product.id 
                product.name ....
                qty
                sum = product.price * qty 
            },
        ]
    }
    '''
    try:
        print("[Request body]: ", request.body)
        data = json.loads(request.body.decode("utf-8").replace("'",'"'))
        decoded_jwt = get_data_obj_from_token(request)
        print("[Decoded data]: ", data, type(data))
        print("[Decoded JWT]: ", decoded_jwt, type(decoded_jwt))
        cart_id = decoded_jwt['cart_id']
        cart_product = data["cart_product"]
        response_obj = {
            "cart": []
        }
        qty = cart_product["qty"]
        product_id=cart_product["product_id"]
        if check_stock(product_id, qty):
            cart_product_obj=update_or_create(cart_id, product_id, qty)
            product_obj = Product.objects.get(product_id=product_id)
            # response_obj["cart"].append({
            #     "product_id": product_obj.product_id,
            #     "name": product_obj.name,
            #     "qty": qty,
            #     "sum": product_obj.price * qty
            # })
            # response_obj['cart'] = CartProductSerializer(cart).data
            cart_list = []
            cart_item_list = CartProduct.objects.filter(cart=Cart.objects.get(cart_id=cart_id))
            for item in cart_item_list:
                item_obj = json.loads(json.dumps(dict(ProductSerializer(item.product).data)))
                item_obj["qty"] = item.quantity
                try:
                    item_obj["sum"] = product_obj.sale_price * item.quantity
                except:
                    item_obj["sum"] = product_obj.price * item.quantity
                print("[Item obj]: ", item_obj)
                cart_list.append(item_obj)
            response_obj["cart"] = cart_list
            print("[RESPONSE_OBJ] ", response_obj)
            return Response(response_obj, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Out of stock"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as error:
        print("[ERROR]: ", error)
        return Response({'error': error.args}, status=status.HTTP_400_BAD_REQUEST)

'''
{
{
    # searchTerm: query.searchTerm,
    # color: query.color ? query.color.split( ',' ) : [],
    size: query.size ? query.size.split( ',' ) : [],
    # brand: query.brand ? query.brand.split( ',' ) : [],
    # minPrice: parseInt( query.minPrice ),
    # maxPrice: parseInt( query.maxPrice ),
    # category: query.category,
    sortBy: query.sortBy ? query.sortBy : 'default',
    page: query.page ? parseInt( query.page ) : 1,
    perPage: perPage,
    list: true
}
}
'''
from django.db.models import Q

@api_view(['POST'])
def GetProductsView(request):
    print(request.body)
    data = json.loads(request.body.decode("utf-8").replace("'",'"'))
    print("[Data]: ", data)
    
    query_dict = {}
    for key, value in data.items():
        if value is not None:
            query_dict[key] = value
    print("[Query dict]: ", query_dict)
    response_list = []
    for key, value in query_dict.items():
        if key == "searchTerm":
            response_list.append(Q(name__icontains=value))
        if key == "brand":
            print("[Brand]: ", value)
            brands_list = [brand.title() for brand in value]
            brands = Brands.objects.filter(name__in = brands_list)
            print("[Brands]: ", brands)
            response_list.append(Q(brands__in=brands))
        if key == "minPrice":
            response_list.append(Q(price__gte=value))
        if key == "maxPrice":
            response_list.append(Q(price__lte=value))
        if key == "category":
            print("[Category]: ", value)
            category = Categories.objects.filter(slug__in=value)
            print("[Categories]: ", category)
            response_list.append(Q(category__in=category))
        if key == "color":
            print("[COLOR]: ", value)
            colors_list = [color.title() for color in value]
            response_list.append(Q(color_name__in=colors_list))
            print("[Colour List]: ", response_list)
    print("[Response List]: ", response_list)
    
    sort_by = query_dict["sortBy"].lower()

    if sort_by == "default":
        filtered_data = Product.objects.filter(*response_list).order_by("name")
    elif sort_by == "high-to-low":
        filtered_data = Product.objects.filter(*response_list).order_by("-price")
    elif sort_by == "low-to-high":
        filtered_data = Product.objects.filter(*response_list).order_by("price")
    elif sort_by == "recently-added":
        filtered_data = Product.objects.filter(*response_list).order_by("new")
    else:
        filtered_data = Product.objects.filter(*response_list)
    # serailizer = ProductSerializer(response_list, many=True)
    print("[Filtered Data]: ", filtered_data)
    filtered_data = ProductSerializer(filtered_data, many=True).data

    return JsonResponse(filtered_data, status=status.HTTP_200_OK, safe=False)



@api_view(['POST'])
def AddProductView(request):
    print("[Request body]: ", request.body)
    data = json.loads(request.body.decode("utf-8").replace("'",'"'))
    print("[Data]: ", data)
    brand, created = Brands.objects.get_or_create(name=data["brands"]["name"])
    category, cat_created = Categories.objects.get_or_create(name=data["category"])
    product = Product.objects.create(
        name = data["name"],
        product_code = data["product_code"],
        short_desc = data["short_desc"],
        price = data["price"],
        sale_price = data["sale_price"],
        until = data["until"],
        color_name = data["color_name"],
        material = data["material"],
        weight = data["weight"],
        stock = data["stock"],
        top = data["top"],
        featured = data["featured"],
        new = data["new"],
        sold_out = data["sold_out"],
        brands = brand,
        category = category,
    )
    product = Product.objects.create(**data)
    print("[Product]: ", product)
    return Response({"message": "Product added successfully"}, status=status.HTTP_201_CREATED)
