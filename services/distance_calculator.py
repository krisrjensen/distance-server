"""
Distance Calculator Service
Handles various distance calculation methods
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Any

class DistanceCalculator:
    """Service for calculating distances between points"""
    
    def __init__(self):
        self.supported_types = [
            'euclidean', 'manhattan', 'cosine', 'hamming', 'jaccard'
        ]
    
    def calculate(self, point_a: List[float], point_b: List[float], 
                 calculation_type: str = 'euclidean') -> Dict[str, Any]:
        """
        Calculate distance between two points
        
        Args:
            point_a: First point coordinates
            point_b: Second point coordinates
            calculation_type: Type of distance calculation
            
        Returns:
            Dictionary containing distance result and metadata
        """
        if calculation_type not in self.supported_types:
            raise ValueError(f"Unsupported calculation type: {calculation_type}")
        
        if len(point_a) != len(point_b):
            raise ValueError("Points must have same dimensionality")
        
        # Convert to numpy arrays for calculation
        arr_a = np.array(point_a)
        arr_b = np.array(point_b)
        
        # Calculate distance based on type
        if calculation_type == 'euclidean':
            distance = self._euclidean_distance(arr_a, arr_b)
        elif calculation_type == 'manhattan':
            distance = self._manhattan_distance(arr_a, arr_b)
        elif calculation_type == 'cosine':
            distance = self._cosine_distance(arr_a, arr_b)
        elif calculation_type == 'hamming':
            distance = self._hamming_distance(arr_a, arr_b)
        elif calculation_type == 'jaccard':
            distance = self._jaccard_distance(arr_a, arr_b)
        
        return {
            'distance': float(distance),
            'calculation_type': calculation_type,
            'point_a': point_a,
            'point_b': point_b,
            'dimensionality': len(point_a),
            'metadata': {
                'timestamp': self._get_timestamp(),
                'calculation_id': self._generate_calculation_id()
            }
        }
    
    def _euclidean_distance(self, point_a: np.ndarray, point_b: np.ndarray) -> float:
        """Calculate Euclidean distance"""
        return np.linalg.norm(point_a - point_b)
    
    def _manhattan_distance(self, point_a: np.ndarray, point_b: np.ndarray) -> float:
        """Calculate Manhattan distance"""
        return np.sum(np.abs(point_a - point_b))
    
    def _cosine_distance(self, point_a: np.ndarray, point_b: np.ndarray) -> float:
        """Calculate Cosine distance"""
        dot_product = np.dot(point_a, point_b)
        norm_a = np.linalg.norm(point_a)
        norm_b = np.linalg.norm(point_b)
        
        if norm_a == 0 or norm_b == 0:
            return 1.0  # Maximum distance for zero vectors
        
        return 1 - (dot_product / (norm_a * norm_b))
    
    def _hamming_distance(self, point_a: np.ndarray, point_b: np.ndarray) -> float:
        """Calculate Hamming distance"""
        return np.sum(point_a != point_b)
    
    def _jaccard_distance(self, point_a: np.ndarray, point_b: np.ndarray) -> float:
        """Calculate Jaccard distance"""
        intersection = np.sum(np.minimum(point_a, point_b))
        union = np.sum(np.maximum(point_a, point_b))
        
        if union == 0:
            return 0.0
        
        return 1 - (intersection / union)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _generate_calculation_id(self) -> str:
        """Generate unique calculation ID"""
        import uuid
        return str(uuid.uuid4())
    
    def batch_calculate(self, points: List[List[float]], 
                       calculation_type: str = 'euclidean') -> Dict[str, Any]:
        """
        Calculate distances between all pairs of points
        
        Args:
            points: List of point coordinates
            calculation_type: Type of distance calculation
            
        Returns:
            Dictionary containing distance matrix and metadata
        """
        if len(points) < 2:
            raise ValueError("At least 2 points required for batch calculation")
        
        distance_matrix = []
        calculation_pairs = []
        
        for i in range(len(points)):
            row = []
            for j in range(len(points)):
                if i == j:
                    row.append(0.0)
                else:
                    result = self.calculate(points[i], points[j], calculation_type)
                    row.append(result['distance'])
                    if i < j:  # Store unique pairs
                        calculation_pairs.append({
                            'point_indices': [i, j],
                            'distance': result['distance']
                        })
            distance_matrix.append(row)
        
        return {
            'distance_matrix': distance_matrix,
            'calculation_type': calculation_type,
            'points': points,
            'calculation_pairs': calculation_pairs,
            'metadata': {
                'timestamp': self._get_timestamp(),
                'batch_id': self._generate_calculation_id(),
                'point_count': len(points)
            }
        }