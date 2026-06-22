# Software Requirements Specification (SRS)

## 1. Purpose
The purpose of this system is to support hospital appointment booking and triage coordination for a pilot launch in September. It will provide patient appointment management, clinician triage record management, admin reporting, and integration with the hospital EHR system.

## 2. Scope
The system shall support:
- Patient authentication using the national health identity account only.
- Patient actions to request, reschedule, and cancel appointments.
- Clinician creation and update of triage records.
- Appointment confirmations with reference codes.
- Delivery of appointment confirmation and cancellation notifications.
- Admin dashboard reporting on daily appointment volume and no-show rate.
- Synchronization of appointment status updates to the hospital EHR system.
- Immutable clinical audit logging retained for 7 years.
- Offline operation for emergency triage and patient lookup during network outages.
- Real-time validation of all user sessions against the central cloud IAM.

Out of scope unless otherwise clarified:
- Other identity providers besides the national health identity account.
- Patient data screen access without real-time IAM validation.
- Any retention policy that overrides the 7-year immutable audit log requirement.

## 3. Stakeholders
- Clinical Operations
- IT Operations
- Clinicians
- Patients
- Administrators
- EHR Team
- Compliance team
- Privacy officer
- Security architecture team

## 4. Functional Requirements
FR-1 The system shall allow patients to authenticate using the national health identity account only.

FR-2 The system shall allow patients to request appointments.

FR-3 The system shall allow patients to reschedule appointments.

FR-4 The system shall allow patients to cancel appointments.

FR-5 The system shall allow clinicians to create triage records.

FR-6 The system shall allow clinicians to update triage records.

FR-7 The system shall capture severity, symptoms, and priority in triage records.

FR-8 The system shall generate an appointment confirmation reference code for confirmed appointments.

FR-9 The system shall deliver confirmation notifications for appointment confirmations.

FR-10 The system shall deliver cancellation notifications for appointment cancellations.

FR-11 The system shall deliver confirmation and cancellation notifications within 10 minutes.

FR-12 The system shall provide an admin dashboard showing daily appointment volume.

FR-13 The system shall provide an admin dashboard showing no-show rate.

FR-14 The system shall sync appointment status updates to the hospital EHR system.

FR-15 The system shall maintain immutable clinical audit logs.

FR-16 The system shall retain immutable clinical audit logs for 7 years.

FR-17 The system shall support emergency triage operation during network outages.

FR-18 The system shall support patient lookup during network outages.

FR-19 The system shall validate all user sessions against the central cloud IAM in real time.

## 5. Non-Functional Requirements
NFR-1 The system shall support 300 concurrent users during peak morning booking windows.

NFR-2 Critical pages shall meet a performance target of under 2.5 seconds p95.

NFR-3 The system shall achieve at least 99.9% monthly uptime.

NFR-4 The system shall retain immutable clinical audit logs for 7 years.

NFR-5 The system shall support offline operation for emergency triage and patient lookup during network outages.

NFR-6 The system shall validate all user sessions against the central cloud IAM in real time.

## 6. Contradictions and Risks
C-1 Offline access for patient data screens:
- Statement 1: “During network outages, emergency triage and patient lookup must still operate offline for continuity of care.”
- Statement 2: “Offline access is not allowed for patient data screens.”
- Risk: The system cannot both provide offline patient lookup and prohibit offline patient data screen access without a narrower definition of permitted offline functionality.

C-2 Retention of logs:
- Statement 1: “Keep immutable clinical audit logs for 7 years for legal and quality audits.”
- Statement 2: “Delete patient interaction logs after 30 days to minimize retention risk.”
- Risk: Patient interaction logs may overlap with audit logs; retention categories need clear separation to avoid conflict.

## 7. Open Questions
- What exact functions are permitted in offline mode for emergency triage and patient lookup?
- Does “patient data screens” include emergency triage lookup screens, or only standard patient-facing screens?
- What constitutes a “patient interaction log,” and is it separate from immutable clinical audit logs?
- What is the exact scope of the national health identity account integration and any fallback recovery process?
- What fields are required in triage records beyond severity, symptoms, and priority?
- What appointment states must be synchronized to the EHR system?
- What specific content should be included in notifications besides the reference code for confirmations?
- What are the access and reporting permissions for the admin dashboard?