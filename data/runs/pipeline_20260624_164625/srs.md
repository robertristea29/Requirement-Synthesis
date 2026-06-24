# Software Requirements Specification (SRS)

## 1. Purpose
The purpose of this system is to support hospital appointment and triage coordination for a pilot launch in September. It will allow patients, clinicians, and administrators to manage appointments, triage records, notifications, and operational reporting.

## 2. Scope
The system is a Hospital Appointment and Triage Coordination System that includes:
- Patient login using the national health identity account only
- Appointment request, rescheduling, and cancellation
- Clinician triage record creation and updating
- Appointment confirmations with reference codes
- Notifications for confirmations and cancellations
- Administrative dashboard reporting
- Synchronization of appointment status updates to the hospital EHR system
- Clinical audit logging
- Emergency offline operation for triage and patient lookup during network outages

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

FR-3: The system shall support the following roles: patient, clinician, admin.

FR-4: Clinicians shall be able to create triage records.

FR-5: Clinicians shall be able to update triage records.

FR-6: Triage records shall include severity, symptoms, and priority.

FR-7: Patients shall be able to request appointments.

FR-8: Patients shall be able to reschedule appointments.

FR-9: Patients shall be able to cancel appointments.

FR-10: Appointment confirmations shall include a reference code.

FR-11: The system shall send notifications for appointment confirmations.

FR-12: The system shall send notifications for appointment cancellations.

FR-13: Confirmation and cancellation notifications shall be delivered within 10 minutes.

FR-14: The admin dashboard shall show daily appointment volume.

FR-15: The admin dashboard shall show no-show rate.

FR-16: The platform shall sync appointment status updates to the hospital EHR system.

FR-17: The system shall keep immutable clinical audit logs for 7 years for legal and quality audits.

FR-18: During network outages, emergency triage shall still operate offline for continuity of care.

FR-19: During network outages, patient lookup shall still operate offline for continuity of care.

## 5. Non-Functional Requirements
NFR-1: The system shall handle 300 concurrent users during peak morning booking windows.

NFR-2: Critical pages shall stay under 2.5 seconds p95.

NFR-3: The monthly uptime target shall be at least 99.9%.

NFR-4: All user sessions shall be validated against the central cloud IAM in real time.

NFR-5: Offline access shall not be allowed for patient data screens.

NFR-6: The system shall keep immutable clinical audit logs for 7 years.

NFR-7: Patient interaction logs shall be deleted after 30 days to minimize retention risk.

## 6. Contradictions and Risks
C-1:
- "During network outages, emergency triage and patient lookup must still operate offline for continuity of care."
- "Offline access is not allowed for patient data screens."

C-2:
- "Keep immutable clinical audit logs for 7 years for legal and quality audits."
- "Delete patient interaction logs after 30 days to minimize retention risk."

## 7. Open Questions
- What exact functionality is required for the pilot launch in September beyond the stated requirements?
- How should the system resolve the conflict between offline continuity for patient lookup and the prohibition on offline access for patient data screens?
- What types of patient interaction logs are covered by the 30-day deletion requirement, and how does this relate to audit logging?
- What specific fields or workflow steps are required for appointment request, reschedule, and cancellation?
- What is the expected format and content of the appointment reference code?
- What data refresh or synchronization frequency is required for appointment status updates to the hospital EHR system?