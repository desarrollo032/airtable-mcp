import { Logger } from './logger';
import { FastMCPConfig } from './config';

export class FastMCPService {
  private config: FastMCPConfig;
  private logger: Logger;

  constructor(config: FastMCPConfig, logger: Logger) {
    this.config = config;
    this.logger = logger;
  }

  public shouldMaskErrorDetails(): boolean {
    return this.config.maskErrorDetails;
  }

  public shouldValidateStrictly(): boolean {
    return this.config.strictInputValidation;
  }

  public shouldIncludeMeta(): boolean {
    return this.config.includeFastMCPMeta;
  }

  public getLogLevel(): string {
    return this.config.logLevel;
  }

  public getAuthConfig(): {
    serverAuth?: string;
    jwtJwksUri?: string;
    jwtIssuer?: string;
    jwtAudience?: string;
  } {
    return {
      serverAuth: this.config.serverAuth,
      jwtJwksUri: this.config.jwtJwksUri,
      jwtIssuer: this.config.jwtIssuer,
      jwtAudience: this.config.jwtAudience
    };
  }

  public logEvent(event: string, data?: any): void {
    this.logger.info(event, data);
  }

  public logError(error: Error, context?: any): void {
    this.logger.error(error.message, { error, context });
  }
}
