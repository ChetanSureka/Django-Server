from datetime import datetime
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import *
from core import settings
from accounts.models import User
from rest_framework import generics
from .serailizers import CartSerializer, CartProductSerializer, ProductSerializer, ShippingSerializer
from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from django.shortcuts import render
import json, jwt, razorpay
from django.conf import settings
from api.utils import *

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@api_view(['GET'])
def GetProducts(request):
    '''
        Returns all products
    '''
    products_obj = Product.objects.all()
    serializer = ProductSerializer(products_obj, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def GetCartView(request):
    '''
        Required data: token
        returns cart object or error
    '''
    try:
        print("[REQUEST]", request.body)
        decoded_jwt = get_data_obj_from_token(request)
        print("[Decoded JWT]", decoded_jwt)
        user = User.objects.get(id=decoded_jwt['user_id'])
        cart = Cart.objects.get(user=user)
        cart_products = CartProduct.objects.filter(cart=cart)
        serializer = CartProductSerializer(cart_products, many=True)
        response_dict={
            "cart": {
                "cart_id": cart.cart_id,
                "cart_products": serializer.data
            }
        }
        return Response(response_dict, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def AddToCartView(request):
    '''
    Adds CartProduct to cart
    Required data: 
        {
            "token": TOKEN,
            "cart": {
                "cart_products": [
                    {
                        "cart_product_id": CartProduct ID / itemid),
                        "product_id": Product ID,
                        "quantity": Quantity
                    }
                ]
            }
        }
    Response: Cart object
    '''
    try:
        print("[REQUEST]", request.body)
        data = json.loads(request.body.decode("utf-8").replace("'",'"'))
        decoded_jwt = get_data_obj_from_token(request)
        print(data, type(data))
        print(decoded_jwt, type(decoded_jwt))
        cart_id = decoded_jwt['cart_id']
        cart_products = data['cart']["cart_products"]
        response_obj = {
            "cart": {
                "cart_id": cart_id,
                "cart_products": []
            }
        }
        for cart_product in cart_products:
            qty = cart_product["qty"]
            product_id=cart_product["product_id"]
            if check_stock(product_id, qty):
                cart_product_obj=update_or_create(cart_id, product_id, qty)
                response_obj['cart']['cart_products'].append({
                    "status": 200,
                    "cart_product_id": str(cart_product_obj.cart_product_id),
                    "product_id": str(cart_product_obj.product.product_id),
                    "quantity": str(cart_product_obj.quantity)
                })
            else:
                cart_product["status"]=400
                cart_product["quantity"] = 0
                response_obj['cart']['cart_products'].append(cart_product)
        return Response(response_obj, status=status.HTTP_200_OK)
    except Exception as error:
        print(error)
        return Response({'error': "error"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def RemoveFromCartView(request):
    '''
    Removes CartProduct from cart
    Required data:
        {
            "token": TOKEN,
            "cart": {
                "cart_products": [
                    {
                        "cart_product_id": CartProduct ID / itemid),
                    }
                ]
            }
        }
    Response: Below object or error
    { 
        "cart": {
            "cart_products": [
                {
                    "cart_product_id": CartProduct ID / itemid),
                    "status": 204
                }
            ]
        }
    }
    '''
    try:
        data = json.loads(request.body.decode("utf-8").replace("'",'"'))
        token_data=get_data_obj_from_token(request)
        cart_items_list = data["cart"]["cart_products"]
        response_data = {
            "cart": {
                "cart_id": token_data["cart_id"],
                "cart_products": []
            }
        }
        for cart_item in cart_items_list:
            CartProduct.objects.get(cart_product_id=cart_item).delete()
            response_data['cart']['cart_products'].append({"cart_product_id": cart_item, "status": "204"})
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as error:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET', 'PUT'])
def ShippingView(request):
    '''
    Adds shipping address to cart
    Required data:
        {
            "token": TOKEN,
            "first_name": first_name,
            "last_name": last_name,
            "country": country,
            "address_line_1": address_line_1,
            "address_line_2": address_line_2,
            "city": city,
            "state": state,
            "zip": zip,
            "phone": phone,
            "email": email
        }
    '''
    data = json.loads(request.body.decode("utf-8").replace("'",'"'))
    decoded_jwt = get_data_obj_from_token(request)

    if request.method == 'GET':
        shipping = Shipping.objects.get(user=User.objects.get(id=decoded_jwt['user_id']))
        serializer = ShippingSerializer(shipping)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8").replace("'",'"'))
            decoded_jwt = get_data_obj_from_token(request)
            serializer = ShippingSerializer(data=data['shipping'])
            serializer.is_valid(raise_exception=True)
            serializer.save(user=User.objects.get(id=decoded_jwt['user_id']))
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PUT':
        try:
            shipping = Shipping.objects.get(user=User.objects.get(id=decoded_jwt['user_id']))
            data = json.loads(request.body.decode("utf-8").replace("'",'"'))
            decoded_jwt = get_data_obj_from_token(request)
            serializer = ShippingSerializer(shipping, data=data['shipping'])
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def index(request):
    '''
    This is the payment page
    '''
    # token_data = get_data_obj_from_token(request)
    amount = 250 * 100
    data = {
        "key": settings.RAZORPAY_KEY_ID,
        "amount": amount,
        "order_id": create_razorpay_order(amount, client)['id'],
    }
    return render(request, 'api/app.html', context=data)


@api_view(['POST'])
def app_charge(request):
    print(request.data['razorpay_payment_id'])
    payment_id = request.data['razorpay_payment_id']
    client.payment.capture(payment_id, 250*100)
    data = json.dumps(client.payment.fetch(payment_id))
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_pay_data(request):
    print(request.body)
    data = {}
    return Response(data, status=status.HTTP_200_OK)

'''
def create_empty_cart(user_id):
    user = User.objects.get(id=user_id)
    cart = Cart.objects.create(user=user)
    cart.save()
    return str(cart.cart_id)


def get_user_from_token(payload):
    data = json.loads(payload.body.decode("utf-8").replace("'",'"'))
    token = data['token']
    decoded_jwt = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    exp = datetime.fromtimestamp(decoded_jwt['exp'])
    if decoded_jwt['token_type'] == 'refresh':
        raise Exception('Token is not access token')
    elif exp < datetime.now():
        raise Exception('Token is expired')
    else:
        token_verify = TokenVerifySerializer().validate({'token': token})
        return decoded_jwt
    


def update_quantity(cart_id, product_id, quantity):
    cart = Cart.objects.get(id=cart_id)
    product = Product.objects.get(id=product_id)
    cart_product = CartProduct.objects.get(cart=cart, product=product)
    cart_product.quantity = quantity+1
    cart_product.save()
    return cart_product



@api_view(['GET', 'POST'])
def get_cart(request):
    if request.method == 'GET':
        try:
            decoded_token = get_user_from_token(request)
            user_id = decoded_token['user_id']
            print(decoded_token)
            if Cart.objects.filter(user_id=user_id).exists():
                cart = Cart.objects.get(user_id=user_id)
                serializer = CartSerializer(cart)
                data = serializer.data
                cart_items = CartProduct.objects.filter(cart_id=data['id'])
                data['cart_items'] = cart_items
                data["message"] = "Cart found"
                return Response(data, status=status.HTTP_200_OK)
            else:
                cart_id = create_empty_cart(user_id)
                cart = Cart.objects.get(id=cart_id)
                serializer = CartSerializer(cart)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
    

    elif request.method == 'POST':
        try:
            decoded_token = get_user_from_token(request)
            user_id = decoded_token['user_id']
            print(decoded_token, request.data)
            if Cart.objects.filter(user_id=user_id).exists():
                cart = Cart.objects.get(user_id=user_id)
                cart_id=cart.cart_id
                products_list = request.data['products']
                quantity_list = request.data['quantity']
                res_data = {}
                print(products_list)
                
                for index in range(len(products_list)):
                    # if similar product does not exist in cart, create new cart item
                    serializer = CartProductSerializer(data={'cart': cart_id, 'product': products_list[index], 'quantity': quantity_list[index]})  # type: ignore
                    if serializer.is_valid():
                        serializer.save()
                        res_data[products_list[index]] = serializer.data
                    else:
                        res_data[products_list[index]] = serializer.errors
                        print(res_data)
                return Response(res_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Cart not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({'error': str(error)}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

# Update Cart

@api_view(['GET'])
def get_products(request):
    products_list = Product.objects.all()
    serializer = ProductSerializer(products_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

'''



