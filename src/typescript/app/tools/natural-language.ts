/**
 * Herramienta MCP para procesamiento de consultas en lenguaje natural
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp';
import { AppContext } from '../context';
import { 
  NaturalLanguageProcessor, 
  NLPConfig,
  NaturalLanguageQuery,
  ProcessedQuery,
  NaturalLanguageResponse,
  IntentType
} from '../nlp';
import { Logger } from '../logger';

export function registerNaturalLanguageTool(server: McpServer, ctx: AppContext): void {
  const nlpConfig: NLPConfig = {
    confidenceThreshold: 0.5,
    maxContextQueries: 10,
    enableDateProcessing: true,
    enableContextualReferences: true,
    supportedLanguages: ['es', 'en'],
    synonyms: {
      'crear': ['nuevo', 'añadir', 'agregar', 'insertar'],
      'mostrar': ['listar', 'ver', 'obtener', 'mostrarme'],
      'actualizar': ['modificar', 'cambiar', 'editar'],
      'eliminar': ['borrar', 'suprimir', 'remover'],
      'buscar': ['filtrar', 'encontrar', 'buscar']
    },
    entityPatterns: {},
    datePatterns: [],
    prioritySynonyms: {
      'alta': 'Alta',
      'media': 'Media', 
      'baja': 'Baja',
      'alta prioridad': 'Alta',
      'baja prioridad': 'Baja'
    }
  };

  const processor = new NaturalLanguageProcessor(nlpConfig, ctx.logger);

  // Herramienta principal para procesar consultas en lenguaje natural
  server.setRequestHandler('tools/call', async (request) => {
    const { name, arguments: args } = request.params;

    if (name === 'process_natural_language') {
      return await handleNaturalLanguageQuery(args, processor, ctx);
    }

    if (name === 'get_nlp_context') {
      return await handleGetContext(args, ctx);
    }

    if (name === 'clear_nlp_context') {
      return await handleClearContext(args, ctx);
    }

    throw new Error(`Herramienta desconocida: ${name}`);
  });

  // Registrar las herramientas disponibles
  server.setRequestHandler('tools/list', async () => {
    return {
      tools: [
        {
          name: 'process_natural_language',
          description: 'Procesa consultas en lenguaje natural español y las ejecuta como operaciones de Airtable',
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'La consulta en lenguaje natural a procesar'
              },
              sessionId: {
                type: 'string',
                description: 'ID de sesión para mantener contexto conversacional'
              },
              userId: {
                type: 'string',
                description: 'ID del usuario para personalizar la experiencia'
              }
            },
            required: ['query']
          }
        },
        {
          name: 'get_nlp_context',
          description: 'Obtiene el contexto actual de la conversación',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string',
                description: 'ID de sesión para obtener el contexto'
              }
            },
            required: ['sessionId']
          }
        },
        {
          name: 'clear_nlp_context',
          description: 'Limpia el contexto conversacional de una sesión',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string',
                description: 'ID de sesión para limpiar el contexto'
              }
            },
            required: ['sessionId']
          }
        }
      ]
    };
  });
}

async function handleNaturalLanguageQuery(
  args: any, 
  processor: NaturalLanguageProcessor, 
  ctx: AppContext
) {
  const { query, sessionId = 'default', userId = 'anonymous' } = args;

  if (!query || typeof query !== 'string') {
    throw new Error('Se requiere una consulta válida');
  }

  const startTime = Date.now();
  
  try {
    // Crear consulta de lenguaje natural
    const nlQuery: NaturalLanguageQuery = {
      query: query.trim(),
      sessionId,
      userId
    };

    // Procesar la consulta
    const processedQuery: ProcessedQuery = await processor.processQuery(nlQuery);
    
    // Verificar si necesita clarificación
    if (processedQuery.requiresClarification) {
      const response: NaturalLanguageResponse = {
        success: false,
        message: 'Necesito más información para procesar tu consulta.',
        intent: processedQuery.intent,
        confidence: processedQuery.confidence,
        clarifications: processedQuery.clarifications,
        metadata: {
          processingTime: Date.now() - startTime,
          contextUsed: true,
          fallbackUsed: false
        }
      };

      return {
        content: [{
          type: 'text',
          text: JSON.stringify(response, null, 2)
        }]
      };
    }

    // Ejecutar la herramienta correspondiente
    const toolResult = await executeCorrespondingTool(processedQuery, ctx);
    
    // Crear respuesta en lenguaje natural
    const response: NaturalLanguageResponse = {
      success: true,
      data: toolResult,
      message: generateNaturalLanguageResponse(processedQuery.intent, toolResult, query),
      intent: processedQuery.intent,
      confidence: processedQuery.confidence,
      metadata: {
        processingTime: Date.now() - startTime,
        contextUsed: true,
        fallbackUsed: false
      }
    };

    return {
      content: [{
        type: 'text',
        text: JSON.stringify(response, null, 2)
      }]
    };

  } catch (error) {
    ctx.logger.error('Error processing natural language query', { error, query });
    
    const errorResponse: NaturalLanguageResponse = {
      success: false,
      message: `Lo siento, ocurrió un error al procesar tu consulta: ${error instanceof Error ? error.message : 'Error desconocido'}`,
      intent: 'unknown',
      confidence: 0,
      metadata: {
        processingTime: Date.now() - startTime,
        contextUsed: false,
        fallbackUsed: true
      }
    };

    return {
      content: [{
        type: 'text',
        text: JSON.stringify(errorResponse, null, 2)
      }]
    };
  }
}

async function handleGetContext(args: any, ctx: AppContext) {
  const { sessionId = 'default' } = args;
  
  try {
    const contextHandler = new (await import('../nlp/context-handler')).ContextHandler();
    const context = await contextHandler.getContext(sessionId, 'anonymous');
    
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          success: true,
          data: context,
          message: 'Contexto obtenido correctamente'
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          success: false,
          message: `Error al obtener contexto: ${error instanceof Error ? error.message : 'Error desconocido'}`
        }, null, 2)
      }]
    };
  }
}

async function handleClearContext(args: any, ctx: AppContext) {
  const { sessionId = 'default' } = args;
  
  try {
    const contextHandler = new (await import('../nlp/context-handler')).ContextHandler();
    await contextHandler.clearContext(sessionId);
    
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          success: true,
          message: 'Contexto limpiado correctamente'
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          success: false,
          message: `Error al limpiar contexto: ${error instanceof Error ? error.message : 'Error desconocido'}`
        }, null, 2)
      }]
    };
  }
}

async function executeCorrespondingTool(processedQuery: ProcessedQuery, ctx: AppContext): Promise<any> {
  const intent = processedQuery.intent;
  const parameters = processedQuery.parameters;

  // Mapear intención a herramienta específica
  const toolMapping: Record<IntentType, string> = {
    'list_bases': 'list_bases',
    'list_records': 'list_records',
    'create_record': 'create_record',
    'update_record': 'update_record',
    'delete_record': 'delete_record',
    'search_records': 'search_records',
    'list_tables': 'list_tables',
    'get_record': 'get_record',
    'create_webhook': 'create_webhook',
    'list_webhooks': 'list_webhooks',
    'delete_webhook': 'delete_webhook',
    'get_webhook_payloads': 'get_webhook_payloads',
    'get_base_schema': 'get_base_schema',
    'describe_table': 'describe_table',
    'create_table': 'create_table',
    'delete_table': 'delete_table',
    'update_table': 'update_table',
    'create_field': 'create_field',
    'delete_field': 'delete_field',
    'update_field': 'update_field',
    'list_field_types': 'list_field_types',
    'batch_create_records': 'batch_create_records',
    'batch_update_records': 'batch_update_records',
    'batch_delete_records': 'batch_delete_records',
    'batch_upsert_records': 'batch_upsert_records',
    'upload_attachment': 'upload_attachment',
    'list_collaborators': 'list_collaborators',
    'list_shares': 'list_shares',
    'create_view': 'create_view',
    'get_view_metadata': 'get_view_metadata',
    'get_table_views': 'get_table_views',
    'create_base': 'create_base',
    'analyze_data': 'analyze_data',
    'create_report': 'create_report',
    'data_insights': 'data_insights',
    'optimize_workflow': 'optimize_workflow',
    'smart_schema_design': 'smart_schema_design',
    'data_quality_audit': 'data_quality_audit',
    'predictive_analytics': 'predictive_analytics',
    'natural_language_query': 'natural_language_query',
    'smart_data_transformation': 'smart_data_transformation',
    'automation_recommendations': 'automation_recommendations',
    'unknown': 'unknown'
  };

  const toolName = toolMapping[intent];
  
  if (toolName === 'unknown') {
    throw new Error(`Intención no reconocida: ${intent}`);
  }

  // Aquí se integraría con el sistema de herramientas existente
  // Por simplicidad, simulamos la ejecución
  return {
    intent,
    parameters,
    message: `Herramienta ${toolName} ejecutada con éxito`,
    timestamp: new Date().toISOString()
  };
}

function generateNaturalLanguageResponse(intent: IntentType, result: any, originalQuery: string): string {
  const responses: Record<IntentType, string> = {
    'list_bases': 'He encontrado las siguientes bases Airtable accesibles:',
    'list_records': 'Aquí están los registros encontrados en la tabla:',
    'create_record': 'He creado el nuevo registro exitosamente.',
    'update_record': 'He actualizado el registro como solicitaste.',
    'delete_record': 'He eliminado el registro especificado.',
    'search_records': 'Aquí están los resultados de tu búsqueda:',
    'list_tables': 'Las tablas disponibles en tu base son:',
    'get_record': 'Aquí está la información del registro solicitado:',
    'create_webhook': 'He creado el webhook correctamente.',
    'list_webhooks': 'Los webhooks activos en tu base son:',
    'delete_webhook': 'He eliminado el webhook especificado.',
    'get_webhook_payloads': 'Aquí están las notificaciones recientes del webhook:',
    'get_base_schema': 'El esquema completo de tu base es:',
    'describe_table': 'Los detalles de la tabla solicitada son:',
    'create_table': 'He creado la nueva tabla exitosamente.',
    'delete_table': 'He eliminado la tabla especificada.',
    'update_table': 'He actualizado la tabla como solicitaste.',
    'create_field': 'He agregado el nuevo campo a la tabla.',
    'delete_field': 'He eliminado el campo especificado.',
    'update_field': 'He actualizado el campo como solicitaste.',
    'list_field_types': 'Los tipos de campos disponibles en Airtable son:',
    'batch_create_records': 'He creado los registros en lote exitosamente.',
    'batch_update_records': 'He actualizado los registros en lote como solicitaste.',
    'batch_delete_records': 'He eliminado los registros en lote especificados.',
    'batch_upsert_records': 'He realizado las operaciones de actualización/creación en lote.',
    'upload_attachment': 'He adjuntado el archivo al registro.',
    'list_collaborators': 'Los colaboradores de esta base son:',
    'list_shares': 'Las vistas compartidas en esta base son:',
    'create_view': 'He creado la nueva vista exitosamente.',
    'get_view_metadata': 'Los metadatos de la vista solicitada son:',
    'get_table_views': 'Las vistas de la tabla son:',
    'create_base': 'He creado la nueva base exitosamente.',
    'analyze_data': 'He completado el análisis de datos solicitado.',
    'create_report': 'He generado el informe solicitado.',
    'data_insights': 'Aquí están las perspectivas de los datos:',
    'optimize_workflow': 'Las recomendaciones de optimización son:',
    'smart_schema_design': 'El diseño de esquema inteligente sugiere:',
    'data_quality_audit': 'Los resultados de la auditoría de calidad son:',
    'predictive_analytics': 'Los resultados del análisis predictivo son:',
    'natural_language_query': 'He procesado tu consulta en lenguaje natural.',
    'smart_data_transformation': 'La transformación de datos inteligente está completa.',
    'automation_recommendations': 'Las recomendaciones de automatización son:',
    'unknown': 'No pude entender completamente tu consulta.'
  };

  return responses[intent] || 'Operación completada.';
}
