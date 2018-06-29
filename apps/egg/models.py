from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

import bcrypt
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        if len(postData['first_name']) <2 or str.isalpha(postData['first_name']) == False:
            errors['first_name'] = 'First Name should be at least 2 characters and must be letters only'
        if len(postData['last_name']) <2 or str.isalpha(postData['last_name']) == False:
            errors['last_name'] = 'Last name should be at least 2 characters and must be letters only'
        if not EMAIL_REGEX.match(postData['email']):
            errors['email'] = 'Email is not a valid format'
        if postData['password'] != postData['passconf']:
            errors['passc'] = 'Passwords must match'
        if len(postData['password'])<8:
            errors['password'] = 'Password must be at least 8 characters'
        if len(User.objects.filter(email = postData['email'])) == 1:
            errors['email2'] = 'Email already in system'
        return errors
    def login_validator(self, postData):
        errors = {}
        if not EMAIL_REGEX.match(postData['login_email']):
            errors['email_login'] = 'Email is not a valid format'
        try:
            user = User.objects.get(email = postData['login_email'])
            if not bcrypt.checkpw(postData['login_password'].encode(), user.password.encode()):
                errors['pass_login2'] = 'Try again'
        except ObjectDoesNotExist:
            errors['email_login2'] = 'Try again'
        
        return errors

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = UserManager()

    def __str__(self):
        return self.first_name+' '+self.last_name
        
class Item(models.Model):
    model_number = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=2, decimal_places = 1)
    price = models.DecimalField(max_digits=5, decimal_places = 2)
    item_type = models.CharField(max_length=255)
    picture = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'cart')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name = 'cart')
    quantity = models.IntegerField(default = 1)

class OrderHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'orderhistory')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name = 'orderhistory')
    quantity = models.IntegerField(default = 1)
    created_at = models.DateTimeField(auto_now_add = True)    




# user = User.objects.get(id=1)
# item = Item.objects.get(model_number  = 'gtx1080ti')
# OrderHistory.objects.create(user = user, item = item)
# user.orderhistory
# OrderHistory.objects.filter(user=user)
#how to have a user leave a message in views
# user = User.objects.get({{get user from POST}})
# my_message = Message.objects.create(user = user, message = {{get message from POST}})

# #how to leave a comment on a message by a user in views
# message = Message.objects.get({{get message ID from post}})
# user = User.objects.get({{get user from post}})
# my_comment = Comment.objects.create(message = message, user = user, comment = {{get comment from post}})