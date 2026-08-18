"""
Intent mapper for translating natural language queries to specific tools
"""

import re
from typing import Dict, List, Optional, Tuple
from .types import IntentType, ExtractedEntities, ConversationContext, SemanticAnalysis

class IntentMapper:
    def __init__(self):
        self.intent_patterns: Dict[IntentType, List[re.Pattern]] = {}
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize regex patterns for intent recognition"""
        
        # Basic operations
        self.intent_patterns[IntentType.LIST_BASES] = [
            re.compile(r'listar\s+(todas\s+mis\s+)?bases\s+airtable\s+accesibles', re.IGNORECASE),
            re.compile(r'mostrarme\s+todas\s+mis\s+bases', re.IGNORECASE),
            re.compile(r'qué\s+bases\s+tengo\s+accesibles', re.IGNORECASE),
            re.compile(r'listar\s+bases', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.LIST_RECORDS] = [
            re.compile(r'mostrarme\s+todos\s+los\s+registros\s+(?:en|en\s+la)\s+tabla\s+\w+', re.IGNORECASE),
            re.compile(r'listar\s+registros\s+(?:de|en)\s+\w+', re.IGNORECASE),
            re.compile(r'ver\s+registros\s+de\s+\w+', re.IGNORECASE),
            re.compile(r'obtener\s+registros\s+de\s+\w+', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.CREATE_RECORD] = [
            re.compile(r'crear\s+(?:una\s+)?nueva\s+tarea', re.IGNORECASE),
            re.compile(r'crear\s+registro\s+nuevo', re.IGNORECASE),
            re.compile(r'agregar\s+registro', re.IGNORECASE),
            re.compile(r'insertar\s+registro', re.IGNORECASE),
            re.compile(r'añadir\s+nuevo\s+registro', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.UPDATE_RECORD] = [
            re.compile(r'actualizar\s+(?:el\s+)?estado\s+de\s+(?:la\s+)?tarea', re.IGNORECASE),
            re.compile(r'cambiar\s+estado\s+de', re.IGNORECASE),
            re.compile(r'modificar\s+registro', re.IGNORECASE),
            re.compile(r'editar\s+registro', re.IGNORECASE),
            re.compile(r'actualizar\s+registro', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.DELETE_RECORD] = [
            re.compile(r'eliminar\s+(?:todos\s+los\s+)?registros\s+donde\s+el\s+estado\s+sea', re.IGNORECASE),
            re.compile(r'borrar\s+registros\s+con\s+estado', re.IGNORECASE),
            re.compile(r'suprimir\s+registros', re.IGNORECASE),
            re.compile(r'eliminar\s+registros', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.SEARCH_RECORDS] = [
            re.compile(r'buscar\s+registros\s+donde\s+\w+\s+sea\s+igual\s+a', re.IGNORECASE),
            re.compile(r'filtrar\s+registros\s+por', re.IGNORECASE),
            re.compile(r'encontrar\s+registros\s+con', re.IGNORECASE),
            re.compile(r'buscar\s+registros\s+que', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.LIST_TABLES] = [
            re.compile(r'qué\s+tablas\s+hay\s+en\s+mi\s+base', re.IGNORECASE),
            re.compile(r'mostrar\s+tablas\s+de\s+la\s+base', re.IGNORECASE),
            re.compile(r'listar\s+tablas', re.IGNORECASE),
            re.compile(r'qué\s+tablas\s+tengo', re.IGNORECASE)
        ]

        # Webhooks
        self.intent_patterns[IntentType.CREATE_WEBHOOK] = [
            re.compile(r'crear\s+un\s+webhook\s+para\s+mi\s+tabla', re.IGNORECASE),
            re.compile(r'crear\s+webhook', re.IGNORECASE),
            re.compile(r'configurar\s+webhook', re.IGNORECASE),
            re.compile(r'establecer\s+webhook', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.LIST_WEBHOOKS] = [
            re.compile(r'listar\s+todos\s+los\s+webhooks\s+activos', re.IGNORECASE),
            re.compile(r'mostrar\s+webhooks', re.IGNORECASE),
            re.compile(r'ver\s+webhooks', re.IGNORECASE),
            re.compile(r'qué\s+webhooks\s+tengo', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.DELETE_WEBHOOK] = [
            re.compile(r'eliminar\s+webhook\s+\w+', re.IGNORECASE),
            re.compile(r'borrar\s+webhook', re.IGNORECASE),
            re.compile(r'remover\s+webhook', re.IGNORECASE)
        ]

        # Schema management
        self.intent_patterns[IntentType.GET_BASE_SCHEMA] = [
            re.compile(r'mostrarme\s+el\s+esquema\s+completo\s+para\s+(?:esta|la)\s+base', re.IGNORECASE),
            re.compile(r'obtener\s+esquema\s+de\s+base', re.IGNORECASE),
            re.compile(r'describir\s+base', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.DESCRIBE_TABLE] = [
            re.compile(r'describir\s+la\s+tabla\s+\w+\s+con\s+todos\s+los\s+detalles\s+de\s+campo', re.IGNORECASE),
            re.compile(r'mostrar\s+estructura\s+de\s+tabla', re.IGNORECASE),
            re.compile(r'ver\s+campos\s+de\s+tabla', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.CREATE_TABLE] = [
            re.compile(r'crear\s+una\s+nueva\s+tabla\s+llamada\s+\w+', re.IGNORECASE),
            re.compile(r'crear\s+tabla\s+nueva', re.IGNORECASE),
            re.compile(r'añadir\s+tabla', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.CREATE_FIELD] = [
            re.compile(r'agregar\s+un\s+campo\s+de\s+\w+\s+a\s+la\s+tabla', re.IGNORECASE),
            re.compile(r'añadir\s+campo', re.IGNORECASE),
            re.compile(r'crear\s+campo', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.LIST_FIELD_TYPES] = [
            re.compile(r'qué\s+tipos\s+de\s+campos\s+están\s+disponibles\s+en\s+airtable', re.IGNORECASE),
            re.compile(r'tipos\s+de\s+campos\s+disponibles', re.IGNORECASE),
            re.compile(r'campos\s+disponibles', re.IGNORECASE)
        ]

        # Batch operations
        self.intent_patterns[IntentType.BATCH_CREATE_RECORDS] = [
            re.compile(r'crear\s+\d+\s+registros\s+nuevos\s+a\s+la\s+vez', re.IGNORECASE),
            re.compile(r'crear\s+múltiples\s+registros', re.IGNORECASE),
            re.compile(r'añadir\s+varios\s+registros', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.BATCH_UPDATE_RECORDS] = [
            re.compile(r'actualizar\s+múltiples\s+registros', re.IGNORECASE),
            re.compile(r'modificar\s+varios\s+registros', re.IGNORECASE),
            re.compile(r'cambiar\s+varios\s+registros', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.BATCH_DELETE_RECORDS] = [
            re.compile(r'eliminar\s+estos\s+\d+\s+registros\s+en\s+una\s+operación', re.IGNORECASE),
            re.compile(r'borrar\s+múltiples\s+registros', re.IGNORECASE),
            re.compile(r'eliminar\s+varios\s+registros', re.IGNORECASE)
        ]

        # Attachments
        self.intent_patterns[IntentType.UPLOAD_ATTACHMENT] = [
            re.compile(r'adjuntar\s+esta\s+url\s+de\s+imagen', re.IGNORECASE),
            re.compile(r'subir\s+archivo', re.IGNORECASE),
            re.compile(r'adjuntar\s+archivo', re.IGNORECASE),
            re.compile(r'añadir\s+adjunto', re.IGNORECASE)
        ]

        # Collaboration
        self.intent_patterns[IntentType.LIST_COLLABORATORS] = [
            re.compile(r'quiénes\s+son\s+los\s+colaboradores\s+en\s+esta\s+base', re.IGNORECASE),
            re.compile(r'mostrar\s+colaboradores', re.IGNORECASE),
            re.compile(r'ver\s+colaboradores', re.IGNORECASE)
        ]

        self.intent_patterns[IntentType.LIST_SHARES] = [
            re.compile(r'mostrarme\s+todas\s+las\s+vistas\s+compartidas\s+en\s+esta\s+base', re.IGNORECASE),
            re.compile(r'ver\s+vistas\s+compartidas', re.IGNORECASE),
            re.compile(r'mostrar\s+compartidos', re.IGNORECASE)
        ]

        # AI operations
        self.intent_patterns[IntentType.ANALYZE_DATA] = [
            re.compile(r'analizar\s+datos\s+de', re.IGNORECASE),
            re.compile(r'analizar\s+tabla', re.IGNORECASE),
            re.compile(r'estudiar\s+datos', re.IGNORECASE)
        ]

    async def map_intent(self, query: str, semantic_analysis: SemanticAnalysis, context: ConversationContext) -> IntentType:
        """
        Map a natural language query to an intent
        """
        # First try direct pattern matching
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern.search(query):
                    return intent

        # If no match, try with context
        if 'esa tabla' in query and context.current_table:
            if any(word in query for word in ['mostrar', 'ver', 'obtener']):
                return IntentType.LIST_RECORDS
            elif any(word in query for word in ['crear', 'añadir']):
                return IntentType.CREATE_RECORD

        if 'ese registro' in query and context.current_record_id:
            if any(word in query for word in ['actualizar', 'cambiar', 'modificar']):
                return IntentType.UPDATE_RECORD
            elif any(word in query for word in ['eliminar', 'borrar']):
                return IntentType.DELETE_RECORD

        # Keyword-based analysis
        action_keywords = ['crear', 'nuevo', 'añadir', 'insertar', 'agregar']
        if any(keyword in query for keyword in action_keywords):
            if 'tabla' in query:
                return IntentType.CREATE_TABLE
            elif 'campo' in query:
                return IntentType.CREATE_FIELD
            else:
                return IntentType.CREATE_RECORD

        display_keywords = ['mostrar', 'listar', 'ver', 'obtener']
        if any(keyword in query for keyword in display_keywords):
            if 'base' in query:
                return IntentType.LIST_BASES
            elif any(word in query for word in ['tabla', 'tablas']):
                return IntentType.LIST_TABLES
            elif 'webhook' in query:
                return IntentType.LIST_WEBHOOKS
            else:
                return IntentType.LIST_RECORDS

        update_keywords = ['actualizar', 'modificar', 'cambiar', 'editar']
        if any(keyword in query for keyword in update_keywords):
            if 'webhook' in query:
                return IntentType.UPDATE_RECORD  # Simplified
            else:
                return IntentType.UPDATE_RECORD

        delete_keywords = ['eliminar', 'borrar', 'suprimir', 'remover']
        if any(keyword in query for keyword in delete_keywords):
            if 'webhook' in query:
                return IntentType.DELETE_WEBHOOK
            else:
                return IntentType.DELETE_RECORD

        return IntentType.UNKNOWN

    def requires_table(self, intent: IntentType) -> bool:
        """Check if intent requires a table parameter"""
        table_required_intents = [
            IntentType.LIST_RECORDS,
            IntentType.CREATE_RECORD,
            IntentType.UPDATE_RECORD,
            IntentType.DELETE_RECORD,
            IntentType.SEARCH_RECORDS,
            IntentType.DESCRIBE_TABLE,
            IntentType.CREATE_FIELD,
            IntentType.CREATE_WEBHOOK,
            IntentType.BATCH_CREATE_RECORDS,
            IntentType.BATCH_UPDATE_RECORDS,
            IntentType.BATCH_DELETE_RECORDS,
            IntentType.UPLOAD_ATTACHMENT
        ]
        return intent in table_required_intents

    def requires_record_id(self, intent: IntentType) -> bool:
        """Check if intent requires a record ID parameter"""
        record_id_required_intents = [
            IntentType.UPDATE_RECORD,
            IntentType.DELETE_RECORD,
            IntentType.GET_RECORD,
            IntentType.UPLOAD_ATTACHMENT
        ]
        return intent in record_id_required_intents

    def get_tool_name(self, intent: IntentType) -> str:
        """Get the corresponding tool name for an intent"""
        tool_mapping = {
            IntentType.LIST_BASES: 'list_bases',
            IntentType.LIST_RECORDS: 'list_records',
            IntentType.CREATE_RECORD: 'create_record',
            IntentType.UPDATE_RECORD: 'update_record',
            IntentType.DELETE_RECORD: 'delete_record',
            IntentType.SEARCH_RECORDS: 'search_records',
            IntentType.LIST_TABLES: 'list_tables',
            IntentType.GET_RECORD: 'get_record',
            IntentType.CREATE_WEBHOOK: 'create_webhook',
            IntentType.LIST_WEBHOOKS: 'list_webhooks',
            IntentType.DELETE_WEBHOOK: 'delete_webhook',
            IntentType.GET_WEBHOOK_PAYLOADS: 'get_webhook_payloads',
            IntentType.GET_BASE_SCHEMA: 'get_base_schema',
            IntentType.DESCRIBE_TABLE: 'describe_table',
            IntentType.CREATE_TABLE: 'create_table',
            IntentType.DELETE_TABLE: 'delete_table',
            IntentType.UPDATE_TABLE: 'update_table',
            IntentType.CREATE_FIELD: 'create_field',
            IntentType.DELETE_FIELD: 'delete_field',
            IntentType.UPDATE_FIELD: 'update_field',
            IntentType.LIST_FIELD_TYPES: 'list_field_types',
            IntentType.BATCH_CREATE_RECORDS: 'batch_create_records',
            IntentType.BATCH_UPDATE_RECORDS: 'batch_update_records',
            IntentType.BATCH_DELETE_RECORDS: 'batch_delete_records',
            IntentType.BATCH_UPSERT_RECORDS: 'batch_upsert_records',
            IntentType.UPLOAD_ATTACHMENT: 'upload_attachment',
            IntentType.LIST_COLLABORATORS: 'list_collaborators',
            IntentType.LIST_SHARES: 'list_shares',
            IntentType.CREATE_VIEW: 'create_view',
            IntentType.GET_VIEW_METADATA: 'get_view_metadata',
            IntentType.GET_TABLE_VIEWS: 'get_table_views',
            IntentType.CREATE_BASE: 'create_base',
            IntentType.ANALYZE_DATA: 'analyze_data',
            IntentType.CREATE_REPORT: 'create_report',
            IntentType.DATA_INSIGHTS: 'data_insights',
            IntentType.OPTIMIZE_WORKFLOW: 'optimize_workflow',
            IntentType.SMART_SCHEMA_DESIGN: 'smart_schema_design',
            IntentType.DATA_QUALITY_AUDIT: 'data_quality_audit',
            IntentType.PREDICTIVE_ANALYTICS: 'predictive_analytics',
            IntentType.NATURAL_LANGUAGE_QUERY: 'natural_language_query',
            IntentType.SMART_DATA_TRANSFORMATION: 'smart_data_transformation',
            IntentType.AUTOMATION_RECOMMENDATIONS: 'automation_recommendations',
            IntentType.UNKNOWN: 'unknown'
        }
        
        return tool_mapping.get(intent, 'unknown')

