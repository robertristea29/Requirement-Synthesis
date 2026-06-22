BEGIN_SRS
# Software Requirements Specification (SRS): Campus Event Booking Platform

## 1. Purpose
Build a Campus Event Booking platform for September launch. The first release should be simple.

## 2. Users and Roles
The system shall support the following roles:
- Attendee
- Organizer
- Admin

All users shall sign in using university SSO only.

## 3. Functional Requirements

### 3.1 Authentication and Access
- The system shall require university SSO for user sign-in.
- The system shall support role-based access for attendee, organizer, and admin.

### 3.2 Event Management
- Organizers shall be able to create events.
- Event creation shall include the following fields:
  - title
  - date/time
  - location
  - capacity
  - category

### 3.3 Ticket Booking
- Attendees shall be able to book tickets for events.
- The system shall generate a QR code confirmation for each successful booking.
- Attendees shall be able to cancel bookings.

### 3.4 Payments
- The system shall support iDEAL payments for launch.
- The system shall support credit card payments for launch.

### 3.5 Notifications
- The system shall send booking confirmation emails.
- The system shall send cancellation emails.
- Booking and cancellation emails shall be sent within 5 minutes of the triggering action.

### 3.6 Admin Dashboard
- Admins shall have a dashboard.
- The dashboard shall show daily sales.
- The dashboard shall show attendance rates.

### 3.7 Audit Logging
- The system shall maintain immutable audit logs.
- Audit logs shall be retained for 7 years.
- Audit logging shall support financial and dispute-related auditability.

## 4. Non-Functional Requirements

### 4.1 Performance
- The system shall support 500 concurrent users during peak ticket drops.
- Core pages shall achieve under 2 seconds p95 response time.

### 4.2 Availability
- The system shall achieve at least 99.5% monthly uptime.

### 4.3 Security / Operational Constraints
- The system shall use live cloud authentication at startup before any feature unlocks.
- No cached or offline authentication shall be used.
- The system shall be fully offline-capable for all core operations, including login and ticket validation.

## 5. Data Retention Requirements
- User activity logs shall be deleted after 30 days.
- Immutable audit logs shall be retained for 7 years.

## 6. Requirement Conflict Note
The transcript contains conflicting requirements regarding offline capability and authentication:
- One statement requires the app to be fully offline-capable for core operations, including login.
- Another statement requires live cloud authentication at startup and forbids cached/offline auth.

Both requirements are included as stated in the source and must be resolved by stakeholders before implementation.

## 7. Open Questions
- How should the conflict between offline-capable login and mandatory live cloud authentication be resolved?
- What exact definition of "core operations" should be used for offline capability?
- What event lifecycle states are needed beyond creation, booking, and cancellation?

END_SRS
BEGIN_MERMAID
C4Context
title Campus Event Booking Platform - Context
Person(attendee, "Attendee", "Books tickets and receives QR code confirmation")
Person(organizer, "Organizer", "Creates and manages events")
Person(admin, "Admin", "Monitors sales and attendance")
System(eventBooking, "Campus Event Booking Platform", "University SSO-only event booking platform for students")
System_Ext(universitySSO, "University SSO", "Authentication provider")
System_Ext(emailService, "Email Service", "Sends booking and cancellation emails")
System_Ext(paymentService, "Payment Providers", "iDEAL and credit card payment processing")
System_Ext(auditStore, "Audit Log Store", "Immutable audit logs retained for 7 years")

Rel(attendee, eventBooking, "Signs in, books/cancels tickets, receives QR code")
Rel(organizer, eventBooking, "Signs in, creates events")
Rel(admin, eventBooking, "Signs in, views dashboard")
Rel(eventBooking, universitySSO, "Authenticates users with")
Rel(eventBooking, emailService, "Sends booking/cancellation notifications via")
Rel(eventBooking, paymentService, "Processes payments via")
Rel(eventBooking, auditStore, "Writes immutable audit logs to")

C4Container
title Campus Event Booking Platform - Containers
System_Boundary(ceb, "Campus Event Booking Platform") {
  Container(webApp, "Web App", "Web UI", "User-facing application for attendees, organizers, and admins")
  Container(api, "Application API", "Backend service", "Handles authentication, events, bookings, payments, notifications, and admin dashboard data")
  ContainerDb(db, "Application Database", "Database", "Stores event, booking, user, and sales data")
  Container(audit, "Audit Log Writer", "Logging component", "Appends immutable audit records")
  Container(worker, "Notification Worker", "Background worker", "Sends booking and cancellation emails within 5 minutes")
}

System_Ext(universitySSO, "University SSO", "Authentication provider")
System_Ext(emailService, "Email Service", "Sends emails")
System_Ext(paymentService, "Payment Providers", "iDEAL and credit card")
System_Ext(auditStore, "Audit Log Store", "Immutable 7-year retention")

Rel(webApp, api, "Uses")
Rel(api, universitySSO, "Authenticates with")
Rel(api, paymentService, "Processes payments via")
Rel(api, db, "Reads/writes")
Rel(api, audit, "Emits audit events to")
Rel(audit, auditStore, "Stores immutable logs in")
Rel(api, worker, "Enqueues notification jobs for")
Rel(worker, emailService, "Sends emails via")
END_MERMAID