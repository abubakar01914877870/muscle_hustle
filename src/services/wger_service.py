"""
Wger Exercise Database API Service

Provides integration with the free, open-source Wger exercise database.
API Documentation: https://wger.de/api/v2/
"""

import requests
from functools import lru_cache
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WgerService:
    """Service for interacting with Wger exercise database API"""
    
    BASE_URL = "https://wger.de/api/v2"
    DEFAULT_LANGUAGE = 2  # English
    TIMEOUT = 10  # seconds
    
    @staticmethod
    @lru_cache(maxsize=100)
    def get_exercises(limit: int = 100, offset: int = 0, language: int = DEFAULT_LANGUAGE) -> Dict:
        """
        Fetch exercises from Wger API with caching
        
        Args:
            limit: Number of exercises to fetch (default: 100)
            offset: Offset for pagination (default: 0)
            language: Language ID (2 = English)
            
        Returns:
            Dict with 'count', 'next', 'previous', 'results' keys
        """
        try:
            url = f"{WgerService.BASE_URL}/exercise/"
            params = {
                'limit': limit,
                'offset': offset,
                'language': language
            }
            
            response = requests.get(url, params=params, timeout=WgerService.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched {len(data.get('results', []))} exercises from Wger API")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching exercises from Wger API: {str(e)}")
            return {
                'count': 0,
                'next': None,
                'previous': None,
                'results': []
            }
    
    @staticmethod
    @lru_cache(maxsize=500)
    def get_exercise_info(exercise_id: int, language: int = DEFAULT_LANGUAGE) -> Optional[Dict]:
        """
        Get detailed exercise information including descriptions
        
        Args:
            exercise_id: Wger exercise ID
            language: Language ID (2 = English)
            
        Returns:
            Dict with detailed exercise information or None
        """
        try:
            url = f"{WgerService.BASE_URL}/exerciseinfo/{exercise_id}/"
            params = {'language': language}
            
            response = requests.get(url, params=params, timeout=WgerService.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched exercise info for ID {exercise_id}")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching exercise info {exercise_id}: {str(e)}")
            return None
    
    @staticmethod
    @lru_cache(maxsize=50)
    def get_categories() -> List[Dict]:
        """
        Get all exercise categories
        
        Returns:
            List of category dicts
        """
        try:
            url = f"{WgerService.BASE_URL}/exercisecategory/"
            response = requests.get(url, timeout=WgerService.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', [])
            
        except requests.RequestException as e:
            logger.error(f"Error fetching categories: {str(e)}")
            return []
    
    @staticmethod
    @lru_cache(maxsize=50)
    def get_muscles() -> List[Dict]:
        """
        Get all muscle groups
        
        Returns:
            List of muscle dicts
        """
        try:
            url = f"{WgerService.BASE_URL}/muscle/"
            response = requests.get(url, timeout=WgerService.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', [])
            
        except requests.RequestException as e:
            logger.error(f"Error fetching muscles: {str(e)}")
            return []
    
    @staticmethod
    @lru_cache(maxsize=50)
    def get_equipment() -> List[Dict]:
        """
        Get all equipment types
        
        Returns:
            List of equipment dicts
        """
        try:
            url = f"{WgerService.BASE_URL}/equipment/"
            response = requests.get(url, timeout=WgerService.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', [])
            
        except requests.RequestException as e:
            logger.error(f"Error fetching equipment: {str(e)}")
            return []
    
    @staticmethod
    def search_exercises(query: str, limit: int = 50) -> List[Dict]:
        """
        Search exercises by name
        
        Args:
            query: Search term
            limit: Max results
            
        Returns:
            List of matching exercises
        """
        try:
            url = f"{WgerService.BASE_URL}/exercise/search/"
            params = {'term': query}
            
            response = requests.get(url, params=params, timeout=WgerService.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            suggestions = data.get('suggestions', [])
            
            # Format results to match standard exercise structure with 'id'
            results = []
            for item in suggestions:
                ex_data = item.get('data', {})
                # Search returns a specific variation ID as 'id', but 'exerciseinfo' endpoint
                # requires the canonical ID which is provided as 'base_id'
                if 'base_id' in ex_data:
                    results.append({'id': ex_data['base_id']})
                elif 'id' in ex_data:
                    results.append({'id': ex_data['id']})
                    
            return results
            
        except Exception as e:
            logger.error(f"Error searching exercises: {str(e)}")
            return []
    
    @staticmethod
    def clear_cache():
        """Clear all cached data"""
        WgerService.get_exercises.cache_clear()
        WgerService.get_exercise_info.cache_clear()
        WgerService.get_categories.cache_clear()
        WgerService.get_muscles.cache_clear()
        WgerService.get_equipment.cache_clear()
        logger.info("Wger service cache cleared")
