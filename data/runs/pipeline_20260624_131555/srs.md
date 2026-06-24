# Software Requirements Specification (SRS)

## 1. Purpose
The purpose of this system is to provide a Hospital Appointment and Triage Coordination System for pilot launch in September.

## 2. Scope
The system will support patient appointment management, clinician triage record management, administrative reporting, identity-based access, notifications, EHR synchronization, audit logging, and continuity-of-care needs related to emergency triage and patient lookup.

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
- FR-1: The system shall allow patients to log in using the national health identity account only.
- FR-2: The system shall support the following roles: patient, clinician, and admin.
- FR-3: The system shall allow clinicians to create triage records.
- FR-4: The system shall allow clinicians to update triage records.
- FR-5: The system shall capture severity in triage records.
- FR-6: The system shall capture symptoms in triage records.
- FR-7: The system shall capture priority in triage records.
- FR-8: The system shall allow patients to request appointments.
- FR-9: The system shall allow patients to reschedule appointments.
- FR-10: The system shall allow patients to cancel appointments.
- FR-11: The system shall include a reference code in appointment confirmations.
- FR-12: The system shall deliver notifications for confirmations within 10 minutes.
- FR-13: The system shall deliver notifications for cancellations within 10 minutes.
- FR-14: The system shall provide an admin dashboard showing daily appointment volume.
- FR-15: The system shall provide an admin dashboard showing no-show rate.
- FR-16: The system shall sync appointment status updates to the hospital EHR system.
- FR-17: The system shall keep immutable clinical audit logs for 7 years.
- FR-18: The system shall support emergency triage during network outages.
- FR-19: The system shall support patient lookup during network outages.
- FR-20: The system shall validate all user sessions against the central cloud IAM in real time.

## 5. Non-Functional Requirements
- NFR-1: The system shall handle 300 concurrent users during peak morning booking windows.
- NFR-2: Critical pages shall respond within 2.5 seconds p95.
- NFR-3: The system shall achieve at least 99.9% monthly uptime.
- NFR-4: The system shall maintain immutable clinical audit logs for 7 years for legal and quality audits.
- NFR-5: The system shall support offline operation for emergency triage and patient lookup during network outages.
- NFR-6: User sessions shall be validated against the central cloud IAM in real time.

## 6. Contradictions and Risks
- C-1:
  - Conflicting statement 1: "During network outages, emergency triage and patient lookup must still operate offline for continuity of care."
  - Conflicting statement 2: "All user sessions must be validated against the central cloud IAM in real time. Offline access is not allowed for patient data screens."
- C-2:
  - Conflicting statement 1: "Keep immutable clinical audit logs for 7 years for legal and quality audits."
  - Conflicting statement 2: "Delete patient interaction logs after 30 days to minimize retention risk."

## 7. Open Questions
- How should patient interaction logs be classified relative to the 7-year immutable clinical audit logs?
- What is the exact definition of "critical pages" for the 2.5 seconds p95 performance target?
- What appointment statuses must be synchronized to the hospital EHR system?
- What specific data or actions are allowed for patient lookup during network outages?
- How should offline emergency triage function if real-time IAM validation is required?