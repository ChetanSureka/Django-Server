import json
from accounts.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from django.http.response import JsonResponse
from api.models import Cart


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        cart, created = Cart.objects.get_or_create(user=user)

        user_object = {}
        user_object['id'] = user.id
        user_object['firstname'] = user.firstname
        user_object['lastname'] = user.lastname
        user_object['email'] = user.email
        token['user'] = user_object
        token['cart_id'] = str(cart.cart_id)
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Add Cart and return cartID on Login
@api_view(['POST'])
def SignUpView(request):
    print(request.body)
    data = json.loads(request.body.decode("utf-8").replace("'",'"'))
    print(data)
    firstname = data['firstname']
    lastname = data['lastname']
    email = data['email']
    password = data['password']
    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "You are already registered."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validate_password(password)
        user = User.objects.create_user(email=email, firstname=firstname, lastname=lastname, password=password)
        user.save()
        return JsonResponse({'message': 'User created successfully'}, status=status.HTTP_200_OK)
    except ValidationError as error:
        return JsonResponse({"error": error}, status=status.HTTP_400_BAD_REQUEST)
    