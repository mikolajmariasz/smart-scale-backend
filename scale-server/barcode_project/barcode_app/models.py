from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username
    
class Meal(models.Model):
    MEAL_TYPES = [
        ('BREAKFAST', 'Breakfast'),
        ('LUNCH', 'Lunch'),
        ('DINNER', 'Dinner'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meals')
    meal_name = models.CharField(max_length=100)
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPES)
    date = models.DateTimeField()

    class Meta:
        unique_together = ['user', 'date', 'meal_type']

    def __str__(self):
        return f"{self.meal_type} - {self.meal_name} ({self.user.username})"

class Ingredient(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='ingredients')
    ingredient_name = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.FloatField()
    calories_per_100g = models.FloatField(null=True, blank=True)
    protein_per_100g = models.FloatField(null=True, blank=True)
    fat_per_100g = models.FloatField(null=True, blank=True)
    carbs_per_100g = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.ingredient_name} ({self.meal.meal_name})"

    @property
    def total_calories(self):
        if self.calories_per_100g is not None:
            return (self.calories_per_100g * self.quantity) / 100
        return 0

    @property
    def total_protein(self):
        if self.protein_per_100g is not None:
            return (self.protein_per_100g * self.quantity) / 100
        return 0

    @property
    def total_fat(self):
        if self.fat_per_100g is not None:
            return (self.fat_per_100g * self.quantity) / 100
        return 0

    @property
    def total_carbs(self):
        if self.carbs_per_100g is not None:
            return (self.carbs_per_100g * self.quantity) / 100
        return 0
    
class Barcode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='barcodes')
    barcode = models.CharField(max_length=100)
    macros = models.JSONField()
    
    def __str__(self):
        return f"{self.barcode} - {self.user.username}"
