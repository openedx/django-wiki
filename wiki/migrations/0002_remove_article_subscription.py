from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_notify', '0001_initial'),
        ('wiki', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ArticleSubscription',
        ),
    ]
