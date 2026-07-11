# Product Validation QA Checklist

This checklist is used to validate the platform's readiness for commercial pilot onboarding.

## 1. Authentication & Tenant Creation
- [ ] **Signup**: New user can register a tenant and admin account.
- [ ] **Email Verification**: User receives verification email and can verify.
- [ ] **Login**: User can log in with verified credentials.
- [ ] **Password Reset**: User can request and complete password reset.
- [ ] **Tenant Isolation**: User cannot access data from another tenant.

## 2. Onboarding Workflow
- [ ] **Business Profile**: Can save business name, description, and website.
- [ ] **Services**: Can add, edit, and delete services.
- [ ] **Availability**: Can set working hours for all days of the week.
- [ ] **FAQs**: Can add common questions and answers for AI knowledge base.
- [ ] **AI Configuration**: Can customize AI personality and enable/disable tools.
- [ ] **Completion**: Dashboard is unlocked after completing onboarding.

## 3. AI Conversation & Lead Qualification
- [ ] **Message Ingestion**: Public API accepts messages and returns valid AI responses.
- [ ] **Personality Adherence**: AI follows the configured personality traits.
- [ ] **Lead Capture**: AI correctly identifies and captures lead information (name, phone, service).
- [ ] **Tool Execution**: AI correctly triggers the booking tool when requested.

## 4. Appointment Booking
- [ ] **Availability Logic**: Booking system correctly identifies available slots based on rules.
- [ ] **Slot Reservation**: Appointments are correctly recorded in the database.
- [ ] **Calendar Provider**: (Optional) Integration with Google/Outlook calendar works.

## 5. CRM & Lead Management
- [ ] **Pipeline Visibility**: Leads appear in the correct stage of the kanban board.
- [ ] **Activity Timeline**: All conversations and status changes are logged in the customer history.
- [ ] **Customer Memory**: AI-learned facts are persisted in the customer profile.

## 6. Analytics & Executive Dashboard
- [ ] **KPI Cards**: Correct counts for MRR, activation, and bookings.
- [ ] **Conversion Funnel**: Funnel visualization accurately reflects user journey steps.
- [ ] **Retention Tracking**: High-risk tenants are correctly identified.

## 7. Operations & Growth Automation
- [ ] **Rescue Workflows**: Automated notifications are triggered for stalled onboarding.
- [ ] **Lead Attribution**: Lead source and campaign data are correctly captured.
- [ ] **Anomaly Detection**: Spikes in failures or activity drops trigger alerts.

## 8. Frontend Quality & UX
- [ ] **Mobile Responsiveness**: All pages are usable on mobile devices.
- [ ] **Empty States**: Clear messaging when no data is available (e.g., no leads).
- [ ] **Loading States**: Visual feedback during data fetching or processing.
- [ ] **Error Handling**: Graceful handling of API errors or network issues.

## 9. Production Infrastructure
- [ ] **Health Checks**: `/health/ready` returns 200.
- [ ] **Rate Limiting**: API protection is active for public endpoints.
- [ ] **Database Migrations**: Database is up to date with the latest schema.
- [ ] **Environment Variables**: All required production secrets are set.
