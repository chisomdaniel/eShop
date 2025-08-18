import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class Category(models.Model):
    """The category model to manage product categories"""
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=500, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["-name"]
    
    def __str__(self) -> str:
        return f"[Category] {self.name}"


class Tag(models.Model):
    """The tag model, to manage product tags"""
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
    
    def __str__(self) -> str:
        return f"[Tag] {self.name}"


class Products(models.Model):
    """The product model"""
    class ProductType(models.TextChoices):
        DIGITAL = "digital", "Digital product"
        PHYSICAL = "physical", "Physical product"
        SERVICE = "service", "Service"
    
    class ProductStatus(models.TextChoices):
        draft = "draft", "Draft"
        active = "active", "Active"
        archived = "archived", "Archived"

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=500)
    description = models.TextField()
    price = models.DecimalField(max_digits=50, decimal_places=2, validators=[MinValueValidator(0.00)])
    stock_quantity = models.PositiveIntegerField()
    low_stock_threshold = models.PositiveIntegerField(
        help_text="What quantity will the stock get to before it is considered too low and an alart can be raised"
    )
    purchase_count = models.PositiveIntegerField(
        default=0,
        help_text="keep a count of how many times this product has been successfully purchased"
        )
    min_order_quantity = models.PositiveIntegerField(
        default=1,
        help_text="The min quantity a customer can buy in a single purchse. Defaults to 1"
    )
    status = models.CharField(
        max_length=10,
        choices=ProductStatus.choices,
        default=ProductStatus.active,
        help_text="Indicate if the product is active, or saved as draft or archived"
    )
    type = models.CharField(
        max_length=10,
        choices=ProductType.choices,
        default=ProductType.PHYSICAL,
        help_text="Identify if the product being listed is a physical or digital (downloadable) product or a service"
    )
    allow_backorder = models.BooleanField(
        default=False,
        help_text="Allow customers to keep placing order on a product after the available stock has finished"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationship
    categories = models.ManyToManyField(Category, related_name="products")
    tags = models.ManyToManyField(Tag, related_name="products")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"[Product] {self.name}"


class ProductImage(models.Model):
    """
    The Product Image model. To manage the relationship
    between a product and image, a product can have multiple images
    """
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    image_url = models.URLField()
    alt_text = models.TextField(blank=True)
    position = models.PositiveIntegerField(
        default=2,
        help_text="Identify the order which the product images will be displayed using numbers to repr first, second, etc. The first will be the cover image."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Relationship
    products = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="images")

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
    
    def __str__(self):
        return f"[Image] for Product: {self.products.name}"
