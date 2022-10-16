from api.models import CartProduct, Cart, Product
import jwt, json
from datetime import datetime
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenVerifySerializer

def create_razorpay_order(amount, client):
    order = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})
    print(order)
    return order

def get_cart_total(cart_id):
    cart_products = CartProduct.objects.filter(cart=Cart.objects.get(cart_id=cart_id))
    total = 0
    for cart_product in cart_products:
        try:
            total += cart_product.product.sale_price * cart_product.quantity
        except:
            total += cart_product.product.price * cart_product.quantity
    return str(total)


def check_stock(product_id, qty):
    stock = Product.objects.get(product_id=product_id).stock
    if stock >0 and stock >= qty:
        return True
    return False

def check_item_in_cart(cart_id, product_id):
    cart_products = CartProduct.objects.filter(cart=cart_id, product_id=product_id)
    if cart_products:
        return True
    else:
        return False
    

def update_or_create(cart_id, product_id, qty):
    # update or create a cart product
    # returns a cart product object
    cart = Cart.objects.get(cart_id=cart_id)
    product = Product.objects.get(product_id=product_id)
    cart_product, created = CartProduct.objects.update_or_create(cart=cart, product=product, defaults={'quantity': qty})
    print(cart_product, created)
    return cart_product

def get_data_obj_from_token(payload):
    print(payload.headers['Authorization'])
    token = payload.headers['Authorization'].split(' ')[1]
    # print(data)
    # # data = json.loads(payload.body.decode("utf-8").replace("'",'"'))
    # token = data['token']
    decoded_jwt = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS512'])
    exp = datetime.fromtimestamp(decoded_jwt['exp'])
    if decoded_jwt['token_type'] == 'refresh':
        raise Exception('Token is not access token')
    elif exp < datetime.now():
        raise Exception('Token is expired')
    else:
        token_verify = TokenVerifySerializer().validate({'token': token})
        return decoded_jwt
