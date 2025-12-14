"""
Validation engine for checking parameters and permissions
"""

from typing import Dict, List, Any, Optional
from .types import (
    IntentType, 
    QueryParameters, 
    ConversationContext, 
    ValidationRule, 
    ValidationResult, 
    ValidationError, 
    ValidationWarning, 
    ValidationSeverity
)

class ValidationEngine:
    def __init__(self):
        self.validation_rules: Dict[IntentType, List[ValidationRule]] = {}
        self._initialize_validation_rules()

    def _initialize_validation_rules(self):
        """Initialize validation rules for each intent type"""
        
        # Rules for list_records
        self.validation_rules[IntentType.LIST_RECORDS] = [
            ValidationRule(
                parameter='table',
                validation_type='required',
                error_message='El nombre de la tabla es requerido',
                validation_func=lambda value: value and isinstance(value, str) and value.strip()
            )
        ]

        # Rules for create_record
        self.validation_rules[IntentType.CREATE_RECORD] = [
            ValidationRule(
                parameter='table',
                validation_type='required',
                error_message='El nombre de la tabla es requerido',
                validation_func=lambda value: value and isinstance(value, str) and value.strip()
            ),
            ValidationRule(
                parameter='fields',
                validation_type='required',
                error_message='Se requiere al menos un campo para crear el registro',
                validation_func=lambda value: value and isinstance(value, dict) and len(value) > 0
            )
        ]

        # Rules for update_record
        self.validation_rules[IntentType.UPDATE_RECORD] = [
            ValidationRule(
                parameter='table',
                validation_type='required',
                error_message='El nombre de la tabla es requerido',
                validation_func=lambda value: value and isinstance(value, str) and value.strip()
            ),
            ValidationRule(
                parameter='record_id',
                validation_type='required',
                error_message='El ID del registro es requerido',
                validation_func=lambda value: value and isinstance(value, str) and value.strip()
            ),
            ValidationRule(
                parameter='fields',
                validation_type='required',
                error_message='Se requiere al menos un campo para actualizar',
                validation_func=lambda value: value and isinstance(value, dict) and len(value) > 0
            )
        ]

        # Rules for delete_record
        self.validation_rules[IntentType.DELETE_RECORD] = [
            ValidationRule(
                parameter='table',
                validation_type='required',
                error_message='El nombre de la tabla es requerido',
                validation_func=lambda value: value and isinstance(value, str) and value.strip()
            ),
            ValidationRule(
                parameter='record_id',
                validation_type='required',
                error_message='El ID del registro es requerido',
                validation_func=lambda value: value and isinstance(value, str) and value.strip()
            )
        ]

        # Rules for create_webhook
        self.validation_rules[IntentType.CREATE_WEBHOOK] = [
            ValidationRule(
                parameter='table',
                validation_type='required',
                error_message='El nombre de la tabla es requerido',
                validation_func=lambda value: value and isinstance(value, str) and value.strip()
            ),
            ValidationRule(
                parameter='webhook_config',
                validation_type='required',
                error_message='La configuración del webhook es requerida',
                validation_func=lambda value: value and isinstance(value, dict) and value.get('notificationUrl')
            )
        ]

        # Rules for upload_attachment
        self.validation_rules[IntentType.UPLOAD_ATTACHMENT] = [
            ValidationRule(
                parameter='table',
                validation_type='required',
                error_message='El nombre de la tabla es requerido',
                validation_func=lambda value: value and isinstance(value, str) and value.strip()
            ),
            ValidationRule(
                parameter='record_id',
                validation_type='required',
                error_message='El ID del registro es requerido',
                validation_func=lambda value: value and isinstance(value, str) and value.strip()
            ),
            ValidationRule(
                parameter='attachment_data',
                validation_type='required',
                error_message='Los datos del adjunto son requeridos',
                validation_func=lambda value: value and isinstance(value, dict) and value.get('url')
            )
        ]

        # Rules for batch_create_records
        self.validation_rules[IntentType.BATCH_CREATE_RECORDS] = [
            ValidationRule(
                parameter='table',
                validation_type='required',
                error_message='El nombre de la tabla es requerido',
                validation_func=lambda value: value and isinstance(value, str) and value.strip()
            ),
            ValidationRule(
                parameter='max_records',
                validation_type='conditional',
                error_message='El número de registros debe estar entre 1 y 10',
                validation_func=lambda value: (
                    True if value is None else  # Optional
                    (isinstance(value, int) and 1 <= value <= 10)
                )
            )
        ]

    async def validate(
        self, 
        intent: IntentType, 
        parameters: QueryParameters, 
        context: ConversationContext
    ) -> ValidationResult:
        """
        Validate parameters against rules for the given intent
        """
        rules = self.validation_rules.get(intent, [])
        errors: List[ValidationError] = []
        warnings: List[ValidationWarning] = []
        suggestions: List[str] = []

        # Validate specific rules
        for rule in rules:
            value = self._get_parameter_value(parameters, rule.parameter)
            
            if rule.validation_type == 'required' and not value:
                errors.append(ValidationError(
                    field=rule.parameter,
                    message=rule.error_message,
                    code=f'MISSING_{rule.parameter.upper()}',
                    severity=ValidationSeverity.ERROR
                ))
            elif rule.validation_type == 'conditional' and value is not None:
                if rule.validation_func and not rule.validation_func(value):
                    errors.append(ValidationError(
                        field=rule.parameter,
                        message=rule.error_message,
                        code=f'INVALID_{rule.parameter.upper()}',
                        severity=ValidationSeverity.ERROR
                    ))

        # Additional validations
        additional_validation = await self._perform_additional_validations(intent, parameters, context)
        errors.extend(additional_validation.errors)
        warnings.extend(additional_validation.warnings)
        suggestions.extend(additional_validation.suggestions)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )

    def _get_parameter_value(self, parameters: QueryParameters, param_name: str) -> Any:
        """Get parameter value from QueryParameters"""
        # Check direct parameters
        if hasattr(parameters, param_name):
            return getattr(parameters, param_name)
        
        # Check nested parameters
        if parameters.fields and param_name in parameters.fields:
            return parameters.fields[param_name]
        
        if parameters.webhook_config and param_name in parameters.webhook_config:
            return parameters.webhook_config[param_name]
        
        if parameters.attachment_data and param_name in parameters.attachment_data:
            return parameters.attachment_data[param_name]
        
        return None

    async def _perform_additional_validations(
        self, 
        intent: IntentType, 
        parameters: QueryParameters, 
        context: ConversationContext
    ) -> ValidationResult:
        """
        Perform additional validations specific to intent
        """
        errors: List[ValidationError] = []
        warnings: List[ValidationWarning] = []
        suggestions: List[str] = []

        # Validate webhook URLs
        if intent == IntentType.CREATE_WEBHOOK and parameters.webhook_config and parameters.webhook_config.get('notificationUrl'):
            url = parameters.webhook_config['notificationUrl']
            if not self._is_valid_url(url):
                errors.append(ValidationError(
                    field='webhook_config.notificationUrl',
                    message='La URL del webhook no es válida',
                    code='INVALID_WEBHOOK_URL',
                    severity=ValidationSeverity.ERROR
                ))

        # Validate attachment URLs
        if intent == IntentType.UPLOAD_ATTACHMENT and parameters.attachment_data and parameters.attachment_data.get('url'):
            url = parameters.attachment_data['url']
            if not self._is_valid_url(url):
                errors.append(ValidationError(
                    field='attachment_data.url',
                    message='La URL del adjunto no es válida',
                    code='INVALID_ATTACHMENT_URL',
                    severity=ValidationSeverity.ERROR
                ))

        # Validate batch sizes
        if 'batch' in intent.value and parameters.max_records:
            if parameters.max_records > 10:
                warnings.append(ValidationWarning(
                    field='max_records',
                    message='El tamaño del lote es mayor a 10, se recomienda usar un valor menor',
                    code='LARGE_BATCH_SIZE',
                    suggestion='Usar un tamaño de lote de 10 o menos para mejor rendimiento'
                ))

        # Validate table names
        if parameters.table:
            if len(parameters.table) > 50:
                errors.append(ValidationError(
                    field='table',
                    message='El nombre de la tabla es demasiado largo',
                    code='TABLE_NAME_TOO_LONG',
                    severity=ValidationSeverity.ERROR
                ))

            if not self._is_valid_table_name(parameters.table):
                errors.append(ValidationError(
                    field='table',
                    message='El nombre de la tabla contiene caracteres no válidos',
                    code='INVALID_TABLE_NAME',
                    severity=ValidationSeverity.ERROR
                ))

        # Validate record IDs
        if parameters.record_id:
            if not self._is_valid_record_id(parameters.record_id):
                errors.append(ValidationError(
                    field='record_id',
                    message='El ID del registro no es válido',
                    code='INVALID_RECORD_ID',
                    severity=ValidationSeverity.ERROR
                ))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https']
        except Exception:
            return False

    def _is_valid_table_name(self, name: str) -> bool:
        """Check if table name is valid"""
        import re
        return bool(re.match(r'^[a-zA-ZáéíóúñÑ][a-zA-Z0-9áéíóúñÑ\s_-]*$', name))

    def _is_valid_record_id(self, record_id: str) -> bool:
        """Check if record ID is valid"""
        import re
        return bool(re.match(r'^[a-zA-Z0-9]+$', record_id))

    async def validate_permissions(
        self, 
        intent: IntentType, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """
        Validate permissions based on context
        """
        # For now, assume we have permissions
        # In real implementation, check user permissions
        
        sensitive_intents = [
            IntentType.DELETE_RECORD,
            IntentType.DELETE_WEBHOOK,
            IntentType.DELETE_TABLE,
            IntentType.DELETE_FIELD,
            IntentType.CREATE_TABLE,
            IntentType.CREATE_FIELD
        ]

        if intent in sensitive_intents:
            # Here we would check specific user permissions
            return {'has_permission': True}

        return {'has_permission': True}

    def generate_suggestions(self, error: ValidationError, context: ConversationContext) -> List[str]:
        """
        Generate correction suggestions for common errors
        """
        suggestions = []

        if error.code == 'MISSING_TABLE':
            if context.mentioned_entities.tables:
                table_list = ', '.join(context.mentioned_entities.tables)
                suggestions.append(f'¿Quisiste decir una de estas tablas: {table_list}?')
            else:
                suggestions.append('Especifica el nombre de la tabla: "en la tabla [nombre]"')

        elif error.code == 'MISSING_RECORD_ID':
            if context.current_record_id:
                suggestions.append(f'¿Te refieres al registro {context.current_record_id}?')
            else:
                suggestions.append('Especifica el ID del registro: "registro [ID]"')

        elif error.code == 'INVALID_TABLE_NAME':
            suggestions.append('Usa solo letras, números, espacios, guiones y guiones bajos')

        elif error.code == 'INVALID_WEBHOOK_URL':
            suggestions.append('La URL debe comenzar con http:// o https://')

        elif error.code == 'LARGE_BATCH_SIZE':
            suggestions.append('Para mejor rendimiento, usa lotes de 10 o menos registros')

        return suggestions

