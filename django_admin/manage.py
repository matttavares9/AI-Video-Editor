#!/usr/bin/env python
"""Django entry point for the editor review/admin site."""
import os
import sys
from pathlib import Path


def main() -> None:
    repository_root = str(Path(__file__).resolve().parent.parent)
    if repository_root not in sys.path:
        sys.path.insert(0, repository_root)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_admin.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
