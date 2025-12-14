
/**
 * Intent mapper for translating natural language queries to specific tools
 */

import { 
  IntentType, 
  ExtractedEntities, 
  ConversationContext, 
  SemanticAnalysis 
} from '../types/nlp';


export class IntentMapper {
  private intentPatterns: Map<string, RegExp[]> = new Map();

  constructor() {
    this.initializePatterns();
  }

  private initializePatterns(): void {
    // Basic operations
    this.intentPatterns.set(IntentType.LIST_BASES, [
      /listar\s+(todas\s+mis\s+)?bases\s+airtable\s+accesibles/gi,
      /mostrarme\s+todas\s+mis\s+bases/gi,
      /qué\s+bases\s+tengo\s+accesibles/gi,
      /listar\s+bases/gi
    ]);

    this.intentPatterns.set(IntentType.LIST_RECORDS, [
      /mostrarme\s+todos\s+los\s+registros\s+(?:en|en\s+la)\s+tabla\s+\w+/gi,
      /listar\s+registros\s+(?:de|en)\s+\w+/gi,
      /ver\s+registros\s+de\s+\w+/gi,
      /obtener\s+registros\s+de\s+\w+/gi
    ]);

    this.intentPatterns.set(IntentType.CREATE_RECORD, [
      /crear\s+(?:una\s+)?nueva\s+tarea/gi,
      /crear\s+registro\s+nuevo/gi,
      /agregar\s+registro/gi,
      /insertar\s+registro/gi,
      /añadir\s+nuevo\s+registro/gi
    ]);

    this.intentPatterns.set(IntentType.UPDATE_RECORD, [
      /actualizar\s+(?:el\s+)?estado\s+de\s+(?:la\s+)?tarea/gi,
      /cambiar\s+estado\s+de/gi,
      /modificar\s+registro/gi,
      /editar\s+registro/gi,
      /actualizar\s+registro/gi
    ]);

    this.intentPatterns.set(IntentType.DELETE_RECORD, [
      /eliminar\s+(?:todos\s+los\s+)?registros\s+donde\s+el\s+estado\s+sea/gi,
      /borrar\s+registros\s+con\s+estado/gi,
      /suprimir\s+registros/gi,
      /eliminar\s+registros/gi
    ]);

    this.intentPatterns.set(IntentType.SEARCH_RECORDS, [
      /buscar\s+registros\s+donde\s+\w+\s+sea\s+igual\s+a/gi,
      /filtrar\s+registros\s+por/gi,
      /encontrar\s+registros\s+con/gi,
      /buscar\s+registros\s+que/gi
    ]);

    this.intentPatterns.set(IntentType.LIST_TABLES, [
      /qué\s+tablas\s+hay\s+en\s+mi\s+base/gi,
      /mostrar\s+tablas\s+de\s+la\s+base/gi,
      /listar\s+tablas/gi,
      /qué\s+tablas\s+tengo/gi
    ]);

    // Webhooks
    this.intentPatterns.set(IntentType.CREATE_WEBHOOK, [
      /crear\s+un\s+webhook\s+para\s+mi\s+tabla/gi,
      /crear\s+webhook/gi,
      /configurar\s+webhook/gi,
      /establecer\s+webhook/gi
    ]);

    this.intentPatterns.set(IntentType.LIST_WEBHOOKS, [
      /listar\s+todos\s+los\s+webhooks\s+activos/gi,
      /mostrar\s+webhooks/gi,
      /ver\s+webhooks/gi,
      /qué\s+webhooks\s+tengo/gi
    ]);

    this.intentPatterns.set(IntentType.DELETE_WEBHOOK, [
      /eliminar\s+webhook\s+\w+/gi,
      /borrar\s+webhook/gi,
      /remover\s+webhook/gi
    ]);

    // Schema management
    this.intentPatterns.set(IntentType.GET_BASE_SCHEMA, [
      /mostrarme\s+el\s+esquema\s+completo\s+para\s+(?:esta|la)\s+base/gi,
      /obtener\s+esquema\s+de\s+base/gi,
      /describir\s+base/gi
    ]);

    this.intentPatterns.set(IntentType.DESCRIBE_TABLE, [
      /describir\s+la\s+tabla\s+\w+\s+con\s+todos\s+los\s+detalles\s+de\s+campo/gi,
      /mostrar\s+estructura\s+de\s+tabla/gi,
      /ver\s+campos\s+de\s+tabla/gi
    ]);

    this.intentPatterns.set(IntentType.CREATE_TABLE, [
      /crear\s+una\s+nueva\s+tabla\s+llamada\s+\w+/gi,
      /crear\s+tabla\s+nueva/gi,
      /añadir\s+tabla/gi
    ]);

    this.intentPatterns.set(IntentType.CREATE_FIELD, [
      /agregar\s+un\s+campo\s+de\s+\w+\s+a\s+la\s+tabla/gi,
      /añadir\s+campo/gi,
      /crear\s+campo/gi
    ]);

    this.intentPatterns.set(IntentType.LIST_FIELD_TYPES, [
      /qué\s+tipos\s+de\s+campos\s+están\s+disponibles\s+en\s+airtable/gi,
      /tipos\s+de\s+campos\s+disponibles/gi,
      /campos\s+disponibles/gi
    ]);

    // Batch operations
    this.intentPatterns.set(IntentType.BATCH_CREATE_RECORDS, [
      /crear\s+\d+\s+registros\s+nuevos\s+a\s+la\s+vez/gi,
      /crear\s+múltiples\s+registros/gi,
      /añadir\s+varios\s+registros/gi
    ]);

    this.intentPatterns.set(IntentType.BATCH_UPDATE_RECORDS, [
      /actualizar\s+múltiples\s+registros/gi,
      /modificar\s+varios\s+registros/gi,
      /cambiar\s+varios\s+registros/gi
    ]);

    this.intentPatterns.set(IntentType.BATCH_DELETE_RECORDS, [
      /eliminar\s+estos\s+\d+\s+registros\s+en\s+una\s+operación/gi,
      /borrar\s+múltiples\s+registros/gi,
      /eliminar\s+varios\s+registros/gi
    ]);

    // Attachments
    this.intentPatterns.set(IntentType.UPLOAD_ATTACHMENT, [
      /adjuntar\s+esta\s+url\s+de\s+imagen/gi,
      /subir\s+archivo/gi,
      /adjuntar\s+archivo/gi,
      /añadir\s+adjunto/gi
    ]);

    // Collaboration
    this.intentPatterns.set(IntentType.LIST_COLLABORATORS, [
      /quiénes\s+son\s+los\s+colaboradores\s+en\s+esta\s+base/gi,
      /mostrar\s+colaboradores/gi,
      /ver\s+colaboradores/gi
    ]);

    this.intentPatterns.set(IntentType.LIST_SHARES, [
      /mostrarme\s+todas\s+las\s+vistas\s+compartidas\s+en\s+esta\s+base/gi,
      /ver\s+vistas\s+compartidas/gi,
      /mostrar\s+compartidos/gi
    ]);

    // AI operations
    this.intentPatterns.set(IntentType.ANALYZE_DATA, [
      /analizar\s+datos\s+de/gi,
      /analizar\s+tabla/gi,
      /estudiar\s+datos/gi
    ]);
  }

  public async mapIntent(
    query: string, 
    semanticAnalysis: SemanticAnalysis, 
    context: ConversationContext
  ): Promise<IntentType> {

    // First try direct pattern matching
    for (const [intent, patterns] of this.intentPatterns.entries()) {
      for (const pattern of patterns) {
        if (pattern.test(query)) {
          return intent as IntentType;
        }
      }
    }

    // If no match, try with context
    if (query.includes('esa tabla') && context.currentTable) {
      if (query.includes('mostrar') || query.includes('ver') || query.includes('obtener')) {
        return IntentType.LIST_RECORDS;
      } else if (query.includes('crear') || query.includes('añadir')) {
        return IntentType.CREATE_RECORD;
      }
    }

    if (query.includes('ese registro') && context.currentRecordId) {
      if (query.includes('actualizar') || query.includes('cambiar') || query.includes('modificar')) {
        return IntentType.UPDATE_RECORD;
      } else if (query.includes('eliminar') || query.includes('borrar')) {
        return IntentType.DELETE_RECORD;
      }
    }

    // Keyword-based analysis
    const actionKeywords = ['crear', 'nuevo', 'añadir', 'insertar', 'agregar'];
    if (actionKeywords.some(keyword => query.includes(keyword))) {
      if (query.includes('tabla')) {
        return IntentType.CREATE_TABLE;
      } else if (query.includes('campo')) {
        return IntentType.CREATE_FIELD;
      } else {
        return IntentType.CREATE_RECORD;
      }
    }

    const displayKeywords = ['mostrar', 'listar', 'ver', 'obtener'];
    if (displayKeywords.some(keyword => query.includes(keyword))) {
      if (query.includes('base')) {
        return IntentType.LIST_BASES;
      } else if (query.includes('tabla') || query.includes('tablas')) {
        return IntentType.LIST_TABLES;
      } else if (query.includes('webhook')) {
        return IntentType.LIST_WEBHOOKS;
      } else {
        return IntentType.LIST_RECORDS;
      }
    }

    const updateKeywords = ['actualizar', 'modificar', 'cambiar', 'editar'];
    if (updateKeywords.some(keyword => query.includes(keyword))) {
      return IntentType.UPDATE_RECORD;
    }

    const deleteKeywords = ['eliminar', 'borrar', 'suprimir', 'remover'];
    if (deleteKeywords.some(keyword => query.includes(keyword))) {
      if (query.includes('webhook')) {
        return IntentType.DELETE_WEBHOOK;
      } else {
        return IntentType.DELETE_RECORD;
      }
    }

    return IntentType.UNKNOWN;
  }

  public requiresTable(intent: IntentType): boolean {
    const tableRequiredIntents = [
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
    ];
    return tableRequiredIntents.includes(intent);
  }

  public requiresRecordId(intent: IntentType): boolean {
    const recordIdRequiredIntents = [
      IntentType.UPDATE_RECORD,
      IntentType.DELETE_RECORD,
      IntentType.GET_RECORD,
      IntentType.UPLOAD_ATTACHMENT
    ];
    return recordIdRequiredIntents.includes(intent);
  }

  public getToolName(intent: IntentType): string {
    const toolMapping: Record<IntentType, string> = {
      [IntentType.LIST_BASES]: 'list_bases',
      [IntentType.LIST_RECORDS]: 'list_records',
      [IntentType.CREATE_RECORD]: 'create_record',
      [IntentType.UPDATE_RECORD]: 'update_record',
      [IntentType.DELETE_RECORD]: 'delete_record',
      [IntentType.SEARCH_RECORDS]: 'search_records',
      [IntentType.LIST_TABLES]: 'list_tables',
      [IntentType.GET_RECORD]: 'get_record',
      [IntentType.CREATE_WEBHOOK]: 'create_webhook',
      [IntentType.LIST_WEBHOOKS]: 'list_webhooks',
      [IntentType.DELETE_WEBHOOK]: 'delete_webhook',
      [IntentType.GET_WEBHOOK_PAYLOADS]: 'get_webhook_payloads',
      [IntentType.GET_BASE_SCHEMA]: 'get_base_schema',
      [IntentType.DESCRIBE_TABLE]: 'describe_table',
      [IntentType.CREATE_TABLE]: 'create_table',
      [IntentType.DELETE_TABLE]: 'delete_table',
      [IntentType.UPDATE_TABLE]: 'update_table',
      [IntentType.CREATE_FIELD]: 'create_field',
      [IntentType.DELETE_FIELD]: 'delete_field',
      [IntentType.UPDATE_FIELD]: 'update_field',
      [IntentType.LIST_FIELD_TYPES]: 'list_field_types',
      [IntentType.BATCH_CREATE_RECORDS]: 'batch_create_records',
      [IntentType.BATCH_UPDATE_RECORDS]: 'batch_update_records',
      [IntentType.BATCH_DELETE_RECORDS]: 'batch_delete_records',
      [IntentType.BATCH_UPSERT_RECORDS]: 'batch_upsert_records',
      [IntentType.UPLOAD_ATTACHMENT]: 'upload_attachment',
      [IntentType.LIST_COLLABORATORS]: 'list_collaborators',
      [IntentType.LIST_SHARES]: 'list_shares',
      [IntentType.CREATE_VIEW]: 'create_view',
      [IntentType.GET_VIEW_METADATA]: 'get_view_metadata',
      [IntentType.GET_TABLE_VIEWS]: 'get_table_views',
      [IntentType.CREATE_BASE]: 'create_base',
      [IntentType.ANALYZE_DATA]: 'analyze_data',
      [IntentType.CREATE_REPORT]: 'create_report',
      [IntentType.DATA_INSIGHTS]: 'data_insights',
      [IntentType.OPTIMIZE_WORKFLOW]: 'optimize_workflow',
      [IntentType.SMART_SCHEMA_DESIGN]: 'smart_schema_design',
      [IntentType.DATA_QUALITY_AUDIT]: 'data_quality_audit',
      [IntentType.PREDICTIVE_ANALYTICS]: 'predictive_analytics',
      [IntentType.NATURAL_LANGUAGE_QUERY]: 'natural_language_query',
      [IntentType.SMART_DATA_TRANSFORMATION]: 'smart_data_transformation',
      [IntentType.AUTOMATION_RECOMMENDATIONS]: 'automation_recommendations',
      [IntentType.UNKNOWN]: 'unknown'
    };
    
    return toolMapping[intent] || 'unknown';
  }
}

