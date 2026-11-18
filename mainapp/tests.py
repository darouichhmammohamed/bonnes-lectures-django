from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape

from .isbn import Isbn, IsbnField
from .models import Author, Book, Review

User = get_user_model()
VALID = "978-2-07-036822-8"
INVALID = "978-2-07-036822-9"   # mauvaise clé


# ---------- Classe Isbn ----------ز
class IsbnTests(TestCase):
    def test_from_string_avec_tirets(self):
        i = Isbn.from_string(VALID)
        self.assertEqual(
            (i.prefix, i.group, i.publisher, i.title, i.check),
            ("978", "2", "07", "036822", "8"))

    def test_str_et_int(self):
        i = Isbn.from_string(VALID)
        self.assertEqual(str(i), VALID)
        self.assertEqual(int(i), 9782070368228)

    def test_sans_tirets(self):
        i = Isbn.from_string("9781718502703")
        self.assertEqual(i.digits(), "9781718502703")
        self.assertEqual(Isbn.from_string(str(i)), i)   
        for value in (VALID, "9781718502703", "9781804613061", "9781098125974"):
            Isbn.validate(value) 

    def test_mauvaise_cle(self):
        with self.assertRaises(ValidationError):
            Isbn.validate(INVALID)

    def test_mauvaise_longueur(self):
        with self.assertRaises(ValidationError):
            Isbn.validate("978-2-07")

    def test_lettres(self):
        with self.assertRaises(ValidationError):
            Isbn.validate("978-2-07-03682A-8")

    def test_mauvais_prefixe(self):
        with self.assertRaises(ValidationError):
            Isbn.validate("9771234567897")

class IsbnFieldTests(TestCase):
    def test_clean_valide(self):
        self.assertEqual(IsbnField().clean(VALID, None), Isbn.from_string(VALID))

    def test_clean_invalide(self):
        with self.assertRaises(ValidationError):
            IsbnField().clean(INVALID, None)

    def test_get_prep_value(self):
        self.assertEqual(IsbnField().get_prep_value(Isbn.from_string(VALID)), VALID)


# ---------- Données communes ----------
class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user("alice", password="motdepasse123")
        cls.bob = User.objects.create_user("bob", password="motdepasse123")
        cls.author = Author.objects.create(first_name="Albert", last_name="Camus",
                                           owner=cls.alice)
        cls.book = Book.objects.create(title="L'Étranger", publisher="Gallimard",
                                       year=1942, isbn=VALID, backCover="...",
                                       owner=cls.alice)
        cls.book.authors.add(cls.author)

    def book_data(self, isbn=VALID):
        return {"authors": [self.author.id], "title": "La Peste",
                "publisher": "Gallimard", "year": 1947, "isbn": isbn,
                "backCover": "Oran..."}



class ModelTests(BaseTestCase):
    def test_isbn_relu_comme_objet_isbn(self):
        book = Book.objects.get(pk=self.book.pk)
        self.assertIsInstance(book.isbn, Isbn)
        self.assertEqual(str(book.isbn), VALID)

    def test_str(self):
        self.assertEqual(str(self.book), "L'Étranger")
        self.assertEqual(str(self.author), "Albert Camus")

    def test_note_hors_limites(self):
        review = Review(book=self.book, body="Bof", rating=6, owner=self.bob)
        with self.assertRaises(ValidationError):
            review.full_clean()

class ViewTests(BaseTestCase):
    def test_liste_des_livres(self):
        r = self.client.get(reverse("books"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, escape("L'Étranger"))

    def test_detail_livre(self):
        r = self.client.get(reverse("book", args=[self.book.id]))
        self.assertContains(r, VALID)

    def test_livre_inexistant(self):
        r = self.client.get(reverse("book", args=[9999]))
        self.assertEqual(r.status_code, 404)

    def test_new_book_demande_connexion(self):
        r = self.client.get(reverse("new_book"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login/", r.url)

    def test_new_book_isbn_invalide(self):
        self.client.login(username="alice", password="motdepasse123")
        r = self.client.post(reverse("new_book"), self.book_data(INVALID))
        self.assertEqual(r.status_code, 200)            # formulaire réaffiché
        self.assertContains(r, "clé de contrôle incorrecte")
        self.assertFalse(Book.objects.filter(title="La Peste").exists())

    def test_new_book_isbn_valide(self):
        self.client.login(username="alice", password="motdepasse123")
        r = self.client.post(reverse("new_book"), self.book_data("9781718502703"))
        self.assertEqual(r.status_code, 302)
        book = Book.objects.get(title="La Peste")
        self.assertEqual(book.owner, self.alice)
        self.assertEqual(book.isbn.digits(), "9781718502703")

    def test_edit_book_par_un_autre_utilisateur(self):
        self.client.login(username="bob", password="motdepasse123")
        r = self.client.get(reverse("edit_book", args=[self.book.id]))
        self.assertEqual(r.status_code, 404)

    def test_edit_book_non_connecte(self):
        r = self.client.get(reverse("edit_book", args=[self.book.id]))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login/", r.url)

    def test_new_review(self):
        self.client.login(username="bob", password="motdepasse123")
        r = self.client.post(reverse("new_review", args=[self.book.id]),
                             {"body": "Super", "rating": 5})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.book.reviews.count(), 1)