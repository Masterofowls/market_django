import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.db import connection
from apps.catalog.models import Category, Brand, Product, ProductImage
print("HOST", connection.settings_dict["HOST"])
print("PORT", connection.settings_dict["PORT"])
print("categories", Category.objects.count())
print("brands", Brand.objects.count())
print("products", Product.objects.count())
print("images", ProductImage.objects.count())
