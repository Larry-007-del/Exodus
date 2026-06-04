---
name: Register flow
description: Registration is immediate login, no email verification
---

**Rule:** Self-registration creates the `User`, creates the `Student` profile (with optional `student_id`, `programme_of_study`, `year`), adds the user to the `Student` group, and immediately logs the user in. No email verification.

**Why:** Remote upstream removed email verification requirement. Keeping it caused friction for students who register.

**How to apply:** The `verify_email` view and URL still exist (for backward compatibility) but are no longer triggered during registration. Do not re-add `user.is_active = False` to the register view.
