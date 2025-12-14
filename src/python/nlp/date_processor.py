"""
Intelligent date and relative value processor
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from .types import (
    DateProcessingResult, 
    DateFormat, 
    RelativeType, 
    RelativeUnit
)

class DateProcessor:
    def __init__(self):
        self.date_patterns = [
            r'hoy',
            r'mañana', 
            r'ayer',
            r'próxima\s+semana',
            r'semana\s+pasada',
            r'próximo\s+mes',
            r'mes\s+pasado',
            r'en\s+(\d+)\s+días?',
            r'hace\s+(\d+)\s+días?',
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{1,2}\/\d{1,2}\/\d{4})',  # DD/MM/YYYY
            r'(\d{1,2}-\d{1,2}-\d{4})',  # DD-MM-YYYY
        ]

        self.relative_time_words = {
            'hoy': {'type': 'future', 'unit': 'days', 'value': 0},
            'mañana': {'type': 'future', 'unit': 'days', 'value': 1},
            'ayer': {'type': 'past', 'unit': 'days', 'value': 1},
            'próxima semana': {'type': 'future', 'unit': 'weeks', 'value': 1},
            'semana pasada': {'type': 'past', 'unit': 'weeks', 'value': 1},
            'próximo mes': {'type': 'future', 'unit': 'months', 'value': 1},
            'mes pasado': {'type': 'past', 'unit': 'months', 'value': 1}
        }

    async def process_date_reference(self, text: str) -> DateProcessingResult:
        """
        Process date references in text and return structured result
        """
        # Check for relative time words
        for word, config in self.relative_time_words.items():
            if word in text:
                processed_date = self._calculate_relative_date(config)
                return DateProcessingResult(
                    original_text=word,
                    processed_date=processed_date,
                    confidence=0.9,
                    format=DateFormat.RELATIVE,
                    relative_type=RelativeType.FUTURE if config['type'] == 'future' else RelativeType.PAST,
                    relative_value=config['value'],
                    relative_unit=RelativeUnit.DAYS if config['unit'] == 'days' else 
                                RelativeUnit.WEEKS if config['unit'] == 'weeks' else
                                RelativeUnit.MONTHS
                )

        # Check for numeric patterns ("en X días", "hace X días")
        future_days_match = re.search(r'en\s+(\d+)\s+días?', text, re.IGNORECASE)
        if future_days_match:
            days_str = future_days_match.group(1)
            if days_str:
                days = int(days_str)
                processed_date = self._calculate_date_from_now(days, 'future')
                return DateProcessingResult(
                    original_text=future_days_match.group(0),
                    processed_date=processed_date,
                    confidence=0.8,
                    format=DateFormat.RELATIVE,
                    relative_type=RelativeType.FUTURE,
                    relative_value=days,
                    relative_unit=RelativeUnit.DAYS
                )

        past_days_match = re.search(r'hace\s+(\d+)\s+días?', text, re.IGNORECASE)
        if past_days_match:
            days_str = past_days_match.group(1)
            if days_str:
                days = int(days_str)
                processed_date = self._calculate_date_from_now(days, 'past')
                return DateProcessingResult(
                    original_text=past_days_match.group(0),
                    processed_date=processed_date,
                    confidence=0.8,
                    format=DateFormat.RELATIVE,
                    relative_type=RelativeType.PAST,
                    relative_value=days,
                    relative_unit=RelativeUnit.DAYS
                )

        # Check for absolute dates
        iso_date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
        if iso_date_match:
            date = iso_date_match.group(1)
            if self._is_valid_date(date):
                return DateProcessingResult(
                    original_text=date,
                    processed_date=date,
                    confidence=1.0,
                    format=DateFormat.ABSOLUTE
                )

        slash_date_match = re.search(r'(\d{1,2}\/\d{1,2}\/\d{4})', text, re.IGNORECASE)
        if slash_date_match:
            date_str = slash_date_match.group(1)
            formatted_date = self._format_date_from_slash(date_str)
            if formatted_date and self._is_valid_date(formatted_date):
                return DateProcessingResult(
                    original_text=date_str,
                    processed_date=formatted_date,
                    confidence=0.9,
                    format=DateFormat.ABSOLUTE
                )

        dash_date_match = re.search(r'(\d{1,2}-\d{1,2}-\d{4})', text, re.IGNORECASE)
        if dash_date_match:
            date_str = dash_date_match.group(1)
            formatted_date = self._format_date_from_dash(date_str)
            if formatted_date and self._is_valid_date(formatted_date):
                return DateProcessingResult(
                    original_text=date_str,
                    processed_date=formatted_date,
                    confidence=0.9,
                    format=DateFormat.ABSOLUTE
                )

        # Could not process
        return DateProcessingResult(
            original_text=text,
            processed_date=None,
            confidence=0.0,
            format=DateFormat.INVALID
        )

    def _calculate_relative_date(self, config: Dict[str, Any]) -> str:
        """Calculate date based on relative configuration"""
        now = datetime.now()
        target_date = now

        if config['unit'] == 'days':
            if config['type'] == 'future':
                target_date = now + timedelta(days=config['value'])
            else:
                target_date = now - timedelta(days=config['value'])
        elif config['unit'] == 'weeks':
            if config['type'] == 'future':
                target_date = now + timedelta(weeks=config['value'])
            else:
                target_date = now - timedelta(weeks=config['value'])
        elif config['unit'] == 'months':
            if config['type'] == 'future':
                target_date = now.replace(month=now.month + config['value'])
            else:
                target_date = now.replace(month=now.month - config['value'])

        return target_date.strftime('%Y-%m-%d')

    def _calculate_date_from_now(self, days: int, direction: str) -> str:
        """Calculate date X days from now"""
        now = datetime.now()
        if direction == 'future':
            target_date = now + timedelta(days=days)
        else:
            target_date = now - timedelta(days=days)
        return target_date.strftime('%Y-%m-%d')

    def _format_date_from_slash(self, date_str: str) -> Optional[str]:
        """Convert DD/MM/YYYY to YYYY-MM-DD"""
        try:
            parts = date_str.split('/')
            if len(parts) == 3:
                day = parts[0].zfill(2)
                month = parts[1].zfill(2)
                year = parts[2]
                return f"{year}-{month}-{day}"
        except (ValueError, IndexError):
            pass
        return None

    def _format_date_from_dash(self, date_str: str) -> Optional[str]:
        """Convert DD-MM-YYYY to YYYY-MM-DD"""
        try:
            parts = date_str.split('-')
            if len(parts) == 3:
                day = parts[0].zfill(2)
                month = parts[1].zfill(2)
                year = parts[2]
                return f"{year}-{month}-{day}"
        except (ValueError, IndexError):
            pass
        return None

    def _is_valid_date(self, date_str: str) -> bool:
        """Check if date string is valid"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    async def process_field_date(self, text: str, field_name: str) -> Optional[str]:
        """Process dates in context of specific fields"""
        result = await self.process_date_reference(text)
        if result.confidence > 0.5:
            return result.processed_date
        return None

    def get_tomorrow_date(self) -> str:
        """Get tomorrow's date"""
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime('%Y-%m-%d')

    def get_today_date(self) -> str:
        """Get today's date"""
        today = datetime.now()
        return today.strftime('%Y-%m-%d')

    def get_yesterday_date(self) -> str:
        """Get yesterday's date"""
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime('%Y-%m-%d')

    def contains_date_reference(self, text: str) -> bool:
        """Check if text contains date references"""
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in self.date_patterns)

    def extract_date_references(self, text: str) -> List[str]:
        """Extract all date references from text"""
        references = []
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            references.extend(matches)
        return list(set(references))  # Remove duplicates

