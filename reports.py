"""
Report Generation Module
Generate PDF and CSV reports for predictions and analytics
"""

import csv
import os
from datetime import datetime
from typing import List, Dict
from io import BytesIO
from xml.sax.saxutils import escape as xml_escape
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Image as RLImage
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import json


def _text_or_na(value: object) -> str:
    if value is None:
        return "N/A"
    text = str(value).strip()
    return text if text else "N/A"


def _paragraph_text(value: object) -> str:
    if value is None:
        return "N/A"
    text = str(value).strip()
    if not text:
        return "N/A"
    return xml_escape(text).replace("\n", "<br/>")


def _severity_color(severity: str):
    severity = (severity or "").strip().lower()
    if severity == "high":
        return colors.HexColor('#fee2e2')
    if severity == "moderate":
        return colors.HexColor('#fef3c7')
    return colors.HexColor('#dcfce7')


def _severity_text_color(severity: str):
    severity = (severity or "").strip().lower()
    if severity == "high":
        return colors.HexColor('#b91c1c')
    if severity == "moderate":
        return colors.HexColor('#b45309')
    return colors.HexColor('#166534')


def _chart_image_from_figure(fig) -> BytesIO:
    buffer = BytesIO()
    fig.savefig(buffer, format='PNG', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    return buffer


def _build_probability_chart_image(probabilities: dict, predicted: str = None) -> BytesIO:
    labels = list(probabilities.keys())
    values = [float(x) * 100 for x in probabilities.values()]
    fig, ax = plt.subplots(figsize=(6, 3))
    bars = ax.barh(labels, values, color=['#1e3a8a' if label != predicted else '#14b8a6' for label in labels])
    ax.set_xlim(0, 100)
    ax.set_xlabel('Probability (%)')
    ax.set_title('Disease Probability Distribution', pad=12, fontsize=12)
    ax.xaxis.set_major_formatter(PercentFormatter())
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    ax.set_facecolor('#0b1120')
    fig.patch.set_facecolor('#0b1120')
    ax.tick_params(colors='white', labelcolor='white')
    ax.spines['bottom'].set_color('#2dd4bf')
    ax.spines['left'].set_color('#2dd4bf')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height() / 2, f'{width:.1f}%', va='center', color='white', fontsize=9)
    return _chart_image_from_figure(fig)


def _build_confidence_chart_image(confidence: float) -> BytesIO:
    fig, ax = plt.subplots(figsize=(6, 2.4))
    ax.bar(['Confidence'], [confidence * 100], color=['#22d3ee'], width=0.6)
    ax.set_ylim(0, 100)
    ax.set_ylabel('Confidence (%)')
    ax.set_title('AI Confidence Score', pad=12, fontsize=12)
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.set_facecolor('#0b1120')
    fig.patch.set_facecolor('#0b1120')
    ax.tick_params(colors='white', labelcolor='white')
    ax.spines['bottom'].set_color('#2dd4bf')
    ax.spines['left'].set_color('#2dd4bf')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for p in ax.patches:
        ax.text(p.get_x() + p.get_width() / 2, p.get_height() + 2, f'{p.get_height():.1f}%', ha='center', color='white', fontsize=10)
    return _chart_image_from_figure(fig)


class ReportGenerator:
    """Generate various reports"""
    
    @staticmethod
    def generate_prediction_report_pdf(prediction: Dict, user_name: str = None) -> BytesIO:
        """Generate PDF report for a single prediction"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=24,
            leading=28,
            textColor=colors.HexColor('#0f172a'),
            alignment=TA_CENTER,
            spaceAfter=12
        )

        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.HexColor('#475569'),
            alignment=TA_CENTER,
            spaceAfter=22
        )

        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=10,
            spaceBefore=10
        )

        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['BodyText'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#0f172a')
        )

        elements.append(Paragraph('AI Crop Diagnostics Report', title_style))
        elements.append(Paragraph('Detailed disease prediction report with AI insights, recommended treatment, and probability analytics.', subtitle_style))

        metadata = [
            ['Report Generated:', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')],
            ['Farmer / User:', user_name or 'Unknown'],
            ['Crop:', _text_or_na(prediction.get('crop')).capitalize()],
            ['Disease Detected:', _text_or_na(prediction.get('disease'))],
            ['Prediction Time:', _text_or_na(prediction.get('created_at'))],
        ]

        metadata_table = Table(metadata, colWidths=[2.2*inch, 3.8*inch], hAlign='LEFT')
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0f172a')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ]))
        elements.append(metadata_table)
        elements.append(Spacer(1, 0.25*inch))

        # Main summary block
        details = [
            ['Confidence Score', f"{float(prediction.get('confidence', 0)) * 100:.2f}%"],
            ['Severity', _text_or_na(prediction.get('severity'))],
            ['Fertilizer Recommendation', _text_or_na(prediction.get('fertilizer_recommendation'))],
            ['Dosage', _text_or_na(prediction.get('dosage'))],
            ['Application Timing', _text_or_na(prediction.get('application_timing'))],
            ['Spraying Interval', _text_or_na(prediction.get('spraying_interval'))],
            ['Organic Alternative', _text_or_na(prediction.get('organic_alternative'))],
            ['Prevention Tips', _text_or_na(prediction.get('prevention_tips'))],
        ]
        details_table = Table(details, colWidths=[2.0*inch, 4.0*inch], hAlign='LEFT')
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#e0f2fe')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0f172a')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ]))

        # Image preview section
        image_path = prediction.get('image_path')
        if image_path and os.path.exists(image_path):
            try:
                report_image = RLImage(image_path, width=3.5*inch, height=3.0*inch)
                report_image.hAlign = 'CENTER'
                elements.append(report_image)
                elements.append(Spacer(1, 0.25*inch))
            except Exception:
                pass

        elements.append(Paragraph('Prediction Overview', heading_style))
        elements.append(details_table)
        elements.append(Spacer(1, 0.25*inch))

        fertilizer_details = [
            ['Fertilizer Name', _text_or_na(prediction.get('fertilizer_name') or prediction.get('fertilizer_recommendation'))],
            ['NPK Values', _text_or_na(prediction.get('npk_values'))],
            ['Dosage', _text_or_na(prediction.get('dosage'))],
            ['Application Timing', _text_or_na(prediction.get('application_timing'))],
            ['Spraying Interval', _text_or_na(prediction.get('spraying_interval'))],
            ['Organic Alternative', _text_or_na(prediction.get('organic_alternative'))],
        ]
        fertilizer_table = Table(fertilizer_details, colWidths=[2.0*inch, 4.0*inch], hAlign='LEFT')
        fertilizer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eff6ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0f172a')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ]))
        elements.append(Paragraph('Fertilizer Guidance', heading_style))
        elements.append(fertilizer_table)
        elements.append(Spacer(1, 0.25*inch))

        # Add charts
        confidence_plot = _build_confidence_chart_image(float(prediction.get('confidence', 0)))
        probability_plot = _build_probability_chart_image(prediction.get('all_probabilities') or {}, prediction.get('disease'))

        chart_table = Table([
            [RLImage(confidence_plot, width=2.9*inch, height=1.9*inch), RLImage(probability_plot, width=3.0*inch, height=1.9*inch)]
        ], colWidths=[3.0*inch, 3.0*inch])
        chart_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        elements.append(chart_table)
        elements.append(Spacer(1, 0.3*inch))

        advice_style = ParagraphStyle(
            'Advice',
            parent=styles['BodyText'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#0f172a')
        )

        if prediction.get('ai_advice') or prediction.get('treatment'):
            elements.append(Paragraph('AI Remedy Summary', heading_style))
            elements.append(Paragraph(_paragraph_text(prediction.get('ai_advice') or prediction.get('treatment')), advice_style))
            elements.append(Spacer(1, 0.2*inch))

        if prediction.get('recovery_plan'):
            elements.append(Paragraph('Recovery & Prevention', heading_style))
            elements.append(Paragraph(_paragraph_text(prediction.get('recovery_plan')), advice_style))
            elements.append(Spacer(1, 0.2*inch))

        signature_style = ParagraphStyle(
            'Signature',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#334155'),
            alignment=TA_RIGHT
        )

        elements.append(Spacer(1, 0.4*inch))
        elements.append(Paragraph('AI Diagnostics Lab | AgriDetect™', signature_style))
        elements.append(Paragraph('Certified AI Crop Health Reporting', signature_style))

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(
            'This document is generated by AgriDetect AI for agricultural diagnosis and advisory. Refer to local agricultural experts for further treatment.',
            footer_style
        ))

        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_history_report_pdf(predictions: List[Dict], user_name: str = None) -> BytesIO:
        """Generate PDF report for prediction history"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=10
        )
        
        # Title
        elements.append(Paragraph("Prediction History Report", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Summary
        summary_data = [
            ['Total Predictions:', str(len(predictions))],
            ['User:', user_name or "Unknown"],
            ['Generated:', datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")],
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f9ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Statistics
        elements.append(Paragraph("Statistics", heading_style))
        
        crops = {}
        diseases = {}
        for pred in predictions:
            crop = pred.get('crop', 'Unknown')
            disease = pred.get('disease', 'Unknown')
            crops[crop] = crops.get(crop, 0) + 1
            diseases[disease] = diseases.get(disease, 0) + 1
        
        stats_data = [['Category', 'Count']]
        for crop, count in sorted(crops.items()):
            stats_data.append([f'Crop: {crop.capitalize()}', str(count)])
        
        stats_table = Table(stats_data, colWidths=[3*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add page break if too many predictions
        if len(predictions) > 5:
            elements.append(PageBreak())
        
        # Predictions table
        elements.append(Paragraph("Recent Predictions", heading_style))
        
        pred_data = [['Date', 'Crop', 'Disease', 'Confidence', 'Fertilizer']]
        for pred in predictions[:20]:  # Limit to first 20
            confidence = float(pred.get('confidence', 0))
            pred_data.append([
                _text_or_na(pred.get('created_at'))[:10],
                _text_or_na(pred.get('crop')).capitalize(),
                _text_or_na(pred.get('disease')),
                f"{confidence * 100:.1f}%",
                Paragraph(_paragraph_text(pred.get('fertilizer_recommendation')), styles['BodyText'])
            ])
        
        pred_table = Table(pred_data, colWidths=[1.1*inch, 1.1*inch, 1.45*inch, 0.9*inch, 2.1*inch])
        pred_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ]))
        elements.append(pred_table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_history_report_csv(predictions: List[Dict]) -> str:
        """Generate CSV report for prediction history"""
        
        output = BytesIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            'Prediction ID',
            'Crop',
            'Disease',
            'Confidence (%)',
            'Severity',
            'Fertilizer Recommendation',
            'NPK Values',
            'Dosage',
            'Application Timing',
            'Spraying Interval',
            'Organic Alternative',
            'Prediction Date',
            'Status'
        ])
        
        # Data rows
        for pred in predictions:
            confidence = float(pred.get('confidence', 0)) * 100
            writer.writerow([
                pred.get('id', ''),
                pred.get('crop', '').capitalize(),
                pred.get('disease', ''),
                f"{confidence:.2f}",
                pred.get('severity', ''),
                pred.get('fertilizer_recommendation', ''),
                pred.get('npk_values', ''),
                pred.get('dosage', ''),
                pred.get('application_timing', ''),
                pred.get('spraying_interval', ''),
                pred.get('organic_alternative', ''),
                pred.get('created_at', ''),
                'Completed'
            ])
        
        return output.getvalue().decode('utf-8')
    
    @staticmethod
    def generate_analytics_report_csv(stats: Dict) -> str:
        """Generate CSV report for analytics data"""
        
        output = BytesIO()
        writer = csv.writer(output)
        
        # Write summary
        writer.writerow(['Analytics Report Generated: ' + datetime.utcnow().isoformat()])
        writer.writerow([])
        
        # Summary section
        writer.writerow(['Summary Statistics'])
        writer.writerow(['Metric', 'Value'])
        
        if isinstance(stats, dict):
            for key, value in stats.items():
                if not isinstance(value, (dict, list)):
                    writer.writerow([key, value])
        
        writer.writerow([])
        
        # Crop distribution
        if 'crop_distribution' in stats:
            writer.writerow(['Crop Distribution'])
            writer.writerow(['Crop', 'Count'])
            for crop, count in stats['crop_distribution'].items():
                writer.writerow([crop.capitalize(), count])
        
        return output.getvalue().decode('utf-8')


class ReportExporter:
    """Export reports to various formats"""
    
    @staticmethod
    def save_pdf(buffer: BytesIO, filename: str) -> str:
        """Save PDF buffer to file"""
        os.makedirs('reports', exist_ok=True)
        filepath = os.path.join('reports', filename)
        
        with open(filepath, 'wb') as f:
            f.write(buffer.getvalue())
        
        return filepath
    
    @staticmethod
    def save_csv(content: str, filename: str) -> str:
        """Save CSV content to file"""
        os.makedirs('reports', exist_ok=True)
        filepath = os.path.join('reports', filename)
        
        with open(filepath, 'w', newline='') as f:
            f.write(content)
        
        return filepath
