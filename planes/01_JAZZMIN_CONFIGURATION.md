# Django Jazzmin Configuration Refactoring & UI Customization Specification

## Objective

Refactor the Django Admin configuration by separating all Jazzmin-related settings into a dedicated configuration module. The goal is to keep the Django settings organized, improve maintainability, and create a professional, branded administration panel that is easy to customize as the project grows.

The implementation should follow Django best practices and be designed for future scalability.

---

# Project Structure

Currently the project contains multiple settings files similar to:

```
config/
    settings/
        __init__.py
        base.py
        dev.py
        prod.py
```

Refactor the configuration by introducing a dedicated Jazzmin configuration file.

The final structure should become:

```
config/
└── settings/
    ├── __init__.py
    ├── base.py
    ├── dev.py
    ├── prod.py
    └── jazz.py
```

The `jazz.py` file should contain **only** Jazzmin-related configuration.

`base.py` should simply import the configuration from `jazz.py` instead of containing large configuration dictionaries.

Example (conceptually):

```
from .jazz import *

JAZZMIN_SETTINGS = JAZZMIN_SETTINGS
JAZZMIN_UI_TWEAKS = JAZZMIN_UI_TWEAKS
```

This keeps the settings modular and easier to maintain.

---

# Jazzmin Configuration Goals

Configure the Django Admin so it reflects the branding of the School ERP application.

The admin panel should feel like a modern enterprise dashboard rather than the default Django administration interface.

Configure as many Jazzmin customization options as possible.

---

# Branding

Customize the overall branding of the admin.

Include configuration for:

* Site title
* Site header
* Site brand
* Browser title
* Welcome message
* Copyright
* Footer text
* Login page title
* Login page subtitle
* Dashboard heading
* Dashboard description
* Home page title
* Home page subtitle

Everything should use consistent School ERP branding.

---

# Logo Configuration

Configure support for:

* Main logo
* Login logo
* Mini sidebar logo
* Favicon
* Dark mode logo (if supported)
* Retina logo (if available)

Logos should reference static files rather than hardcoded URLs.

---

# Navigation

Customize the navigation experience.

Configure:

* Sidebar visibility
* Top navigation
* Navigation expansion
* Ordering of applications
* Ordering of models
* Custom menu labels
* Custom application grouping
* Custom separators

Frequently used modules should appear first.

Administrative modules should be grouped logically.

---

# Application Icons

Assign icons for every Django application using a consistent icon library supported by Jazzmin (such as Font Awesome).

Examples include:

Dashboard

* Gauge
* Home

Students

* Graduation Cap

Teachers

* Chalkboard Teacher

Staff

* Users

Attendance

* Calendar Check

Fees

* Money Bill

Examinations

* Clipboard Check

Library

* Book

Transport

* Bus

Inventory

* Boxes

Reports

* Chart Bar

Settings

* Cog

Authentication

* User Shield

Audit Logs

* History

Notifications

* Bell

Plans / Subscription

* Crown

Analytics

* Chart Line

Every app should have an appropriate and visually consistent icon.

---

# UI Theme

Configure the overall appearance.

Define:

* Primary color
* Secondary color
* Sidebar color
* Accent color
* Navbar color
* Button styles
* Border radius
* Shadows
* Typography preferences

The theme should match the main School ERP frontend so the admin panel has a consistent visual identity.

---

# Button Styles

Where supported by Jazzmin, configure modern button styles.

Prefer outlined button variants instead of solid buttons.

Examples:

```
Primary Outline

Success Outline

Warning Outline

Danger Outline

Info Outline
```

If Jazzmin does not support outlined buttons natively, document alternative approaches such as custom CSS overrides.

---

# Dashboard Customization

Improve the administrator dashboard.

Configure:

* Dashboard title
* Dashboard subtitle
* Quick links
* Frequently used models
* Recent actions
* Favorite applications
* Shortcuts
* Statistics panels (where supported)
* Welcome banner

The dashboard should provide quick access to the most commonly used administrative functions.

---

# User Menu

Customize the user dropdown menu.

Include:

* Profile
* Change Password
* Documentation
* Support
* Logout

If custom links are supported, add placeholders for future features.

---

# Search Configuration

Improve the admin search experience.

Configure:

* Search bar visibility
* Global search
* Search result ordering
* Quick navigation
* Related object search

---

# Sidebar Configuration

Customize:

* Sidebar compact mode
* Sidebar expansion
* Fixed sidebar
* Scroll behavior
* Custom separators
* Collapsible menus
* Default expanded applications

---

# Forms and Tables

Improve the appearance of:

* Tables
* Inline forms
* Filters
* Pagination
* Form layouts
* Date pickers
* Action buttons
* Fieldsets

Ensure readability and consistency across all admin pages.

---

# Performance

Avoid unnecessary configuration duplication.

Only define options that are actually used.

Keep the configuration clean, modular, and well documented.

---

# Documentation

Every section inside `jazz.py` should include comments explaining:

* Purpose
* Supported Jazzmin option
* Default value
* Reason for customization

The file should be easy for future developers to modify without consulting external documentation.

---

# Future Extensibility

Structure the configuration so future additions are straightforward.

Examples:

* Custom themes
* Dark mode
* Organization branding
* Multi-tenant branding
* Custom dashboard widgets
* Additional navigation links
* Plugin integrations

Avoid hardcoded values wherever practical.

---

# Deliverables

The implementation should include:

1. A new `config/settings/jazz.py` module containing all Jazzmin configuration.
2. Refactored `base.py` that imports Jazzmin settings from the dedicated module.
3. Complete branding configuration for the School ERP admin panel.
4. Icons assigned to all applications.
5. Improved navigation and dashboard configuration.
6. Modern UI tweaks and styling where supported.
7. Clean, well-commented, and maintainable configuration.
8. Documentation for unsupported Jazzmin features along with recommended alternatives (such as custom CSS or template overrides).
9. A configuration structure that can be easily extended as the project evolves without requiring major refactoring.
