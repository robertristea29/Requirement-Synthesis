# Stakeholder Input Dump (Synthetic)

## Email from Clinical Operations (Mon 08:30)
We need a Hospital Appointment and Triage Coordination System for pilot launch in September. Patients should log in using the national health identity account only.

## Slack thread with IT Ops (Mon 09:10)
- The system must handle 300 concurrent users during peak morning booking windows.
- Critical pages should stay under 2.5 seconds p95.
- Monthly uptime target is at least 99.9%.

## Joint meeting notes (Mon 10:45)
- Roles: patient, clinician, admin.
- Clinicians need to create and update triage records with severity, symptoms, and priority.
- Patients can request, reschedule, and cancel appointments.
- Appointment confirmation must include a reference code.
- Notifications for confirmations/cancellations should be delivered within 10 minutes.
- Admin dashboard should show daily appointment volume and no-show rate.

## Integration note from EHR team (Mon 13:15)
The platform must sync appointment status updates to the hospital EHR system.

## Compliance memo (Mon 14:20)
Keep immutable clinical audit logs for 7 years for legal and quality audits.

## Emergency preparedness requirement (Mon 15:00)
During network outages, emergency triage and patient lookup must still operate offline for continuity of care.

## Security architecture response (Mon 15:18)
All user sessions must be validated against the central cloud IAM in real time. Offline access is not allowed for patient data screens.

## Privacy officer note (Tue 09:00)
Delete patient interaction logs after 30 days to minimize retention risk.

## Compliance follow-up (Tue 10:25)
Do not change the 7-year immutable audit logging requirement.
