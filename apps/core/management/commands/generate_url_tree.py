import inspect
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver


def get_view_info(view):
    info = {
        "view": None,
        "description": inspect.getdoc(view),
    }

    # Class based view
    if hasattr(view, "view_class"):
        view_class = view.view_class

        info["view"] = (
            f"{view_class.__module__}.{view_class.__name__}"
        )

    # Function based view
    elif hasattr(view, "__module__"):
        name = getattr(view, "__name__", None)

        if name:
            info["view"] = (
                f"{view.__module__}.{name}"
            )

    return info


def build_url_tree(patterns):
    tree = {}

    for pattern in patterns:

        route = str(pattern.pattern)

        # --------------------------------
        # Normal URL
        # --------------------------------
        if isinstance(pattern, URLPattern):

            view = pattern.callback

            data = {
                "_type": "url",
                "name": pattern.name,
                **get_view_info(view),
            }

            tree[route] = data

        # --------------------------------
        # include(...)
        # --------------------------------
        elif isinstance(pattern, URLResolver):

            tree[route] = {
                "_type": "include",
                "namespace": pattern.namespace,
                "app_name": pattern.app_name,
                "children": build_url_tree(
                    pattern.url_patterns
                ),
            }

    return tree


class Command(BaseCommand):

    help = "Generate a recursive tree of all Django project URLs."

    def add_arguments(self, parser):

        parser.add_argument(
            "--output",
            default="docs",
            help=(
                "Directory relative to BASE_DIR "
                "where urls.json will be generated. "
                "Default: docs"
            ),
        )

        parser.add_argument(
            "--filename",
            default="urls.json",
            help="Output filename. Default: urls.json",
        )

        parser.add_argument(
            "--indent",
            type=int,
            default=2,
            help="JSON indentation. Default: 2",
        )

    def handle(self, *args, **options):

        output_dir = options["output"]
        filename = options["filename"]
        indent = options["indent"]

        # ------------------------------
        # Resolve output directory
        # ------------------------------

        base_dir = Path(settings.BASE_DIR)

        output_path = base_dir / output_dir

        output_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = output_path / filename

        # ------------------------------
        # Generate tree
        # ------------------------------

        resolver = get_resolver()

        tree = build_url_tree(
            resolver.url_patterns
        )

        # ------------------------------
        # Write JSON
        # ------------------------------

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                tree,
                file,
                indent=indent,
                ensure_ascii=False,
            )

            file.write("\n")

        self.stdout.write(
            self.style.SUCCESS(
                f"URL tree generated: {output_file}"
            )
        )