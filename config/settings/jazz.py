from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Jazzmin branding and UI configuration.
# See https://django-jazzmin.readthedocs.io/en/latest/configuration/ for supported options.
JAZZMIN_SETTINGS = {
    "site_title": "School ERP Admin",
    "site_header": "School ERP",
    "site_brand": "School ERP",
    "site_logo": "images/logo.png",
    "login_logo": "images/logo.png",
    "login_logo_dark": "images/logo.png",
    "site_icon": "images/favicon.png",
    "welcome_sign": "Welcome to School ERP administration",
    "copyright": "School ERP © 2026",
    "search_model": "auth.User",
    "user_avatar": "user-avatar.png",
    "topmenu_links": [
        {"name": "Home", "url": "/", "permissions": ["auth.view_user"]},
        {"model": "auth.user", "name": "Users", "permissions": ["auth.view_user"]},
        {"app": "plans", "name": "Plans", "permissions": ["plans.view_plan"]},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "auth",
        "apps.accounts",
        "apps.schools",
        "apps.fees",
        "apps.results",
        "apps.plans",
        "apps.core",
    ],
    "custom_links": {
        "accounts": [
            {
                "name": "Profile",
                "url": "#",
                "icon": "fas fa-user",
                "permissions": ["auth.view_user"],
            }
        ]
    },
    "icons": {
        "auth": "fas fa-user-shield",
        "apps.accounts": "fas fa-users",
        "apps.schools": "fas fa-school",
        "apps.fees": "fas fa-money-bill-wave",
        "apps.results": "fas fa-clipboard-check",
        "apps.plans": "fas fa-crown",
        "apps.core": "fas fa-home",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "custom_css": None,
    "custom_js": None,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "pill_badge": True,
    "navbar_fixed": True,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar_scrollbar": True,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_flat": True,
    "theme": "darkly",
    "dark_mode_theme": None,
}

JAZZMIN_SETTINGS.update(
    {
        "topmenu_links": [
            {"name": "Dashboard", "url": "/admin/", "permissions": ["auth.view_user"]},
            {"name": "School Website", "url": "/", "new_window": True},
        ]
    }
)
