from django.db import models
from accounts.models import User

# Create your models here.
class Post(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.owner.id} - {self.id}'