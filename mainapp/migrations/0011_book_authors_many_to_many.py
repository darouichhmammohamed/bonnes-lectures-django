from django.db import migrations, models
import django.db.models.deletion


def copier_associations(apps, schema_editor):
    Book = apps.get_model("mainapp", "Book")
    database = schema_editor.connection.alias

    for book in Book.objects.using(database).all():
        if book.author_id is not None:
            book.authors.add(book.author_id)


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0010_proprietaire_obligatoire"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="authors",
            field=models.ManyToManyField(
                related_name="books",
                to="mainapp.author",
            ),
        ),
        migrations.RunPython(copier_associations),
        migrations.RemoveField(
            model_name="book",
            name="author",
        ),
    ]