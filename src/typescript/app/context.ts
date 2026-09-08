import { AppConfig } from './config';
import { AirtableClient } from './airtable-client';
import { GovernanceService } from './governance';
import { ExceptionStore } from './exceptions';
import { Logger } from './logger';
import { FastMCPService } from './fastmcp-service';
import { AuthService } from './auth-service';
import { ExternalIntegrationsService } from './integrations-service';

export interface AppContext {
  config: AppConfig;
  logger: Logger;
  airtable: AirtableClient;
  governance: GovernanceService;
  exceptions: ExceptionStore;
  fastmcp: FastMCPService;
  auth: AuthService;
  integrations: ExternalIntegrationsService;
}
