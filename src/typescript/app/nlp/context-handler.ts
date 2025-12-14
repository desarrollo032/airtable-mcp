/**
 * Context handler for maintaining conversation state and resolving references
 */

import { 
  ConversationContext, 
  PreviousQuery, 
  MentionedEntities, 
  ConversationPreferences,
  ContextReference
} from '../types/nlp';

export class ContextHandler {
  private contexts: Map<string, ConversationContext> = new Map();
  private maxContextQueries: number;

  constructor(maxContextQueries: number = 10) {
    this.maxContextQueries = maxContextQueries;
  }

  public async getContext(sessionId: string, userId: string): Promise<ConversationContext> {
    let context = this.contexts.get(sessionId);
    
    if (!context) {
      context = this.createNewContext(sessionId, userId);
      this.contexts.set(sessionId, context);
    }
    
    return context;
  }


  public async updateContext(
    sessionId: string, 
    queryData: { 
      query: string; 
      intent: string; 
      timestamp: Date; 
      entities: any; 
      result?: any 
    }
  ): Promise<void> {
    const context = this.contexts.get(sessionId);
    if (!context) {
      throw new Error(`Context not found for session: ${sessionId}`);
    }

    // Add new query to history
    const previousQuery: PreviousQuery = {
      query: queryData.query,
      intent: queryData.intent as any, // Will be properly typed
      timestamp: queryData.timestamp,
      result: queryData.result
    };

    context.previousQueries.push(previousQuery);

    // Limit history size
    if (context.previousQueries.length > this.maxContextQueries) {
      context.previousQueries = context.previousQueries.slice(-this.maxContextQueries);
    }

    // Update mentioned entities if available
    if (queryData.entities) {
      const entities = queryData.entities;
      
      if (entities.tableName && typeof entities.tableName === 'string') {
        const tableName = entities.tableName;
        if (!context.mentionedEntities.tables.includes(tableName)) {
          context.mentionedEntities.tables.push(tableName);
        }
        context.currentTable = tableName;
      }

      if (entities.recordId && typeof entities.recordId === 'string') {
        const recordId = entities.recordId;
        context.currentRecordId = recordId;
        if (!context.mentionedEntities.records.includes(recordId)) {
          context.mentionedEntities.records.push(recordId);
        }
      }

      if (entities.baseId && typeof entities.baseId === 'string') {
        const baseId = entities.baseId;
        context.currentBaseId = baseId;
      }

      if (entities.fieldName && typeof entities.fieldName === 'string') {
        const fieldName = entities.fieldName;
        if (!context.mentionedEntities.fields.includes(fieldName)) {
          context.mentionedEntities.fields.push(fieldName);
        }
      }
    }

    this.contexts.set(sessionId, context);
  }

  public async resolveReference(
    sessionId: string, 
    reference: string, 
    type: string
  ): Promise<ContextReference> {
    const context = this.contexts.get(sessionId);
    if (!context) {
      return {
        referenceType: type,
        reference: '',
        resolved: false,
        confidence: 0
      };
    }

    const lowerReference = reference.toLowerCase();

    if (type === 'table') {
      // Resolve table references
      if (lowerReference.includes('esa tabla') || lowerReference.includes('la tabla')) {
        if (context.currentTable) {
          return {
            referenceType: 'table',
            reference: context.currentTable,
            resolved: true,
            confidence: 0.9
          };
        }
      }

      // Try to match with mentioned tables
      const mentionedTables = context.mentionedEntities.tables;
      if (mentionedTables.length > 0) {
        const lastTable = mentionedTables[mentionedTables.length - 1];
        return {
          referenceType: 'table',
          reference: lastTable,
          resolved: true,
          alternatives: mentionedTables.slice(-3),
          confidence: 0.7
        };
      }
    }

    if (type === 'record') {
      // Resolve record references
      if (lowerReference.includes('ese registro') || lowerReference.includes('el registro')) {
        if (context.currentRecordId) {
          return {
            referenceType: 'record',
            reference: context.currentRecordId,
            resolved: true,
            confidence: 0.9
          };
        }
      }

      // Try to match with mentioned records
      const mentionedRecords = context.mentionedEntities.records;
      if (mentionedRecords.length > 0) {
        const lastRecord = mentionedRecords[mentionedRecords.length - 1];
        return {
          referenceType: 'record',
          reference: lastRecord,
          resolved: true,
          alternatives: mentionedRecords.slice(-3),
          confidence: 0.7
        };
      }
    }

    if (type === 'base') {
      if (context.currentBaseId) {
        return {
          referenceType: 'base',
          reference: context.currentBaseId,
          resolved: true,
          confidence: 0.9
        };
      }
    }

    return {
      referenceType: type,
      reference: '',
      resolved: false,
      confidence: 0
    };
  }

  public async getCurrentEntities(sessionId: string): Promise<any> {
    const context = this.contexts.get(sessionId);
    if (!context) {
      return {
        currentTable: null,
        currentRecordId: null,
        currentBaseId: null,
        mentionedEntities: {
          tables: [],
          fields: [],
          records: []
        },
        recentQueries: []
      };
    }




    return {
      currentTable: context.currentTable ?? null,
      currentRecordId: context.currentRecordId ?? null,
      currentBaseId: context.currentBaseId ?? null,
      mentionedEntities: context.mentionedEntities,
      recentQueries: context.previousQueries.slice(-5).map(q => ({
        query: q.query,
        intent: q.intent,
        timestamp: q.timestamp
      }))
    };
  }

  public async clearContext(sessionId: string): Promise<void> {
    this.contexts.delete(sessionId);
  }

  public async updatePreferences(
    sessionId: string, 
    preferences: Partial<ConversationPreferences>
  ): Promise<void> {
    const context = this.contexts.get(sessionId);
    if (context) {
      context.preferences = { ...context.preferences, ...preferences };
      this.contexts.set(sessionId, context);
    }
  }

  public async getContextualTableSuggestion(sessionId: string): Promise<string | null> {
    const context = this.contexts.get(sessionId);
    if (!context) return null;

    // Suggest current table if available
    if (context.currentTable) {
      return context.currentTable;
    }

    // Suggest most recently mentioned table
    const mentionedTables = context.mentionedEntities.tables;
    if (mentionedTables.length > 0) {
      return mentionedTables[mentionedTables.length - 1];
    }

    return null;
  }

  public async getContextualRecordSuggestion(sessionId: string): Promise<string | null> {
    const context = this.contexts.get(sessionId);
    if (!context) return null;

    // Suggest current record if available
    if (context.currentRecordId) {
      return context.currentRecordId;
    }

    // Suggest most recently mentioned record
    const mentionedRecords = context.mentionedEntities.records;
    if (mentionedRecords.length > 0) {
      return mentionedRecords[mentionedRecords.length - 1];
    }

    return null;
  }

  public async findRecentQueryByIntent(
    sessionId: string, 
    intent: string, 
    limit: number = 3
  ): Promise<PreviousQuery[]> {
    const context = this.contexts.get(sessionId);
    if (!context) return [];

    return context.previousQueries
      .filter(query => query.intent === intent)
      .slice(-limit);
  }

  public async setCurrentContext(
    sessionId: string, 
    table?: string, 
    recordId?: string, 
    baseId?: string
  ): Promise<void> {
    const context = this.contexts.get(sessionId);
    if (context) {
      if (table) context.currentTable = table;
      if (recordId) context.currentRecordId = recordId;
      if (baseId) context.currentBaseId = baseId;
      this.contexts.set(sessionId, context);
    }
  }


  private createNewContext(sessionId: string, userId: string): ConversationContext {
    return {
      sessionId,
      userId,
      currentBaseId: null,
      currentTable: null,
      currentRecordId: null,
      previousQueries: [],
      mentionedEntities: {
        tables: [],
        fields: [],
        records: []
      },
      preferences: {
        language: 'es', // Default to Spanish
        dateFormat: 'YYYY-MM-DD',
        responseFormat: 'natural'
      }
    };
  }

  // Utility method to get context summary
  public getContextSummary(sessionId: string): any {
    const context = this.contexts.get(sessionId);
    if (!context) return null;

    return {
      sessionId: context.sessionId,
      userId: context.userId,
      currentTable: context.currentTable,
      currentRecordId: context.currentRecordId,
      currentBaseId: context.currentBaseId,
      queryCount: context.previousQueries.length,
      mentionedTables: context.mentionedEntities.tables,
      mentionedFields: context.mentionedEntities.fields,
      mentionedRecords: context.mentionedEntities.records,
      preferences: context.preferences
    };
  }
}

