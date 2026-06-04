---
name: Token normalisation
description: Attendance tokens are always uppercase; lookups use iexact
---

**Rule:** `AttendanceToken.token` is strip+upper-cased in `AttendanceToken.save()`. All lookups use `token__iexact`. User-submitted token values in views are also `.strip().upper()`-ed before any query.

**Why:** Students might type tokens in lowercase. Without normalisation, a valid token would appear invalid.

**How to apply:** Any new code that looks up `AttendanceToken` by token string must use `token__iexact=value.strip().upper()` or simply `token=value.strip().upper()` (since the stored value is always uppercase).
