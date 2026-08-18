"""
Basic semantic analyzer for extracting meaning from queries
"""

import re
from typing import List, Dict, Any
from .types import (
    SemanticAnalysis, 
    ConversationContext, 
    SentimentType, 
    UrgencyLevel, 
    QueryType, 
    QueryComplexity
)

class SemanticAnalyzer:
    def __init__(self):
        self.action_words = [
            'crear', 'mostrar', 'listar', 'ver', 'obtener', 'buscar', 'filtrar',
            'actualizar', 'modificar', 'cambiar', 'editar', 'eliminar', 'borrar',
            'agregar', 'añadir', 'insertar', 'subir', 'adjuntar'
        ]

        self.context_words = [
            'tabla', 'registro', 'base', 'campo', 'webhook', 'archivo', 'imagen',
            'proyecto', 'tarea', 'estado', 'prioridad', 'fecha', 'vencimiento'
        ]

        self.entity_patterns = [
            r'\b[A-Z][a-záéíóúñÑ\s]+\b',  # Proper nouns
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b[a-záéíóúñÑ_][a-zA-Z0-9áéíóúñÑ_]*\b'  # Identifiers
        ]

    async def analyze(self, query: str, context: ConversationContext) -> SemanticAnalysis:
        """
        Perform semantic analysis of a natural language query
        """
        words = query.lower().split()
        
        # Extract actions
        actions = [word for word in words if word in self.action_words]
        
        # Extract context
        context_entities = [word for word in words if word in self.context_words]
        
        # Extract named entities
        entities = self._extract_named_entities(query)
        
        # Determine sentiment
        sentiment = self._analyze_sentiment(words)
        
        # Determine urgency
        urgency = self._analyze_urgency(words, entities)
        
        # Calculate confidence
        confidence = self._calculate_confidence(actions, entities, context_entities)
        
        # Extract keywords
        keywords = self.extract_keywords(query)
        
        # Identify query type
        query_type = self.identify_query_type(query)
        
        # Analyze complexity
        complexity = self.analyze_complexity(query)
        
        return SemanticAnalysis(
            confidence=confidence,
            entities=entities,
            actions=actions,
            context=context_entities,
            sentiment=sentiment,
            urgency=urgency,
            keywords=keywords,
            query_type=query_type,
            complexity=complexity
        )

    def _extract_named_entities(self, query: str) -> List[str]:
        """Extract named entities from query"""
        entities = []
        
        for pattern in self.entity_patterns:
            matches = re.findall(pattern, query)
            # Filter out common words
            filtered_matches = [
                match for match in matches 
                if len(match) > 2 and not self._is_common_word(match.lower())
            ]
            entities.extend(filtered_matches)
        
        return list(set(entities))  # Remove duplicates

    def _is_common_word(self, word: str) -> bool:
        """Check if word is a common Spanish word"""
        common_words = [
            'una', 'un', 'el', 'la', 'de', 'en', 'con', 'para', 'por', 'sobre',
            'esta', 'este', 'esa', 'ese', 'todas', 'todos', 'que', 'donde',
            'como', 'cuando', 'donde', 'cual', 'cuales', 'quien', 'quienes'
        ]
        return word in common_words

    def _analyze_sentiment(self, words: List[str]) -> SentimentType:
        """Analyze sentiment of the query"""
        positive_words = ['bueno', 'excelente', 'perfecto', 'correcto', 'bien']
        negative_words = ['malo', 'incorrecto', 'error', 'problema', 'fallo']
        
        positive_count = len([word for word in words if word in positive_words])
        negative_count = len([word for word in words if word in negative_words])
        
        if positive_count > negative_count:
            return SentimentType.POSITIVE
        elif negative_count > positive_count:
            return SentimentType.NEGATIVE
        else:
            return SentimentType.NEUTRAL

    def _analyze_urgency(self, words: List[str], entities: List[str]) -> UrgencyLevel:
        """Analyze urgency level of the query"""
        urgent_words = ['urgente', 'rápido', 'inmediato', 'ahora', 'ya']
        medium_words = ['pronto', 'rápido', 'próximo']
        
        has_urgent = any(word in words for word in urgent_words)
        has_medium = any(word in words for word in medium_words)
        
        if has_urgent:
            return UrgencyLevel.HIGH
        elif has_medium:
            return UrgencyLevel.MEDIUM
        else:
            return UrgencyLevel.LOW

    def _calculate_confidence(self, actions: List[str], entities: List[str], context_words: List[str]) -> float:
        """Calculate confidence score for the analysis"""
        confidence = 0.3  # Base confidence
        
        # Increase for detected actions
        confidence += min(len(actions) * 0.2, 0.4)
        
        # Increase for detected entities
        confidence += min(len(entities) * 0.1, 0.3)
        
        # Increase for context words
        confidence += min(len(context_words) * 0.1, 0.2)
        
        return min(confidence, 1.0)

    def extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from a query"""
        words = re.sub(r'[^\w\sáéíóúñÑ]', ' ', query.lower()).split()
        words = [word for word in words if len(word) > 2]
        
        # Filter stop words
        stop_words = [
            'una', 'un', 'el', 'la', 'de', 'en', 'con', 'para', 'por', 'sobre',
            'esta', 'este', 'esa', 'ese', 'todas', 'todos', 'que', 'donde',
            'como', 'cuando', 'donde', 'cual', 'cuales', 'quien', 'quienes'
        ]
        
        return [word for word in words if word not in stop_words]

    def identify_query_type(self, query: str) -> QueryType:
        """Identify the type of query"""
        if '?' in query:
            return QueryType.QUESTION
        elif any(phrase in query for phrase in ['por favor', 'podrías']):
            return QueryType.REQUEST
        elif any(action in query.lower() for action in self.action_words):
            return QueryType.ACTION
        else:
            return QueryType.UNKNOWN

    def analyze_complexity(self, query: str) -> QueryComplexity:
        """Analyze the complexity of a query"""
        word_count = len(query.split())
        entity_count = len(self._extract_named_entities(query))
        
        if word_count <= 5 and entity_count <= 1:
            return QueryComplexity.SIMPLE
        elif word_count <= 15 and entity_count <= 3:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.COMPLEX

    def get_action_density(self, query: str) -> float:
        """Calculate action word density in query"""
        words = query.lower().split()
        action_count = len([word for word in words if word in self.action_words])
        return action_count / len(words) if words else 0.0

    def get_entity_density(self, query: str) -> float:
        """Calculate entity density in query"""
        words = query.split()
        entity_count = len(self._extract_named_entities(query))
        return entity_count / len(words) if words else 0.0

    def identify_query_patterns(self, query: str) -> List[str]:
        """Identify common query patterns"""
        patterns = []
        
        if any(word in query.lower() for word in ['listar', 'mostrar', 'ver']):
            patterns.append('listing_pattern')
        
        if any(word in query.lower() for word in ['crear', 'agregar', 'añadir']):
            patterns.append('creation_pattern')
        
        if any(word in query.lower() for word in ['actualizar', 'modificar', 'cambiar']):
            patterns.append('update_pattern')
        
        if any(word in query.lower() for word in ['eliminar', 'borrar', 'suprimir']):
            patterns.append('deletion_pattern')
        
        if any(word in query.lower() for word in ['buscar', 'filtrar', 'encontrar']):
            patterns.append('search_pattern')
        
        if any(word in query.lower() for word in ['crear tabla', 'añadir campo']):
            patterns.append('schema_pattern')
        
        return patterns

