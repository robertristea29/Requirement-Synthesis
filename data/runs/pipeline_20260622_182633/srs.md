# Software Requirements Specification (SRS)

## 1. Purpose
The purpose of this system is to provide a Hospital Appointment and Triage Coordination System for pilot launch in September.

## 2. Scope
The system will support patient appointment management, clinical triage record handling, administrative reporting, identity-based login, notifications, and synchronization with the hospital EHR system. It will also support emergency triage and patient lookup during network outages, subject to stated security and compliance constraints.

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
FR-1: The system shall be a Hospital Appointment and Triage Coordination System for pilot launch in September.

FR-2: Patients shall log in using the national health identity account only.

FR-3: The system shall support the following roles: patient, clinician, and admin.

FR-4: Clinicians shall be able to create triage records.

FR-5: Clinicians shall be able to update triage records.

FR-6: Triage records shall include severity, symptoms, and priority.

FR-7: Patients shall be able to request appointments.

FR-8: Patients shall be able to reschedule appointments.

FR-9: Patients shall be able to cancel appointments.

FR-10: Appointment confirmations shall include a reference code.

FR-11: The system shall send notifications for confirmations.

FR-12: The system shall send notifications for cancellations.

FR-13: Notifications for confirmations and cancellations shall be delivered within 10 minutes.

FR-14: The admin dashboard shall show daily appointment volume.

FR-15: The admin dashboard shall show no-show rate.

FR-16: The platform shall sync appointment status updates to the hospital EHR system.

FR-17: During network outages, emergency triage shall still operate offline for continuity of care.

FR-18: During network outages, patient lookup shall still operate offline for continuity of care.

FR-19: All user sessions shall be validated against the central cloud IAM in real time.

## 5. Non-Functional Requirements
NFR-1: The system shall handle 300 concurrent users during peak morning booking windows.

NFR-2: Critical pages shall stay under 2.5 seconds p95.

NFR-3: Monthly uptime target shall be at least 99.9%.

NFR-4: The system shall keep immutable clinical audit logs for 7 years for legal and quality audits.

NFR-5: The system shall not allow offline access to patient data screens.

## 6. Contradictions and Risks
C-1: Conflicting requirements for offline access:
- "During network outages, emergency triage and patient lookup must still operate offline for continuity of care."
- "Offline access is not allowed for patient data screens."

C-2: Conflicting requirements for retention of patient interaction logs:
- "Delete patient interaction logs after 30 days to minimize retention risk."
- "Do not change the 7-year immutable audit logging requirement."

## 7. Open Questions
- How should "patient data screens" be defined relative to offline emergency triage and patient lookup?
- Does the 30-day deletion requirement apply to all patient interaction logs, or only non-audit logs?
- What is the exact date or milestone for the September pilot launch?
- What system behavior is expected if central cloud IAM validation is unavailable?
- What details are required in the immutable clinical audit logs beyond the stated 7-year retention?