#!/usr/bin/env node
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { McpServer } = require('@modelcontextprotocol/sdk/server/mcp');
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio');
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { HttpServerTransport } = require('@modelcontextprotocol/sdk/server/http');
import { loadConfig } from './app/config';
import { Logger } from './app/logger';
import { RateLimiter } from './app/rateLimiter';
import { AirtableClient } from './app/airtable-client';
import { GovernanceService } from './app/governance';
import { ExceptionStore } from './app/exceptions';
import { registerAllTools } from './app/tools';
import { AppContext } from './app/context';


const PROTOCOL_VERSION = '2025-12-08';


function buildContext(config: ReturnType<typeof loadConfig>, rootLogger: Logger): AppContext {
  const baseLimiter = new RateLimiter({ maxRequestsPerSecond: 5 });
  const patLimiter = new RateLimiter({ maxRequestsPerSecond: 50 });

  const airtable = new AirtableClient(config.auth.personalAccessToken, {
    baseLimiter,
    patLimiter,
    logger: rootLogger.child({ component: 'airtable_client' }),
    userAgent: `airtable-brain-mcp/${config.version}`,
    patHash: config.auth.patHash
  });

  const governance = new GovernanceService(config.governance);
  const exceptions = new ExceptionStore(config.exceptionQueueSize, rootLogger);

  return {
    config,
    logger: rootLogger,
    airtable,
    governance,
    exceptions
  };
}

export async function start(): Promise<void> {
  const config = loadConfig();
  const logger = new Logger(config.logLevel, { component: 'server' });

  const context = buildContext(config, logger);

  const server = new McpServer(
    {
      name: 'airtable-brain',
      version: config.version,
      protocolVersion: PROTOCOL_VERSION
    },
    {
      capabilities: {
        tools: {},
        prompts: {},
        resources: {}
      },
      instructions:
        'Use describe and query tools for read flows. All mutations require diff review and idempotency keys.'
    }
  );

  registerAllTools(server, context);

  // Always start Stdio transport for local development
  const stdioTransport = new StdioServerTransport();
  await server.connect(stdioTransport);
  logger.info('MCP server connected over Stdio');

  // Optionally start HTTP transport for remote clients
  const transportType = process.env.MCP_TRANSPORT;
  if (transportType === 'http') {
    const port = process.env.PORT ? Number(process.env.PORT) : 8000;
    const useSSE = process.env.MCP_USE_SSE === 'true';
    const httpTransport = new HttpServerTransport({ host: '0.0.0.0', port, useSSE });
    await server.connect(httpTransport);
    logger.info('MCP server connected over HTTP', { port, useSSE });
  }

  logger.info('Airtable Brain MCP server ready', {
    version: config.version,
    protocolVersion: PROTOCOL_VERSION,
    transport: transportType
  });

  const shutdown = async (signal: string) => {
    logger.info('Shutting down due to signal', { signal });
    await server.close();
    await transport.close();
    process.exit(0);
  };

  process.on('SIGINT', () => void shutdown('SIGINT'));
  process.on('SIGTERM', () => void shutdown('SIGTERM'));
}

// Run if executed directly
if (typeof require !== 'undefined' && require.main === module) {
  start().catch((error) => {
    console.error('Failed to start Airtable Brain MCP server:', error);
    process.exit(1);
  });
}
