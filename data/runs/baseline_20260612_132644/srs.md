# Software Requirements Specification (SRS)
## Campus Event Booking Platform

### 1. Purpose
Provide a simple campus event booking platform for September launch where students sign in using university SSO only, organizers create events, attendees book tickets and receive QR code confirmations, and admins view sales and attendance dashboards.

### 2. Scope
The system shall support:
- University SSO-based sign-in only.
- Roles: attendee, organizer, admin.
- Event creation by organizers.
- Ticket booking by attendees.
- QR code confirmation for bookings.
- Payments via iDEAL and credit card.
- Booking/cancellation email notifications.
- Admin dashboard for daily sales and attendance rates.
- Audit logging retained for 7 years.

### 3. Stakeholders
- Students / attendees
- Organizers
- Admins
- Operations
- Compliance / Finance
- IT architecture / Security
- Privacy officer

### 4. Functional Requirements

#### 4.1 Authentication and Access
FR-1: The system shall require university SSO for user sign-in.  
FR-2: The system shall not support any non-SSO login method.  
FR-3: The system shall support the roles attendee, organizer, and admin.  
FR-4: The system shall restrict features according to user role.

#### 4.2 Event Management
FR-5: Organizers shall be able to create events.  
FR-6: Event creation shall include title, date/time, location, capacity, and category.  
FR-7: Organizers shall be able to view/manage their events.

#### 4.3 Ticket Booking
FR-8: Attendees shall be able to book tickets for events.  
FR-9: The system shall generate a QR code confirmation for each successful booking.  
FR-10: Attendees shall be able to cancel bookings.

#### 4.4 Payments
FR-11: The system shall support iDEAL payments for launch.  
FR-12: The system shall support credit card payments for launch.

#### 4.5 Notifications
FR-13: The system shall send booking confirmation emails.  
FR-14: The system shall send cancellation emails.  
FR-15: Booking and cancellation emails shall be sent within 5 minutes of the triggering action.

#### 4.6 Admin Reporting
FR-16: Admin users shall have access to a dashboard.  
FR-17: The dashboard shall display daily sales.  
FR-18: The dashboard shall display attendance rates.

#### 4.7 Audit Logging
FR-19: The system shall record immutable audit logs for user and transaction-related actions.  
FR-20: Audit logs shall be retained for 7 years.  
FR-21: Audit log retention shall not be shortened below 7 years.

### 5. Non-Functional Requirements

#### 5.1 Performance
NFR-1: The system shall support 500 concurrent users during peak ticket drops.  
NFR-2: Core pages shall respond within 2 seconds p95.

#### 5.2 Availability
NFR-3: The system shall achieve at least 99.5% monthly uptime.

#### 5.3 Auditability
NFR-4: Audit logs shall be immutable.  
NFR-5: Audit logs shall be retained for 7 years.

#### 5.4 Offline/Resilience
NFR-6: For resilience drills, the app shall be fully offline-capable for all core operations, including login and ticket validation.

#### 5.5 Security / Policy Constraint
NFR-7: At every app startup, the system shall perform live cloud authentication before any feature unlocks.  
NFR-8: The system shall not use cached/offline authentication for feature access.

#### 5.6 Privacy
NFR-9: User activity logs shall be deleted after 30 days.

### 6. External Interface Requirements
IR-1: The system shall integrate with university SSO.  
IR-2: The system shall integrate with payment providers supporting iDEAL and credit card.  
IR-3: The system shall send emails via an email delivery service.  
IR-4: The system shall generate QR codes for booking confirmation.  
IR-5: The system shall provide a dashboard interface for admins.

### 7. Constraints and Conflict Notes
C-1: There is a direct conflict between:
- “fully offline-capable for all core operations, including login and ticket validation”
- “every app startup must perform live cloud authentication before any feature unlocks; no cached/offline auth is allowed”

C-2: There is a direct conflict between:
- “immutable audit logs for 7 years”
- “delete all user activity logs after 30 days”

C-3: The requirements above are recorded as stated; conflict resolution is not provided in the transcript.

### 8. Acceptance Notes
- September launch scope shall remain simple.
- Requirements involving conflicts require stakeholder resolution before implementation sign-off.