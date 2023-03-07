from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class List(models.Model):
    listname=models.CharField(max_length=255)
    cuser=models.ForeignKey(User,on_delete=models.CASCADE)
    cdate=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.listname

    def get_absolute_url(self):
        return reverse('lista-sida',kwargs={'pk':self.pk})

class Object(models.Model):
    objectname=models.CharField(max_length=255)
    amount=models.DecimalField(max_digits=5,decimal_places=2)
    purchased=models.BooleanField(default=False)
    list=models.ForeignKey(List,on_delete=models.CASCADE)

    def __str__(self):
        return self.objectname

    def get_absolute_url(self):
        return reverse('lista-sida',kwargs={'pk':self.list.pk})
    
class SharedList(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='list_shared')
    email = models.EmailField()

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user = User.objects.get(email=self.email)
        super().save(*args, **kwargs)
