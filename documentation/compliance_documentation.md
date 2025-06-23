## Compliance Documentation

### Data Privacy and Protection

- All personally identifiable information (PII) is managed exclusively through AWS Cognito
- OAuth tokens and user credentials are encrypted in-transit and at-rest using AWS-managed keys.
- App tokens (e.g., Spotify/Gmail) are never exposed to the frontend or logged.

### Regulatory Compliance

- The system adheres to **GDPR** principles: user data is stored minimally, is deletable on request, and never shared with third parties.
- No payment information is collected, avoiding PCI-DSS scope.

### Data Retention and Deletion

- User connection metadata is stored in DynamoDB and can be deleted on account removal.
- No chat history or user messages are persisted beyond session lifetime.
- All user data is deletable via backend admin tools or user request.

### Secure Development Practices

- All environment variables (e.g., API keys, client secrets) are never committed to source control.
- Infrastructure is isolated per environment (e.g., dev vs. prod) using scoped environment variable groups.
- Code undergoes regular linting and test coverage tracking using `pytest-cov`.

### External Service Integration

- All third-party integrations (Spotify, Gmail, etc.) use standard OAuth 2.0 flows with scopes restricted to minimal required permissions
- Token scopes are defined explicitly and reviewed to ensure least privilege access

### Hosting and Network Security

- Backend is containerized via Docker and deployed using Railway with no exposed admin interfaces
- CORS is tightly controlled via origin whitelisting
- HTTPS is enforced by default across all user-facing routes

### Logging and Auditability

- All authentication, token issuance, and protected resource access are logged in AWS CloudWatch and/or AWS CloudTrail
- Error logs are scrubbed of PII before ingestion
- Logs are rotated and retained per environment policy

### Incident Response

- All access to sensitive data is logged and reviewed
- Docker builds and Git-based versioning are implemented for easy rollback