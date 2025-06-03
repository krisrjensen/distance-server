"""
Visualization Generator Service
Creates visualizations for distance calculations
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
import io
import base64
from typing import Dict, List, Any
import seaborn as sns

class VisualizationGenerator:
    """Service for generating distance visualization charts"""
    
    def __init__(self):
        self.supported_chart_types = [
            'scatter', 'heatmap', 'network', 'histogram', 'line'
        ]
        self.supported_styles = [
            'default', 'seaborn', 'ggplot', 'dark_background'
        ]
        # Universal Color Palette - Demo Standards
        self.universal_colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'error': '#d62728',
            'warning': '#ff9800',
            'info': '#17a2b8',
            'background': '#ffffff',
            'text': '#2c3e50'
        }
        self.color_sequence = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def generate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate visualization based on configuration
        
        Args:
            config: Visualization configuration
            
        Returns:
            Dictionary containing visualization data and metadata
        """
        chart_type = config.get('chart_type', 'scatter')
        style = config.get('style', 'default')
        
        if chart_type not in self.supported_chart_types:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        # Set matplotlib style with universal color palette
        plt.style.use('default')  # Start with clean default
        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=self.color_sequence)
        plt.rcParams['figure.facecolor'] = self.universal_colors['background']
        plt.rcParams['axes.facecolor'] = self.universal_colors['background']
        plt.rcParams['text.color'] = self.universal_colors['text']
        plt.rcParams['axes.labelcolor'] = self.universal_colors['text']
        plt.rcParams['xtick.color'] = self.universal_colors['text']
        plt.rcParams['ytick.color'] = self.universal_colors['text']
        
        # Generate visualization based on chart type
        if chart_type == 'scatter':
            chart_data = self._generate_scatter_plot(config)
        elif chart_type == 'heatmap':
            chart_data = self._generate_heatmap(config)
        elif chart_type == 'network':
            chart_data = self._generate_network_plot(config)
        elif chart_type == 'histogram':
            chart_data = self._generate_histogram(config)
        elif chart_type == 'line':
            chart_data = self._generate_line_plot(config)
        
        return {
            'chart_type': chart_type,
            'style': style,
            'chart_data': chart_data,
            'metadata': {
                'timestamp': self._get_timestamp(),
                'visualization_id': self._generate_visualization_id()
            }
        }
    
    def _generate_scatter_plot(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scatter plot visualization"""
        points = config.get('points', [])
        distances = config.get('distances', [])
        
        if not points:
            raise ValueError("Points data required for scatter plot")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Extract x, y coordinates
        if len(points[0]) >= 2:
            x_coords = [point[0] for point in points]
            y_coords = [point[1] for point in points]
            
            # Color points based on distances if available
            if distances and len(distances) == len(points):
                scatter = ax.scatter(x_coords, y_coords, c=distances, 
                                   cmap='Blues', s=120, alpha=0.8, 
                                   edgecolors=self.universal_colors['primary'], linewidth=2)
                cbar = plt.colorbar(scatter, label='Distance Values')
                cbar.ax.yaxis.label.set_color(self.universal_colors['text'])
            else:
                ax.scatter(x_coords, y_coords, s=120, alpha=0.8, 
                          color=self.universal_colors['primary'], 
                          edgecolors=self.universal_colors['text'], linewidth=1.5)
            
            # Add point labels
            for i, (x, y) in enumerate(zip(x_coords, y_coords)):
                ax.annotate(f'P{i}', (x, y), xytext=(5, 5), 
                           textcoords='offset points')
        
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.set_title('Distance Analysis - Point Distribution')
        ax.grid(True, alpha=0.3)
        
        return self._figure_to_base64(fig)
    
    def _generate_heatmap(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate heatmap visualization"""
        distance_matrix = config.get('distance_matrix', [])
        
        if not distance_matrix:
            raise ValueError("Distance matrix required for heatmap")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create heatmap
        sns.heatmap(distance_matrix, annot=True, cmap='coolwarm', 
                   center=0, square=True, ax=ax)
        
        ax.set_title('Distance Matrix Heatmap')
        ax.set_xlabel('Point Index')
        ax.set_ylabel('Point Index')
        
        return self._figure_to_base64(fig)
    
    def _generate_network_plot(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate network plot visualization"""
        points = config.get('points', [])
        distances = config.get('distances', [])
        threshold = config.get('connection_threshold', 0.5)
        
        if not points:
            raise ValueError("Points data required for network plot")
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot points
        if len(points[0]) >= 2:
            x_coords = [point[0] for point in points]
            y_coords = [point[1] for point in points]
            
            ax.scatter(x_coords, y_coords, s=200, alpha=0.8, c='lightblue', 
                      edgecolors='black', linewidth=2)
            
            # Add connections based on distance threshold
            if distances:
                for i in range(len(points)):
                    for j in range(i + 1, len(points)):
                        if i < len(distances) and j < len(distances[i]):
                            distance = distances[i][j] if isinstance(distances[i], list) else distances[min(i, j)]
                            if distance <= threshold:
                                ax.plot([x_coords[i], x_coords[j]], 
                                       [y_coords[i], y_coords[j]], 
                                       'k-', alpha=0.6, linewidth=1)
            
            # Add point labels
            for i, (x, y) in enumerate(zip(x_coords, y_coords)):
                ax.annotate(f'P{i}', (x, y), ha='center', va='center', 
                           fontweight='bold')
        
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.set_title(f'Network Plot (Connection Threshold: {threshold})')
        ax.grid(True, alpha=0.3)
        
        return self._figure_to_base64(fig)
    
    def _generate_histogram(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate histogram visualization"""
        distances = config.get('distances', [])
        
        if not distances:
            raise ValueError("Distance data required for histogram")
        
        # Flatten distance data if it's a matrix
        flat_distances = []
        if isinstance(distances[0], list):
            for row in distances:
                flat_distances.extend([d for d in row if d > 0])  # Exclude zero distances
        else:
            flat_distances = [d for d in distances if d > 0]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.hist(flat_distances, bins=20, alpha=0.7, color='skyblue', 
                edgecolor='black', linewidth=1.2)
        
        ax.set_xlabel('Distance')
        ax.set_ylabel('Frequency')
        ax.set_title('Distance Distribution Histogram')
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        mean_dist = np.mean(flat_distances)
        median_dist = np.median(flat_distances)
        ax.axvline(mean_dist, color='red', linestyle='--', 
                  label=f'Mean: {mean_dist:.3f}')
        ax.axvline(median_dist, color='green', linestyle='--', 
                  label=f'Median: {median_dist:.3f}')
        ax.legend()
        
        return self._figure_to_base64(fig)
    
    def _generate_line_plot(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate line plot visualization"""
        distances = config.get('distances', [])
        labels = config.get('labels', [])
        
        if not distances:
            raise ValueError("Distance data required for line plot")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if labels and len(labels) == len(distances):
            x_values = range(len(distances))
            ax.plot(x_values, distances, marker='o', linewidth=2, 
                   markersize=8, alpha=0.8)
            ax.set_xticks(x_values)
            ax.set_xticklabels(labels, rotation=45)
        else:
            ax.plot(distances, marker='o', linewidth=2, markersize=8, alpha=0.8)
        
        ax.set_xlabel('Data Points')
        ax.set_ylabel('Distance')
        ax.set_title('Distance Trend Analysis')
        ax.grid(True, alpha=0.3)
        
        return self._figure_to_base64(fig)
    
    def _figure_to_base64(self, fig) -> Dict[str, Any]:
        """Convert matplotlib figure to base64 string"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)  # Clean up memory
        
        return {
            'image_base64': image_base64,
            'format': 'png',
            'encoding': 'base64'
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _generate_visualization_id(self) -> str:
        """Generate unique visualization ID"""
        import uuid
        return str(uuid.uuid4())