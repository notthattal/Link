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
- API Gateway is configured with a Cognito Authorizer to verify JWT tokens for each request.
- Only verified users are allowed to invoke protected endpoints.
- Lambda functions extract the validated `sub` claim securely from the token via API Gateway's request context.

### Rate Limiting

- Flask backend enforces rate limiting at 25 requests per minute using `flask-limiter`.
- Additional throttling and usage plans can be configured via API Gateway for production deployments.

### Data Handling and Privacy

- No user PII (e.g., emails, names) is logged or stored.
- User identity is tracked internally using the Cognito `sub` UUID only.
- Prompt contents are optionally hashed or archived securely in S3.
- All environment variables and credentials are scoped per environment and never exposed publicly.

### Audit Logging

- Each API invocation is logged to CloudWatch with:
  - Timestamp
  - Cognito user `sub`
  - Request ID
  - Prompt text
  - Model response
- Logs are structured with a consistent `AUDIT_LOG` prefix for easy traceability.
- Request IDs can be correlated with CloudTrail events to determine full invocation context and user action.
- Logs are stored in immutable AWS-managed infrastructure and monitored for unusual patterns.

### Safety Filters and Monitoring

- AWS Bedrock Guardrails apply real-time content moderation policies.
- All prompt/response flows are subject to Bedrock's safety filters.
- AWS CloudWatch is used to monitor API usage, latency, and access patterns.
- All authentication events and access attempts are tracked via CloudTrail for audit compliance.