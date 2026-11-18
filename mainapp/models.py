from django.db import models
from django import forms
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings 
from .isbn import IsbnField  

class Book(models.Model):
    title = models.CharField(max_length=300)
    publisher = models.CharField(max_length=200)
    year = models.IntegerField()
    isbn = IsbnField()
    backCover = models.TextField()
    cover = models.BooleanField(default=False)
    authors = models.ManyToManyField(
    "Author",related_name="books")
    owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="owned_books",
)
    
    def __str__(self):
        return self.title

class Review(models.Model):
    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    publication_date = models.DateTimeField(default=timezone.now)

    body = models.TextField()

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="owned_reviews",
    
     )

    def __str__(self):
        return f"Avis sur {self.book} - {self.rating}/5"
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["body", "rating"]

class Author(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=200)
    
    owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="owned_authors",
)
    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()

