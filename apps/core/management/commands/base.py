from django.core.management.base import BaseCommand


class DemoCommand(BaseCommand):
    DEMO_DOMAIN = "demo.schoolerp.test"
    DEMO_SCHOOL_PREFIX = "DEMO"

    def notice(self, message):
        self.stdout.write(self.style.NOTICE(message))

    def success(self, message):
        self.stdout.write(self.style.SUCCESS(message))

    def warning(self, message):
        self.stdout.write(self.style.WARNING(message))