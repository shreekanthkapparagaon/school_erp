# Tenant Implementation Plan for Shared-Schema Multitenancy

## Overview

This plan describes a shared-schema multitenancy approach for a Django-based school ERP project. It defines key concepts, explains why shared-schema is recommended, and outlines an implementation plan with relevant models and future considerations.

---

## Definitions

### Tenant
- A tenant represents an isolated customer or organization within the system.
- In a school ERP, a tenant usually corresponds to a single school, college, or educational institution.
- Each tenant has its own data scope, users, and operational boundaries.

### Multitenancy
- Multitenancy is an architecture where a single application instance serves multiple tenants.
- Tenants share application code and infrastructure while keeping data logically separated.
- It enables efficient resource use, easier deployment, and simplified maintenance.

### Shared-Schema Multitenancy
- Shared-schema means all tenants store their data in the same set of database tables.
- Tenant separation is enforced with a tenant identifier column on shared tables.
- This approach is often simpler than separate-schema or separate-database models and works well for small-to-medium projects.

---

## Why Recommend Shared-Schema

- Lower operational complexity
  - One database instance and one schema to maintain.
  - Simpler migrations and fewer deployment steps.

- Cost-effective
  - Uses a single database connection pool.
  - Reduces hosting and administration overhead.

- Easier development
  - Standard Django ORM models work without custom routing.
  - Query logic can use tenant filters rather than full database routing.

- Good fit for school ERP
  - Many shared entities like students, classes, fees, exams, and results.
  - Tenant isolation can be achieved with school-specific foreign keys and filters.

---

## Implementation Plan

### 1. Define Tenant Model
- Create a `School` (or `Tenant`) model to represent each school.
- Store tenant metadata such as:
  - name
  - code
  - address
  - contact information
  - active flag
  - tenant-specific settings

### 2. Associate Shared Entities with Tenant
- Add a foreign key to `School` on core data models.
- Important models include:
  - `School`
  - `Class`
  - `Subject`
  - `Teacher`
  - `Student`
  - `FeeStructure`
  - `StudentFee`
  - `Exam`
  - `Result`
  - `Receipt`
  - `UserProfile` or extended `User`

### 3. Enforce Tenant Filtering
- Implement tenant-aware querysets and model managers.
- Example pattern:
  - `School.objects.get(id=school_id)`
  - `Student.objects.filter(school=school)`
- Prefer centralized tenant filtering helpers or middleware.

### 4. Tenant-Aware Access Control
- Ensure views and APIs only operate within the current tenant context.
- Use middleware or request-level context to identify the active school.
- Validate that logged-in users belong to the tenant before serving data.

### 5. Configure Authentication and Authorization
- Extend the user model or create a profile linking `User` to `School`.
- Add roles for different tenant-level users:
  - principal
  - manager
  - teacher
  - student
- Ensure login and permissions are scoped to the tenant.

### 6. Deploy Shared-Schema Data Isolation
- Add tenant-specific filters in all data access paths.
- Guard create/read/update/delete operations with `school` association.
- Consider a `BaseTenantModel` mixin to standardize fields and behavior.

### 7. Test Tenant Isolation
- Write test cases for multiple tenants.
- Verify that:
  - data for one school is not visible to another
  - tenant-specific validation works
  - role-based access respects tenant boundaries

---

## Relevant Models

### School / Tenant Model
- `School`
  - `name`
  - `code`
  - `address`
  - `phone`
  - `email`
  - `is_active`
  - `created_at`
  - `updated_at`

### Base Tenant-Aware Model
- `TenantBaseModel` mixin or abstract base class
  - `school = ForeignKey(School, on_delete=CASCADE)`
  - `created_at`
  - `updated_at`
  - custom manager filtering by `school`

### Example Shared Models
- `Class`
  - `school`
  - `name`
  - `grade`
  - `teacher`

- `Subject`
  - `school`
  - `name`
  - `code`

- `Student`
  - `school`
  - `first_name`
  - `last_name`
  - `roll_number`
  - `class`

- `Teacher`
  - `school`
  - `user`
  - `subjects`

- `FeeStructure`
  - `school`
  - `name`
  - `amount`
  - `description`

- `StudentFee`
  - `school`
  - `student`
  - `fee_structure`
  - `amount_due`
  - `amount_paid`

- `Exam`
  - `school`
  - `name`
  - `term`
  - `start_date`
  - `end_date`

- `Result`
  - `school`
  - `student`
  - `exam`
  - `grade`
  - `remarks`

---

## Future Considerations

### Scaling and Performance
- Monitor performance as tenant count and row volume grow.
- Add database indexes on tenant fields such as `school_id`.
- Consider partitioning or sharding later if one tenant becomes very large.

### Security
- Enforce tenant checks consistently in all business logic and API endpoints.
- Review permissions to prevent cross-tenant data leaks.

### Tenant Configuration
- Allow tenant-specific settings through a JSON or settings model.
- Example: `school_settings` with themes, attendance rules, fee policies.

### Data Migration and Reporting
- Plan reporting queries that aggregate across tenants carefully.
- Use tenant-aware reporting filters to avoid accidental cross-tenant visibility.

### Migration Strategy
- Keep migrations simple by evolving shared tables.
- Avoid tenant-specific schema changes that complicate the shared-schema design.

### Expansion to Separate Schema Later
- If requirements change, a separate-schema model can be introduced later.
- Shared-schema is a good starting point, with migration paths possible to dedicated schemas or databases.

---

## Summary

A shared-schema multitenancy approach is well-suited for this Django school ERP:
- minimizes infrastructure complexity,
- supports standard Django models,
- and enables straightforward tenant-aware filtering.

Implementation should focus on:
- a `School` tenant model,
- tenant foreign keys on shared models,
- centralized tenant filtering,
- and strict access control.

Future planning should include performance, security, tenant-specific settings, and a possible migration path if tenants outgrow the shared-schema model.
