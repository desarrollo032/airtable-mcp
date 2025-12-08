#!/usr/bin/env node
/**
 * Airtable MCP OAuth Server
 * Complete OAuth2 flow for Airtable + MCP integration
 */

import express from 'express';
import fetch from 'node-fetch';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import cors from 'cors';
import crypto from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// ================================
// 1. CONFIGURATION
// ================================
const CLIENT_ID = process.env.AIRTABLE_CLIENT_ID;
const CLIENT_SECRET = process.env.AIRTABLE_CLIENT_SECRET;
const REDIRECT_URI = process.env.AIRTABLE_REDIRECT_URI || `http://localhost:${PORT}/oauth/callback`;
const TOKEN_DB_PATH = path.join(__dirname, 'tokens.db.json');

// Airtable OAuth URLs
const AIRTABLE_AUTHORIZE_URL = 'https://airtable.com/oauth2/v1/authorize';
const AIRTABLE_TOKEN_URL = 'https://airtable.com/oauth2/v1/token';

// OAuth Scopes
const OAUTH_SCOPES = [
  'data.records:read',
  'data.records:write',
  'schema.bases:read',
  'schema.tables:read'
].join(' ');

// ================================
// 2. MIDDLEWARE
// ================================
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// ================================
// 3. TOKEN DATABASE MANAGEMENT
// ================================
function loadTokens() {
  try {
    if (!fs.existsSync(TOKEN_DB_PATH)) {
      return {};
    }
    const data = fs.readFileSync(TOKEN_DB_PATH, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Error loading tokens:', error);
    return {};
  }
}

function saveTokens(db) {
  try {
    fs.writeFileSync(TOKEN_DB_PATH, JSON.stringify(db, null, 2));
    console.log('Tokens saved successfully');
  } catch (error) {
    console.error('Error saving tokens:', error);
  }
}

let tokenDB = loadTokens(); // { session_id: { access_token, refresh_token, expires_at, user_info } }

// ================================
// 4. SESSION MANAGEMENT
// ================================
function generateSessionId() {
  return 'sess_' + crypto.randomBytes(16).toString('hex');
}

function generateState() {
  return crypto.randomBytes(32).toString('hex');
}

// ================================
// 5. OAUTH ROUTES
// ================================

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    server: 'Airtable MCP OAuth Server',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// Initiate OAuth login
app.get('/oauth/login', (req, res) => {
  const sessionId = req.query.session_id || generateSessionId();
  const state = generateState();

  // Store state for CSRF protection
  tokenDB[sessionId] = tokenDB[sessionId] || {};
  tokenDB[sessionId].oauth_state = state;
  saveTokens(tokenDB);

  const authUrl = new URL(AIRTABLE_AUTHORIZE_URL);
  authUrl.searchParams.set('client_id', CLIENT_ID);
  authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('scope', OAUTH_SCOPES);
  authUrl.searchParams.set('state', state);

  console.log(`OAuth login initiated for session: ${sessionId}`);
  res.redirect(authUrl.toString());
});

// OAuth callback
app.get('/oauth/callback', async (req, res) => {
  const { code, state, error, error_description } = req.query;

  if (error) {
    console.error('OAuth error:', error, error_description);
    return res.status(400).json({
      error: 'oauth_error',
      message: error_description || 'OAuth authentication failed'
    });
  }

  if (!code || !state) {
    return res.status(400).json({
      error: 'invalid_request',
      message: 'Missing authorization code or state'
    });
  }

  // Find session by state
  let sessionId = null;
  for (const [sid, data] of Object.entries(tokenDB)) {
    if (data.oauth_state === state) {
      sessionId = sid;
      break;
    }
  }

  if (!sessionId) {
    return res.status(400).json({
      error: 'invalid_state',
      message: 'Invalid or expired state parameter'
    });
  }

  try {
    // Exchange code for tokens
    const tokenResponse = await fetch(AIRTABLE_TOKEN_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code,
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        redirect_uri: REDIRECT_URI,
      }),
    });

    const tokenData = await tokenResponse.json();

    if (!tokenResponse.ok) {
      console.error('Token exchange failed:', tokenData);
      return res.status(400).json({
        error: 'token_exchange_failed',
        message: tokenData.error_description || 'Failed to exchange authorization code'
      });
    }

    // Store tokens
    const expiresAt = tokenData.expires_in
      ? Date.now() + (tokenData.expires_in * 1000)
      : null;

    tokenDB[sessionId] = {
      ...tokenDB[sessionId],
      access_token: tokenData.access_token,
      refresh_token: tokenData.refresh_token,
      token_type: tokenData.token_type,
      expires_at: expiresAt,
      scope: tokenData.scope,
      created_at: new Date().toISOString()
    };

    // Remove OAuth state
    delete tokenDB[sessionId].oauth_state;
    saveTokens(tokenDB);

    console.log(`OAuth successful for session: ${sessionId}`);

    // Success page
    res.send(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Airtable OAuth Success</title>
          <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .success { color: #28a745; }
            .session-id { background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; }
          </style>
        </head>
        <body>
          <h1 class="success">✅ Authentication Successful!</h1>
          <p>You can now return to ChatGPT and use Airtable tools.</p>
          <p><strong>Session ID:</strong> <span class="session-id">${sessionId}</span></p>
          <p><small>You can close this window.</small></p>
        </body>
      </html>
    `);

  } catch (error) {
    console.error('OAuth callback error:', error);
    res.status(500).json({
      error: 'server_error',
      message: 'Internal server error during authentication'
    });
  }
});

// Get token status for a session
app.get('/oauth/status/:sessionId', (req, res) => {
  const { sessionId } = req.params;
  const sessionData = tokenDB[sessionId];

  if (!sessionData || !sessionData.access_token) {
    return res.json({
      authenticated: false,
      session_id: sessionId
    });
  }

  // Check if token is expired
  const isExpired = sessionData.expires_at && Date.now() > sessionData.expires_at;

  res.json({
    authenticated: !isExpired,
    session_id: sessionId,
    expires_at: sessionData.expires_at,
    created_at: sessionData.created_at,
    scope: sessionData.scope
  });
});

// Logout / revoke session
app.post('/oauth/logout/:sessionId', (req, res) => {
  const { sessionId } = req.params;

  if (tokenDB[sessionId]) {
    delete tokenDB[sessionId];
    saveTokens(tokenDB);
    console.log(`Session ${sessionId} logged out`);
  }

  res.json({ success: true, message: 'Logged out successfully' });
});

// ================================
// 6. MCP INTEGRATION ENDPOINTS
// ================================

// MCP-compatible endpoint for listing tools
app.post('/mcp/list_tools', (req, res) => {
  const { session_id } = req.body || {};

  const tools = [
    {
      name: 'list_bases',
      description: 'List all accessible Airtable bases',
      inputSchema: {
        type: 'object',
        properties: {
          session_id: { type: 'string', description: 'User session ID' }
        },
        required: ['session_id']
      }
    },
    {
      name: 'list_tables',
      description: 'List tables in a specific base',
      inputSchema: {
        type: 'object',
        properties: {
          session_id: { type: 'string', description: 'User session ID' },
          base_id: { type: 'string', description: 'Airtable base ID' }
        },
        required: ['session_id', 'base_id']
      }
    },
    {
      name: 'list_records',
      description: 'List records from a table',
      inputSchema: {
        type: 'object',
        properties: {
          session_id: { type: 'string', description: 'User session ID' },
          base_id: { type: 'string', description: 'Airtable base ID' },
          table_name: { type: 'string', description: 'Table name' },
          max_records: { type: 'number', description: 'Maximum records to return', default: 100 }
        },
        required: ['session_id', 'base_id', 'table_name']
      }
    },
    {
      name: 'create_records',
      description: 'Create records in a table',
      inputSchema: {
        type: 'object',
        properties: {
          session_id: { type: 'string', description: 'User session ID' },
          base_id: { type: 'string', description: 'Airtable base ID' },
          table_name: { type: 'string', description: 'Table name' },
          records: {
            type: 'array',
            description: 'Array of record objects with fields',
            items: { type: 'object' }
          }
        },
        required: ['session_id', 'base_id', 'table_name', 'records']
      }
    },
    {
      name: 'update_records',
      description: 'Update records in a table',
      inputSchema: {
        type: 'object',
        properties: {
          session_id: { type: 'string', description: 'User session ID' },
          base_id: { type: 'string', description: 'Airtable base ID' },
          table_name: { type: 'string', description: 'Table name' },
          records: {
            type: 'array',
            description: 'Array of record objects with id and fields',
            items: {
              type: 'object',
              properties: {
                id: { type: 'string', description: 'Record ID' },
                fields: { type: 'object', description: 'Updated fields' }
              },
              required: ['id', 'fields']
            }
          }
        },
        required: ['session_id', 'base_id', 'table_name', 'records']
      }
    }
  ];

  res.json({ tools });
});

// MCP-compatible endpoint for calling tools
app.post('/mcp/call_tool', async (req, res) => {
  const { name, arguments: args } = req.body;

  if (!args || !args.session_id) {
    return res.status(400).json({
      error: {
        type: 'invalid_request',
        message: 'session_id is required'
      }
    });
  }

  const sessionData = tokenDB[args.session_id];

  if (!sessionData || !sessionData.access_token) {
    return res.json({
      content: [{
        type: 'text',
        text: `Authentication required. Please visit: ${process.env.BASE_URL || `http://localhost:${PORT}`}/oauth/login?session_id=${args.session_id}`
      }]
    });
  }

  // Check if token is expired
  if (sessionData.expires_at && Date.now() > sessionData.expires_at) {
    return res.json({
      content: [{
        type: 'text',
        text: `Session expired. Please re-authenticate: ${process.env.BASE_URL || `http://localhost:${PORT}`}/oauth/login?session_id=${args.session_id}`
      }]
    });
  }

  try {
    let result;

    switch (name) {
      case 'list_bases':
        result = await callAirtableAPI(sessionData.access_token, 'meta/bases');
        if (result.error) throw new Error(result.error);
        const bases = result.bases || [];
        return res.json({
          content: [{
            type: 'text',
            text: bases.map((b, i) => `${i + 1}. ${b.name} (ID: ${b.id})`).join('\n') || 'No bases found.'
          }]
        });

      case 'list_tables':
        if (!args.base_id) throw new Error('base_id is required');
        result = await callAirtableAPI(sessionData.access_token, `meta/bases/${args.base_id}/tables`);
        if (result.error) throw new Error(result.error);
        const tables = result.tables || [];
        return res.json({
          content: [{
            type: 'text',
            text: tables.map((t, i) => `${i + 1}. ${t.name} (ID: ${t.id})`).join('\n') || 'No tables found.'
          }]
        });

      case 'list_records':
        if (!args.base_id || !args.table_name) throw new Error('base_id and table_name are required');
        const maxRecords = args.max_records || 100;
        result = await callAirtableAPI(sessionData.access_token, `${args.base_id}/${args.table_name}`, {
          maxRecords
        });
        if (result.error) throw new Error(result.error);
        const records = result.records || [];
        return res.json({
          content: [{
            type: 'text',
            text: records.map((r, i) => `${i + 1}. ${r.id} - ${JSON.stringify(r.fields)}`).join('\n') || 'No records found.'
          }]
        });

      case 'create_records':
        if (!args.base_id || !args.table_name || !args.records) throw new Error('base_id, table_name, and records are required');
        result = await callAirtableAPI(sessionData.access_token, `${args.base_id}/${args.table_name}`, null, {
          method: 'POST',
          body: JSON.stringify({ records: args.records.map(fields => ({ fields })) })
        });
        if (result.error) throw new Error(result.error);
        return res.json({
          content: [{
            type: 'text',
            text: `Successfully created ${result.records?.length || 0} records.`
          }]
        });

      case 'update_records':
        if (!args.base_id || !args.table_name || !args.records) throw new Error('base_id, table_name, and records are required');
        result = await callAirtableAPI(sessionData.access_token, `${args.base_id}/${args.table_name}`, null, {
          method: 'PATCH',
          body: JSON.stringify({ records: args.records })
        });
        if (result.error) throw new Error(result.error);
        return res.json({
          content: [{
            type: 'text',
            text: `Successfully updated ${result.records?.length || 0} records.`
          }]
        });

      default:
        throw new Error(`Unknown tool: ${name}`);
    }

  } catch (error) {
    console.error(`Tool execution error (${name}):`, error);
    res.json({
      content: [{
        type: 'text',
        text: `Error: ${error.message}`
      }]
    });
  }
});

// ================================
// 7. HELPER FUNCTIONS
// ================================

async function callAirtableAPI(accessToken, endpoint, params = null, options = {}) {
  const url = new URL(`https://api.airtable.com/v0/${endpoint}`);
  if (params) {
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
  }

  const response = await fetch(url.toString(), {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    ...options
  });

  return await response.json();
}

// ================================
// 8. START SERVER
// ================================

app.listen(PORT, () => {
  console.log(`🚀 Airtable MCP OAuth Server running on port ${PORT}`);
  console.log(`📋 Health check: http://localhost:${PORT}/health`);
  console.log(`🔐 OAuth login: http://localhost:${PORT}/oauth/login`);
  console.log(`🔧 MCP endpoint: http://localhost:${PORT}/mcp`);

  // Check configuration
  if (!CLIENT_ID || !CLIENT_SECRET) {
    console.warn('⚠️  WARNING: AIRTABLE_CLIENT_ID and AIRTABLE_CLIENT_SECRET not set!');
    console.warn('   Set these environment variables for OAuth to work.');
  }

  console.log(`📁 Token storage: ${TOKEN_DB_PATH}`);
});

export default app;
