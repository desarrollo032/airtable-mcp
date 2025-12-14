"""
Context handler for maintaining conversational state and resolving references
"""

from typing import Dict, List, Optional, Any
from .types import (
    ConversationContext, 
    ContextReference, 
    MentionedEntities, 
    ConversationPreferences,
    PreviousQuery
)

class ContextHandler:
    def __init__(self, max_context_queries: int = 10):
        self.contexts: Dict[str, ConversationContext] = {}
        self.max_context_queries = max_context_queries

    async def get_context(self, session_id: str, user_id: str) -> ConversationContext:
        """Get or create context for a session"""
        context_key = f"{user_id}:{session_id}"
        
        if context_key not in self.contexts:
            self.contexts[context_key] = self._create_new_context(session_id, user_id)

        return self.contexts[context_key]

    async def update_context(
        self, 
        session_id: str, 
        update: Dict[str, Any]
    ) -> None:
        """Update context with new query information"""
        context_key = f"anonymous:{session_id}"  # Simplified for now
        
        if context_key not in self.contexts:
            return  # No context to update

        context = self.contexts[context_key]
        
        # Add to query history
        previous_query = PreviousQuery(
            query=update.get('query', ''),
            intent=update.get('intent'),
            timestamp=update.get('timestamp'),
            result=update.get('result', None)
        )
        context.previous_queries.append(previous_query)

        # Keep only recent queries
        if len(context.previous_queries) > self.max_context_queries:
            context.previous_queries = context.previous_queries[-self.max_context_queries:]

        # Update mentioned entities
        entities = update.get('entities', {})
        if entities.get('table_name'):
            if entities['table_name'] not in context.mentioned_entities.tables:
                context.mentioned_entities.tables.append(entities['table_name'])
            context.current_table = entities['table_name']

        if entities.get('record_id'):
            context.current_record_id = entities['record_id']
            if entities['record_id'] not in context.mentioned_entities.records:
                context.mentioned_entities.records.append(entities['record_id'])

        if entities.get('base_id'):
            context.current_base_id = entities['base_id']

        # Update preferences if detected
        query = update.get('query', '')
        if 'español' in query or 'en español' in query:
            context.preferences.language = 'es'
        elif 'english' in query or 'en inglés' in query:
            context.preferences.language = 'en'

    async def resolve_reference(
        self, 
        session_id: str, 
        reference: str, 
        reference_type: str
    ) -> ContextReference:
        """Resolve contextual references like 'esa tabla' or 'ese registro'"""
        context_key = f"anonymous:{session_id}"
        context = self.contexts.get(context_key)

        if not context:
            return ContextReference(
                reference_type=reference_type,
                reference=reference,
                resolved=False,
                confidence=0.0
            )

        # Resolve specific references
        if reference_type == 'table':
            if reference in ['esa tabla', 'la tabla', 'esta tabla']:
                if context.current_table:
                    return ContextReference(
                        reference_type='table',
                        reference=context.current_table,
                        resolved=True,
                        confidence=0.9,
                        alternatives=context.mentioned_entities.tables
                    )

            # Search in recent queries
            for query_data in reversed(context.previous_queries):
                if context.current_table:
                    return ContextReference(
                        reference_type='table',
                        reference=context.current_table,
                        resolved=True,
                        confidence=0.7,
                        alternatives=context.mentioned_entities.tables
                    )

        elif reference_type == 'record':
            if reference in ['ese registro', 'el registro', 'este registro']:
                if context.current_record_id:
                    return ContextReference(
                        reference_type='record',
                        reference=context.current_record_id,
                        resolved=True,
                        confidence=0.9
                    )

        elif reference_type == 'base':
            if reference in ['esta base', 'la base']:
                if context.current_base_id:
                    return ContextReference(
                        reference_type='base',
                        reference=context.current_base_id,
                        resolved=True,
                        confidence=0.9
                    )

        # If cannot resolve, return original reference with alternatives
        return ContextReference(
            reference_type=reference_type,
            reference=reference,
            resolved=False,
            confidence=0.0,
            alternatives=self._get_alternatives(reference_type, context)
        )

    def _create_new_context(self, session_id: str, user_id: str) -> ConversationContext:
        """Create a new conversation context"""
        return ConversationContext(
            session_id=session_id,
            user_id=user_id,
            current_base_id=None,
            current_table=None,
            current_record_id=None,
            previous_queries=[],
            mentioned_entities=MentionedEntities(),
            preferences=ConversationPreferences()
        )

    def _get_alternatives(self, reference_type: str, context: ConversationContext) -> List[str]:
        """Get alternative references for unresolved references"""
        if reference_type == 'table':
            return context.mentioned_entities.tables
        elif reference_type == 'field':
            return context.mentioned_entities.fields
        elif reference_type == 'record':
            return context.mentioned_entities.records
        elif reference_type == 'base':
            return [context.current_base_id] if context.current_base_id else []
        return []

    async def clear_context(self, session_id: str) -> None:
        """Clear context for a session"""
        context_key = f"anonymous:{session_id}"
        self.contexts.pop(context_key, None)

    async def get_context_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get query history for a session"""
        context_key = f"anonymous:{session_id}"
        context = self.contexts.get(context_key)
        return [
            {
                'query': pq.query,
                'intent': pq.intent.value,
                'timestamp': pq.timestamp,
                'result': pq.result
            }
            for pq in context.previous_queries
        ] if context else []

    async def get_current_entities(self, session_id: str) -> Dict[str, Any]:
        """Get current entities mentioned in conversation"""
        context_key = f"anonymous:{session_id}"
        context = self.contexts.get(context_key)
        
        if not context:
            return {
                'current_table': None,
                'current_record_id': None,
                'current_base_id': None,
                'mentioned_tables': [],
                'mentioned_fields': [],
                'mentioned_records': []
            }

        return {
            'current_table': context.current_table,
            'current_record_id': context.current_record_id,
            'current_base_id': context.current_base_id,
            'mentioned_tables': context.mentioned_entities.tables,
            'mentioned_fields': context.mentioned_entities.fields,
            'mentioned_records': context.mentioned_entities.records,
            'recent_queries': context.previous_queries[-3:]  # Last 3 queries
        }

    async def set_current_table(self, session_id: str, table_name: str) -> None:
        """Set the current table for context"""
        context_key = f"anonymous:{session_id}"
        context = self.contexts.get(context_key) or self._create_new_context(session_id, 'anonymous')
        
        context.current_table = table_name
        if table_name not in context.mentioned_entities.tables:
            context.mentioned_entities.tables.append(table_name)
        
        self.contexts[context_key] = context

    async def set_current_record(self, session_id: str, record_id: str) -> None:
        """Set the current record for context"""
        context_key = f"anonymous:{session_id}"
        context = self.contexts.get(context_key) or self._create_new_context(session_id, 'anonymous')
        
        context.current_record_id = record_id
        if record_id not in context.mentioned_entities.records:
            context.mentioned_entities.records.append(record_id)
        
        self.contexts[context_key] = context

    async def set_current_base(self, session_id: str, base_id: str) -> None:
        """Set the current base for context"""
        context_key = f"anonymous:{session_id}"
        context = self.contexts.get(context_key) or self._create_new_context(session_id, 'anonymous')
        
        context.current_base_id = base_id
        self.contexts[context_key] = context

