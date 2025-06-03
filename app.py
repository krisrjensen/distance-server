"""
Distance Server - Web service for distance calculations and visualizations
Version: 20250602_000000_0_0_0_001
"""

from flask import Flask, request, jsonify, render_template
from services.distance_calculator import DistanceCalculator
from services.visualization_generator import VisualizationGenerator
from services.results_exporter import ResultsExporter
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

distance_calculator = DistanceCalculator()
visualization_generator = VisualizationGenerator()
results_exporter = ResultsExporter()

@app.route('/')
def index():
    """Main interface for distance calculations"""
    return render_template('index.html')

@app.route('/api/calculate-distance', methods=['POST'])
def calculate_distance():
    """Calculate distance between points"""
    try:
        data = request.get_json()
        point_a = data.get('point_a')
        point_b = data.get('point_b')
        calculation_type = data.get('type', 'euclidean')
        
        if not point_a or not point_b:
            return jsonify({'error': 'Both points are required'}), 400
        
        result = distance_calculator.calculate(point_a, point_b, calculation_type)
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Distance calculation error: {str(e)}")
        return jsonify({'error': 'Calculation failed'}), 500

@app.route('/api/generate-visualization', methods=['POST'])
def generate_visualization():
    """Generate visualization for distance data"""
    try:
        data = request.get_json()
        visualization_config = {
            'points': data.get('points', []),
            'distances': data.get('distances', []),
            'chart_type': data.get('chart_type', 'scatter'),
            'style': data.get('style', 'default')
        }
        
        visualization_result = visualization_generator.generate(visualization_config)
        return jsonify(visualization_result)
    
    except Exception as e:
        app.logger.error(f"Visualization generation error: {str(e)}")
        return jsonify({'error': 'Visualization generation failed'}), 500

@app.route('/api/export-results', methods=['POST'])
def export_results():
    """Export calculation results in various formats"""
    try:
        data = request.get_json()
        export_format = data.get('format', 'json')
        results_data = data.get('results', {})
        
        export_result = results_exporter.export(results_data, export_format)
        return jsonify(export_result)
    
    except Exception as e:
        app.logger.error(f"Export error: {str(e)}")
        return jsonify({'error': 'Export failed'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'distance-server'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)