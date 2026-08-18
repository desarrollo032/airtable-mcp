"""
Natural Language Processing tool for Airtable MCP Python
"""

import logging
import json
from typing import Any, Dict, Optional
from ..nlp import (
    NaturalLanguageProcessor,
    NLPConfig,
    NaturalLanguageQuery,
    ProcessedQuery,
    NaturalLanguageResponse,
    IntentType
)

class NaturalLanguageTool:
    def __init__(self, airtable_service, logger: Optional[logging.Logger] = None):
        self.service = airtable_service
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize NLP processor
        nlp_config = NLPConfig(
            confidence_threshold=0.5,
            max_context_queries=10,
            enable_date_processing=True,
            enable_contextual_references=True,
            supported_languages=['es', 'en'],
            synonyms={
                'crear': ['nuevo', 'añadir', 'agregar', 'insertar'],
                'mostrar': ['listar', 'ver', 'obtener', 'mostrarme'],
                'actualizar': ['modificar', 'cambiar', 'editar'],
                'eliminar': ['borrar', 'suprimir', 'remover'],
                'buscar': ['filtrar', 'encontrar', 'buscar']
            },
            priority_synonyms={
                'alta': 'Alta',
                'media': 'Media',
                'baja': 'Baja',
                'alta prioridad': 'Alta',
                'baja prioridad': 'Baja'
            }
        )
        
        self.processor = NaturalLanguageProcessor(nlp_config, self.logger)

    async def process_natural_language_query(
        self, 
        query: str, 
        session_id: str = 'default', 
        user_id: str = 'anonymous'
    ) -> Dict[str, Any]:
        """
        Main method to process natural language queries
        """
        start_time = self.logger.info(f"Processing NLP query: {query}")
        
        try:
            # Create natural language query
            nl_query = NaturalLanguageQuery(
                query=query.strip(),
                session_id=session_id,
                user_id=user_id
            )

            # Process the query
            processed_query = await self.processor.process_query(nl_query)
            
            # Check if clarification is needed
            if processed_query.requires_clarification:
                response = NaturalLanguageResponse(
                    success=False,
                    message="Necesito más información para procesar tu consulta.",
                    intent=processed_query.intent,
                    confidence=processed_query.confidence,
                    clarifications=processed_query.clarifications,
                    metadata={
                        'processing_time': 0,  # Will be calculated
                        'context_used': True,
                        'fallback_used': False
                    }
                )
                return self._response_to_dict(response)

            # Execute the corresponding tool
            tool_result = await self._execute_corresponding_tool(processed_query)
            
            # Create natural language response
            response = NaturalLanguageResponse(
                success=True,
                data=tool_result,
                message=self._generate_natural_language_response(
                    processed_query.intent, tool_result, query
                ),
                intent=processed_query.intent,
                confidence=processed_query.confidence,
                metadata={
                    'processing_time': 0,  # Will be calculated
                    'context_used': True,
                    'fallback_used': False
                }
            )

            return self._response_to_dict(response)

        except Exception as e:
            self.logger.error(f"Error processing natural language query: {e}")
            
            error_response = NaturalLanguageResponse(
                success=False,
                message=f"Lo siento, ocurrió un error al procesar tu consulta: {str(e)}",
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                metadata={
                    'processing_time': 0,
                    'context_used': False,
                    'fallback_used': True
                }
            )
            return self._response_to_dict(error_response)

    async def _execute_corresponding_tool(self, processed_query: ProcessedQuery) -> Dict[str, Any]:
        """Execute the tool corresponding to the processed intent"""
        intent = processed_query.intent
        parameters = processed_query.parameters

        # Map intent to tool execution
        try:
            if intent == IntentType.LIST_BASES:
                result = await self.service.list_bases()
                return {'bases': result.get('bases', [])}
            
            elif intent == IntentType.LIST_RECORDS:
                if not parameters.table:
                    raise ValueError("Nombre de tabla requerido")
                result = await self.service.list_records(
                    base_id=parameters.base_id or 'default',
                    table_name=parameters.table,
                    filter_by_formula=parameters.filter_by_formula,
                    max_records=parameters.max_records
                )
                return result
            
            elif intent == IntentType.CREATE_RECORD:
                if not parameters.table or not parameters.fields:
                    raise ValueError("Tabla y campos requeridos")
                result = await self.service.create_record(
                    base_id=parameters.base_id or 'default',
                    table_name=parameters.table,
                    fields=parameters.fields
                )
                return result
            
            elif intent == IntentType.UPDATE_RECORD:
                if not parameters.table or not parameters.record_id or not parameters.fields:
                    raise ValueError("Tabla, ID de registro y campos requeridos")
                result = await self.service.update_record(
                    base_id=parameters.base_id or 'default',
                    table_name=parameters.table,
                    record_id=parameters.record_id,
                    fields=parameters.fields
                )
                return result
            
            elif intent == IntentType.DELETE_RECORD:
                if not parameters.table or not parameters.record_id:
                    raise ValueError("Tabla e ID de registro requeridos")
                result = await self.service.delete_record(
                    base_id=parameters.base_id or 'default',
                    table_name=parameters.table,
                    record_id=parameters.record_id
                )
                return result
            
            elif intent == IntentType.SEARCH_RECORDS:
                if not parameters.table:
                    raise ValueError("Nombre de tabla requerido")
                result = await self.service.list_records(
                    base_id=parameters.base_id or 'default',
                    table_name=parameters.table,
                    filter_by_formula=parameters.filter_by_formula,
                    max_records=parameters.max_records
                )
                return result
            
            elif intent == IntentType.LIST_TABLES:
                result = await self.service.list_tables(
                    base_id=parameters.base_id or 'default'
                )
                return result
            
            elif intent == IntentType.CREATE_WEBHOOK:
                if not parameters.table or not parameters.webhook_config:
                    raise ValueError("Tabla y configuración de webhook requeridas")
                result = await self.service.create_webhook(
                    base_id=parameters.base_id or 'default',
                    table_name=parameters.table,
                    webhook_config=parameters.webhook_config
                )
                return result
            
            elif intent == IntentType.LIST_WEBHOOKS:
                result = await self.service.list_webhooks(
                    base_id=parameters.base_id or 'default'
                )
                return result
            
            elif intent == IntentType.GET_BASE_SCHEMA:
                if not parameters.base_id:
                    raise ValueError("ID de base requerido")
                result = await self.service.get_base_schema(
                    base_id=parameters.base_id
                )
                return result
            
            elif intent == IntentType.DESCRIBE_TABLE:
                if not parameters.table:
                    raise ValueError("Nombre de tabla requerido")
                result = await self.service.describe_table(
                    base_id=parameters.base_id or 'default',
                    table_name=parameters.table
                )
                return result
            
            else:
                # For intents not yet implemented, return a placeholder response
                return {
                    'intent': intent.value,
                    'parameters': parameters.__dict__,
                    'message': f'Operación {intent.value} solicitada pero no implementada completamente',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
        
        except Exception as e:
            self.logger.error(f"Error executing tool for intent {intent}: {e}")
            raise

    def _generate_natural_language_response(
        self, 
        intent: IntentType, 
        result: Dict[str, Any], 
        original_query: str
    ) -> str:
        """Generate natural language response for the operation"""
        responses = {
            IntentType.LIST_BASES: 'He encontrado las siguientes bases Airtable accesibles:',
            IntentType.LIST_RECORDS: 'Aquí están los registros encontrados en la tabla:',
            IntentType.CREATE_RECORD: 'He creado el nuevo registro exitosamente.',
            IntentType.UPDATE_RECORD: 'He actualizado el registro como solicitaste.',
            IntentType.DELETE_RECORD: 'He eliminado el registro especificado.',
            IntentType.SEARCH_RECORDS: 'Aquí están los resultados de tu búsqueda:',
            IntentType.LIST_TABLES: 'Las tablas disponibles en tu base son:',
            IntentType.CREATE_WEBHOOK: 'He creado el webhook correctamente.',
            IntentType.LIST_WEBHOOKS: 'Los webhooks activos en tu base son:',
            IntentType.GET_BASE_SCHEMA: 'El esquema completo de tu base es:',
            IntentType.DESCRIBE_TABLE: 'Los detalles de la tabla solicitada son:',
            IntentType.UNKNOWN: 'No pude entender completamente tu consulta.'
        }

        base_response = responses.get(intent, 'Operación completada.')
        
        # Add specific details based on result
        if intent == IntentType.LIST_BASES and 'bases' in result:
            base_count = len(result['bases'])
            return f"{base_response} Encontré {base_count} bases accesibles."
        
        elif intent == IntentType.LIST_RECORDS and 'records' in result:
            record_count = len(result['records'])
            return f"{base_response} Se encontraron {record_count} registros."
        
        return base_response

    def _response_to_dict(self, response: NaturalLanguageResponse) -> Dict[str, Any]:
        """Convert NaturalLanguageResponse to dictionary"""
        return {
            'success': response.success,
            'data': response.data,
            'message': response.message,
            'intent': response.intent.value,
            'confidence': response.confidence,
            'clarifications': [
                {
                    'question': c.question,
                    'type': c.type.value,
                    'suggestions': c.suggestions,
                    'required': c.required
                }
                for c in (response.clarifications or [])
            ],
            'metadata': response.metadata
        }

    async def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of current conversation context"""
        return await self.processor.get_context_summary(session_id)

    async def clear_context(self, session_id: str) -> None:
        """Clear conversation context"""
        await self.processor.clear_context(session_id)

# MCP Tool Registration Functions
def register_nlp_tools(mcp, service):
    """Register all NLP tools with MCP server"""
    nlp_tool = NaturalLanguageTool(service)
    
    @mcp.tool()
    async def process_natural_language(query: str, session_id: str = 'default', user_id: str = 'anonymous') -> str:
        """Procesa consultas en lenguaje natural español y las ejecuta como operaciones de Airtable"""
        result = await nlp_tool.process_natural_language_query(query, session_id, user_id)
        return json.dumps(result, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def get_nlp_context(session_id: str) -> str:
        """Obtiene el contexto actual de la conversación"""
        context = await nlp_tool.get_context_summary(session_id)
        return json.dumps({
            'success': True,
            'data': context,
            'message': 'Contexto obtenido correctamente'
        }, indent=2, ensure_ascii=False)

    @mcp.tool()
    async def clear_nlp_context(session_id: str) -> str:
        """Limpia el contexto conversacional de una sesión"""
        await nlp_tool.clear_context(session_id)
        return json.dumps({
            'success': True,
            'message': 'Contexto limpiado correctamente'
        }, indent=2, ensure_ascii=False)

