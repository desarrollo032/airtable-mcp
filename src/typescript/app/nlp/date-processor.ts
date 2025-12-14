/**
 * Procesador inteligente de fechas y valores relativos
 */

import { DateProcessingResult } from '../types/nlp';

export class DateProcessor {
  private datePatterns: RegExp[] = [
    /hoy/i,
    /mañana/i,
    /ayer/i,
    /próxima\s+semana/i,
    /semana\s+pasada/i,
    /próximo\s+mes/i,
    /mes\s+pasado/i,
    /en\s+(\d+)\s+días?/i,
    /hace\s+(\d+)\s+días?/i,
    /(\d{4}-\d{2}-\d{2})/i, // YYYY-MM-DD
    /(\d{1,2}\/\d{1,2}\/\d{4})/i, // DD/MM/YYYY
    /(\d{1,2}-\d{1,2}-\d{4})/i, // DD-MM-YYYY
  ];

  private relativeTimeWords: Record<string, { type: 'past' | 'future'; unit: 'days' | 'weeks' | 'months' | 'years'; value: number }> = {
    'hoy': { type: 'future', unit: 'days', value: 0 },
    'mañana': { type: 'future', unit: 'days', value: 1 },
    'ayer': { type: 'past', unit: 'days', value: 1 },
    'próxima semana': { type: 'future', unit: 'weeks', value: 1 },
    'semana pasada': { type: 'past', unit: 'weeks', value: 1 },
    'próximo mes': { type: 'future', unit: 'months', value: 1 },
    'mes pasado': { type: 'past', unit: 'months', value: 1 }
  };

  async processDateReference(text: string): Promise<DateProcessingResult> {
    // Verificar palabras de tiempo relativo
    for (const [word, config] of Object.entries(this.relativeTimeWords)) {
      if (text.includes(word)) {
        const processedDate = this.calculateRelativeDate(config);
        return {
          originalText: word,
          processedDate,
          confidence: 0.9,
          format: 'relative',
          relativeType: config.type,
          relativeValue: config.value,
          relativeUnit: config.unit
        };
      }
    }


    // Verificar patrones numéricos ("en X días", "hace X días")
    const futureDaysMatch = text.match(/en\s+(\d+)\s+días?/i);
    if (futureDaysMatch) {
      const daysStr = futureDaysMatch[1];
      if (daysStr) {
        const days = parseInt(daysStr, 10);
        const processedDate = this.calculateDateFromNow(days, 'future');
        return {
          originalText: futureDaysMatch[0] || '',
          processedDate,
          confidence: 0.8,
          format: 'relative',
          relativeType: 'future',
          relativeValue: days,
          relativeUnit: 'days'
        };
      }
    }


    const pastDaysMatch = text.match(/hace\s+(\d+)\s+días?/i);
    if (pastDaysMatch) {
      const daysStr = pastDaysMatch[1];
      if (daysStr) {
        const days = parseInt(daysStr, 10);
        const processedDate = this.calculateDateFromNow(days, 'past');
        return {
          originalText: pastDaysMatch[0] || '',
          processedDate,
          confidence: 0.8,
          format: 'relative',
          relativeType: 'past',
          relativeValue: days,
          relativeUnit: 'days'
        };
      }
    }

    // Verificar fechas absolutas
    const isoDateMatch = text.match(/(\d{4}-\d{2}-\d{2})/i);
    if (isoDateMatch) {
      const date = isoDateMatch[1];
      if (this.isValidDate(date)) {
        return {
          originalText: date,
          processedDate: date,
          confidence: 1.0,
          format: 'absolute'
        };
      }
    }

    const slashDateMatch = text.match(/(\d{1,2}\/\d{1,2}\/\d{4})/i);
    if (slashDateMatch) {
      const dateStr = slashDateMatch[1];
      const formattedDate = this.formatDateFromSlash(dateStr);
      if (formattedDate && this.isValidDate(formattedDate)) {
        return {
          originalText: dateStr,
          processedDate: formattedDate,
          confidence: 0.9,
          format: 'absolute'
        };
      }
    }

    const dashDateMatch = text.match(/(\d{1,2}-\d{1,2}-\d{4})/i);
    if (dashDateMatch) {
      const dateStr = dashDateMatch[1];
      const formattedDate = this.formatDateFromDash(dateStr);
      if (formattedDate && this.isValidDate(formattedDate)) {
        return {
          originalText: dateStr,
          processedDate: formattedDate,
          confidence: 0.9,
          format: 'absolute'
        };
      }
    }

    // No se pudo procesar
    return {
      originalText: text,
      processedDate: null,
      confidence: 0,
      format: 'invalid'
    };
  }

  private calculateRelativeDate(config: { type: 'past' | 'future'; unit: 'days' | 'weeks' | 'months' | 'years'; value: number }): string {
    const now = new Date();
    let targetDate = new Date(now);

    switch (config.unit) {
      case 'days':
        targetDate.setDate(now.getDate() + (config.type === 'future' ? config.value : -config.value));
        break;
      case 'weeks':
        targetDate.setDate(now.getDate() + (config.type === 'future' ? config.value * 7 : -config.value * 7));
        break;
      case 'months':
        targetDate.setMonth(now.getMonth() + (config.type === 'future' ? config.value : -config.value));
        break;
      case 'years':
        targetDate.setFullYear(now.getFullYear() + (config.type === 'future' ? config.value : -config.value));
        break;
    }

    return targetDate.toISOString().split('T')[0];
  }

  private calculateDateFromNow(days: number, type: 'past' | 'future'): string {
    const now = new Date();
    const targetDate = new Date(now);
    targetDate.setDate(now.getDate() + (type === 'future' ? days : -days));
    return targetDate.toISOString().split('T')[0];
  }

  private formatDateFromSlash(dateStr: string): string | null {
    const parts = dateStr.split('/');
    if (parts.length === 3) {
      const day = parts[0].padStart(2, '0');
      const month = parts[1].padStart(2, '0');
      const year = parts[2];
      return `${year}-${month}-${day}`;
    }
    return null;
  }

  private formatDateFromDash(dateStr: string): string | null {
    const parts = dateStr.split('-');
    if (parts.length === 3) {
      const day = parts[0].padStart(2, '0');
      const month = parts[1].padStart(2, '0');
      const year = parts[2];
      return `${year}-${month}-${day}`;
    }
    return null;
  }

  private isValidDate(dateStr: string): boolean {
    const date = new Date(dateStr);
    return date instanceof Date && !isNaN(date.getTime());
  }

  /**
   * Procesa fechas en contexto de campos específicos
   */
  async processFieldDate(text: string, fieldName: string): Promise<string | null> {
    const result = await this.processDateReference(text);
    
    if (result.confidence > 0.5) {
      return result.processedDate;
    }

    return null;
  }

  /**
   * Obtiene fecha de vencimiento "mañana" para tareas
   */
  getTomorrowDate(): string {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  }

  /**
   * Obtiene fecha de hoy
   */
  getTodayDate(): string {
    const today = new Date();
    return today.toISOString().split('T')[0];
  }

  /**
   * Obtiene fecha de ayer
   */
  getYesterdayDate(): string {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    return yesterday.toISOString().split('T')[0];
  }

  /**
   * Verifica si un texto contiene referencias de fecha
   */
  containsDateReference(text: string): boolean {
    return this.datePatterns.some(pattern => pattern.test(text));
  }

  /**
   * Extrae todas las referencias de fecha de un texto
   */
  extractDateReferences(text: string): string[] {
    const references: string[] = [];
    
    for (const pattern of this.datePatterns) {
      const matches = text.match(pattern);
      if (matches) {
        references.push(...matches);
      }
    }

    return [...new Set(references)]; // Eliminar duplicados
  }
}
