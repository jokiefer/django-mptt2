# Generated by Django 4.2 on 2023-06-16 01:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mptt2', '0001_initial'),
        ('tests', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simplenode',
            name='mptt_tree',
            field=models.ForeignKey(editable=False, help_text='The unique tree, where this node is part of', on_delete=django.db.models.deletion.CASCADE, related_name='nodes', related_query_name='node', to='mptt2.tree', verbose_name='tree'),
        ),
    ]