from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# =============================================================================
# JAZZMIN
# =============================================================================

JAZZMIN_SETTINGS = {

    # -------------------------------------------------------------------------
    # Branding
    # -------------------------------------------------------------------------

    "site_title": "School ERP Admin",
    "site_header": "School ERP",
    "site_brand": "School ERP",

    "site_logo": "images/logo.png",
    "site_icon": "images/icon.ico",

    "welcome_sign": "Welcome to School ERP administration",
    "copyright": "School ERP © 2026",


    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------

    "search_model": "accounts.User",


    # -------------------------------------------------------------------------
    # Top Menu
    # -------------------------------------------------------------------------

    "topmenu_links": [

        {
            "name": "School Website",
            "url": "/",
            "new_window": True,
        },

        {
            "model": "accounts.User",
            "name": "Users",
            "permissions": ["accounts.view_user"],
        },

        {
            "app": "plans",
            "name": "Plans",
            "permissions": ["plans.view_plan"],
        },
    ],


    # -------------------------------------------------------------------------
    # Sidebar
    # -------------------------------------------------------------------------

    "show_sidebar": True,
    "navigation_expanded": True,

    "hide_apps": [],
    "hide_models": [],


    # IMPORTANT:
    # These are Django APP LABELS, not Python package paths.
    #
    # Correct:
    #     accounts
    #
    # Incorrect:
    #     apps.accounts
    #

    "order_with_respect_to": [
        "accounts",
        "schools",
        "fees",
        "results",
        "document",
        "plans",
        "core",
        "auth",
    ],


    # -------------------------------------------------------------------------
    # Icons
    # -------------------------------------------------------------------------

    "icons": {

        # =====================================================================
        # Django
        # =====================================================================

        "admin": "fas fa-cogs",

        "auth": "fas fa-user-shield",
        "auth.group": "fas fa-users-cog",
        "auth.permission": "fas fa-key",

        "contenttypes": "fas fa-database",
        "contenttypes.contenttype": "fas fa-table",

        "sessions": "fas fa-clock",
        "sessions.session": "fas fa-user-clock",


        # =====================================================================
        # ACCOUNTS
        # =====================================================================

        "accounts": "fas fa-users",

        "accounts.user": "fas fa-user",

        "accounts.profile": "fas fa-id-card",

        "accounts.profilefield": "fas fa-list-alt",

        "accounts.profilefieldvalue": "fas fa-edit",


        # =====================================================================
        # SCHOOLS
        # =====================================================================

        "schools": "fas fa-school",

        "schools.school": "fas fa-school",

        "schools.subject": "fas fa-book",

        "schools.schoolclass": "fas fa-chalkboard",

        "schools.teachersubjectassignment": "fas fa-chalkboard-teacher",


        # =====================================================================
        # FEES
        # =====================================================================

        "fees": "fas fa-money-check-alt",

        "fees.feestructure": "fas fa-file-invoice-dollar",

        "fees.studentfee": "fas fa-money-bill-wave",

        "fees.feepayment": "fas fa-receipt",

        "fees.teachersalary": "fas fa-hand-holding-usd",


        # =====================================================================
        # RESULTS
        # =====================================================================

        "results": "fas fa-graduation-cap",

        "results.exam": "fas fa-file-alt",

        "results.result": "fas fa-chart-line",


        # =====================================================================
        # DOCUMENTS
        # =====================================================================

        "document": "fas fa-folder-open",

        "document.documenttype": "fas fa-file-signature",

        "document.document": "fas fa-file-alt",


        # =====================================================================
        # PLANS / SUBSCRIPTIONS
        # =====================================================================

        "plans": "fas fa-crown",

        "plans.feature": "fas fa-puzzle-piece",

        "plans.plan": "fas fa-layer-group",

        "plans.planfeature": "fas fa-link",

        "plans.subscription": "fas fa-credit-card",


        # =====================================================================
        # CORE
        # =====================================================================

        "core": "fas fa-cogs",

        "core.contact": "fas fa-address-book",


        # =====================================================================
        # ADMIN HONEYPOT
        # =====================================================================

        "admin_honeypot": "fas fa-shield-alt",

        "admin_honeypot.loginattempt": "fas fa-user-secret",
    },


    # -------------------------------------------------------------------------
    # Default icons
    # -------------------------------------------------------------------------

    "default_icon_parents": "fas fa-folder",

    "default_icon_children": "fas fa-circle",


    # -------------------------------------------------------------------------
    # Related model popup
    # -------------------------------------------------------------------------

    "related_modal_active": True,


    # -------------------------------------------------------------------------
    # Custom CSS / JS
    # -------------------------------------------------------------------------

    "custom_css": "css/jazzmin-custom.css",

    "custom_js": None,
}


# =============================================================================
# JAZZMIN UI TWEAKS
# =============================================================================

JAZZMIN_UI_TWEAKS = {

    # -------------------------------------------------------------------------
    # Text sizing
    # -------------------------------------------------------------------------

    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,

    "sidebar_nav_small_text": False,


    # -------------------------------------------------------------------------
    # Badges
    # -------------------------------------------------------------------------

    "pill_badge": True,


    # -------------------------------------------------------------------------
    # Navbar
    # -------------------------------------------------------------------------

    "navbar_fixed": True,


    # -------------------------------------------------------------------------
    # Footer
    # -------------------------------------------------------------------------

    "footer_fixed": False,


    # -------------------------------------------------------------------------
    # Sidebar
    # -------------------------------------------------------------------------

    "sidebar_fixed": True,
    "sidebar_scrollbar": True,

    "sidebar_disable_expand": False,

    "sidebar_nav_flat": True,


    # -------------------------------------------------------------------------
    # Theme
    # -------------------------------------------------------------------------

    # Valid Bootswatch theme.
    "theme": "flatly",

    # Automatically follow light/dark system preference.
    "default_theme_mode": "auto",
}