/**
 * Motor de validación para verificar parámetros y permisos
 */

import { IntentType, QueryParameters, ConversationContext, ValidationRule } from '../types/nlp';

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  suggestions: string[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
  severity: 'error' | 'critical';
}

export interface ValidationWarning {
  field: string;
  message: string;
  code: string;
  suggestion?: string;
}

export class ValidationEngine {
  private validationRules: Map<IntentType, ValidationRule[]> = new Map();

  constructor() {
    this.initializeValidationRules();
  }

  private initializeValidationRules(): void {
    // Reglas para list_records
    this.validationRules.set('list_records', [
      {
        parameter: 'table',
        type: 'required',
        validation: (value) => value && typeof value === 'string' && value.trim().length > 0,
        errorMessage: 'El nombre de la tabla es requerido'
      }
    ]);

    // Reglas para create_record
    this.validationRules.set('create_record', [
      {
        parameter: 'table',
        type: 'required',
        validation: (value) => value && typeof value === 'string' && value.trim().length > 0,
        errorMessage: 'El nombre de la tabla es requerido'
      },
      {
        parameter: 'fields',
        type: 'required',
        validation: (value) => value && typeof value === 'object' && Object.keys(value).length > 0,
        errorMessage: 'Se requiere al menos un campo para crear el registro'
      }
    ]);

    // Reglas para update_record
    this.validationRules.set('update_record', [
      {
        parameter: 'table',
        type: 'required',
        validation: (value) => value && typeof value === 'string' && value.trim().length > 0,
        errorMessage: 'El nombre de la tabla es requerido'
      },
      {
        parameter: 'recordId',
        type: 'required',
        validation: (value) => value && typeof value === 'string' && value.trim().length > 0,
        errorMessage: 'El ID del registro es requerido'
      },
      {
        parameter: 'fields',
        type: 'required',
        validation: (value) => value && typeof value === 'object' && Object.keys(value).length > 0,
        errorMessage: 'Se requiere al menos un campo para actualizar'
      }
    ]);

    // Reglas para delete_record
    this.validationRules.set('delete_record', [
      {
        parameter: 'table',
        type: 'required',
        validation: (value) => value && typeof value === 'string' && value.trim().length > 0,
        errorMessage: 'El nombre de la tabla es requerido'
      },
      {
        parameter: 'recordId',
        type: 'required',
        validation: (value) => value && typeof value === 'string' && value.trim().length > 0,
        errorMessage: 'El ID del registro es requerido'
      }
    ]);

    // Reglas para create_webhook
    this.validationRules.set('create_webhook', [
      {
        parameter: 'table',
        type: 'required',
        validation: (value) => value && typeof value === 'string' && value.trim().length > 0,
        errorMessage: 'El nombre de la tabla es requerido'
      },
      {
        parameter: 'webhookConfig',
        type: 'required',
        validation: (value) => value && typeof value === 'object' && value.notificationUrl,
        errorMessage: 'La configuración del webhook es requerida'
      }
    ]);

    // Reglas para upload_attachment
    this.validationRules.set('upload_attachment', [
      {
        parameter: 'table',
        type: 'required',
        validation: (value) => value && typeof value === 'string' && value.trim().length > 0,
        errorMessage: 'El nombre de la tabla es requerido'
      },
      {
        parameter: 'recordId',
        type: 'required',
        validation: (value) => value && typeof value === 'string' && value.trim().length > 0,
        errorMessage: 'El ID del registro es requerido'
      },
      {
        parameter: 'attachmentData',
        type: 'required',
        validation: (value) => value && typeof value === 'object' && value.url,
        errorMessage: 'Los datos del adjunto son requeridos'
      }
    ]);

    // Reglas para batch_create_records
    this.validationRules.set('batch_create_records', [
      {
        parameter: 'table',
        type: 'required',
        validation: (value) => value && typeof value === 'string' && value.trim().length > 0,
        errorMessage: 'El nombre de la tabla es requerido'
      },
      {
        parameter: 'maxRecords',
        type: 'conditional',
        validation: (value) => {
          if (!value) return true; // Opcional
          return typeof value === 'number' && value > 0 && value <= 10;
        },
        errorMessage: 'El número de registros debe estar entre 1 y 10'
      }
    ]);
  }

  async validate(
    intent: IntentType, 
    parameters: QueryParameters, 
    context: ConversationContext
  ): Promise<ValidationResult> {
    const rules = this.validationRules.get(intent) || [];
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];
    const suggestions: string[] = [];

    // Validar reglas específicas
    for (const rule of rules) {
      const value = this.getParameterValue(parameters, rule.parameter);
      
      if (rule.type === 'required' && !value) {
        errors.push({
          field: rule.parameter,
          message: rule.errorMessage,
          code: `MISSING_${rule.parameter.toUpperCase()}`,
          severity: 'error'
        });
      } else if (rule.type === 'conditional' && value) {
        const isValid = await rule.validation(value);
        if (!isValid) {
          errors.push({
            field: rule.parameter,
            message: rule.errorMessage,
            code: `INVALID_${rule.parameter.toUpperCase()}`,
            severity: 'error'
          });
        }
      }
    }

    // Validaciones adicionales específicas por intención
    const additionalValidation = await this.performAdditionalValidations(intent, parameters, context);
    errors.push(...additionalValidation.errors);
    warnings.push(...additionalValidation.warnings);
    suggestions.push(...additionalValidation.suggestions);

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      suggestions
    };
  }

  private getParameterValue(parameters: QueryParameters, paramName: string): any {
    return parameters[paramName] || 
           (parameters.fields && parameters.fields[paramName]) ||
           (parameters.webhookConfig && parameters.webhookConfig[paramName]) ||
           (parameters.attachmentData && parameters.attachmentData[paramName]);
  }

  private async performAdditionalValidations(
    intent: IntentType,
    parameters: QueryParameters,
    context: ConversationContext
  ): Promise<ValidationResult> {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];
    const suggestions: string[] = [];

    // Validar URLs de webhook
    if (intent === 'create_webhook' && parameters.webhookConfig?.notificationUrl) {
      const url = parameters.webhookConfig.notificationUrl;
      if (!this.isValidUrl(url)) {
        errors.push({
          field: 'webhookConfig.notificationUrl',
          message: 'La URL del webhook no es válida',
          code: 'INVALID_WEBHOOK_URL',
          severity: 'error'
        });
      }
    }

    // Validar URLs de adjuntos
    if (intent === 'upload_attachment' && parameters.attachmentData?.url) {
      const url = parameters.attachmentData.url;
      if (!this.isValidUrl(url)) {
        errors.push({
          field: 'attachmentData.url',
          message: 'La URL del adjunto no es válida',
          code: 'INVALID_ATTACHMENT_URL',
          severity: 'error'
        });
      }
    }

    // Validar tamaño de lotes
    if (intent.includes('batch_') && parameters.maxRecords) {
      if (parameters.maxRecords > 10) {
        warnings.push({
          field: 'maxRecords',
          message: 'El tamaño del lote es mayor a 10, se recomienda usar un valor menor',
          code: 'LARGE_BATCH_SIZE',
          suggestion: 'Usar un tamaño de lote de 10 o menos para mejor rendimiento'
        });
      }
    }

    // Validar nombres de tabla
    if (parameters.table) {
      if (parameters.table.length > 50) {
        errors.push({
          field: 'table',
          message: 'El nombre de la tabla es demasiado largo',
          code: 'TABLE_NAME_TOO_LONG',
          severity: 'error'
        });
      }

      if (!/^[a-zA-ZáéíóúñÑ][a-zA-Z0-9áéíóúñÑ\s_-]*$/.test(parameters.table)) {
        errors.push({
          field: 'table',
          message: 'El nombre de la tabla contiene caracteres no válidos',
          code: 'INVALID_TABLE_NAME',
          severity: 'error'
        });
      }
    }

    // Validar IDs de registro
    if (parameters.recordId) {
      if (!/^[a-zA-Z0-9]+$/.test(parameters.recordId)) {
        errors.push({
          field: 'recordId',
          message: 'El ID del registro no es válido',
          code: 'INVALID_RECORD_ID',
          severity: 'error'
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      suggestions
    };
  }



  private isValidUrl(url: string): boolean {
    try {
      const urlPattern = /^https?:\/\/[^\s/$.?#].[^\s]*$/i;
      return urlPattern.test(url);
    } catch {
      return false;
    }
  }

  /**
   * Valida permisos basados en el contexto
   */
  async validatePermissions(
    intent: IntentType, 
    context: ConversationContext
  ): Promise<{ hasPermission: boolean; reason?: string }> {
    // Por ahora, asumimos que tenemos permisos
    // En una implementación real, verificaríamos los permisos del usuario
    
    const sensitiveIntents: IntentType[] = [
      'delete_record', 
      'delete_webhook', 
      'create_table', 
      'delete_table',
      'create_field',
      'delete_field'
    ];

    if (sensitiveIntents.includes(intent)) {
      // Aquí se podría verificar si el usuario tiene permisos específicos
      return { hasPermission: true };
    }

    return { hasPermission: true };
  }

  /**
   * Genera sugerencias de corrección para errores comunes
   */
  generateSuggestions(error: ValidationError, context: ConversationContext): string[] {
    const suggestions: string[] = [];

    switch (error.code) {
      case 'MISSING_TABLE':
        if (context.mentionedEntities.tables.length > 0) {
          suggestions.push(`¿Quisiste decir una de estas tablas: ${context.mentionedEntities.tables.join(', ')}?`);
        } else {
          suggestions.push('Especifica el nombre de la tabla: "en la tabla [nombre]"');
        }
        break;

      case 'MISSING_RECORD_ID':
        if (context.currentRecordId) {
          suggestions.push(`¿Te refieres al registro ${context.currentRecordId}?`);
        } else {
          suggestions.push('Especifica el ID del registro: "registro [ID]"');
        }
        break;

      case 'INVALID_TABLE_NAME':
        suggestions.push('Usa solo letras, números, espacios, guiones y guiones bajos');
        break;

      case 'INVALID_WEBHOOK_URL':
        suggestions.push('La URL debe comenzar con http:// o https://');
        break;

      case 'LARGE_BATCH_SIZE':
        suggestions.push('Para mejor rendimiento, usa lotes de 10 o menos registros');
        break;
    }

    return suggestions;
  }
}
