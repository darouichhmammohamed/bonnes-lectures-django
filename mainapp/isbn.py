from django.core.exceptions import ValidationError
from django.db import models

class Isbn:
    def __init__(self, prefix, group, publisher, title, check):
        self.prefix = prefix
        self.group = group
        self.publisher = publisher
        self.title = title
        self.check = check

    @classmethod
    def from_string(cls, value):
        value = str(value).strip().replace(" ", "-")
        parts = [p for p in value.split("-") if p]
        if len(parts) == 5:
            return cls(*parts)
        digits = "".join(parts)
        # sans tirets : on ne peut pas séparer groupe / éditeur / titre
        return cls(digits[:3], digits[3:-1], "", "", digits[-1:])

    def digits(self):
        return f"{self.prefix}{self.group}{self.publisher}{self.title}{self.check}"

    @staticmethod
    def compute_check(first12):
        total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(first12))
        return str((10 - total % 10) % 10)

    @staticmethod
    def validate(value):
        isbn = value if isinstance(value, Isbn) else Isbn.from_string(value)
        d = isbn.digits()
        if len(d) != 13 or not d.isdigit():
            raise ValidationError(
                "%(value)s : un ISBN doit contenir 13 chiffres.",
                params={"value": value}, code="invalid_length")
        if isbn.prefix not in ("978", "979"):
            raise ValidationError(
                "%(value)s : le préfixe doit être 978 ou 979.",
                params={"value": value}, code="invalid_prefix")
        if Isbn.compute_check(d[:12]) != d[12]:
            raise ValidationError(
                "%(value)s : clé de contrôle incorrecte.",
                params={"value": value}, code="invalid_check")

    def __str__(self):
        return "-".join(p for p in (self.prefix, self.group, self.publisher,
                                    self.title, self.check) if p)

    def __int__(self):
        return int(self.digits())

    def __eq__(self, other):
        return isinstance(other, Isbn) and self.digits() == other.digits()

    def __repr__(self):
        return f"Isbn('{self}')"

    from django.db import models   # <- en haut du fichier, avec l'autre import


class IsbnField(models.Field):
    description = "Un ISBN-13"
    default_validators = [Isbn.validate]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 17)   # 13 chiffres + 4 tirets
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"                    # colonne VARCHAR en base

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return Isbn.from_string(value)

    def to_python(self, value):
        if value is None or isinstance(value, Isbn):
            return value
        return Isbn.from_string(value)

    def get_prep_value(self, value):
        if value is None:
            return None
        return str(self.to_python(value))

    def value_to_string(self, obj):
        return str(self.value_from_object(obj))  

    def formfield(self, **kwargs):
        return super().formfield(**{"max_length": self.max_length, **kwargs})