# Feature Specification: AgentFlow AI Platform Core

**Feature Branch**: `001-platform-core`
**Created**: 2026-05-11
**Last Updated**: 2026-07-07
**Status**: Draft
**Input**: Full platform specifications for multi-tenant AI receptionist and lead automation

---

## Assumptions

This spec covers the initial platform MVP. The following reasonable defaults are applied:

- **Authentication**: Email/password with JWT, secure sessions, password reset via email link
- **Database**: PostgreSQL for all structured data
- **Notifications**: Email (Phase 1), WhatsApp and SMS in future phases
- **AI Model**: OpenAI-compatible API (GPT-4o) with tool-calling support
- **Calendar**: Integration via webhook-based API (Cal.com compatible pattern)
- **Language**: English for initial release; multilingual support in Phase 2
- **Storage**: All file/media assets stored externally (S3-compatible or cloud storage)
- **Lead Data Retention**: 2 years minimum; configurable per tenant for compliance
- **Session Management**: JWT tokens with 24-hour expiry, refresh tokens for 30-day sessions

---

## User Scenarios & Testing

### User Story 1 - Business Onboarding (Priority: P1)

A business owner (Dental Clinic Admin) signs up, configures their AI receptionist, and starts receiving qualified leads within one hour of setup, with the AI receptionist active in **Mode 1 (Supervised)** by default.

**Why this priority**: Without onboarding, no business can use the platform. This is the gateway to all value.

**Independent Test**: Can be tested by creating a new business account, configuring AI settings, and verifying the AI is active and responsive to test inquiries (with human approval required for replies) — all without any other users or data in the system.

**Acceptance Scenarios**:

1. **Given** a new business admin visits the signup page, **When** they enter valid business details and email, **Then** they receive a confirmation email and can set their password within 10 minutes.
2. **Given** a new business admin completes account setup, **When** they configure their business hours and services, **Then** the AI receptionist activates in **Mode 1 (Supervised)** and can draft responses to incoming inquiries.
3. **Given** a new business admin has an active AI receptionist, **When** a potential customer sends a chat message, **Then** the AI drafts a response within 5 seconds and awaits staff approval before sending.
4. **Given** a business admin has configured their AI, **When** they access the dashboard, **Then** they see their business metrics, recent conversations, and lead status.

---

### User Story 2 - AI Lead Qualification (Priority: P1)

A potential customer (Home Services Lead) discovers the business through a website widget, has a natural conversation with the AI receptionist, and their qualified lead record is created with all details captured automatically.

**Why this priority**: Lead qualification is the core differentiator. Without it, the platform is just a chatbot.

**Independent Test**: Can be tested by simulating a customer conversation via the web widget — AI captures name, service type, urgency, and availability — and verifying the resulting lead record contains all fields with correct values.

**Acceptance Scenarios**:

1. **Given** a customer visits the business website and opens the chat widget, **When** they type "I need an appointment", **Then** the AI greets them by the business name and begins a conversational flow.
2. **Given** an AI conversation is in progress, **When** the customer provides their name, service needed, and contact info, **Then** the system creates a lead record with all information captured in structured fields.
3. **Given** a customer provides incomplete information, **When** the AI asks follow-up questions about urgency and preferred times, **Then** the AI collects remaining required fields before marking the lead as qualified.
4. **Given** a lead is created, **When** the business admin views the leads list, **Then** they see the lead with all captured details, qualification status, and conversation summary.
5. **Given** a lead is unqualified or unclear, **When** the AI detects the inquiry is not a real booking opportunity, **Then** the lead is flagged for manual review with reason noted.

---

### User Story 3 - Appointment Booking (Priority: P1)

A qualified lead (Restaurant Customer) books an appointment through the AI conversation. The system detects availability, confirms the slot, creates the appointment record, and notifies the business.

**Why this priority**: Booking is the primary business outcome. A platform that qualifies leads but cannot book appointments fails its core promise.

**Independent Test**: Can be tested by submitting a booking request through the AI chat — verifying the appointment is created, calendar is updated, and confirmation is sent — without any manual intervention.

**Acceptance Scenarios**:

1. **Given** a qualified lead expresses intent to book, **When** the AI checks available slots for the requested service and time, **Then** the AI presents relevant options to the customer.
2. **Given** a customer selects an available slot, **When** they confirm the booking, **Then** an appointment record is created and the customer receives a confirmation notification.
3. **Given** a customer requests a time outside business hours, **When** the AI attempts to book, **Then** it informs the customer of available hours and suggests alternatives.
4. **Given** an appointment is booked, **When** the business staff views the calendar, **Then** the new appointment appears with customer details, service type, and contact information.
5. **Given** a customer needs to reschedule or cancel, **When** they request this via chat or staff interface, **Then** the appointment is updated and both customer and business are notified.

---

### User Story 4 - CRM & Lead Management (Priority: P2)

A business admin (Salon Owner) reviews customer records, updates lead status, and manages follow-up actions. Staff members handle escalations and update appointment statuses.

**Why this priority**: Businesses need to manage ongoing customer relationships. This enables repeat business and ensures no lead falls through the cracks.

**Independent Test**: Can be tested by creating customer records, updating lead status through the CRM, and verifying the history, notes, and status changes all persist correctly and appear in the correct views.

**Acceptance Scenarios**:

1. **Given** a business admin views the CRM, **When** they filter by lead status (New, Qualified, Booked, Lost), **Then** only leads matching the selected status are displayed.
2. **Given** a staff member updates a lead's status from Qualified to Booked, **When** they add a note about the outcome, **Then** the note is saved to the lead's history and the status change is timestamped.
3. **Given** a customer calls the business directly (offline), **When** the staff member records the interaction in the CRM, **Then** the conversation is linked to the customer's existing record.
4. **Given** a business admin needs to follow up with a lead, **When** they schedule a follow-up reminder, **Then** the system triggers a notification at the scheduled time.
5. **Given** a business admin reviews a customer's full history, **When** they view the record, **Then** they see all past conversations, appointments, notes, and lead status changes in chronological order.

---

### User Story 5 - Business Dashboard & Analytics (Priority: P2)

A business admin (Gym Owner) reviews their dashboard to understand AI performance, identify missed opportunities, track conversion metrics, and monitor correction rates. They can export reports and spot trends.

**Why this priority**: Without visibility into performance, businesses cannot optimize their AI or workflows. Data-driven decisions are key to long-term retention.

**Independent Test**: Can be tested by generating a dashboard report with test data and verifying all metrics (total leads, conversion rate, response time, correction rate, booking rate) are calculated correctly and displayed without errors.

**Acceptance Scenarios**:

1. **Given** a business admin logs into the dashboard, **When** they view the overview page, **Then** they see total leads, booked appointments, conversion rate, correction rate, and average response time for the current period.
2. **Given** a business admin views the analytics section, **When** they select a date range, **Then** the metrics update to reflect the selected period with daily or weekly breakdowns.
3. **Given** a business has missed leads (inquiries that went unanswered or unconverted), **When** the admin reviews the missed lead list, **Then** they see each missed lead with context and can manually attempt recovery.
4. **Given** a business admin needs a report, **When** they export analytics as a summary, **Then** they receive a structured report covering key metrics for the selected period.
5. **Given** the AI performance data is available, **When** the admin reviews AI metrics, **Then** they see response accuracy, escalation rate, correction rate, and customer satisfaction indicators.

---

### User Story 6 - AI Escalation & Human Handoff (Priority: P2)

When the AI encounters a situation it cannot handle confidently, or when an action falls outside the AI Worker's Permission Budget, it escalates to a human staff member. Staff can take over the conversation and resolve the customer's needs.

**Why this priority**: AI should know its limits. Unhandled escalations cost businesses customers. Human-in-the-loop ensures reliability for high-stakes interactions.

**Independent Test**: Can be tested by triggering escalation scenarios (unclear intent, explicit request for human, action outside Permission Budget, system confidence below threshold) and verifying the escalation is triggered, staff is notified, and handoff occurs smoothly.

**Acceptance Scenarios**:

1. **Given** a customer asks a question the AI cannot answer, **When** the AI's confidence drops below the threshold, **Then** the conversation is flagged for escalation and the staff member receives a notification.
2. **Given** a customer explicitly requests to speak with a human, **When** they type "talk to a person" or similar, **Then** the AI immediately escalates and notifies available staff.
3. **Given** a customer requests a refund or discount outside defined policies, **When** the AI detects this request, **Then** it flags the conversation for human approval because the action is outside its Permission Budget.
4. **Given** a staff member receives an escalation notification, **When** they open the conversation, **Then** they see the full conversation history and can respond directly to the customer.
5. **Given** a staff member resolves an escalated conversation, **When** they mark it as resolved, **Then** the resolution is logged and the AI can resume if the customer continues.

---

### User Story 7 - Autonomy Management (Priority: P1)

The Business Admin reviews and adjusts the AI Worker's autonomy level per tenant. They monitor live Graduation Progress against defined criteria and can manually toggle between Mode 1 (Supervised) and Mode 2 (Autonomous).

**Why this priority**: Autonomy must be earned through supervised performance to ensure business safety and avoid costly AI mistakes.

**Independent Test**: Can be tested by verifying the current autonomy state of a tenant, observing the graduation progress metrics updates on chat correction, and testing that the AI responds directly only when Mode 2 is active.

**Acceptance Scenarios**:

1. **Given** a tenant is in Mode 1 (Supervised), **When** they view the dashboard, **Then** they see their live Graduation Progress (total reviewed chats, correction rate, critical error checklist).
2. **Given** a tenant has met the Graduation Criteria (e.g., 50 supervised chats, <10% correction rate, 0 critical errors), **When** they check their status, **Then** they are flagged as "Eligible for Mode 2".
3. **Given** a Business Admin wants to promote the AI, **When** they toggle the autonomy state to Mode 2 (Autonomous), **Then** the AI is authorized to respond directly and unsupervised.
4. **Given** a tenant is in Mode 2 (Autonomous), **When** the admin detects poor performance, **Then** they can manually downgrade the AI back to Mode 1 (Supervised) instantly.

---

### User Story 8 - AI Workflow Automation (Priority: P3)

A business admin configures automated AI workflows for follow-up reminders, missed-call recovery, and booking confirmation sequences. The AI executes these workflows without manual intervention.

**Why this priority**: Automation at scale is why businesses choose AI over human receptionists. This delivers recurring value with minimal ongoing effort.

**Independent Test**: Can be tested by creating a follow-up workflow, triggering it with a test appointment, and verifying the automated message is sent at the scheduled time, the workflow logs are recorded, and the outcome is reflected in the lead record.

**Acceptance Scenarios**:

1. **Given** a customer books an appointment, **When** the booking is confirmed, **Then** the AI automatically schedules a confirmation follow-up for 24 hours before the appointment.
2. **Given** a customer misses their appointment without cancellation, **When** the no-show is recorded, **Then** the AI triggers a follow-up workflow to re-engage the customer.
3. **Given** a lead goes cold (no response after initial contact), **When** the configured cold-lead threshold is reached, **Then** the AI sends an automated follow-up message to re-engage.
4. **Given** a business admin configures business rules (e.g., "no bookings on Sundays"), **When** a customer requests a blocked time, **Then** the AI provides an alternative without breaking the rule.
5. **Given** a workflow fails to execute (e.g., email delivery fails), **When** the system detects the failure, **Then** the failure is logged, a retry is attempted, and staff is notified if retry also fails.

---

## Permission Budget & Escalation Policy

The system enforces strict boundaries around the actions the AI can execute without human verification:

*   **Always Allowed Unsupervised** (any autonomy level):
    *   Answering FAQ / policy questions grounded in seeded data.
    *   Quoting listed services and prices.
    *   Checking calendar availability.
    *   Capturing customer contact info/preferences.
    *   Proposing and holding appointment slots.
*   **Always Requires Human Approval** (regardless of autonomy level, triggers Mode 1 workflow):
    *   Applying discounts, credits, or processing refunds.
    *   Cancelling confirmed appointments.
    *   Replying to customers when sentiment analysis flags frustration, anger, or urgency.
    *   Answering questions outside seeded business context or FAQs.

---

## Edge Cases

- **Customer submits invalid contact info**: AI asks for valid email/phone; lead is created with "unverified contact" flag if validation fails after 3 attempts
- **Business has no available slots**: AI informs customer, offers waitlist registration, and notifies admin of demand spike
- **Duplicate lead detection**: If customer name + phone/email matches existing record, the lead is merged with history preserved
- **AI receives out-of-scope request** (e.g., "what is 2+2?"): AI redirects to relevant business topics; no error but also no random responses
- **High-volume burst**: System queues incoming messages; AI processes within 10 seconds even during peak
- **Staff member updates appointment while AI is also processing the same customer**: Last-write-wins with full audit trail of both actions
- **Customer cancels during AI booking flow**: AI gracefully closes the flow, saves partial lead data, and thanks the customer
- **Super admin deactivates tenant while active conversations exist**: Active conversations complete gracefully with a system notice, then pause
- **AI generates potentially harmful response**: Content guardrails block the response; safe fallback message shown; incident logged
- **Network failure during booking confirmation**: Booking is held in pending state; customer is informed; retry on reconnect; no double-booking possible

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST allow new businesses to create an account with a business name, admin email, and password
- **FR-002**: System MUST send a verification email upon business account creation; account activates upon email confirmation
- **FR-003**: System MUST allow Business Admins to reset their password via a secure email link
- **FR-004**: System MUST enforce JWT-based authentication with role-based access control (RBAC) for Super Admin, Business Admin, and Staff Member roles
- **FR-005**: System MUST isolate each business tenant's data completely — no cross-tenant data access is possible at any layer
- **FR-006**: System MUST support three role types with distinct permissions: Super Admin (platform management), Business Admin (business settings + AI config), Staff Member (appointments + escalations)
- **FR-007**: System MUST provide a web-based AI receptionist widget that businesses can embed on their website via a script tag or iframe
- **FR-008**: System MUST allow the AI to conduct natural, multi-turn conversations with customers in a goal-oriented flow
- **FR-009**: System MUST capture lead qualification data: customer name, service requested, urgency level, location (city/zip), budget range, preferred availability, and contact method
- **FR-010**: System MUST automatically create a lead record when a customer initiates a conversation, updating it in real time as information is collected
- **FR-011**: System MUST qualify leads as: Unqualified, Partially Qualified, Fully Qualified, or Booked — based on completeness of required fields and booking status
- **FR-012**: System MUST allow customers to book appointments through the AI conversation when available slots exist
- **FR-013**: System MUST detect available booking slots based on business hours and existing appointments; present options that are within the requested time window
- **FR-014**: System MUST confirm bookings and create an appointment record with customer details, service type, date/time, and status
- **FR-015**: System MUST send appointment confirmation notifications to customers via email upon successful booking
- **FR-016**: System MUST allow customers to reschedule or cancel existing appointments through the AI chat or a direct link
- **FR-017**: System MUST send rescheduling/cancellation notifications to both customer and business staff
- **FR-018**: System MUST provide a CRM view for each business showing all customers, leads, and their conversation history, with filtering by status
- **FR-019**: System MUST allow Business Admins and Staff Members to update lead status, add notes, and log interactions in the CRM
- **FR-020**: System MUST support follow-up reminders — scheduled automated messages triggered by business-configured workflows
- **FR-021**: System MUST provide a dashboard for each Business Admin showing: total leads, booking rate, conversation count, conversion rate, correction rate, and missed lead count for the current period
- **FR-022**: System MUST allow filtering of dashboard metrics by customizable date ranges (7 days, 30 days, 90 days, custom)
- **FR-023**: System MUST track and display AI performance metrics: average response time, escalation rate, correction rate, booking conversion per conversation, and customer satisfaction indicators
- **FR-024**: System MUST allow Super Admins to view all business tenants, their subscription status, and platform-wide aggregate metrics
- **FR-025**: System MUST escalate AI conversations to human staff when: AI confidence is low, customer requests human, triggers outside Permission Budget occur, or business-configured triggers activate
- **FR-026**: System MUST notify staff members via email and in-app notification when an escalation occurs
- **FR-027**: System MUST allow staff to take over any active conversation and respond directly to the customer
- **FR-028**: System MUST log all AI conversations with full message history for audit, training, and dispute resolution
- **FR-029**: System MUST support timezone-aware scheduling for all bookings and notifications
- **FR-030**: System MUST enforce HTTPS-only access for all API endpoints and the web interface
- **FR-031**: System MUST store all secrets (API keys, database credentials, JWT signing keys) in environment variables, never in source code
- **FR-032**: System MUST validate and sanitize all user input to prevent injection attacks
- **FR-033**: System MUST support AI tool-calling for actions: create lead, check availability, book appointment, send notification, escalate, log note
- **FR-034**: System MUST support AI context injection — passing business-specific data (hours, services, staff names) to the AI at conversation start
- **FR-035**: System MUST be designed to support future capabilities: Model Context Protocol (MCP), WhatsApp integration, RAG knowledge base, vector memory, without breaking existing workflows
- **FR-036**: System MUST track tenant-specific autonomy levels (`mode_1_supervised` vs `mode_2_autonomous`) and block autonomous replies if Mode 1 is active

### Key Entities

- **Tenant**: Represents a business account. Attributes: tenant_id, business_name, domain, timezone, subscription_tier, status, autonomy_level (supervised | autonomous), created_at, settings (JSON)
- **User**: Represents a person with access to the platform. Attributes: user_id, tenant_id, email, password_hash, role (super_admin | business_admin | staff), status, last_login
- **Customer**: Represents an end customer of a business. Attributes: customer_id, tenant_id, name, email, phone, location, notes, created_at
- **Lead**: Represents an incoming inquiry. Attributes: lead_id, tenant_id, customer_id, status (unqualified | partially_qualified | qualified | booked | lost), conversation_summary, urgency, budget_range, preferred_service, preferred_times, source, assigned_to, created_at, updated_at
- **Conversation**: Represents an AI chat session. Attributes: conversation_id, lead_id, tenant_id, messages (JSON array), status (active | escalated | closed), started_at, ended_at, escalated_to
- **Appointment**: Represents a booked slot. Attributes: appointment_id, lead_id, customer_id, tenant_id, service_type, start_time, end_time, status (confirmed | cancelled | rescheduled | completed | no_show), notes, created_at, updated_at
- **Workflow**: Represents an automated AI workflow. Attributes: workflow_id, tenant_id, name, trigger_type, trigger_config (JSON), actions (JSON), is_active, created_at
- **Notification**: Represents a sent notification. Attributes: notification_id, tenant_id, recipient_type, recipient_address, channel (email | sms | whatsapp), template, status (pending | sent | failed), sent_at, error_message
- **AuditLog**: Represents system activity for compliance. Attributes: log_id, tenant_id, user_id, action, entity_type, entity_id, details (JSON), ip_address, timestamp

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: **Setup Speed**: A new business admin can complete account setup and have an active AI receptionist within 30 minutes of signup, default-active in Mode 1 (Supervised).
- **SC-002**: **Automation Handoff**: 90% of routine booking inquiries complete without human escalation in Mode 2 (Autonomous).
- **SC-003**: **Accuracy**: Required lead fields (name, service, urgency, location, budget, availability) are captured in ≥80% of successful interactions.
- **SC-004**: Customers can complete a full booking from first message to confirmation in under 5 minutes.
- **SC-005**: Business Admins see dashboard metrics updated within 5 minutes of any conversation, lead, or booking event.
- **SC-006**: **Responsiveness**: API response time remains under 500ms for 95% of requests during normal load.
- **SC-007**: System handles 100 concurrent business tenants with 50 concurrent AI conversations each without degradation.
- **SC-008**: **Isolation**: Zero cross-tenant data leakage — confirmed through automated isolation tests on every deployment.
- **SC-009**: **Graduation Readiness**: A tenant becomes eligible to request Mode 2 after ≥50 supervised conversations reviewed, a correction rate <10% over the most recent 20 conversations, and zero critical errors (wrong booking, wrong price, policy violation) in that window. Defaults configurable per plan tier.
- **SC-010**: **Auditability**: For any AI action, the Business Admin can answer "what did it do, what did it recommend, who approved it, what happened next" from the dashboard in under 2 minutes.
- **SC-011**: 99.5% notification delivery success rate for confirmation and reminder emails.
- **SC-012**: 95% of booking confirmations are reflected in the calendar view within 10 seconds of completion.
- **SC-013**: Staff members receive escalation notifications within 30 seconds of trigger activation.