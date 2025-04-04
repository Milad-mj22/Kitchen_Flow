from django.db import models

# Create your models here.




class SMS(models.Model):
    sender = models.CharField(max_length=50)
    message = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} - {self.received_at}"