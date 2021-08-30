from django.db import models

# Create your models here.
class Proposal(models.Model):
    p_id = models.CharField(unique=True, max_length=250)
    ref_id = models.TextField()