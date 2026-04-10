# Exodus — Prioritized Task List

## 🔴 Critical (Correctness / Security)

- [x] **Fix N+1 query in `chart_lecturer_course_stats`** — replace per-session `present_students.count()` loop with a single annotated query
- [x] **Secure `save_fcm_token` endpoint** — validate token format/length, reject garbage data
- [x] **Complete FCM Push Notification Dispatch** — integrate `firebase-admin` SDK, wire into `notification_service.py`, add env var to `render.yaml`

## 🟡 Medium (Features / Reliability)

- [x] **Tailwind CSS Rebuild** — run `npm run build`, verify all new template classes in `styles.css`
- [x] **Reports Page Audit** — fixed N+1 per-course loop (O(2N) → O(3) queries) and 8-loop weekly trend (O(8) → O(1)); export views already efficient
- [x] **Profile picture in navbar/dashboard** — surface avatar in sidebar/user dropdown
- [x] **Production Email (Brevo)** — ensured `django-anymail[sendinblue]` is tracking and active in production bypassing port 25 restrictions.

## 🟢 Polish (UI / Verification)

- [x] **Glassmorphism consistency audit** — patch `errors/404.html`, `errors/500.html` and any stale templates
- [x] **Student 2FA self-enrollment flow** — verify TOTP `setup_2fa.html` → QR scan → verify → enable works end-to-end
- [x] **Live QA** — Inspect Render live deployment (exodus-nsji.onrender.com) for visual and functional anomalies
