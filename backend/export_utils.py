import json
import csv
import io
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import logging

logger = logging.getLogger(__name__)

class ExportManager:
    """Handles exporting recognition results in various formats"""
    
    def __init__(self):
        self.supported_formats = ['json', 'csv', 'pdf']
    
    def export_recognition_results(self, results: Dict[str, Any], format_type: str, 
                                 include_images: bool = False) -> tuple[bytes, str]:
        """
        Export recognition results in the specified format
        
        Args:
            results: Recognition results dictionary
            format_type: Export format ('json', 'csv', 'pdf')
            include_images: Whether to include images in export
            
        Returns:
            Tuple of (exported_data_bytes, filename)
        """
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == 'json':
            return self._export_json(results, timestamp, include_images)
        elif format_type == 'csv':
            return self._export_csv(results, timestamp)
        elif format_type == 'pdf':
            return self._export_pdf(results, timestamp, include_images)
    
    def _export_json(self, results: Dict[str, Any], timestamp: str, 
                    include_images: bool = False) -> tuple[bytes, str]:
        """Export results as JSON"""
        try:
            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'format': 'json',
                    'version': '1.0'
                },
                'recognition_results': results
            }
            
            if not include_images:
                # Remove image paths for cleaner export
                if 'image_path' in export_data['recognition_results']:
                    del export_data['recognition_results']['image_path']
                if 'annotated_image_path' in export_data['recognition_results']:
                    del export_data['recognition_results']['annotated_image_path']
            
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
            filename = f"face_recognition_results_{timestamp}.json"
            
            return json_data.encode('utf-8'), filename
            
        except Exception as e:
            logger.error(f"Error exporting JSON: {str(e)}")
            raise
    
    def _export_csv(self, results: Dict[str, Any], timestamp: str) -> tuple[bytes, str]:
        """Export results as CSV"""
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Face_Index', 'Name', 'Employee_ID', 'Department', 'Position', 
                'Email', 'Phone', 'Confidence', 'Face_Location_Top', 
                'Face_Location_Right', 'Face_Location_Bottom', 'Face_Location_Left',
                'Processing_Time', 'Detection_Model'
            ])
            
            # Write summary row
            writer.writerow([
                'SUMMARY', f"Total Faces: {results.get('total_faces_detected', 0)}", 
                f"Recognized: {results.get('total_faces_recognized', 0)}", 
                f"Unknown: {results.get('total_faces_detected', 0) - results.get('total_faces_recognized', 0)}",
                '', '', '', '', '', '', '', '',
                f"{results.get('processing_time', 0):.3f}s",
                results.get('detection_model', 'N/A')
            ])
            
            # Write face data
            for index, face in enumerate(results.get('recognized_faces', [])):
                location = face.get('face_location', [0, 0, 0, 0])
                writer.writerow([
                    index + 1,
                    face.get('name', 'Unknown'),
                    face.get('employee_id', 'N/A'),
                    face.get('department', 'N/A'),
                    face.get('position', 'N/A'),
                    face.get('email', 'N/A'),
                    face.get('phone', 'N/A'),
                    f"{face.get('confidence', 0):.2f}%" if face.get('confidence') else 'N/A',
                    location[0] if len(location) > 0 else 'N/A',
                    location[1] if len(location) > 1 else 'N/A',
                    location[2] if len(location) > 2 else 'N/A',
                    location[3] if len(location) > 3 else 'N/A',
                    f"{results.get('processing_time', 0):.3f}s",
                    results.get('detection_model', 'N/A')
                ])
            
            filename = f"face_recognition_results_{timestamp}.csv"
            csv_data = output.getvalue().encode('utf-8')
            output.close()
            
            return csv_data, filename
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {str(e)}")
            raise
    
    def _export_pdf(self, results: Dict[str, Any], timestamp: str, 
                   include_images: bool = False) -> tuple[bytes, str]:
        """Export results as PDF report"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2d3748')
            )
            story.append(Paragraph("Face Recognition Report", title_style))
            story.append(Spacer(1, 20))
            
            # Summary section
            summary_style = ParagraphStyle(
                'Summary',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=10
            )
            
            story.append(Paragraph("<b>Recognition Summary</b>", styles['Heading2']))
            story.append(Paragraph(f"<b>Processing Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", summary_style))
            story.append(Paragraph(f"<b>Total Faces Detected:</b> {results.get('total_faces_detected', 0)}", summary_style))
            story.append(Paragraph(f"<b>Faces Recognized:</b> {results.get('total_faces_recognized', 0)}", summary_style))
            story.append(Paragraph(f"<b>Unknown Faces:</b> {results.get('total_faces_detected', 0) - results.get('total_faces_recognized', 0)}", summary_style))
            story.append(Paragraph(f"<b>Processing Time:</b> {results.get('processing_time', 0):.3f} seconds", summary_style))
            story.append(Paragraph(f"<b>Detection Model:</b> {results.get('detection_model', 'N/A')}", summary_style))
            story.append(Spacer(1, 20))
            
            # Faces table
            if results.get('recognized_faces'):
                story.append(Paragraph("<b>Detected Faces Details</b>", styles['Heading2']))
                story.append(Spacer(1, 10))
                
                # Create table data
                table_data = [
                    ['#', 'Name', 'Employee ID', 'Department', 'Position', 'Confidence']
                ]
                
                for index, face in enumerate(results['recognized_faces']):
                    confidence = f"{face.get('confidence', 0):.1f}%" if face.get('confidence') else 'N/A'
                    table_data.append([
                        str(index + 1),
                        face.get('name', 'Unknown'),
                        face.get('employee_id', 'N/A'),
                        face.get('department', 'N/A'),
                        face.get('position', 'N/A'),
                        confidence
                    ])
                
                # Create and style table
                table = Table(table_data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(table)
                story.append(Spacer(1, 20))
            
            # Technical details
            story.append(Paragraph("<b>Technical Details</b>", styles['Heading2']))
            if results.get('image_dimensions'):
                story.append(Paragraph(f"<b>Image Dimensions:</b> {results['image_dimensions']}", summary_style))
            if results.get('recognition_tolerance'):
                story.append(Paragraph(f"<b>Recognition Tolerance:</b> {results['recognition_tolerance']}", summary_style))
            
            # Footer
            story.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            story.append(Paragraph("Generated by Face Recognition System", footer_style))
            
            # Build PDF
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            filename = f"face_recognition_report_{timestamp}.pdf"
            return pdf_data, filename
            
        except Exception as e:
            logger.error(f"Error exporting PDF: {str(e)}")
            raise
    
    def export_face_database(self, faces_data: List[Dict[str, Any]], format_type: str) -> tuple[bytes, str]:
        """Export known faces database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == 'json':
            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'format': 'json',
                    'type': 'face_database',
                    'total_faces': len(faces_data)
                },
                'faces': faces_data
            }
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
            filename = f"face_database_{timestamp}.json"
            return json_data.encode('utf-8'), filename
            
        elif format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['ID', 'Name', 'Employee_ID', 'Department', 'Position', 'Email', 'Phone', 'Created_At'])
            
            # Write face data
            for face in faces_data:
                writer.writerow([
                    face.get('id', ''),
                    face.get('name', ''),
                    face.get('employee_id', ''),
                    face.get('department', ''),
                    face.get('position', ''),
                    face.get('email', ''),
                    face.get('phone', ''),
                    face.get('created_at', '')
                ])
            
            filename = f"face_database_{timestamp}.csv"
            csv_data = output.getvalue().encode('utf-8')
            output.close()
            return csv_data, filename
        
        else:
            raise ValueError(f"Unsupported format for database export: {format_type}")

# Global export manager instance
export_manager = ExportManager()
