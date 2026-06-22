# Software Requirements Specification (SRS)

## 1. Purpose
Provide a Hospital Appointment and Triage Coordination System for pilot launch in September.

## 2. Scope
The system will support patient login, appointment management, triage record management, notifications, admin reporting, EHR synchronization, audit logging, and security controls for hospital appointment and triage coordination.

## 3. Stakeholders
- Clinical Operations
- IT Ops
- Clinicians
- Patients
- Admin users
- EHR team
- Compliance team
- Privacy officer
- Security architecture team

## 4. Functional Requirements
FR-1: The system shall support a Hospital Appointment and Triage Coordination System for pilot launch in September.

FR-2: Patients shall log in using the national health identity account only.

FR-3: The system shall support the roles patient, clinician, and admin.

FR-4: Clinicians shall be able to create triage records.

FR-5: Clinicians shall be able to update triage records.

FR-6: Triage records shall include severity.

FR-7: Triage records shall include symptoms.

FR-8: Triage records shall include priority.

FR-9: Patients shall be able to request appointments.

FR-10: Patients shall be able to reschedule appointments.

FR-11: Patients shall be able to cancel appointments.

FR-12: Appointment confirmation shall include a reference code.

FR-13: Notifications for confirmations shall be delivered within 10 minutes.

FR-14: Notifications for cancellations shall be delivered within 10 minutes.

FR-15: The admin dashboard shall show daily appointment volume.

FR-16: The admin dashboard shall show no-show rate.

FR-17: The platform shall sync appointment status updates to the hospital EHR system.

FR-18: The system shall keep immutable clinical audit logs for 7 years for legal and quality audits.

FR-19: During network outages, emergency triage shall still operate offline for continuity of care.

FR-20: During network outages, patient lookup shall still operate offline for continuity of care.

FR-21: All user sessions shall be validated against the central cloud IAM in real time.

## 5. Non-Functional Requirements
NFR-1: The system shall handle 300 concurrent users during peak morning booking windows.

NFR-2: Critical pages shall stay under 2.5 seconds p95.

NFR-3: Monthly uptime target shall be at least 99.9%.

NFR-4: All user sessions shall be validated against the central cloud IAM in real time.

NFR-5: Offline access shall not be allowed for patient data screens.

NFR-6: Clinical audit logs shall be immutable and retained for 7 years.

## 6. Contradictions and Risks
C-1:
- "During network outages, emergency triage and patient lookup must still operate offline for continuity of care."
- "Offline access is not allowed for patient data screens."

C-2:
- "Keep immutable clinical audit logs for 7 years for legal and quality audits."
- "Delete patient interaction logs after 30 days to minimize retention risk."

## 7. Open Questions
- Which clinical or operational events are included in "patient interaction logs" versus "immutable clinical audit logs"?
- What does "patient data screens" specifically include for the offline access restriction?
- How should the system behave for appointment-related functions during network outages, if any?
- What exact fields and workflow steps are required for triage record creation and update beyond severity, symptoms, and priority?
- What format or content is required for the appointment reference code?
- Which specific appointment status updates must be synced to the hospital EHR system, and how often?
- Are there any additional admin dashboard metrics required beyond daily appointment volume and no-show rate?