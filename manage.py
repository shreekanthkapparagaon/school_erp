#!/usr/bin/env python
import os
import sys


def main():
    # Default to development settings for local management commands. To run
    # production commands or deploy, set the DJANGO_SETTINGS_MODULE environment
    # variable to `config.settings.prod`.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
