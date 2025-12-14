"""
Types and interfaces for Natural Language Processing in Airtable MCP Python
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

class IntentType(Enum):
    """Intent types for natural language processing"""
    LIST_BASES = 'list_bases'
    LIST_RECORDS = 'list_records'
    CREATE_RECORD = 'create_record'
    UPDATE_RECORD = 'update_record'
    DELETE_RECORD = 'delete_record'
    SEARCH_RECORDS = 'search_records'
    LIST_TABLES = 'list_tables'
    GET_RECORD = 'get_record'
    CREATE_WEBHOOK = 'create_webhook'
    LIST_WEBHOOKS = 'list_webhooks'
    DELETE_WEBHOOK = 'delete_webhook'
    GET_WEBHOOK_PAYLOADS = 'get_webhook_payloads'
    GET_BASE_SCHEMA = 'get_base_schema'
    DESCRIBE_TABLE = 'describe_table'
    CREATE_TABLE = 'create_table'
    DELETE_TABLE = 'delete_table'
    UPDATE_TABLE = 'update_table'
    CREATE_FIELD = 'create_field'
    DELETE_FIELD = 'delete_field'
    UPDATE_FIELD = 'update_field'
    LIST_FIELD_TYPES = 'list_field_types'
    BATCH_CREATE_RECORDS = 'batch_create_records'
    BATCH_UPDATE_RECORDS = 'batch_update_records'
    BATCH_DELETE_RECORDS = 'batch_delete_records'
    BATCH_UPSERT_RECORDS = 'batch_upsert_records'
    UPLOAD_ATTACHMENT = 'upload_attachment'
    LIST_COLLABORATORS = 'list_collaborators'
    LIST_SHARES = 'list_shares'
    CREATE_VIEW = 'create_view'
    GET_VIEW_METADATA = 'get_view_metadata'
    GET_TABLE_VIEWS = 'get_table_views'
    CREATE_BASE = 'create_base'
    ANALYZE_DATA = 'analyze_data'
    CREATE_REPORT = 'create_report'
    DATA_INSIGHTS = 'data_insights'
    OPTIMIZE_WORKFLOW = 'optimize_workflow'
    SMART_SCHEMA_DESIGN = 'smart_schema_design'
    DATA_QUALITY_AUDIT = 'data_quality_audit'
    PREDICTIVE_ANALYTICS = 'predictive_analytics'
    NATURAL_LANGUAGE_QUERY = 'natural_language_query'
    SMART_DATA_TRANSFORMATION = 'smart_data_transformation'
    AUTOMATION_RECOMMENDATIONS = 'automation_recommendations'
    UNKNOWN = 'unknown'

@dataclass
class NaturalLanguageQuery:
    """Input for natural language processing"""
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional['ConversationContext'] = None
    timestamp: Optional[Any] = None

@dataclass
class ExtractedEntities:
    """Entities extracted from natural language query"""
    table_name: Optional[str] = None
    record_id: Optional[str] = None
    field_name: Optional[str] = None
    field_value: Optional[str] = None
    field_type: Optional[str] = None
    base_id: Optional[str] = None
    webhook_url: Optional[str] = None
    webhook_id: Optional[str] = None
    attachment_url: Optional[str] = None
    priority: Optional[str] = None  # 'Alta', 'Media', 'Baja'
    status: Optional[str] = None
    date_reference: Optional[str] = None
    count: Optional[int] = None
    field_names: Optional[List[str]] = None
    view_name: Optional[str] = None
    permissions: Optional[str] = None
    share_url: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QueryParameters:
    """Parameters for executing Airtable operations"""
    table: Optional[str] = None
    base_id: Optional[str] = None
    record_id: Optional[str] = None
    fields: Optional[Dict[str, Any]] = None
    filter_by_formula: Optional[str] = None
    max_records: Optional[int] = None
    sort: Optional[List[Dict[str, str]]] = None
    view: Optional[str] = None
    webhook_config: Optional[Dict[str, Any]] = None
    attachment_data: Optional[Dict[str, Any]] = None
    extra: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PreviousQuery:
    """Previous query in conversation context"""
    query: str
    intent: IntentType
    timestamp: Any
    result: Any

@dataclass
class MentionedEntities:
    """Entities mentioned in conversation"""
    tables: List[str] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    records: List[str] = field(default_factory=list)

@dataclass
class ConversationPreferences:
    """User preferences for conversation"""
    language: str = 'es'  # 'es' or 'en'
    date_format: str = 'YYYY-MM-DD'
    response_format: str = 'natural'  # 'natural' or 'structured'

@dataclass
class ConversationContext:
    """Context for maintaining conversation state"""
    session_id: str
    user_id: str
    current_base_id: Optional[str] = None
    current_table: Optional[str] = None
    current_record_id: Optional[str] = None
    previous_queries: List[PreviousQuery] = field(default_factory=list)
    mentioned_entities: MentionedEntities = field(default_factory=MentionedEntities)
    preferences: ConversationPreferences = field(default_factory=ConversationPreferences)

class ClarificationType(Enum):
    """Types of clarifications that might be needed"""
    MISSING_TABLE = 'missing_table'
    MISSING_FIELD = 'missing_field'
    MISSING_VALUE = 'missing_value'
    AMBIGUOUS_REFERENCE = 'ambiguous_reference'
    PERMISSION_ISSUE = 'permission_issue'

@dataclass
class Clarification:
    """Clarification needed from user"""
    question: str
    type: ClarificationType
    suggestions: Optional[List[str]] = None
    required: bool = True

@dataclass
class ProcessedQuery:
    """Result of natural language processing"""
    intent: IntentType
    entities: ExtractedEntities
    parameters: QueryParameters
    confidence: float
    requires_clarification: bool
    clarifications: Optional[List[Clarification]] = None

@dataclass
class NaturalLanguageResponse:
    """Response from natural language processing"""
    success: bool
    message: str
    intent: IntentType
    confidence: float
    data: Optional[Any] = None
    clarifications: Optional[List[Clarification]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class NLPConfig:
    """Configuration for NLP processing"""
    confidence_threshold: float = 0.5
    max_context_queries: int = 10
    enable_date_processing: bool = True
    enable_contextual_references: bool = True
    supported_languages: List[str] = field(default_factory=lambda: ['es', 'en'])
    synonyms: Dict[str, List[str]] = field(default_factory=dict)
    entity_patterns: Dict[str, List[str]] = field(default_factory=dict)
    date_patterns: List[str] = field(default_factory=list)
    priority_synonyms: Dict[str, str] = field(default_factory=lambda: {
        'alta': 'Alta',
        'media': 'Media', 
        'baja': 'Baja',
        'alta prioridad': 'Alta',
        'baja prioridad': 'Baja'
    })

class DateFormat(Enum):
    """Date format types"""
    RELATIVE = 'relative'
    ABSOLUTE = 'absolute'
    INVALID = 'invalid'

class RelativeType(Enum):
    """Relative time types"""
    PAST = 'past'
    FUTURE = 'future'

class RelativeUnit(Enum):
    """Relative time units"""
    DAYS = 'days'
    WEEKS = 'weeks'
    MONTHS = 'months'
    YEARS = 'years'

@dataclass
class DateProcessingResult:
    """Result of date processing"""
    original_text: str
    processed_date: Optional[str]
    confidence: float
    format: DateFormat
    relative_type: Optional[RelativeType] = None
    relative_value: Optional[int] = None
    relative_unit: Optional[RelativeUnit] = None

@dataclass
class ContextReference:
    """Reference resolution result"""
    reference_type: str  # 'table', 'field', 'record', 'base'
    reference: str
    resolved: bool
    alternatives: Optional[List[str]] = None
    confidence: float = 0.0

@dataclass
class ValidationRule:
    """Validation rule for parameters"""
    parameter: str
    validation_type: str  # 'required', 'optional', 'conditional'
    error_message: str
    validation_func: Optional[callable] = None

class ValidationSeverity(Enum):
    """Validation error severity"""
    ERROR = 'error'
    CRITICAL = 'critical'

@dataclass
class ValidationError:
    """Validation error"""
    field: str
    message: str
    code: str
    severity: ValidationSeverity

@dataclass
class ValidationWarning:
    """Validation warning"""
    field: str
    message: str
    code: str
    suggestion: Optional[str] = None

@dataclass
class ValidationResult:
    """Result of validation"""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationWarning] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

class SentimentType(Enum):
    """Sentiment analysis results"""
    POSITIVE = 'positive'
    NEGATIVE = 'negative'
    NEUTRAL = 'neutral'

class UrgencyLevel(Enum):
    """Urgency levels"""
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

class QueryComplexity(Enum):
    """Query complexity levels"""
    SIMPLE = 'simple'
    MODERATE = 'moderate'
    COMPLEX = 'complex'

class QueryType(Enum):
    """Types of queries"""
    ACTION = 'action'
    QUESTION = 'question'
    REQUEST = 'request'
    UNKNOWN = 'unknown'

@dataclass
class SemanticAnalysis:
    """Result of semantic analysis"""
    confidence: float
    entities: List[str]
    actions: List[str]
    context: List[str]
    sentiment: SentimentType
    urgency: UrgencyLevel
    keywords: List[str] = field(default_factory=list)
    query_type: QueryType = QueryType.UNKNOWN
    complexity: QueryComplexity = QueryComplexity.SIMPLE

