/**
 * Types and interfaces for Natural Language Processing in Airtable MCP TypeScript
 */

export enum IntentType {
  LIST_BASES = 'list_bases',
  LIST_RECORDS = 'list_records',
  CREATE_RECORD = 'create_record',
  UPDATE_RECORD = 'update_record',
  DELETE_RECORD = 'delete_record',
  SEARCH_RECORDS = 'search_records',
  LIST_TABLES = 'list_tables',
  GET_RECORD = 'get_record',
  CREATE_WEBHOOK = 'create_webhook',
  LIST_WEBHOOKS = 'list_webhooks',
  DELETE_WEBHOOK = 'delete_webhook',
  GET_WEBHOOK_PAYLOADS = 'get_webhook_payloads',
  GET_BASE_SCHEMA = 'get_base_schema',
  DESCRIBE_TABLE = 'describe_table',
  CREATE_TABLE = 'create_table',
  DELETE_TABLE = 'delete_table',
  UPDATE_TABLE = 'update_table',
  CREATE_FIELD = 'create_field',
  DELETE_FIELD = 'delete_field',
  UPDATE_FIELD = 'update_field',
  LIST_FIELD_TYPES = 'list_field_types',
  BATCH_CREATE_RECORDS = 'batch_create_records',
  BATCH_UPDATE_RECORDS = 'batch_update_records',
  BATCH_DELETE_RECORDS = 'batch_delete_records',
  BATCH_UPSERT_RECORDS = 'batch_upsert_records',
  UPLOAD_ATTACHMENT = 'upload_attachment',
  LIST_COLLABORATORS = 'list_collaborators',
  LIST_SHARES = 'list_shares',
  CREATE_VIEW = 'create_view',
  GET_VIEW_METADATA = 'get_view_metadata',
  GET_TABLE_VIEWS = 'get_table_views',
  CREATE_BASE = 'create_base',
  ANALYZE_DATA = 'analyze_data',
  CREATE_REPORT = 'create_report',
  DATA_INSIGHTS = 'data_insights',
  OPTIMIZE_WORKFLOW = 'optimize_workflow',
  SMART_SCHEMA_DESIGN = 'smart_schema_design',
  DATA_QUALITY_AUDIT = 'data_quality_audit',
  PREDICTIVE_ANALYTICS = 'predictive_analytics',
  NATURAL_LANGUAGE_QUERY = 'natural_language_query',
  SMART_DATA_TRANSFORMATION = 'smart_data_transformation',
  AUTOMATION_RECOMMENDATIONS = 'automation_recommendations',
  UNKNOWN = 'unknown'
}

export interface NaturalLanguageQuery {
  query: string;
  userId?: string;
  sessionId?: string;
  context?: ConversationContext;
  timestamp?: Date;
}

export interface ExtractedEntities {
  tableName?: string;
  recordId?: string;
  fieldName?: string;
  fieldValue?: string;
  fieldType?: string;
  baseId?: string;
  webhookUrl?: string;
  webhookId?: string;
  attachmentUrl?: string;
  priority?: string; // 'Alta', 'Media', 'Baja'
  status?: string;
  dateReference?: string;
  count?: number;
  fieldNames?: string[];
  viewName?: string;
  permissions?: string;
  shareUrl?: string;
  extra?: Record<string, any>;
}

export interface QueryParameters {
  table?: string;
  baseId?: string;
  recordId?: string;
  fields?: Record<string, any>;
  filterByFormula?: string;
  maxRecords?: number;
  sort?: Array<{ field: string; direction: 'asc' | 'desc' }>;
  view?: string;
  webhookConfig?: Record<string, any>;
  attachmentData?: Record<string, any>;
  extra?: Record<string, any>;
}

export interface PreviousQuery {
  query: string;
  intent: IntentType;
  timestamp: Date;
  result?: any;
}

export interface MentionedEntities {
  tables: string[];
  fields: string[];
  records: string[];
}

export interface ConversationPreferences {
  language: string; // 'es' or 'en'
  dateFormat: string; // 'YYYY-MM-DD'
  responseFormat: string; // 'natural' or 'structured'
}


export interface ConversationContext {
  sessionId: string;
  userId: string;
  currentBaseId: string | null;
  currentTable: string | null;
  currentRecordId: string | null;
  previousQueries: PreviousQuery[];
  mentionedEntities: MentionedEntities;
  preferences: ConversationPreferences;
}

export enum ClarificationType {
  MISSING_TABLE = 'missing_table',
  MISSING_FIELD = 'missing_field',
  MISSING_VALUE = 'missing_value',
  AMBIGUOUS_REFERENCE = 'ambiguous_reference',
  PERMISSION_ISSUE = 'permission_issue'
}

export interface Clarification {
  question: string;
  type: ClarificationType;
  suggestions?: string[];
  required: boolean;
}

export interface ProcessedQuery {
  intent: IntentType;
  entities: ExtractedEntities;
  parameters: QueryParameters;
  confidence: number;
  requiresClarification: boolean;
  clarifications?: Clarification[];
}

export interface NaturalLanguageResponse {
  success: boolean;
  message: string;
  intent: IntentType;
  confidence: number;
  data?: any;
  clarifications?: Clarification[];
  metadata?: Record<string, any>;
}

export interface NLPConfig {
  confidenceThreshold: number;
  maxContextQueries: number;
  enableDateProcessing: boolean;
  enableContextualReferences: boolean;
  supportedLanguages: string[];
  synonyms: Record<string, string[]>;
  entityPatterns: Record<string, string[]>;
  datePatterns: string[];
  prioritySynonyms: Record<string, string>;
}

export enum DateFormat {
  RELATIVE = 'relative',
  ABSOLUTE = 'absolute',
  INVALID = 'invalid'
}

export enum RelativeType {
  PAST = 'past',
  FUTURE = 'future'
}

export enum RelativeUnit {
  DAYS = 'days',
  WEEKS = 'weeks',
  MONTHS = 'months',
  YEARS = 'years'
}

export interface DateProcessingResult {
  originalText: string;
  processedDate?: string;
  confidence: number;
  format: DateFormat;
  relativeType?: RelativeType;
  relativeValue?: number;
  relativeUnit?: RelativeUnit;
}

export interface ContextReference {
  referenceType: string; // 'table', 'field', 'record', 'base'
  reference: string;
  resolved: boolean;
  alternatives?: string[];
  confidence: number;
}

export interface ValidationRule {
  parameter: string;
  validationType: string; // 'required', 'optional', 'conditional'
  errorMessage: string;
  validationFunc?: (value: any) => boolean;
}

export enum ValidationSeverity {
  ERROR = 'error',
  CRITICAL = 'critical'
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
  severity: ValidationSeverity;
}

export interface ValidationWarning {
  field: string;
  message: string;
  code: string;
  suggestion?: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  suggestions: string[];
}

export enum SentimentType {
  POSITIVE = 'positive',
  NEGATIVE = 'negative',
  NEUTRAL = 'neutral'
}

export enum UrgencyLevel {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low'
}

export enum QueryComplexity {
  SIMPLE = 'simple',
  MODERATE = 'moderate',
  COMPLEX = 'complex'
}

export enum QueryType {
  ACTION = 'action',
  QUESTION = 'question',
  REQUEST = 'request',
  UNKNOWN = 'unknown'
}

export interface SemanticAnalysis {
  confidence: number;
  entities: string[];
  actions: string[];
  context: string[];
  sentiment: SentimentType;
  urgency: UrgencyLevel;
  keywords: string[];
  queryType: QueryType;
  complexity: QueryComplexity;
}

