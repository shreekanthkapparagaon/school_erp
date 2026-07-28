from django.utils.html import format_html


EMPTY_VALUE = format_html(
    '<span style="color:#999;">— Empty —</span>'
)


def boolean_badge(
    value,
    *,
    true_text="Yes",
    false_text="No",
    true_color="green",
    false_color="red",
):
    return format_html(
        '<span style="color:{};font-weight:bold;">● {}</span>',
        true_color if value else false_color,
        true_text if value else false_text,
    )


def required_badge(value):
    return boolean_badge(
        value,
        true_text="Required",
        false_text="Optional",
        false_color="#777",
    )


def active_badge(value):
    return boolean_badge(
        value,
        true_text="Active",
        false_text="Inactive",
    )


def file_badge(file):
    if not file:
        return EMPTY_VALUE

    return format_html(
        '<a href="{}">📎 {}</a>',
        file.url,
        file.name.split("/")[-1],
    )


def truncate_value(value, length=60):
    if not value:
        return EMPTY_VALUE

    value = str(value)

    if len(value) <= length:
        return value

    return f"{value[:length]}..."