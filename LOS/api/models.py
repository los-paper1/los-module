from django.conf import settings
import uuid
from django.db import models


class  RefNutritioncalculator(models.Model):
    nutritionid = models.BigIntegerField(primary_key=True)
    feedtypeId = models.CharField(db_column="feedtype_id",max_length=255)
    calcium = models.IntegerField()
    energy = models.IntegerField()
    fat = models.IntegerField()
    iron = models.IntegerField()
    phosphorus = models.IntegerField()
    protein = models.IntegerField()
    vitamina = models.IntegerField()
    vitamind = models.IntegerField()
    
    class Meta:
        db_table = 'ref_nutritioncalculator'