/**
 * Airtable MCP Server - Main Export
 *
 * This module exports the main server functionality for programmatic use.
 * For CLI usage, use the bin/airtable-mcp.js executable.
 */

export { start } from './airtable-mcp-server';
export * from './errors';

// Re-export types for consumers
export type { AppConfig, AirtableAuthConfig, LogLevel } from './app/config';
export type { AppContext } from './app/context';

export interface ToolParameter {
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  description: string;
  required?: boolean;
  default?: unknown;
  enum?: string[];
}

export interface ToolSchema {
  name: string;
  description: string;
  inputSchema: {
    type: 'object';
    properties: Record<string, ToolParameter>;
    required?: string[];
  };
}

export interface PromptArgument {
  name: string;
  description: string;
  required: boolean;
  type?: 'string' | 'number' | 'boolean';
  enum?: string[];
}

export interface PromptSchema {
  name: string;
  description: string;
  arguments: PromptArgument[];
}
