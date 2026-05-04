# Generated manually to fix DataError: value too long for type character varying(10)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0025_add_student_year_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='student_id',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
