# Create a file management/commands/check_streaks.py
from django.core.management.base import BaseCommand
from users.models import DailyActivity

class Command(BaseCommand):
    help = 'Check and reset user streaks if they missed a day'

    def handle(self, *args, **kwargs):
        DailyActivity.check_and_reset_streaks()
        self.stdout.write(self.style.SUCCESS('Successfully checked and reset streaks'))