from django.db import models
from services.models import Users
choices = ((1,"Classic"),(2,"Elite"),(3, "Royal"))

# Create your models here.
class BlrHistory(models.Model):
    ref = models.BooleanField(default=False)
    hash_transaction = models.TextField()
    amount_send_usdt = models.FloatField(null=True)
    amount_recieved_blr = models.FloatField(null=True)
    address_send = models.TextField(null=True)
    status = models.BooleanField(default=False)
    username_from = models.TextField(null=True)
    date_creation =  models.DateField(auto_now_add=True, null=True, blank=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    
class NftHistory(models.Model):
    # nft = models.IntegerField(null=True)
    ref = models.BooleanField(default=False)
    type_nft = models.CharField(max_length=20, choices=choices, null=True)
    hash_transaction = models.TextField()
    amount_send_usdt = models.FloatField(null=True)
    nft_recieved= models.TextField(null=True)
    address_send = models.TextField(null=True)
    username_from = models.TextField(null=True)
    status = models.BooleanField(default=False)
    date_creation =  models.DateField(auto_now_add=True, null=True, blank=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)

class Historic(models.Model):
    address_send = models.TextField(null=True)
    hash_transaction = models.TextField()
    amount_send_usdt = models.FloatField(null=True)
    username_from = models.TextField(null=True)
    date_creation =  models.DateField(auto_now_add=True, null=True, blank=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)

class Nft(models.Model):
    type_nft = models.CharField(max_length=20, choices=choices, null=True)
    name = models.TextField(null=True)
    price = models.FloatField()
    owner = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, default=None)
    date_creation =  models.DateField(auto_now_add=True, null=True, blank=True)
    focus_id = models.IntegerField(null=True)

    
class BinanceKeys(models.Model):
    api_key_public = models.CharField(max_length=200, unique=True)
    api_key_private = models.CharField(max_length=200, unique=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)