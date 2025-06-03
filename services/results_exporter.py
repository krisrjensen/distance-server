"""
Results Exporter Service
Exports calculation results in various formats
"""

import json
import csv
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Union
import io
import pandas as pd
from datetime import datetime

class ResultsExporter:
    """Service for exporting distance calculation results"""
    
    def __init__(self):
        self.supported_formats = [
            'json', 'csv', 'xml', 'excel', 'txt', 'html'
        ]
    
    def export(self, results_data: Dict[str, Any], 
               export_format: str = 'json') -> Dict[str, Any]:
        """
        Export results in specified format
        
        Args:
            results_data: Data to export
            export_format: Target export format
            
        Returns:
            Dictionary containing exported data and metadata
        """
        if export_format not in self.supported_formats:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        # Generate export based on format
        if export_format == 'json':
            exported_data = self._export_json(results_data)
        elif export_format == 'csv':
            exported_data = self._export_csv(results_data)
        elif export_format == 'xml':
            exported_data = self._export_xml(results_data)
        elif export_format == 'excel':
            exported_data = self._export_excel(results_data)
        elif export_format == 'txt':
            exported_data = self._export_txt(results_data)
        elif export_format == 'html':
            exported_data = self._export_html(results_data)
        
        return {
            'format': export_format,
            'data': exported_data,
            'filename': self._generate_filename(export_format),
            'metadata': {
                'timestamp': self._get_timestamp(),
                'export_id': self._generate_export_id(),
                'original_data_size': len(str(results_data))
            }
        }
    
    def _export_json(self, results_data: Dict[str, Any]) -> str:
        """Export data as JSON"""
        export_data = {
            'export_info': {
                'format': 'json',
                'timestamp': self._get_timestamp(),
                'version': '1.0'
            },
            'results': results_data
        }
        return json.dumps(export_data, indent=2, default=str)
    
    def _export_csv(self, results_data: Dict[str, Any]) -> str:
        """Export data as CSV"""
        output = io.StringIO()
        
        # Handle different data structures
        if 'distance_matrix' in results_data:
            # Export distance matrix
            matrix = results_data['distance_matrix']
            writer = csv.writer(output)
            
            # Header row
            header = ['Point'] + [f'P{i}' for i in range(len(matrix))]
            writer.writerow(header)
            
            # Data rows
            for i, row in enumerate(matrix):
                writer.writerow([f'P{i}'] + row)
        
        elif 'calculation_pairs' in results_data:
            # Export calculation pairs
            pairs = results_data['calculation_pairs']
            writer = csv.writer(output)
            
            # Header
            writer.writerow(['Point_A_Index', 'Point_B_Index', 'Distance'])
            
            # Data
            for pair in pairs:
                indices = pair['point_indices']
                writer.writerow([indices[0], indices[1], pair['distance']])
        
        else:
            # Generic export
            writer = csv.writer(output)
            writer.writerow(['Key', 'Value'])
            for key, value in results_data.items():
                writer.writerow([key, str(value)])
        
        return output.getvalue()
    
    def _export_xml(self, results_data: Dict[str, Any]) -> str:
        """Export data as XML"""
        root = ET.Element('distance_analysis_results')
        
        # Add metadata
        metadata = ET.SubElement(root, 'metadata')
        ET.SubElement(metadata, 'export_timestamp').text = self._get_timestamp()
        ET.SubElement(metadata, 'format').text = 'xml'
        ET.SubElement(metadata, 'version').text = '1.0'
        
        # Add results data
        results_elem = ET.SubElement(root, 'results')
        self._dict_to_xml(results_data, results_elem)
        
        return ET.tostring(root, encoding='unicode')
    
    def _export_excel(self, results_data: Dict[str, Any]) -> str:
        """Export data as Excel (base64 encoded)"""
        import base64
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': ['Export Timestamp', 'Data Type', 'Record Count'],
                'Value': [
                    self._get_timestamp(),
                    'Distance Analysis Results',
                    len(str(results_data))
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, 
                                              sheet_name='Summary', 
                                              index=False)
            
            # Distance matrix sheet (if available)
            if 'distance_matrix' in results_data:
                matrix = results_data['distance_matrix']
                df = pd.DataFrame(matrix, 
                                columns=[f'P{i}' for i in range(len(matrix))],
                                index=[f'P{i}' for i in range(len(matrix))])
                df.to_excel(writer, sheet_name='Distance_Matrix')
            
            # Calculation pairs sheet (if available)
            if 'calculation_pairs' in results_data:
                pairs_data = []
                for pair in results_data['calculation_pairs']:
                    indices = pair['point_indices']
                    pairs_data.append({
                        'Point_A': f'P{indices[0]}',
                        'Point_B': f'P{indices[1]}',
                        'Distance': pair['distance']
                    })
                pd.DataFrame(pairs_data).to_excel(writer, 
                                                sheet_name='Calculation_Pairs', 
                                                index=False)
        
        output.seek(0)
        return base64.b64encode(output.getvalue()).decode('utf-8')
    
    def _export_txt(self, results_data: Dict[str, Any]) -> str:
        """Export data as plain text"""
        lines = []
        lines.append("DISTANCE ANALYSIS RESULTS")
        lines.append("=" * 50)
        lines.append(f"Export Timestamp: {self._get_timestamp()}")
        lines.append("")
        
        # Format different data types
        if 'distance_matrix' in results_data:
            lines.append("DISTANCE MATRIX:")
            lines.append("-" * 30)
            matrix = results_data['distance_matrix']
            
            # Header
            header = "     " + "".join([f"P{i:>8}" for i in range(len(matrix))])
            lines.append(header)
            
            # Rows
            for i, row in enumerate(matrix):
                row_str = f"P{i:<4} " + "".join([f"{val:>8.3f}" for val in row])
                lines.append(row_str)
        
        if 'calculation_pairs' in results_data:
            lines.append("")
            lines.append("CALCULATION PAIRS:")
            lines.append("-" * 30)
            for pair in results_data['calculation_pairs']:
                indices = pair['point_indices']
                lines.append(f"P{indices[0]} <-> P{indices[1]}: {pair['distance']:.6f}")
        
        # Add metadata
        if 'metadata' in results_data:
            lines.append("")
            lines.append("METADATA:")
            lines.append("-" * 30)
            for key, value in results_data['metadata'].items():
                lines.append(f"{key}: {value}")
        
        return "\n".join(lines)
    
    def _export_html(self, results_data: Dict[str, Any]) -> str:
        """Export data as HTML"""
        html_parts = []
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html><head>")
        html_parts.append("<title>Distance Analysis Results</title>")
        html_parts.append("<style>")
        html_parts.append("body { font-family: Arial, sans-serif; margin: 20px; }")
        html_parts.append("table { border-collapse: collapse; width: 100%; margin: 20px 0; }")
        html_parts.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }")
        html_parts.append("th { background-color: #f2f2f2; }")
        html_parts.append("h1, h2 { color: #333; }")
        html_parts.append("</style>")
        html_parts.append("</head><body>")
        
        html_parts.append("<h1>Distance Analysis Results</h1>")
        html_parts.append(f"<p><strong>Export Timestamp:</strong> {self._get_timestamp()}</p>")
        
        # Distance matrix table
        if 'distance_matrix' in results_data:
            html_parts.append("<h2>Distance Matrix</h2>")
            html_parts.append("<table>")
            
            matrix = results_data['distance_matrix']
            # Header
            html_parts.append("<tr><th>Point</th>")
            for i in range(len(matrix)):
                html_parts.append(f"<th>P{i}</th>")
            html_parts.append("</tr>")
            
            # Rows
            for i, row in enumerate(matrix):
                html_parts.append(f"<tr><td><strong>P{i}</strong></td>")
                for val in row:
                    html_parts.append(f"<td>{val:.6f}</td>")
                html_parts.append("</tr>")
            
            html_parts.append("</table>")
        
        # Calculation pairs table
        if 'calculation_pairs' in results_data:
            html_parts.append("<h2>Calculation Pairs</h2>")
            html_parts.append("<table>")
            html_parts.append("<tr><th>Point A</th><th>Point B</th><th>Distance</th></tr>")
            
            for pair in results_data['calculation_pairs']:
                indices = pair['point_indices']
                html_parts.append("<tr>")
                html_parts.append(f"<td>P{indices[0]}</td>")
                html_parts.append(f"<td>P{indices[1]}</td>")
                html_parts.append(f"<td>{pair['distance']:.6f}</td>")
                html_parts.append("</tr>")
            
            html_parts.append("</table>")
        
        html_parts.append("</body></html>")
        return "\n".join(html_parts)
    
    def _dict_to_xml(self, data: Union[Dict, List, Any], parent: ET.Element):
        """Convert dictionary to XML elements recursively"""
        if isinstance(data, dict):
            for key, value in data.items():
                elem = ET.SubElement(parent, str(key))
                self._dict_to_xml(value, elem)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                elem = ET.SubElement(parent, f'item_{i}')
                self._dict_to_xml(item, elem)
        else:
            parent.text = str(data)
    
    def _generate_filename(self, export_format: str) -> str:
        """Generate filename for export"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"distance_analysis_{timestamp}.{export_format}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()
    
    def _generate_export_id(self) -> str:
        """Generate unique export ID"""
        import uuid
        return str(uuid.uuid4())