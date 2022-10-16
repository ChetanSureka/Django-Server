from email.policy import default
import uuid
from django.db import models
from PIL import Image
from django.utils.text import slugify
from accounts.models import User
from django.utils import timezone


'''
{
	"id": 87,
    "name": "Beige metal hoop tote bag",
	"slug": "beige-metal-hoop-tote-bag",
	"product_code": "GSDHJQ",
	"short_desc": "Sed egestas, ante et vulputate volutpat, eros pede semper est, vitae luctus metus libero eu augue. Morbi purus libero, faucibus adipiscing. Sed lectus.",
	"price": 76,
	"sale_price": null,
	"until": null,

	"color_name": "golden black",
	"material": "mm",
	"weight": 2000,
	"stock": 100,
	"top": true,
	"featured": true,
	"new": null,
	"sold-out": "bool",
	"category": [
	{
		"name": "Women",
		"slug": "women"
	}],
	"brands": [
	{
		"name": "UGG",
		"slug": "ugg"
	}],
	"pictures": [
	{
		"width": "800",
		"height": "800",
		"url": "/uploads/product_1_1_45e247fd69.jpg"
	}],

},
'''

class Categories(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, auto_created=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Categories, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Product(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    product_code = models.CharField(max_length=100, null=True, blank=True)
    short_desc = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    sale_price = models.DecimalField(decimal_places=2, max_digits=10)
    until = models.DateField()
    color_name = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    weight = models.DecimalField(decimal_places=2, max_digits=10)

    stock = models.IntegerField(default=0)
    top = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    new = models.BooleanField(default=True)
    sold_out = models.BooleanField(default=False)
    
    category = models.ManyToManyField(Categories, related_name="categories", default=None)
    brands = models.ForeignKey("Brands", on_delete=models.CASCADE, related_name="brands", default=None)


    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.color_name = self.color_name.title()
        super(Product, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"



class Brands(models.Model):
    brand_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, auto_created=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.name = self.name.title()
        super(Brands, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"


class Pictures(models.Model):
    picture_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="pictures")
    ref_name = models.CharField(max_length=20, null=True, blank=True, default=None)
    ref_url = models.CharField(max_length=200, null=True, blank=True, default=None)
    media_url = models.FileField(upload_to="uploads/", null=True, blank=True, default=None)
    width = models.IntegerField(editable=False, default=1200)
    height = models.IntegerField(editable=False, default=1600)

    def save(self, *args, **kwargs):
        self.media_url = self.ref_url
        # try:
        #     image = Image.open(self.ref_url)
        #     self.width = image.size[0]
        #     self.height = image.size[1]
        # except:
            # pass
        
        # self.ref_name = self.media_url.name
        super(Pictures, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.media_url.url

    class Meta:
        verbose_name = "Pictures"
        verbose_name_plural = "Pictures"
    


class Cart(models.Model):
    cart_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart", default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.cart_id)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

class CartProduct(models.Model):
    cart_product_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product")
    quantity = models.IntegerField(default=1)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_products")


    def __str__(self):
        return self.product.name
    
    class Meta:
        verbose_name = "CartProduct"
        verbose_name_plural = "CartProducts"


class Shipping(models.Model):
    shipping_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shipping")
    first_name = models.CharField(max_length=100, default=None, null=True, blank=True)
    last_name = models.CharField(max_length=100, default=None, null=True, blank=True)
    country = models.CharField(max_length=100, default=None, null=True, blank=True)
    address_line_1 = models.CharField(max_length=100, default=None, null=True, blank=True)
    address_line_2 = models.CharField(max_length=100, default=None, null=True, blank=True)
    city = models.CharField(max_length=100, default=None, null=True, blank=True)
    state = models.CharField(max_length=100, default=None, null=True, blank=True)
    zip = models.CharField(max_length=100, default=None, null=True, blank=True)
    phone = models.CharField(max_length=10, default=None, null=True, blank=True)
    email = models.EmailField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.shipping_id)
    
    class Meta:
        verbose_name = "Shipping"
        verbose_name_plural = "Shipping"


class Orders(models.Model):
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE, related_name="orders")
    order_status = models.CharField(max_length=100, default="pending")
    order_date = models.DateTimeField(auto_now_add=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)   # type: ignore

    def __str__(self):
        return str(self.order_id)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"



class OrderItem(models.Model):
    order_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_item")
    quantity = models.IntegerField(default=1)
    order = models.ForeignKey("Orders", on_delete=models.CASCADE, related_name="order_items")

    def __str__(self):
        return self.product.name

    def save(self, *args, **kwargs):
        self.order.order_total = self.order.order_total + (self.product.price * self.quantity)
        self.order.save()
        super(OrderItem, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = "OrderItem"
        verbose_name_plural = "OrderItems"


class Payment(models.Model):
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name="payment")
    currency = models.CharField(max_length=3, default="INR")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)  # type: ignore
    rz_order_id = models.CharField(max_length=100, default=None, null=True, blank=True)

    def __str__(self):
        return str(self.payment_id)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"


# class Size(models.Model):
#     name = models.CharField(max_length=100)
    
#     def __str__(self):
#         return self.name
    
#     class Meta:
#         verbose_name = "Size"
#         verbose_name_plural = "Sizes"


# class Variant(models.Model):
#     color = models.CharField(max_length=100, default=None)
#     color_name = models.CharField(max_length=100, default=None)
#     price = models.DecimalField(decimal_places=2, max_digits=10)

#     size = models.ManyToManyField("Size", related_name="size")

#     def __str__(self):
#         return self.color

#     class Meta:
#         verbose_name = "Variant"
#         verbose_name_plural = "Variants"


# class TestProduct(models.Model):
#     name = models.CharField(max_length=100)
