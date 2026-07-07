# Fee and Result Structure Redesign Plan

## Overview

Refactor the fee and result systems to support:
- class-level fee structures and automatic student fee generation
- exam entities with exam-based result navigation
- cleaner frontend templates for fee schedules and exam/class result browsing
- consistent subject filtering per class

---

## 1. Fee App Redesign

### New model
Add a `FeeStructure` or `ClassFeeSchedule` model with:
- `school`
- `school_class`
- `title`
- `academic_year`
- `total_amount`
- `due_date`
- `notes`
- `created_by`
- `created_at`

### Student fee linkage
- Add `fee_structure = ForeignKey(...)` on `StudentFee` (optional)
- Use this to track generated fees for all students in a class

### Behavior
- Creating a fee structure should automatically generate `StudentFee` records for every student in that class
- Keep individual student fee CRUD available for adjustments

### UX/templates
- `templates/fees/fee_structure_list.html`
- `templates/fees/fee_structure_detail.html`
- update `templates/fees/fee_list.html`
- keep `templates/fees/fee_detail.html` with source structure reference

---

## 2. Result App Redesign

### New model
Add an `Exam` model with:
- `school`
- `name`
- `academic_year`
- optional `exam_type`
- `created_by`
- `created_at`

### Result model update
- Change `Result.exam_name` and `Result.academic_year` into `ForeignKey("Exam")`
- Keep subject validation by class
- Add migration logic to convert existing free-text exam entries into `Exam` records

### Behavior
- Create exams first
- Then add/import results tied to an `Exam`
- Preserve ability to edit individual result rows

### UX/templates
- Replace `templates/results/home.html` with an exam catalog page
- Add `templates/results/exam_detail.html`
- Update `templates/results/class_results.html` to be exam-scoped
- Ensure class subjects are shown only for that class

---

## 3. Views and Routes

### Fee routes
- `fees/structures/`
- `fees/structures/<id>/`
- `fees/structures/<id>/edit`
- `fees/structures/<id>/delete`

### Result routes
- `results/exams/`
- `results/exams/<id>/`
- `results/exams/<id>/classes/<class_id>/`
- `results/exams/<id>/classes/<class_id>/new/`

### Permissions
- Heads/principals manage fee structures and exams
- Teachers view assigned class fees/results
- Students view their own fees and published results

---

## 4. Implementation Files

### Fee app
- `apps/fees/models.py`
- `apps/fees/forms.py`
- `apps/fees/views.py`
- `apps/fees/urls.py`
- `templates/fees/*`

### Result app
- `apps/results/models.py`
- `apps/results/forms.py`
- `apps/results/views.py`
- `apps/results/urls.py`
- `templates/results/*`

---

## 5. Verification Checklist

1. Create a class fee schedule and confirm generated student fees exist
2. Create an exam and verify exam list / exam detail navigation
3. Confirm result creation only shows subjects assigned to the class
4. Ensure URLs still work for existing student fees and new exam workflow
5. Confirm permissions for head/principal/teacher/student

---

## Notes

- Keep individual records editable after generation
- Consider automatic fee sync when students join a class
- Add `exam_type` if you want categories like “end exam” or “semester exam”