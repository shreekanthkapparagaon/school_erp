# Service Package Plan for School ERP

## Overview

This plan introduces tiered service packages and subscription-based feature control for the School ERP. The new `plans` app will support:
- feature definitions and plan feature maps
- school subscriptions tied to plans
- admin management of packages and subscriptions
- runtime feature gating through a plan-aware helper

---

## 1) Package Tiers and Feature Mapping

### Basic

Included features:
- user authentication and dashboards
- school, class, and student listing
- basic fee viewing
- basic exam/result viewing

Intended for smaller schools with manual operations.

### Intermediate

Included features:
- fee structures and receipts
- student fees and payment tracking
- exam creation and result import
- teacher subject assignment
- search, filtering, and reporting

Intended for schools that need standard fee/result workflows.

### Premium

Included features:
- all Intermediate features
- payroll and salary tracking
- advanced results reporting
- multi-school support and tenant-aware dashboards
- automated exports and advanced workflows
- custom branding and higher service limits

Intended for larger schools and organizations requiring advanced administration.

---

## 2) Data Model Proposal

### Feature
Represents a distinct capability or gated behavior.
Fields:
- `code` (unique string identifier, e.g. `results.import`)
- `name`
- `description`
- `default_enabled`

### Plan
Represents a named package tier.
Fields:
- `slug`
- `name`
- `description`
- `price_monthly`
- `price_yearly`
- `is_active`
- `limits` (JSON)
- `features` (many-to-many through `PlanFeature`)

### PlanFeature
Maps features onto plans with explicit enable/disable state.
Fields:
- `plan`
- `feature`
- `enabled`

### Subscription
Represents a school’s active plan.
Fields:
- `school`
- `plan`
- `start_date`
- `end_date`
- `status`
- `created_at`
- `updated_at`

---

## 3) Runtime Permission Enforcement

### Strategy
- Use plan-based feature mapping for gating.
- Optionally support Django permissions for coarse actions.
- Prefer `request.user.has_perm(...)` where existing permissions already apply.

### Helper
Provide a helper like `require_feature(school, feature_code)` that:
- loads the school’s current subscription
- verifies the plan includes the feature
- supports expired or cancelled subscriptions
- returns a 403 or upgrade prompt if not allowed

---

## 4) Admin UI

### Feature admin
- manage feature codes and descriptions
- toggle default enabled state

### Plan admin
- edit plan metadata, pricing, and limits
- inline assignment of features via `PlanFeature`
- quickly view plan feature counts

### Subscription admin
- list subscriptions by school and status
- display current/expired state
- search by school and plan

---

## 5) Implementation Steps

1. Create `apps.plans` app with models and admin registration.
2. Add `apps.plans` to `INSTALLED_APPS`.
3. Create initial migrations for `Feature`, `Plan`, `PlanFeature`, and `Subscription`.
4. Add helper utilities for subscription lookup and feature gating.
5. Add admin classes and optional custom admin actions.
6. Add tests for plan mapping and current-subscription behavior.

---

## 6) Future Enhancements

- add billing/invoice integration
- support add-on services and seat counts
- create self-service upgrade pages
- add usage limits and metering
- add automated sync between plan features and Django permissions
