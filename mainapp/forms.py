from django import forms
from .models import Book, Review, Author


class BookForm(forms.ModelForm):

    class Meta:
        model = Book
        fields = [
            "authors",
            "title",
            "publisher",
            "year",
            "isbn",
            "backCover",
            "cover",
        ]
        labels = {
            "authors": "Auteurs",
            "title": "Titre",
            "publisher": "Maison d'édition",
            "year": "Année",
            "isbn": "ISBN",
            "backCover": "Présentation",
            "cover": "Couverture",
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["body", "rating"]


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ["first_name", "last_name"]

        labels = {
            "first_name": "Prénom",
            "last_name": "Nom",
        }