# 🔐 Airtable MCP OAuth Server

Complete OAuth2 authentication flow for Airtable MCP server with ChatGPT integration.

## 🚀 Features

- ✅ Complete OAuth2 flow for Airtable
- ✅ Secure token storage per user session
- ✅ MCP-compatible endpoints for ChatGPT
- ✅ Session management with CSRF protection
- ✅ Token refresh capability
- ✅ Express.js + Node.js implementation
- ✅ CORS enabled for web integration

## 📋 Prerequisites

- Node.js 18+
- Airtable account with OAuth app registered
- HTTPS-enabled domain (required for production)

## 🛠️ Setup Instructions

### 1. Register Airtable OAuth App

1. Go to [Airtable OAuth Apps](https://airtable.com/developers/web/api/oauth)
2. Click "Create a new OAuth integration"
3. Fill in app details:
   - **Name**: Your app name
   - **Redirect URI**: `https://your-domain.com/oauth/callback`
4. Note down:
   - **Client ID**
   - **Client Secret**

### 2. Configure Environment Variables

Create a `.env` file in the `src/` directory:

```bash
# Airtable OAuth Configuration
AIRTABLE_CLIENT_ID=your_client_id_here
AIRTABLE_CLIENT_SECRET=your_client_secret_here
AIRTABLE_REDIRECT_URI=https://your-domain.com/oauth/callback

# Server Configuration
PORT=3000
NODE_ENV=production

# Optional: Base URL for links (useful in production)
BASE_URL=https://your-domain.com
```

### 3. Install Dependencies

```bash
cd src/
npm install
```

### 4. Start the Server

```bash
# Development
npm run dev

# Production
npm start
```

## 🔗 Endpoints

### OAuth Endpoints

- `GET /` - Web interface for testing OAuth
- `GET /health` - Server health check
- `GET /oauth/login?session_id=xxx` - Initiate OAuth flow
- `GET /oauth/callback` - OAuth callback handler
- `GET /oauth/status/:sessionId` - Check authentication status
- `POST /oauth/logout/:sessionId` - Logout user session

### MCP Endpoints

- `POST /mcp/list_tools` - List available MCP tools
- `POST /mcp/call_tool` - Execute MCP tools

## 🔄 OAuth Flow

1. **Initiate Login**: User visits `/oauth/login?session_id=user_session_123`
2. **Airtable Authorization**: User is redirected to Airtable OAuth page
3. **User Consent**: User grants permissions to your app
4. **Callback**: Airtable redirects to `/oauth/callback` with authorization code
5. **Token Exchange**: Server exchanges code for access token
6. **Token Storage**: Token is stored securely per session
7. **Success**: User can now use Airtable tools in ChatGPT

## 🛡️ Security Features

- **CSRF Protection**: State parameter validation
- **Secure Token Storage**: File-based storage (can be upgraded to database)
- **Session Management**: Unique session IDs for each user
- **Token Expiration**: Automatic token expiry handling
- **HTTPS Required**: OAuth requires secure connections in production

## 🧪 Testing the OAuth Flow

### Local Development

1. Start the server: `npm run dev`
2. Visit `http://localhost:3000` in your browser
3. Click "Generate Session ID" or enter one manually
4. Click "Start OAuth Login"
5. Complete Airtable OAuth flow
6. Check `/oauth/status/your_session_id` to verify authentication

### MCP Tool Testing

Use curl to test MCP endpoints:

```bash
# List tools
curl -X POST http://localhost:3000/mcp/list_tools \
  -H "Content-Type: application/json"

# Call tool (requires authentication)
curl -X POST http://localhost:3000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "list_bases",
    "arguments": {
      "session_id": "your_session_id"
    }
  }'
```

## 🚀 Deployment

### Railway (Recommended)

1. Connect your GitHub repo to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically
4. Get your HTTPS domain from Railway

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### Other Platforms

- **Vercel**: Use serverless functions
- **Heroku**: Standard Node.js deployment
- **AWS/GCP**: Container or serverless deployment

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AIRTABLE_CLIENT_ID` | ✅ | OAuth client ID from Airtable |
| `AIRTABLE_CLIENT_SECRET` | ✅ | OAuth client secret from Airtable |
| `AIRTABLE_REDIRECT_URI` | ❌ | OAuth redirect URI (auto-detected) |
| `PORT` | ❌ | Server port (default: 3000) |
| `BASE_URL` | ❌ | Base URL for links (auto-detected) |

### Token Storage

Tokens are stored in `src/tokens.db.json`:

```json
{
  "sess_abc123": {
    "access_token": "patXXXXX...",
    "refresh_token": "rfrXXXXX...",
    "token_type": "Bearer",
    "expires_at": 1640995200000,
    "scope": "data.records:read data.records:write...",
    "created_at": "2023-01-01T00:00:00.000Z"
  }
}
```

## 🔗 ChatGPT Integration

### 1. Add Custom Tool

In ChatGPT, add a custom tool with:
- **URL**: `https://your-domain.com/mcp`
- **Method**: POST
- **Headers**: `Content-Type: application/json`

### 2. Authentication Flow

When ChatGPT tries to use Airtable tools:

1. If no session: Returns login URL
2. User authenticates via OAuth
3. ChatGPT can now access Airtable data

### 3. Example Usage

```javascript
// ChatGPT will call your MCP endpoint like:
POST https://your-domain.com/mcp/call_tool
{
  "name": "list_bases",
  "arguments": {
    "session_id": "user_session_123"
  }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid client" error**
   - Check `AIRTABLE_CLIENT_ID` and `AIRTABLE_CLIENT_SECRET`

2. **"Redirect URI mismatch"**
   - Ensure redirect URI matches Airtable OAuth app settings

3. **"Token expired"**
   - Implement token refresh logic (TODO)

4. **CORS errors**
   - CORS is enabled by default, check your domain settings

### Logs

Check server logs for detailed error information:

```bash
npm run dev  # Shows detailed logs
```

## 📈 Future Enhancements

- [ ] Token refresh automation
- [ ] Database storage (PostgreSQL/Redis)
- [ ] Rate limiting
- [ ] Audit logging
- [ ] Multi-tenant support
- [ ] Webhook integrations

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

- Create an issue on GitHub
- Check the troubleshooting section
- Review Airtable OAuth documentation
