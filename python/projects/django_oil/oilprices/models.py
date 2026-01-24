from django.db import models

class OilPrice(models.Model):
    price_date = models.DateField()
    price = models.FloatField()
    euro_price = models.FloatField()

    def __str__(self):
        return f"Price {self.id} on {self.price_date}"
    
# Django looks at your model and creates a SQL table with columns:

# id (auto-increment primary key, added by default)

# price_date

# price

# euro_price

# You interact with the table using the OilPrice class in Python, instead of raw SQL.
    
