# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project follows [Semantic Versioning](https://semver.org/).

---
## [1.1.0] - 2026-07-28

### Added

- Modular package structure for multiple Django applications.
- Document status management.
- Results export utility modules.
- Report card and result management pages.
- Profile-specific stylesheet.
- Environment configuration example (`.env.example`).
- Project changelog for release tracking.

### Changed

- Modularized Accounts app into dedicated models, views, forms, admin, and utilities.
- Modularized Schools app for improved maintainability.
- Modularized Fees app with reusable components.
- Modularized Plans app and feature management structure.
- Modularized Results app with separated models, views, forms, utilities, and tests.
- Modularized Document app with reusable utilities and improved organization.
- Refactored results export workflow with centralized workbook generation.
- Improved management commands and project organization.
- Updated Django settings structure.
- Enhanced profile page UI.
- Improved results, schools, fees, and document management templates.
- Updated shared application theme and base layout.
- Improved overall project maintainability and code organization.

### Fixed

- Improved import/export workflow reliability.
- Fixed document workflow consistency.
- Improved reusable utility handling across applications.
- Reduced code duplication across modules.
- General UI consistency improvements.
- Minor bug fixes and performance optimizations.

---


## [1.0.2] - 2026-07-22

### Added

- Redesigned homepage with a modern landing page.
- Added Core Modules showcase.
- Improved dashboard summary cards.
- Updated project documentation.

### Changed

- Simplified feature-based permission architecture.
- Improved dashboard layouts.
- Enhanced homepage UI and navigation.
- Refactored feature management.
- Improved project structure and maintainability.

### Fixed

- Fixed UI inconsistencies.
- Improved permission handling.
- General code cleanup.
- Minor performance improvements.

---

## [1.0.1] - 2026-07-09

### Added

- Subscription management.
- Subscription plans.
- Feature management.
- Examination module.
- Fee management module.
- Academic year management.
- Student promotion workflow.

### Changed

- Improved project architecture.
- Better database relationships.
- Enhanced Django Admin.
- Improved scalability.

### Fixed

- Permission handling improvements.
- Database migration reliability.
- Navigation fixes.
- UI improvements.

---

## [1.0.0] - 2026-06-30

### Added

- Initial School ERP release.
- Multi-school architecture.
- Authentication and authorization.
- Student management.
- Teacher management.
- Academic management.