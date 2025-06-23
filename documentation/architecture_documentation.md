## Architecture Documentation

### Overview
This system is a chatbot that a user can connect external applications to and use as a personal assistant. It uses Claude's 3.5 haiku model and leverages AWS Bedrock for the chat interaction and tool calling functionality.

### Architecture Diagram

![Architecture Diagram](./img/architecture_diagram.png)

### Flow
1. A user can either sign-in or create an account which is authenticated through AWS Cognito
2. A user can either connect an application or begin chatting
3. If a user selects to connect apps, they will be sent to that app's respective authentication page before being redirected back to the site
5. From then on, the user can interact with the chatbot as normal. If a user decides to request an action from the chatbot that would require the use of that external application, link will handle that for the user
6. Logs are sent to CloudWatch from AWS Cognito and AWS Bedrock and DynamoDB for security and performance monitoring 

### Components

1. Frontend (Optional): 
    - React Native frontend 

2. Backend:
    - Amazon Cognito is used as the base for the authentication service
    - A router is used to connect to applications or chat with bedrock
    - AWS Bedrock/Anthropic's claude for the chat interactions
    - AWS DynamoDB to store apps the user has connected to
    - In-memory store for local caching of necessary information for faster processing
    - AWS Cloudwatch for monitoring and logging

### Requirements

1. Backend
```python
python-dotenv==1.1.0
requests==2.32.4
flask==3.1.1
flask-cors==6.0.1
pytest==8.4.0
pytest-cov==6.1.1
pydantic==2.11.5
pandas==2.3.0
boto3==1.38.41
```

2. Frontend
    - Node v23.11.0

### Model Configuration

2. Bedrock
    - Model: anthropic.claude-3-haiku-20240307-v1:0
    - Method: client.converse()
    - Schema enforcement: Tool dependent