from django.db import models
from store.models import Product
from django.contrib.auth.models import User 

# Create your models here.

class Shipping_Address(models.Model):
    fullname= models.CharField(max_length=255)
    email= models.CharField(max_length=255)

    address1= models.CharField(max_length=255)
    address2= models.CharField(max_length=255)
    city= models.CharField(max_length=255)

    state= models.CharField(max_length=255, blank=True, null=True)
    zipcode= models.CharField(max_length=255 , blank=True ,null=True)

    user= models.ForeignKey(User, on_delete= models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name_plural= 'Shipping_Address'

    def __str__(self):
        return 'Shipping_Address ... - '+ str(self.pk)

class Order(models.Model):
    fullname= models.CharField(max_length=255)
    email= models.CharField(max_length=255)

    shipping_address= models.TextField(max_length=1000)

    amount_paid= models.DecimalField(max_digits=8, decimal_places=2)
    date_ordered= models.DateTimeField(auto_now_add=True)

    user= models.ForeignKey(User, on_delete= models.CASCADE, blank=True, null=True)

    def __str__(self):
        return 'Order -#'+ str(self.pk)

class OrderItem(models.Model):
    order= models.ForeignKey(Order, on_delete= models.CASCADE, null= True, blank= True)
    product= models.ForeignKey(Product, on_delete= models.CASCADE, null= True, blank=True)

    quantity= models.PositiveSmallIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    user= models.ForeignKey(User, on_delete= models.CASCADE, blank=True, null=True)

    def __str__(self):
        return 'Order Item -#'+ str(self.pk)