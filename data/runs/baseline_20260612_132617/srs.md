# Software Requirements Specification (SRS)
## Campus Event Booking Platform

### 1. Purpose
The system shall provide a campus event booking platform for September launch.

### 2. Scope
The platform shall support:
- University SSO sign-in only
- Event creation by organizers
- Ticket booking by attendees
- QR code booking confirmation
- Payments via iDEAL and credit card
- Booking/cancellation notifications by email
- Admin dashboard for sales and attendance rates
- Immutable audit logging

### 3. User Roles
The system shall support the following roles:
- Attendee
- Organizer
- Admin

### 4. Functional Requirements

#### 4.1 Authentication and Access
FR-1. The system shall allow users to sign in using university SSO only.
FR-2. The system shall support the roles attendee, organizer, and admin.
FR-3. The system shall require live cloud authentication at application startup before any feature is unlocked.
FR-4. The system shall not use cached/offline authentication.

#### 4.2 Event Management
FR-5. Organizers shall be able to create events.
FR-6. Event creation shall include the following fields:
- Title
- Date/time
- Location
- Capacity
- Category

#### 4.3 Ticket Booking
FR-7. Attendees shall be able to book tickets for events.
FR-8. The system shall generate and provide a QR code confirmation for each successful booking.
FR-9. The system shall support ticket validation using the QR code.

#### 4.4 Payments
FR-10. The system shall support iDEAL as a payment method.
FR-11. The system shall support credit card as a payment method.

#### 4.5 Notifications
FR-12. The system shall send booking confirmation emails.
FR-13. The system shall send cancellation emails.
FR-14. Booking and cancellation emails shall be sent within 5 minutes.

#### 4.6 Admin Reporting
FR-15. Admin users shall have access to a dashboard.
FR-16. The dashboard shall display daily sales.
FR-17. The dashboard shall display attendance rates.

#### 4.7 Audit Logging
FR-18. The system shall maintain immutable audit logs.
FR-19. Audit logs shall be retained for 7 years.
FR-20. Audit logs shall be preserved for financial and dispute reasons.

### 5. Non-Functional Requirements

#### 5.1 Performance
NFR-1. The system shall support 500 concurrent users during peak ticket drops.
NFR-2. Core pages shall have a p95 response time under 2 seconds.

#### 5.2 Availability
NFR-3. The system shall achieve at least 99.5% monthly uptime.

#### 5.3 Offline Capability
NFR-4. The system shall be fully offline-capable for all core operations, including login and ticket validation, for resilience drills.

#### 5.4 Data Retention and Privacy
NFR-5. User activity logs shall be deleted after 30 days to minimize retained personal data.
NFR-6. Audit logs shall be retained for 7 years.

### 6. Constraints and Conflicts
CR-1. The system shall use university SSO only.
CR-2. The system shall perform live cloud authentication at startup before any feature unlocks.
CR-3. The system shall not allow cached/offline authentication.
CR-4. The system shall be fully offline-capable for all core operations, including login and ticket validation.
CR-5. The requirements for offline-capable login and mandatory live cloud authentication are in conflict and require stakeholder resolution.
CR-6. The requirement to delete user activity logs after 30 days may conflict with auditability needs if such logs are used for audit purposes; audit log retention shall remain 7 years.

### 7. Acceptance Criteria
AC-1. A user can sign in via university SSO and access only permitted role functions.
AC-2. An organizer can create an event with title, date/time, location, capacity, and category.
AC-3. An attendee can book a ticket and receive a QR code confirmation.
AC-4. Booking and cancellation emails are delivered within 5 minutes.
AC-5. An admin can view daily sales and attendance rates.
AC-6. Audit logs are immutable and retained for 7 years.
AC-7. Core pages meet the p95 under-2-seconds target under expected peak usage.
AC-8. The system is available at or above 99.5% monthly uptime.