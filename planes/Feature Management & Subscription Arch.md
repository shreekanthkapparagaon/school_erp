# Feature Management & Subscription Architecture Specification

## Objective

Design and implement a scalable, modular, and enterprise-grade **Feature Management and Subscription System** for the School ERP project.

The primary objective is to build the project in such a way that **new Django applications, modules, and premium features can be added in the future without modifying the existing subscription or permission logic**.

The current project uses Django Templates (Server-Side Rendering) and **does not currently implement REST APIs**. Therefore, the implementation should focus only on Django Views, Templates, URLs, Permissions, and the Admin Panel while keeping the architecture future-ready for API integration.

The system should follow software engineering best practices and remain maintainable as the project grows into a complete SaaS platform.

---

# Current Project Architecture

The current project consists of:

* Django
* Django Templates
* Django Views (Function/Class Based)
* Django Authentication
* Django Groups
* Django Permissions
* Django Admin (Jazzmin)
* Multiple modular Django Apps

The project does **NOT** currently include:

* REST API
* Mobile Backend
* GraphQL
* External Integrations

The subscription system should therefore integrate only with the existing Django architecture.

---

# Design Principles

The implementation must follow these principles:

* Modular
* Database-driven
* Scalable
* Reusable
* Configurable
* Future-proof
* Low coupling
* High cohesion

Nothing should be hardcoded if it is expected to evolve in the future.

---

# Core Architecture

The system should follow the architecture below.

```text
School
    │
    ▼
Subscription
    │
    ▼
Subscription Plan
    │
    ▼
Enabled Features
    │
    ▼
Django Groups (Roles)
    │
    ▼
Permissions
    │
    ▼
Views / Templates
```

Each layer has its own responsibility.

---

# Layer Responsibilities

## School

Represents an individual customer (tenant).

Every school has:

* Active Subscription
* Enabled Features
* Users
* Roles
* Permissions

---

## Subscription

Represents the purchased package.

Responsible for:

* Active Plan
* Start Date
* Expiry Date
* Trial Status
* Active Status
* Renewal
* Billing (future)

The Subscription should **never** directly decide application logic.

---

## Subscription Plan

Represents predefined packages.

Examples:

* Free
* Basic
* Intermediate
* Professional
* Enterprise
* Government
* University
* Custom

Plans only define **which Features are included**.

---

## Features

A Feature represents a complete application module or premium capability.

Examples:

```
students
teachers
attendance
fees
library
inventory
transport
hostel
academics
examinations
analytics
dashboard
reports
sms
whatsapp
online_exam
ai_reports
api_access
custom_branding
multi_campus
```

A Feature is independent from user permissions.

Features determine whether an entire module is available to a school.

---

## User Roles

Continue using Django Groups.

Examples:

* Principal
* Head Master
* Teacher
* Accountant
* Librarian
* Receptionist
* Parent
* Student

Roles manage permissions.

Roles do NOT manage subscriptions.

---

## Permissions

Continue using Django's built-in permission system.

Examples:

Attendance

```
attendance.view
attendance.add
attendance.change
attendance.delete
attendance.mark
attendance.export
```

Fees

```
fees.view
fees.collect
fees.refund
fees.export
```

Students

```
student.view
student.add
student.change
student.delete
student.promote
student.archive
student.import
student.export
```

Permissions define **what a user can do**, while Features define **whether the module exists for that school**.

---

# Database Models

Design a flexible database structure similar to:

## Feature

Fields

* code
* name
* description
* app_name
* icon
* category
* is_active
* is_premium
* is_beta
* coming_soon
* display_order
* created_at
* updated_at

---

## SubscriptionPlan

Fields

* name
* slug
* description
* monthly_price
* yearly_price
* is_active
* display_order

Do not hardcode plan names.

---

## PlanFeature

Many-to-Many relationship.

```
Plan
↓

Features
```

This determines which features belong to each plan.

---

## SchoolSubscription

Fields

* school
* plan
* start_date
* end_date
* status
* trial
* auto_renew

Future billing fields can be added later.

---

# Feature-Based Architecture

Every Django application should be treated as a Feature.

Examples

```
students/
teachers/
attendance/
fees/
library/
transport/
inventory/
```

Each application should register itself as a Feature.

The system should never assume a fixed number of applications.

---

# Automatic Expansion

The architecture should allow the following workflow.

Current project

```
students
teachers
fees
```

Six months later

Create

```
attendance/
```

Implementation should require only:

1. Create Django App

2. Register Feature

```
Attendance
```

3. Assign Feature to one or more Subscription Plans

Done.

No other application code should require modification.

---

# Dynamic Navigation

The sidebar should automatically display only enabled Features.

Example

Basic Plan

```
Dashboard
Students
Teachers
Fees
Library
```

Attendance should not appear.

---

Professional Plan

```
Dashboard
Students
Teachers
Attendance
Fees
Library
Transport
Inventory
Analytics
```

Menus should be generated dynamically.

Avoid hardcoded navigation.

---

# Upgrade Behaviour

The implementation should support two modes.

## Mode 1 (Recommended)

Hide unavailable Features.

Cleaner user experience.

---

## Mode 2

Show unavailable Features with lock icon.

Example

```
Attendance 🔒

Transport 🔒

Inventory 🔒
```

Clicking opens

```
Upgrade Required

Attendance is not available in your current subscription.

Current Plan

Basic

Required Plan

Intermediate

[ Upgrade ]
```

Allow switching between these modes through configuration.

---

# URL Protection

If a user manually opens

```
/attendance/

/attendance/list/

/attendance/create/
```

The request should never reach the view.

Instead show

* Upgrade Required

or

* 403 Permission Denied

depending on configuration.

---

# View Protection

Create reusable decorators or mixins.

Example

```
@feature_required("attendance")
```

or

```
FeatureRequiredMixin
```

Every Feature should use the same implementation.

Avoid duplicated code.

---

# Template Support

Create reusable template tags.

Example

```
{% if school|has_feature:"attendance" %}
```

or

```
{% feature_enabled "attendance" %}
```

Avoid writing raw subscription logic in templates.

---

# Context Processor

Create a context processor that exposes enabled Features globally.

Example

```
enabled_features

school_subscription

current_plan
```

This avoids repeated database queries.

---

# Middleware (Optional)

If appropriate, create middleware that can validate feature access before the request reaches the view.

The middleware should remain generic and configurable.

---

# Django Admin

Administrators should be able to:

* Create Subscription Plans
* Edit Plans
* Activate Plans
* Disable Plans
* Create Features
* Assign Features to Plans
* Configure display order
* Configure Coming Soon Features
* Configure Premium Features

without changing source code.

---

# Pricing Page

Create a dedicated Pricing page.

Display

* Plan Cards
* Monthly Pricing
* Annual Pricing
* Included Features
* Locked Features
* Upgrade Buttons
* Coming Soon Plans

Everything should be generated dynamically from the database.

---

# Future Compatibility

Although the project currently does not contain REST APIs, the architecture should be designed so that future API integration is straightforward.

When an API application is added later, it should reuse the existing Feature Management system without requiring database or architectural changes.

Do **not** implement API support now—only ensure the design is compatible with future expansion.

---

# Future Expansion

The architecture must support adding new modules such as:

* Hostel
* Transport
* Inventory
* Cafeteria
* Visitor Management
* HR & Payroll
* CRM
* SMS
* WhatsApp
* AI Assistant
* Analytics
* Online Classes
* Video Meetings
* API Access
* Marketplace
* Plugin System

without modifying existing subscription logic.

---

# Optional Add-ons

The system should be designed so that future support for paid add-ons can be implemented without redesign.

Example:

Basic Plan

*

Attendance Add-on

*

SMS Add-on

*

Transport Add-on

This should only require extending the data model, not rewriting the architecture.

---

# Coding Standards

The implementation must:

* Follow Django best practices.
* Be modular.
* Avoid duplicated logic.
* Use reusable decorators, mixins, services, and utilities.
* Keep business logic outside templates.
* Use clean naming conventions.
* Include docstrings and comments where necessary.

---

# Documentation

Document every major component.

Include:

* Purpose
* Relationships
* Usage
* Future improvements
* Design decisions

The codebase should be understandable by future developers and AI coding agents.

---

# Deliverables

The implementation should produce:

1. Complete Feature Management System.
2. Subscription Plan Management.
3. Feature-to-Plan Mapping.
4. School Subscription Management.
5. Dynamic Navigation.
6. Feature-aware Sidebar.
7. Template Tags.
8. Context Processor.
9. Feature Decorators/Mixins.
10. Upgrade Required Page.
11. Pricing Page.
12. Django Admin Management.
13. Comprehensive documentation.
14. Architecture that supports unlimited future Django apps and subscription plans.

---

# Success Criteria

The implementation will be considered successful if the following workflow is possible without modifying existing business logic:

1. Develop a new Django app (for example, `attendance`).
2. Register the app as a Feature.
3. Assign the Feature to one or more Subscription Plans.
4. The sidebar, menus, templates, and views automatically respect the feature availability.
5. Existing role-based permissions continue to work without changes.
6. No existing code needs to be rewritten when introducing new modules or subscription plans.

The final architecture should become the long-term foundation of the School ERP SaaS platform, enabling continuous expansion while maintaining clean, modular, and maintainable code.
