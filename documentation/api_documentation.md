## API Documentation

### `Base URL`

https://link-production-06c4.up.railway.app

All endpoints expect an `Authorization` header containing a valid Cognito JWT access token.

---

### `POST /generate`

Generates a response from the chatbot based on user input and context

**Headers**
- `Authorization: Bearer <JWT>`
- `Content-Type: application/json`

**Body**
```json
{
  "message": "How's the weather today?",
  "reset": false
}
```

**Response**
```json
{
    "response": "The weather today is sunny with a high of 75°F."
}
```

---

### `GET /api/user/get_connections`

Returns a list of external apps the user has connected

**Headers**
- Authorization: Bearer <JWT>

**Response**
```json
["spotify", "gmail", "calendar"]
```
---

### `POST /callback/<provider>`

OAuth callback endpoint that finalizes third-party app connection (e.g., spotify, gmail)

**URL Parameters**
- provider: One of the supported providers (spotify, gmail, etc.)

**Query Parameters**
- code: The OAuth authorization code

**Response**
```json
{
  "message": "Spotify successfully connected"
}
```