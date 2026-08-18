/**
 * Procesador principal de lenguaje natural para Airtable MCP
 */

import { 
  NaturalLanguageQuery, 
  ProcessedQuery, 
  IntentType, 
  ExtractedEntities, 
  QueryParameters,
  ConversationContext,
  Clarification,
  NLPConfig,
  DateProcessingResult
} from '../types/nlp';
import { IntentMapper } from './intent-mapper';
import { ContextHandler } from './context-handler';
import { DateProcessor } from './date-processor';
import { SemanticAnalyzer } from './semantic-analyzer';
import { ValidationEngine } from './validation-engine';
import { Logger } from '../logger';

export class NaturalLanguageProcessor {
  private config: NLPConfig;
  private intentMapper: IntentMapper;
  private contextHandler: ContextHandler;
  private dateProcessor: DateProcessor;
  private semanticAnalyzer: SemanticAnalyzer;
  private validationEngine: ValidationEngine;
  private logger: Logger;

  constructor(config: NLPConfig, logger: Logger) {
    this.config = config;
    this.intentMapper = new IntentMapper();
    this.contextHandler = new ContextHandler();
    this.dateProcessor = new DateProcessor();
    this.semanticAnalyzer = new SemanticAnalyzer();
    this.validationEngine = new ValidationEngine();
    this.logger = logger.child({ component: 'nlp-processor' });
  }

  async processQuery(query: NaturalLanguageQuery): Promise<ProcessedQuery> {
    const startTime = Date.now();
    
    try {
      this.logger.debug('Processing natural language query', { 
        query: query.query, 
        userId: query.userId,
        sessionId: query.sessionId 
      });

      // 1. Limpiar y normalizar la consulta
      const normalizedQuery = this.normalizeQuery(query.query);
      
      // 2. Obtener contexto conversacional
      const context = await this.contextHandler.getContext(
        query.sessionId || 'default',
        query.userId || 'anonymous'
      );
      
      // 3. Análisis semántico inicial
      const semanticAnalysis = await this.semanticAnalyzer.analyze(normalizedQuery, context);
      
      // 4. Extraer intenciones
      const intent = await this.intentMapper.mapIntent(normalizedQuery, semanticAnalysis, context);
      
      // 5. Extraer entidades
      const entities = await this.extractEntities(normalizedQuery, intent, context);
      
      // 6. Procesar fechas y valores relativos
      const processedEntities = await this.processRelativeValues(entities, query.query);
      
      // 7. Construir parámetros de consulta
      const parameters = await this.buildQueryParameters(intent, processedEntities, context);
      
      // 8. Validar parámetros
      const validation = await this.validationEngine.validate(intent, parameters, context);
      
      // 9. Determinar si necesita clarificación
      const clarifications = this.determineClarifications(intent, processedEntities, validation);
      const requiresClarification = clarifications.length > 0;
      
      // 10. Calcular confianza
      const confidence = this.calculateConfidence(intent, processedEntities, validation, semanticAnalysis);
      
      // 11. Actualizar contexto
      await this.contextHandler.updateContext(query.sessionId || 'default', {
        intent,
        entities: processedEntities,
        parameters,
        query: query.query,
        confidence
      });

      const processingTime = Date.now() - startTime;
      this.logger.debug('Query processed successfully', {
        intent,
        confidence,
        processingTime,
        requiresClarification
      });

      return {
        intent,
        entities: processedEntities,
        parameters,
        confidence,
        requiresClarification,
        clarifications
      };

    } catch (error) {
      this.logger.error('Error processing query', { error, query: query.query });
      
      return {
        intent: 'unknown',
        entities: {},
        parameters: {},
        confidence: 0,
        requiresClarification: true,
        clarifications: [{
          question: 'Lo siento, no pude entender tu consulta. ¿Podrías reformularla de manera más específica?',
          type: 'ambiguous_reference',
          required: true
        }]
      };
    }
  }

  private normalizeQuery(query: string): string {
    return query
      .toLowerCase()
      .trim()
      .replace(/\s+/g, ' ')
      .replace(/[^\w\s\.\-\_\@\#]/g, '')
      .replace(/\b(crea|crear|nuevo|nueva)\b/g, 'crear')
      .replace(/\b(mostrar|mostrarme|muestra|ver|listar)\b/g, 'listar')
      .replace(/\b(actualizar|modificar|cambiar|editar)\b/g, 'actualizar')
      .replace(/\b(eliminar|borrar|suprimir)\b/g, 'eliminar')
      .replace(/\b(buscar|encontrar|filtrar)\b/g, 'buscar');
  }

  private async extractEntities(
    query: string, 
    intent: IntentType, 
    context: ConversationContext
  ): Promise<ExtractedEntities> {
    const entities: ExtractedEntities = {};
    
    // Extraer nombre de tabla
    const tableMatch = query.match(/(?:en|para|tabla)\s+([a-zA-ZáéíóúñÑ_][a-zA-Z0-9áéíóúñÑ_\s]*?)(?:\s|$|\.|,)/);
    if (tableMatch) {
      entities.tableName = tableMatch[1].trim();
    } else if (context.currentTable) {
      entities.tableName = context.currentTable;
    }

    // Extraer ID de registro
    const recordIdMatch = query.match(/(?:id|registro|record)\s*[:#]?\s*([a-zA-Z0-9]+)/);
    if (recordIdMatch) {
      entities.recordId = recordIdMatch[1];
    }

    // Extraer prioridad
    const priorityMatch = query.match(/prioridad\s+(alta|media|baja)/);
    if (priorityMatch) {
      const priority = priorityMatch[1].toLowerCase();
      entities.priority = priority === 'alta' ? 'Alta' : priority === 'media' ? 'Media' : 'Baja';
    }

    // Extraer estado
    const statusMatch = query.match(/(?:estado|status)\s*(?:sea\s+|=|igual\s+a\s+)?([a-zA-ZáéíóúñÑ\s]+?)(?:\s|$|\.|,)/);
    if (statusMatch) {
      entities.status = statusMatch[1].trim();
    }

    // Extraer URL de webhook
    const webhookUrlMatch = query.match(/https?:\/\/[^\s]+/);
    if (intent === 'create_webhook' && webhookUrlMatch) {
      entities.webhookUrl = webhookUrlMatch[0];
    }

    // Extraer ID de webhook
    const webhookIdMatch = query.match(/(?:webhook\s+)?([a-zA-Z0-9]+)/);
    if (intent === 'delete_webhook' && webhookIdMatch) {
      entities.webhookId = webhookIdMatch[1];
    }

    // Extraer URLs de adjuntos
    const attachmentMatch = query.match(/https?:\/\/[^\s]+/);
    if (intent === 'upload_attachment' && attachmentMatch) {
      entities.attachmentUrl = attachmentMatch[0];
    }

    // Extraer conteos
    const countMatch = query.match(/(\d+)\s+(?:registros?|registro|records?|record)/);
    if (countMatch) {
      entities.count = parseInt(countMatch[1], 10);
    }

    // Extraer nombres de campos mencionados
    const fieldMatches = query.matchAll(/campo\s+([a-zA-ZáéíóúñÑ_][a-zA-Z0-9áéíóúñÑ_\s]*?)/g);
    const fields = Array.from(fieldMatches, m => m[1].trim());
    if (fields.length > 0) {
      entities.fieldNames = fields;
    }

    // Procesar referencias contextuales
    if (query.includes('esa tabla') && context.currentTable) {
      entities.tableName = context.currentTable;
    }

    if (query.includes('ese registro') && context.currentRecordId) {
      entities.recordId = context.currentRecordId;
    }

    return entities;
  }

  private async processRelativeValues(entities: ExtractedEntities, originalQuery: string): Promise<ExtractedEntities> {
    const processed = { ...entities };

    // Procesar fechas relativas
    if (originalQuery.includes('mañana')) {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      processed.dateReference = tomorrow.toISOString().split('T')[0];
    } else if (originalQuery.includes('hoy')) {
      const today = new Date();
      processed.dateReference = today.toISOString().split('T')[0];
    } else if (originalQuery.includes('ayer')) {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      processed.dateReference = yesterday.toISOString().split('T')[0];
    }

    return processed;
  }

  private async buildQueryParameters(
    intent: IntentType, 
    entities: ExtractedEntities, 
    context: ConversationContext
  ): Promise<QueryParameters> {
    const params: QueryParameters = {};

    // Parámetros comunes
    if (entities.tableName) params.table = entities.tableName;
    if (entities.baseId) params.baseId = entities.baseId;
    if (entities.recordId) params.recordId = entities.recordId;

    // Parámetros específicos por intención
    switch (intent) {
      case 'list_records':
      case 'search_records':
        if (entities.status) {
          params.filterByFormula = `{Status} = '${entities.status}'`;
        }
        if (entities.maxRecords || entities.count) {
          params.maxRecords = Math.min(entities.count || entities.maxRecords || 10, 100);
        }
        break;

      case 'create_record':
        params.fields = {};
        if (entities.priority) params.fields['Priority'] = entities.priority;
        if (entities.status) params.fields['Status'] = entities.status;
        if (entities.dateReference) params.fields['Due Date'] = entities.dateReference;
        break;

      case 'update_record':
        if (entities.status) {
          params.fields = { 'Status': entities.status };
        }
        if (entities.priority) {
          params.fields = { ...params.fields, 'Priority': entities.priority };
        }
        break;

      case 'create_webhook':
        if (entities.webhookUrl) {
          params.webhookConfig = {
            notificationUrl: entities.webhookUrl,
            specification: {
              options: { filters: { dataChangeType: 'all' } }
            }
          };
        }
        break;

      case 'batch_create_records':
        if (entities.count) {
          params.maxRecords = Math.min(entities.count, 10);
        }
        break;

      case 'upload_attachment':
        if (entities.attachmentUrl) {
          params.attachmentData = {
            url: entities.attachmentUrl
          };
        }
        break;
    }

    return params;
  }

  private determineClarifications(
    intent: IntentType, 
    entities: ExtractedEntities, 
    validation: any
  ): Clarification[] {
    const clarifications: Clarification[] = [];

    // Verificar tabla requerida
    if (this.intentMapper.requiresTable(intent) && !entities.tableName) {
      clarifications.push({
        question: '¿En qué tabla quieres realizar esta operación?',
        type: 'missing_table',
        required: true
      });
    }

    // Verificar ID de registro requerido
    if (this.intentMapper.requiresRecordId(intent) && !entities.recordId) {
      clarifications.push({
        question: '¿Cuál es el ID del registro que quieres actualizar?',
        type: 'missing_value',
        required: true
      });
    }

    // Verificar URL de webhook requerida
    if (intent === 'create_webhook' && !entities.webhookUrl) {
      clarifications.push({
        question: '¿Cuál es la URL del webhook que quieres crear?',
        type: 'missing_value',
        required: true
      });
    }

    // Verificar URL de adjunto requerida
    if (intent === 'upload_attachment' && !entities.attachmentUrl) {
      clarifications.push({
        question: '¿Cuál es la URL del archivo que quieres adjuntar?',
        type: 'missing_value',
        required: true
      });
    }

    return clarifications;
  }

  private calculateConfidence(
    intent: IntentType, 
    entities: ExtractedEntities, 
    validation: any,
    semanticAnalysis: any
  ): number {
    let confidence = 0.5; // Base confidence

    // Incrementar confianza por intención clara
    if (intent !== 'unknown') confidence += 0.2;

    // Incrementar confianza por entidades extraídas
    const entityCount = Object.keys(entities).length;
    confidence += Math.min(entityCount * 0.1, 0.3);

    // Incrementar confianza por validación exitosa
    if (validation.isValid) confidence += 0.2;

    // Incrementar confianza por análisis semántico fuerte
    if (semanticAnalysis.confidence > 0.7) confidence += 0.1;

    return Math.min(confidence, 1.0);
  }
}
