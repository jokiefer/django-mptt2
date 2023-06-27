# Generated by Django 4.2.2 on 2023-06-26 00:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mptt2', '0001_initial'),
        ('tests', '0003_simplenode_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtherNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mptt_lft', models.PositiveIntegerField(editable=False, help_text='The left value of the node', verbose_name='left')),
                ('mptt_rgt', models.PositiveIntegerField(editable=False, help_text='The right value of the node', verbose_name='right')),
                ('mptt_depth', models.PositiveIntegerField(editable=False, help_text='The hierarchy level of this node inside the tree', verbose_name='depth')),
                ('title', models.CharField(default='some node', max_length=10)),
            ],
            options={
                'ordering': ['mptt_tree_id', 'mptt_lft'],
                'abstract': False,
            },
        ),
        migrations.RemoveConstraint(
            model_name='simplenode',
            name='rgt_gt_lft',
        ),
        migrations.AlterField(
            model_name='simplenode',
            name='mptt_tree',
            field=models.ForeignKey(editable=False, help_text='The unique tree, where this node is part of', on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_nodes', related_query_name='%(app_label)s_%(class)s_node', to='mptt2.tree', verbose_name='tree'),
        ),
        migrations.AddConstraint(
            model_name='simplenode',
            constraint=models.CheckConstraint(check=models.Q(('mptt_rgt__gt', models.F('mptt_lft'))), name='tests_simplenode_rgt_gt_lft', violation_error_message='The right side value rgt is allways greater than the node left side value lft.'),
        ),
        migrations.AddField(
            model_name='othernode',
            name='mptt_parent',
            field=models.ForeignKey(editable=False, help_text='The parent of this node', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chilren', related_query_name='child', to='tests.othernode', verbose_name='parent'),
        ),
        migrations.AddField(
            model_name='othernode',
            name='mptt_tree',
            field=models.ForeignKey(editable=False, help_text='The unique tree, where this node is part of', on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_nodes', related_query_name='%(app_label)s_%(class)s_node', to='mptt2.tree', verbose_name='tree'),
        ),
        migrations.AddIndex(
            model_name='othernode',
            index=models.Index(fields=['mptt_tree_id', 'mptt_lft', 'mptt_rgt'], name='tests_other_mptt_tr_0acc71_idx'),
        ),
        migrations.AddConstraint(
            model_name='othernode',
            constraint=models.CheckConstraint(check=models.Q(('mptt_rgt__gt', models.F('mptt_lft'))), name='tests_othernode_rgt_gt_lft', violation_error_message='The right side value rgt is allways greater than the node left side value lft.'),
        ),
    ]
