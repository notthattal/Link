## Security Documentation

### API Key Management

- API keys are stored using environment variables.
- They are never hardcoded anywhere in source code or frontend files.

### Input Validation and Sanitization

- Inputs are schema-validated before processing.
- AWS Bedrock Guardrails are used to enforce prompt safety and block malicious instructions.
- Unsafe or malformed inputs are automatically handled via Bedrock’s `guardrailConfig` policies.

### Authentication and Authorization

- AWS Cognito handles all user authentication flows.
- Only verified users are allowed to invoke protected endpoints.

### Rate Limiting

- Flask backend enforces rate limiting at 25 requests per minute using `flask-limiter`.
- Additional throttling and usage plans can be configured via API Gateway for production deployments.

### Data Handling and Privacy

- User identity is tracked internally using the Cognito `sub` UUID only.
- All environment variables and credentials are scoped per environment and never exposed publicly.

### Safety Filters and Monitoring

- AWS Bedrock Guardrails apply real-time content moderation policies.
- All prompt/response flows are subject to Bedrock's safety filters.
- AWS CloudWatch is used to monitor API usage, latency, and access patterns.
- All authentication events and access attempts are tracked via CloudTrail for audit compliance.