"""
Main natural language processor that orchestrates all NLP components
"""

import logging
from typing import Optional, Dict, Any
from .types import (
    NaturalLanguageQuery,
    ProcessedQuery,
    NaturalLanguageResponse,
    IntentType,
    ExtractedEntities,
    QueryParameters,
    ConversationContext,
    Clarification,
    ClarificationType,
    NLPConfig
)
from .intent_mapper import IntentMapper
from .context_handler import ContextHandler
from .date_processor import DateProcessor
from .semantic_analyzer import SemanticAnalyzer
from .validation_engine import ValidationEngine

class NaturalLanguageProcessor:
    def __init__(self, config: NLPConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        self.intent_mapper = IntentMapper()
        self.context_handler = ContextHandler(max_context_queries=config.max_context_queries)
        self.date_processor = DateProcessor()
        self.semantic_analyzer = SemanticAnalyzer()
        self.validation_engine = ValidationEngine()

    async def process_query(self, nl_query: NaturalLanguageQuery) -> ProcessedQuery:
        """
        Main method to process natural language queries
        """
        self.logger.info(f"Processing query: {nl_query.query}")
        
        # Get or create context
        context = await self.context_handler.get_context(
            nl_query.session_id or 'default',
            nl_query.user_id or 'anonymous'
        )
        
        try:
            # Perform semantic analysis
            semantic_analysis = await self.semantic_analyzer.analyze(nl_query.query, context)
            self.logger.info(f"Semantic analysis confidence: {semantic_analysis.confidence}")
            
            # Map intent
            intent = await self.intent_mapper.map_intent(nl_query.query, semantic_analysis, context)
            self.logger.info(f"Mapped intent: {intent}")
            
            # Extract entities
            entities = await self._extract_entities(nl_query.query, context, semantic_analysis)
            self.logger.info(f"Extracted entities: {entities}")
            
            # Build parameters
            parameters = await self._build_parameters(nl_query.query, entities, context)
            
            # Validate parameters
            validation_result = await self.validation_engine.validate(intent, parameters, context)
            
            # Check if clarification is needed
            requires_clarification, clarifications = self._check_clarification_needed(
                intent, entities, validation_result, context
            )
            
            # Update context with this query
            await self.context_handler.update_context(
                nl_query.session_id or 'default',
                {
                    'query': nl_query.query,
                    'intent': intent,
                    'timestamp': nl_query.timestamp,
                    'entities': entities,
                    'result': None  # Will be updated later
                }
            )
            
            return ProcessedQuery(
                intent=intent,
                entities=entities,
                parameters=parameters,
                confidence=semantic_analysis.confidence,
                requires_clarification=requires_clarification,
                clarifications=clarifications if requires_clarification else None
            )
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            # Return fallback result
            return ProcessedQuery(
                intent=IntentType.UNKNOWN,
                entities=ExtractedEntities(),
                parameters=QueryParameters(),
                confidence=0.0,
                requires_clarification=False
            )

    async def _extract_entities(
        self, 
        query: str, 
        context: ConversationContext, 
        semantic_analysis
    ) -> ExtractedEntities:
        """Extract entities from query"""
        entities = ExtractedEntities()
        
        # Extract table names
        table_matches = self._extract_table_names(query)
        if table_matches:
            entities.table_name = table_matches[0]
            if not entities.table_name in context.mentioned_entities.tables:
                context.mentioned_entities.tables.append(entities.table_name)
        else:
            # Use context reference
            if 'esa tabla' in query or 'la tabla' in query or 'esta tabla' in query:
                reference = await self.context_handler.resolve_reference(
                    context.session_id, 'esa tabla', 'table'
                )
                if reference.resolved:
                    entities.table_name = reference.reference

        # Extract record IDs
        record_matches = self._extract_record_ids(query)
        if record_matches:
            entities.record_id = record_matches[0]

        # Extract field names
        field_matches = self._extract_field_names(query)
        if field_matches:
            entities.field_name = field_matches[0]
            if not entities.field_name in context.mentioned_entities.fields:
                context.mentioned_entities.fields.append(entities.field_name)

        # Extract priority
        priority = self._extract_priority(query)
        if priority:
            entities.priority = priority

        # Extract status
        status = self._extract_status(query)
        if status:
            entities.status = status

        # Extract date references
        if self.config.enable_date_processing:
            date_result = await self.date_processor.process_date_reference(query)
            if date_result.confidence > 0.5:
                entities.date_reference = date_result.processed_date

        # Extract count
        count = self._extract_count(query)
        if count:
            entities.count = count

        # Extract field names
        entities.field_names = self._extract_field_names(query)

        return entities

    def _extract_table_names(self, query: str) -> list:
        """Extract table names from query"""
        import re
        patterns = [
            r'en\s+la\s+tabla\s+([A-Za-záéíóúñÑ][\w\s]+)',
            r'tabla\s+([A-Za-záéíóúñÑ][\w\s]+)',
            r'de\s+la\s+tabla\s+([A-Za-záéíóúñÑ][\w\s]+)'
        ]
        
        tables = []
        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                table_name = match.strip()
                if table_name and len(table_name) > 0:
                    tables.append(table_name)
        
        return tables

    def _extract_record_ids(self, query: str) -> list:
        """Extract record IDs from query"""
        import re
        patterns = [
            r'registro\s+([a-zA-Z0-9]+)',
            r'ID\s+([a-zA-Z0-9]+)',
            r'rec([a-zA-Z0-9]+)'
        ]
        
        ids = []
        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            ids.extend(matches)
        
        return ids

    def _extract_field_names(self, query: str) -> list:
        """Extract field names from query"""
        import re
        patterns = [
            r'campo\s+([A-Za-záéíóúñÑ][\w\s]+)',
            r'([A-Za-záéíóúñÑ][\w\s]+)\s+y\s+([A-Za-záéíóúñÑ][\w\s]+)',  # Multiple fields
        ]
        
        fields = []
        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if isinstance(matches[0], tuple) if matches else False:
                fields.extend([match.strip() for match in matches[0] if match.strip()])
            else:
                fields.extend([match.strip() for match in matches if match.strip()])
        
        return list(set(fields))  # Remove duplicates

    def _extract_priority(self, query: str) -> Optional[str]:
        """Extract priority level from query"""
        priority_words = {
            'alta': 'Alta',
            'media': 'Media',
            'baja': 'Baja',
            'alta prioridad': 'Alta',
            'media prioridad': 'Media',
            'baja prioridad': 'Baja',
            'high priority': 'Alta',
            'medium priority': 'Media',
            'low priority': 'Baja'
        }
        
        query_lower = query.lower()
        for word, priority in priority_words.items():
            if word in query_lower:
                return priority
        
        return None

    def _extract_status(self, query: str) -> Optional[str]:
        """Extract status from query"""
        status_words = [
            'activo', 'completado', 'archivado', 'pendiente', 'en progreso',
            'active', 'completed', 'archived', 'pending', 'in progress'
        ]
        
        query_lower = query.lower()
        for status in status_words:
            if status in query_lower:
                return status.title()
        
        return None

    def _extract_count(self, query: str) -> Optional[int]:
        """Extract count from query"""
        import re
        match = re.search(r'(\d+)', query)
        if match:
            return int(match.group(1))
        return None

    async def _build_parameters(
        self, 
        query: str, 
        entities: ExtractedEntities, 
        context: ConversationContext
    ) -> QueryParameters:
        """Build parameters for tool execution"""
        parameters = QueryParameters()
        
        # Set table if available
        if entities.table_name:
            parameters.table = entities.table_name
        elif context.current_table:
            parameters.table = context.current_table

        # Set record ID if available
        if entities.record_id:
            parameters.record_id = entities.record_id
        elif context.current_record_id:
            parameters.record_id = context.current_record_id

        # Build fields based on extracted information
        fields = {}
        
        if entities.field_name and entities.field_value:
            fields[entities.field_name] = entities.field_value
        
        if entities.priority:
            fields['Prioridad'] = entities.priority
        
        if entities.status:
            fields['Estado'] = entities.status
        
        if entities.date_reference:
            fields['Fecha de Vencimiento'] = entities.date_reference
        
        if fields:
            parameters.fields = fields

        # Set max records if count is available
        if entities.count:
            parameters.max_records = entities.count

        # Set webhook config if needed
        if 'webhook' in query.lower() and 'https://' in query:
            import re
            url_match = re.search(r'https?://[^\s]+', query)
            if url_match:
                parameters.webhook_config = {
                    'notificationUrl': url_match.group(0)
                }

        # Set attachment data if needed
        if 'adjuntar' in query.lower() and 'https://' in query:
            import re
            url_match = re.search(r'https?://[^\s]+', query)
            if url_match:
                parameters.attachment_data = {
                    'url': url_match.group(0)
                }

        return parameters

    def _check_clarification_needed(
        self, 
        intent: IntentType, 
        entities: ExtractedEntities, 
        validation_result, 
        context: ConversationContext
    ) -> tuple[bool, list]:
        """Check if clarification is needed"""
        clarifications = []
        
        # Check validation errors
        if not validation_result.is_valid:
            for error in validation_result.errors:
                if error.field == 'table' and not entities.table_name:
                    clarifications.append(Clarification(
                        question="¿En qué tabla quieres realizar esta operación?",
                        type=ClarificationType.MISSING_TABLE,
                        suggestions=context.mentioned_entities.tables[:3] if context.mentioned_entities.tables else None,
                        required=True
                    ))
                
                elif error.field == 'record_id' and not entities.record_id:
                    clarifications.append(Clarification(
                        question="¿Cuál es el ID del registro que quieres modificar?",
                        type=ClarificationType.MISSING_VALUE,
                        required=True
                    ))
        
        # Check contextual references
        if any(ref in context.session_id.lower() for ref in ['esa tabla', 'ese registro']) and not entities.table_name:
            clarifications.append(Clarification(
                question="¿A qué tabla te refieres con 'esa tabla'?",
                type=ClarificationType.AMBIGUOUS_REFERENCE,
                suggestions=context.mentioned_entities.tables[:3] if context.mentioned_entities.tables else None,
                required=False
            ))

        return len(clarifications) > 0, clarifications

    async def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of current conversation context"""
        return await self.context_handler.get_current_entities(session_id)

    async def clear_context(self, session_id: str) -> None:
        """Clear conversation context"""
        await self.context_handler.clear_context(session_id)

