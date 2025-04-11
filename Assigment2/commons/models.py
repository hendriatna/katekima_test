from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True) # auto add datetime once save
    updated_at = models.DateTimeField(auto_now=True) # auto add datetime every save
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
