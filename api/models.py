import uuid
from django.db import models
from django.utils.text import slugify


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
    slug = models.SlugField(auto_created=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Categories, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Products(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    product_code = models.CharField(max_length=100, null=True, blank=True)
    short_desc = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    sale_price = models.DecimalField(decimal_places=2, max_digits=10)
    until = models.DateField()
    color_name = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    weight = models.IntegerField(default=0)
    ratings = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    top = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    new = models.BooleanField(default=True)
    sold_out = models.BooleanField(default=False)
    
    category = models.ManyToManyField(Categories, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    # brands = models.ForeignKey("Brands", on_delete=models.CASCADE, related_name="brands", default=None)


    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.color_name = self.color_name.title()
        super(Products, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"


class Variants(models.Model):
    variant_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="variants")
    color = models.CharField(max_length=100)
    size = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Variant"
        verbose_name_plural = "Variants"



class Brands(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="brands")
    brand_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(auto_created=True, editable=False)

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
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="pictures")
    picture_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ref_name = models.CharField(max_length=200, null=True, blank=True, default=None)
    ref_url = models.CharField(max_length=200, null=True, blank=True, default=None)
    media_url = models.FileField(upload_to="uploads/", null=True, blank=True, default=None)
    width = models.IntegerField(editable=False, default=1200)
    height = models.IntegerField(editable=False, default=1600)

    def save(self, *args, **kwargs):
        self.media_url = self.ref_url
        self.ref_name = self.media_url.name
        super(Pictures, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.media_url.url

class SmallPictures(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="sm_pictures")
    picture_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ref_name = models.CharField(max_length=200, null=True, blank=True, default=None)
    ref_url = models.CharField(max_length=200, null=True, blank=True, default=None)
    media_url = models.FileField(upload_to="uploads/", null=True, blank=True, default=None)
    width = models.IntegerField(editable=False, default=600)
    height = models.IntegerField(editable=False, default=800)

    def save(self, *args, **kwargs):
        self.media_url = self.ref_url
        self.ref_name = self.media_url.name
        super(SmallPictures, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.media_url.url

    class Meta:
        verbose_name = "SmallPictures"
        verbose_name_plural = "SmallPictures"
    