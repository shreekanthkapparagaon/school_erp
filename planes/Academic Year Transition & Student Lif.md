# Academic Year Transition & Student Lifecycle Management Specification

## Objective

Design and implement a complete Academic Year Transition System for the School ERP.

The system should automate the transition between academic years while maintaining complete historical records and allowing manual intervention when necessary.

The architecture should support bulk promotion, individual promotion, detention (failed students), graduation, transfers, withdrawals, alumni management, and student archival.

The implementation should be scalable and suitable for schools of different sizes.

---

# Core Principles

The student should **never lose historical academic records**.

Instead of changing the student's existing history, create new academic records for each academic year.

Every promotion should preserve:

* Academic Year
* Class
* Section
* Roll Number
* Attendance
* Results
* Fees
* Remarks

Historical data should always remain accessible.

---

# Student Lifecycle

A student should move through the following lifecycle.

```text
Admission

↓

Active Student

↓

Academic Promotion

↓

Active Student

↓

Academic Promotion

↓

Graduation

↓

Alumni
```

Other possible paths

```text
Admission

↓

Transfer

↓

Transferred
```

```text
Admission

↓

Dropout

↓

Inactive
```

```text
Admission

↓

Expelled

↓

Archived
```

The lifecycle should always be traceable.

---

# Academic Session

The system should support multiple Academic Years.

Examples

```
2025-26

2026-27

2027-28
```

Every record should belong to an Academic Year.

The current academic year should be configurable.

---

# Examination Types

The system should distinguish between examination types.

Examples

* Unit Test
* Mid Term
* Semester
* Quarterly
* Half Yearly
* Final Examination
* Annual Examination

Only examinations configured as:

```
Promotion Eligible
```

should allow academic promotion.

Example

Semester Exam

```
Promotion Eligible

NO
```

Annual Examination

```
Promotion Eligible

YES
```

The school should be able to configure this.

---

# Result Finalization

Promotion should only be available after:

* Marks Entry Completed
* Result Published
* Result Locked
* Principal Approval (optional)

This prevents accidental promotions.

---

# Promotion Dashboard

Create a dedicated Promotion Dashboard.

Display

* Academic Year
* Current Class
* Next Class
* Total Students
* Passed
* Failed
* Pending
* Not Evaluated
* Promotion Status

The dashboard should provide a complete overview before promotion.

---

# Bulk Promotion

The Headmaster or Principal should be able to promote an entire class with a single action.

Example

```
Class 5-A

↓

Promote All

↓

Class 6-A
```

The system should:

* Create new academic records
* Assign new class
* Assign new section (optional)
* Assign new roll numbers (optional)
* Preserve historical records

Students should not be edited individually.

---

# Promotion Preview

Before promotion, show a preview.

Example

```
Current Class

5-A

↓

Next Class

6-A

Students

48

Passed

45

Failed

2

Pending

1
```

Provide confirmation before execution.

---

# Failed Students

The system should allow exceptions.

Example

Student

Rahul

Status

Failed

The administrator should be able to choose

* Repeat Current Class
* Promote Anyway
* Hold Promotion

Each decision should be stored.

---

# Individual Promotion

After bulk promotion, administrators should still be able to modify individual students.

Examples

* Promote manually
* Revert promotion
* Change section
* Change roll number
* Repeat class

All changes should be logged.

---

# Graduation

Students completing the highest class should not be promoted.

Instead

```
Class 10

↓

Graduate

↓

Alumni
```

or

```
Class 12

↓

Graduate

↓

Alumni
```

depending on school configuration.

---

# Student Status

Every student should have a status.

Examples

```
Active

Inactive

Transferred

Graduated

Alumni

Suspended

Expelled

Archived

Dropout
```

Status should be configurable.

---

# Student Transfer

Support transferring students.

Transfer Out

```
Active

↓

Transferred
```

Transfer In

```
Transferred

↓

Active
```

Maintain transfer history.

---

# Student Withdrawal

Parents may withdraw students.

Example

```
Active

↓

Withdrawn
```

Store

* Date
* Reason
* Remarks

Do not delete records.

---

# Student Archival

Never permanently delete students.

Instead

Archive them.

Archived students

* Do not appear in normal lists
* Cannot log in
* Preserve all historical data

Administrators can restore them later.

---

# Roll Number Generation

Allow automatic roll number regeneration after promotion.

Options

* Preserve Existing
* Generate Sequentially
* Manual

---

# Section Allocation

Allow

```
5-A

↓

6-A
```

or

```
5-A

↓

6-B
```

Support automatic or manual mapping.

---

# Promotion History

Every promotion should be recorded.

Example

```
Student

Rahul

Academic Year

2025-26

From

5-A

To

6-A

Promoted By

Principal

Date

15-04-2026
```

Nothing should be lost.

---

# Audit Log

Record

* Promotion
* Rollback
* Manual Changes
* Class Changes
* Status Changes

Every action should be auditable.

---

# Rollback

If promotion was executed incorrectly

Allow rollback before the new academic session begins.

Rollback should restore previous academic records.

---

# Permissions

Create permissions.

Examples

```
promotion.view

promotion.execute

promotion.rollback

promotion.override

promotion.bulk

promotion.individual

student.archive

student.restore

student.transfer

student.graduate
```

Only authorized users should perform these actions.

---

# Notifications

Future support

After promotion

Notify

* Student
* Parent
* Teacher

Current implementation

Design architecture only.

Do not implement messaging.

---

# Reports

Create reports

* Promotion Report
* Failed Students
* Graduated Students
* Archived Students
* Transfer Report
* Student Status Report

---

# Admin Configuration

Allow administrators to configure

* Promotion Rules
* Promotion Eligible Exams
* Graduation Class
* Roll Number Policy
* Section Allocation Policy

without changing source code.

---

# Future Compatibility

The implementation should support future additions such as

* Auto Promotion Rules
* AI Promotion Recommendations
* Scholarship Promotion
* Fee Clearance Validation
* Attendance Validation
* Parent Approval
* Online Promotion Workflow

without redesigning the system.

---

# Documentation

Document

* Promotion Workflow
* Student Lifecycle
* Academic Session Management
* Status Management
* Rollback Process

---

# Deliverables

The implementation should include

1. Academic Year Management
2. Promotion Dashboard
3. Bulk Promotion
4. Individual Promotion
5. Promotion Preview
6. Failed Student Management
7. Student Status Management
8. Graduation Workflow
9. Transfer Workflow
10. Withdrawal Workflow
11. Student Archive System
12. Rollback Support
13. Promotion History
14. Audit Logs
15. Admin Configuration
16. Comprehensive documentation

---

# Success Criteria

The system should allow a Principal or Headmaster to complete an entire academic year transition in a few clicks while preserving all historical academic data.

The architecture must support both bulk operations and individual exceptions, ensuring flexibility without compromising data integrity.

No student records should ever be permanently deleted as part of academic progression or lifecycle management. Historical data must remain accessible for reporting, audits, and future reference.
