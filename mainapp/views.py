from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book , Review , Author
from .forms import BookForm 
from .forms import ReviewForm
from .forms import AuthorForm
from django.core.paginator import Paginator
from django.db.models.deletion import ProtectedError
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Create your views here.
def about(request):
    return HttpResponse("Application Bonnes Lectures, développée en TP de Framework Web, Université d’Orléans ,2026")


def welcome(request):
    return render(request, "mainapp/welcome.html")


def books(request):
    books_list = Book.objects.all().order_by("id")
    paginator = Paginator(books_list, 10)

    page_number = request.GET.get("page")
    books = paginator.get_page(page_number)

    return render(request, "mainapp/books.html", {
        "books": books,
    })


def book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    reviews_list = book.reviews.all().order_by("id")
    paginator = Paginator(reviews_list, 5)

    page_number = request.GET.get("page")
    reviews = paginator.get_page(page_number)

    return render(request, "mainapp/book.html", {
        "book": book,
        "reviews": reviews,
    })

@login_required
def new_book(request):
    if request.method == "POST":
        form = BookForm(request.POST)

        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user
            book.save()
            form.save_m2m()
            return redirect("book", book_id=book.id)
    else:
        form = BookForm()

    return render(request, "mainapp/book_form.html", {
        "form": form
    })


@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id , owner=request.user)
    if request.method == "POST":
        book.delete()        
        return redirect("books")
    return render(request, "mainapp/book_confirm_delete.html", {"book": book})

@login_required
def edit_book(request, book_id):  
    book = get_object_or_404(Book, id=book_id ,owner=request.user)    
    if request.method == "POST":        
        form = BookForm(request.POST, instance=book)        
        if form.is_valid():            
            form.save()            
            return redirect("book", book_id=book.id)    
    else:        
        form = BookForm(instance=book)
                
    return render( 
        request,
            "mainapp/book_form.html",        
            {"form": form}    )
@login_required
def new_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.owner = request.user
            review.save()
            form.save_m2m()
            return redirect("book", book_id=book.id)
    else:
        form = ReviewForm()

    return render(request, "mainapp/review_form.html", {
        "form": form,
        "book": book,
    })


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id , owner=request.user)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)

        if form.is_valid():
            form.save()
            return redirect("book", book_id=review.book.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, "mainapp/review_form.html", {
        "form": form,
        "book": review.book,
    })


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id , owner=request.user)
    book_id = review.book.id

    if request.method == "POST":
        review.delete()
        return redirect("book", book_id=book_id)

    return render(request, "mainapp/review_confirm_delete.html", {
        "review": review,
        "book": review.book,
    })

def authors(request):
    authors_list = Author.objects.all().order_by("last_name")

    return render(
        request,
        "mainapp/authors.html",
        {"authors": authors_list}
    )

def author_detail(request, author_id):
    author = get_object_or_404(Author, pk=author_id)

    return render(
        request,
        "mainapp/author_detail.html",
        {"author": author}
    )
@login_required
def new_author(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)

        if form.is_valid():
            author = form.save(commit=False)
            author.owner = request.user
            author.save()
            form.save_m2m()
            return redirect("author_detail", author_id=author.id)
    else:
        form = AuthorForm()

    return render(
        request,
        "mainapp/author_form.html",
        {"form": form}
    )

@login_required
def edit_author(request, author_id):
    author = get_object_or_404(Author, pk=author_id , owner=request.user)

    if request.method == "POST":
        form = AuthorForm(request.POST, instance=author)

        if form.is_valid():
            form.save()
            return redirect("author_detail", author_id=author.id)
    else:
        form = AuthorForm(instance=author)

    return render(
        request,
        "mainapp/author_form.html",
        {
            "form": form,
            "author": author
        }
    )

def delete_author(request, author_id):
    author = get_object_or_404(Author, pk=author_id)

    if request.method == "POST":
        try:
            author.delete()
            return redirect("authors")
        except ProtectedError:
            return render(
                request,
                "mainapp/author_confirm_delete.html",
                {
                    "author": author,
                    "error": (
                        "Impossible de supprimer cet auteur : "
                        "il est encore associé à un ou plusieurs livres."
                    )
                },
                status=200
            )

    return render(
        request,
        "mainapp/author_confirm_delete.html",
        {"author": author}
    )