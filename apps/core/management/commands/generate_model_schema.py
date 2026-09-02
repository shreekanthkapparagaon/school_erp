import json
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Generate Django model schema as JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="docs",
        )

        parser.add_argument(
            "--filename",
            default="models.json",
        )

    def handle(self, *args, **options):

        output_dir = (
            Path(settings.BASE_DIR)
            / options["output"]
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            output_dir
            / options["filename"]
        )

        schema = {}

        for model in apps.get_models():

            app_label = model._meta.app_label
            model_name = model.__name__

            app = schema.setdefault(
                app_label,
                {
                    "models": {}
                }
            )

            model_data = {
                "name": model_name,
                "db_table": model._meta.db_table,
                "fields": [],
            }

            for field in model._meta.get_fields():

                field_data = {
                    "name": field.name,
                    "type": type(field).__name__,
                    "many_to_many": field.many_to_many,
                    "many_to_one": field.many_to_one,
                    "one_to_many": field.one_to_many,
                    "one_to_one": field.one_to_one,
                }

                # Concrete database field
                if hasattr(field, "column"):
                    field_data["column"] = field.column

                if hasattr(field, "primary_key"):
                    field_data["primary_key"] = (
                        field.primary_key
                    )

                if hasattr(field, "unique"):
                    field_data["unique"] = field.unique

                if hasattr(field, "null"):
                    field_data["null"] = field.null

                if hasattr(field, "blank"):
                    field_data["blank"] = field.blank

                # Relationship
                if hasattr(field, "related_model"):
                    if field.related_model:
                        field_data["related_model"] = (
                            field.related_model._meta.label
                        )

                if hasattr(field, "remote_field"):
                    remote = field.remote_field

                    if remote:
                        if remote.model:
                            field_data["target"] = (
                                remote.model._meta.label
                            )

                        if hasattr(remote, "related_name"):
                            field_data["related_name"] = (
                                remote.related_name
                            )

                        if hasattr(remote, "on_delete"):
                            field_data["on_delete"] = (
                                getattr(
                                    remote.on_delete,
                                    "__name__",
                                    str(remote.on_delete),
                                )
                            )

                model_data["fields"].append(
                    field_data
                )

            app["models"][model_name] = model_data

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                schema,
                f,
                indent=2,
                ensure_ascii=False,
            )

            f.write("\n")

        self.stdout.write(
            self.style.SUCCESS(
                f"Model schema generated: {output_file}"
            )
        )