# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_game_away_pitcher_name_game_away_pitcher_stats_and_more'),
    ]

    operations = [
        # Add new Team fields
        migrations.AddField(
            model_name='team',
            name='games_played',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team',
            name='points_for',
            field=models.DecimalField(decimal_places=1, default=0.0, help_text='Average points scored', max_digits=6),
        ),
        migrations.AddField(
            model_name='team',
            name='points_against',
            field=models.DecimalField(decimal_places=1, default=0.0, help_text='Average points allowed', max_digits=6),
        ),
        migrations.AddField(
            model_name='team',
            name='differential',
            field=models.DecimalField(decimal_places=1, default=0.0, help_text='Point differential', max_digits=6),
        ),
        migrations.AddField(
            model_name='team',
            name='division_win_percent',
            field=models.DecimalField(decimal_places=3, default=0.0, help_text='Division win percentage', max_digits=5),
        ),
        migrations.AddField(
            model_name='team',
            name='games_behind',
            field=models.DecimalField(decimal_places=1, default=0.0, help_text='Games behind leader', max_digits=4),
        ),
        migrations.AddField(
            model_name='team',
            name='conference_rank',
            field=models.IntegerField(blank=True, help_text='Conference ranking', null=True),
        ),
        migrations.AddField(
            model_name='team',
            name='division_rank',
            field=models.IntegerField(blank=True, help_text='Division ranking', null=True),
        ),
        
        # Create Player model
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(help_text='External API ID for this player', max_length=50, unique=True)),
                ('first_name', models.CharField(blank=True, default='', max_length=100)),
                ('last_name', models.CharField(blank=True, default='', max_length=100)),
                ('full_name', models.CharField(blank=True, default='', max_length=200)),
                ('display_name', models.CharField(blank=True, default='', max_length=200)),
                ('short_name', models.CharField(blank=True, default='', max_length=100)),
                ('jersey_number', models.CharField(blank=True, max_length=5)),
                ('position', models.CharField(blank=True, max_length=50)),
                ('position_abbreviation', models.CharField(blank=True, max_length=10)),
                ('height', models.CharField(blank=True, help_text='Display height (e.g., 6\' 5")', max_length=20)),
                ('weight', models.CharField(blank=True, help_text='Display weight (e.g., 210 lbs)', max_length=20)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('headshot_url', models.URLField(blank=True, null=True)),
                ('status', models.CharField(default='Active', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='core.team')),
            ],
            options={
                'verbose_name': 'Player',
                'verbose_name_plural': 'Players',
                'ordering': ['team', 'last_name', 'first_name'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='player',
            index=models.Index(fields=['team', 'jersey_number'], name='core_player_team_id_jersey_idx'),
        ),
        migrations.AddIndex(
            model_name='player',
            index=models.Index(fields=['team', 'position_abbreviation'], name='core_player_team_id_position_idx'),
        ),
    ]
