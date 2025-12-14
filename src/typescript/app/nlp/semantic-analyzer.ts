/**
 * Analizador semántico básico para extraer significado de consultas
 */

import { ConversationContext } from '../types/nlp';

export interface SemanticAnalysis {
  confidence: number;
  entities: string[];
  actions: string[];
  context: string[];
  sentiment: 'positive' | 'negative' | 'neutral';
  urgency: 'high' | 'medium' | 'low';
}

export class SemanticAnalyzer {
  private actionWords: string[] = [
    'crear', 'mostrar', 'listar', 'ver', 'obtener', 'buscar', 'filtrar',
    'actualizar', 'modificar', 'cambiar', 'editar', 'eliminar', 'borrar',
    'agregar', 'añadir', 'insertar', 'subir', 'adjuntar'
  ];

  private contextWords: string[] = [
    'tabla', 'registro', 'base', 'campo', 'webhook', 'archivo', 'imagen',
    'proyecto', 'tarea', 'estado', 'prioridad', 'fecha', 'vencimiento'
  ];

  private entityPatterns: RegExp[] = [
    /\b[A-Z][a-záéíóúñÑ\s]+\b/g, // Nombres propios
    /\b[A-Z]{2,}\b/g, // Acrónimos
    /\b[a-záéíóúñÑ_][a-zA-Z0-9áéíóúñÑ_]*\b/g // Identificadores
  ];

  async analyze(query: string, context: ConversationContext): Promise<SemanticAnalysis> {
    const words = query.toLowerCase().split(/\s+/);
    
    // Extraer acciones
    const actions = words.filter(word => this.actionWords.includes(word));
    
    // Extraer contexto
    const contextEntities = words.filter(word => this.contextWords.includes(word));
    
    // Extraer entidades nombradas
    const entities = this.extractNamedEntities(query);
    
    // Determinar sentimiento
    const sentiment = this.analyzeSentiment(words);
    
    // Determinar urgencia
    const urgency = this.analyzeUrgency(words, entities);
    
    // Calcular confianza
    const confidence = this.calculateConfidence(actions, entities, contextEntities);
    
    return {
      confidence,
      entities,
      actions,
      context: contextEntities,
      sentiment,
      urgency
    };
  }

  private extractNamedEntities(query: string): string[] {
    const entities: string[] = [];
    
    for (const pattern of this.entityPatterns) {
      const matches = query.match(pattern);
      if (matches) {
        entities.push(...matches.filter(match => 
          match.length > 2 && 
          !this.isCommonWord(match.toLowerCase())
        ));
      }
    }
    
    return [...new Set(entities)]; // Eliminar duplicados
  }

  private isCommonWord(word: string): boolean {
    const commonWords = [
      'una', 'un', 'el', 'la', 'de', 'en', 'con', 'para', 'por', 'sobre',
      'esta', 'este', 'esa', 'ese', 'todas', 'todos', 'todos', 'que', 'donde'
    ];
    
    return commonWords.includes(word);
  }

  private analyzeSentiment(words: string[]): 'positive' | 'negative' | 'neutral' {
    const positiveWords = ['bueno', 'excelente', 'perfecto', 'correcto', 'bien'];
    const negativeWords = ['malo', 'incorrecto', 'error', 'problema', 'fallo'];
    
    const positiveCount = words.filter(word => positiveWords.includes(word)).length;
    const negativeCount = words.filter(word => negativeWords.includes(word)).length;
    
    if (positiveCount > negativeCount) return 'positive';
    if (negativeCount > positiveCount) return 'negative';
    return 'neutral';
  }

  private analyzeUrgency(words: string[], entities: string[]): 'high' | 'medium' | 'low' {
    const urgentWords = ['urgente', 'rápido', 'inmediato', 'ahora', 'ya'];
    const mediumWords = ['pronto', 'rápido', 'próximo'];
    
    const hasUrgent = words.some(word => urgentWords.includes(word));
    const hasMedium = words.some(word => mediumWords.includes(word));
    
    if (hasUrgent) return 'high';
    if (hasMedium) return 'medium';
    return 'low';
  }

  private calculateConfidence(actions: string[], entities: string[], contextWords: string[]): number {
    let confidence = 0.3; // Base confidence
    
    // Incrementar por acciones detectadas
    confidence += Math.min(actions.length * 0.2, 0.4);
    
    // Incrementar por entidades detectadas
    confidence += Math.min(entities.length * 0.1, 0.3);
    
    // Incrementar por palabras de contexto
    confidence += Math.min(contextWords.length * 0.1, 0.2);
    
    return Math.min(confidence, 1.0);
  }

  /**
   * Extrae palabras clave importantes de una consulta
   */
  extractKeywords(query: string): string[] {
    const words = query.toLowerCase()
      .replace(/[^\w\sáéíóúñÑ]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 2);
    
    // Filtrar palabras comunes
    const stopWords = [
      'una', 'un', 'el', 'la', 'de', 'en', 'con', 'para', 'por', 'sobre',
      'esta', 'este', 'esa', 'ese', 'todas', 'todos', 'que', 'donde',
      'como', 'cuando', 'donde', 'cual', 'cuales', 'quien', 'quienes'
    ];
    
    return words.filter(word => !stopWords.includes(word));
  }

  /**
   * Identifica el tipo de consulta
   */
  identifyQueryType(query: string): 'action' | 'question' | 'request' | 'unknown' {
    if (query.includes('?')) return 'question';
    if (query.includes('por favor') || query.includes('podrías')) return 'request';
    if (this.actionWords.some(action => query.includes(action))) return 'action';
    return 'unknown';
  }

  /**
   * Analiza la complejidad de una consulta
   */
  analyzeComplexity(query: string): 'simple' | 'moderate' | 'complex' {
    const wordCount = query.split(/\s+/).length;
    const entityCount = this.extractNamedEntities(query).length;
    
    if (wordCount <= 5 && entityCount <= 1) return 'simple';
    if (wordCount <= 15 && entityCount <= 3) return 'moderate';
    return 'complex';
  }
}
