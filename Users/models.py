from django.db import models

# Create your models here.
# This model stores special keys that allow users to register as Administrators.
class AdminKey(models.Model):
    # admin_key: A text field (max 50 chars) that must be unique.
    # If a user enters a key matching one in this table, they get admin privileges.
    admin_key = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.admin_key