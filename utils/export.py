"""
Export Functions for Excel and PDF
"""

import io
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ExportManager:
    """Manage exports to Excel and PDF"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet() if REPORTLAB_AVAILABLE else None
    
    def export_products_to_excel(
        self,
        products: List[Dict],
        include_specs: bool = True,
        include_licenses: bool = True,
        include_accessories: bool = False
    ) -> io.BytesIO:
        """
        Export products to Excel file
        
        Returns BytesIO buffer with Excel file
        """
        output = io.BytesIO()
        
        # Create Excel writer
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Main product sheet
            product_data = self._prepare_product_data(products, include_specs)
            df_products = pd.DataFrame(product_data)
            df_products.to_excel(writer, sheet_name='Produkte', index=False)
            
            # License sheet
            if include_licenses:
                license_data = self._prepare_license_data(products)
                if license_data:
                    df_licenses = pd.DataFrame(license_data)
                    df_licenses.to_excel(writer, sheet_name='Lizenzen', index=False)
            
            # Accessories sheet
            if include_accessories:
                accessory_data = self._prepare_accessory_data(products)
                if accessory_data:
                    df_accessories = pd.DataFrame(accessory_data)
                    df_accessories.to_excel(writer, sheet_name='Zubehör', index=False)
            
            # Format worksheets
            self._format_excel_worksheets(writer)
        
        output.seek(0)
        return output
    
    def export_project_bom_to_excel(
        self,
        project_name: str,
        project_items: List[Dict],
        include_summary: bool = True
    ) -> io.BytesIO:
        """
        Export project Bill of Materials (BOM) to Excel
        
        project_items format:
        [
            {
                'product_name': str,
                'sku': str,
                'quantity': int,
                'category': str,
                'comment': str (optional)
            }
        ]
        """
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # BOM Sheet
            df_bom = pd.DataFrame(project_items)
            df_bom.to_excel(writer, sheet_name='Stückliste', index=False)
            
            # Summary Sheet
            if include_summary:
                summary_data = self._prepare_project_summary(project_name, project_items)
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Zusammenfassung', index=False)
            
            # Format
            self._format_bom_worksheets(writer, project_name)
        
        output.seek(0)
        return output
    
    def export_products_to_pdf(
        self,
        products: List[Dict],
        title: str = "Produktkatalog",
        include_details: bool = True
    ) -> io.BytesIO:
        """
        Export products to PDF
        
        Returns BytesIO buffer with PDF file
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF export")
        
        output = io.BytesIO()
        doc = SimpleDocTemplate(
            output,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=12
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Metadata
        meta_style = self.styles['Normal']
        story.append(Paragraph(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}", meta_style))
        story.append(Paragraph(f"Anzahl Produkte: {len(products)}", meta_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Products table
        if include_details:
            table_data = self._prepare_pdf_detailed_table(products)
        else:
            table_data = self._prepare_pdf_simple_table(products)
        
        # Create table
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        story.append(table)
        
        # Build PDF
        doc.build(story)
        output.seek(0)
        return output
    
    def export_project_bom_to_pdf(
        self,
        project_name: str,
        project_items: List[Dict],
        customer_info: Optional[Dict] = None
    ) -> io.BytesIO:
        """
        Export project BOM to PDF
        
        customer_info format:
        {
            'name': str,
            'contact': str,
            'date': str
        }
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF export")
        
        output = io.BytesIO()
        doc = SimpleDocTemplate(
            output,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=12
        )
        story.append(Paragraph(f"Stückliste: {project_name}", title_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Customer info
        if customer_info:
            info_style = self.styles['Normal']
            story.append(Paragraph(f"<b>Kunde:</b> {customer_info.get('name', 'N/A')}", info_style))
            story.append(Paragraph(f"<b>Kontakt:</b> {customer_info.get('contact', 'N/A')}", info_style))
            story.append(Paragraph(f"<b>Datum:</b> {customer_info.get('date', datetime.now().strftime('%d.%m.%Y'))}", info_style))
            story.append(Spacer(1, 0.5*cm))
        
        # BOM Table
        table_data = [['Pos.', 'Produktname', 'SKU', 'Menge', 'Kategorie', 'Kommentar']]
        
        for idx, item in enumerate(project_items, start=1):
            table_data.append([
                str(idx),
                item.get('product_name', ''),
                item.get('sku', ''),
                str(item.get('quantity', 1)),
                item.get('category', ''),
                item.get('comment', '')
            ])
        
        table = Table(table_data, colWidths=[1.5*cm, 5*cm, 3*cm, 2*cm, 3*cm, 5.5*cm])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Pos. centered
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Quantity centered
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 1*cm))
        
        # Summary
        summary_style = self.styles['Normal']
        story.append(Paragraph(f"<b>Gesamtanzahl Positionen:</b> {len(project_items)}", summary_style))
        total_quantity = sum(item.get('quantity', 1) for item in project_items)
        story.append(Paragraph(f"<b>Gesamtmenge:</b> {total_quantity} Stück", summary_style))
        
        # Build PDF
        doc.build(story)
        output.seek(0)
        return output
    
    # Helper methods
    
    def _prepare_product_data(self, products: List[Dict], include_specs: bool) -> List[Dict]:
        """Prepare product data for Excel export"""
        data = []
        
        for product in products:
            row = {
                'Name': product.get('name', ''),
                'Kategorie': product.get('category', ''),
                'Unterkategorie': product.get('subcategory', ''),
                'SKU': product.get('sku_base', ''),
                'Status': product.get('status', ''),
            }
            
            if include_specs:
                # Add category-specific specs
                if product.get('category') in ['MR', 'Catalyst AP']:
                    row['Wi-Fi Standard'] = product.get('wifi_standard', '')
                    row['Max. Data Rate'] = product.get('max_data_rate', '')
                    row['PoE Anforderung'] = product.get('poe_requirement', '')
                    row['Empf. Clients'] = product.get('recommended_clients', '')
                
                elif product.get('category') == 'MX':
                    row['Firewall Throughput'] = product.get('firewall_throughput', '')
                    row['VPN Throughput'] = product.get('vpn_throughput', '')
                    row['Max VPN Tunnel'] = product.get('max_vpn_tunnels', '')
                    row['Empf. User'] = product.get('recommended_users', '')
                
                elif product.get('category') in ['MS', 'Catalyst Switch']:
                    row['Ports Gesamt'] = product.get('total_ports', '')
                    row['PoE Ports'] = product.get('poe_ports', 0)
                    row['PoE Budget'] = product.get('poe_budget', '')
                    row['Stacking'] = product.get('stacking', '')
                
                elif product.get('category') == 'ISE':
                    row['Deployment Typ'] = product.get('deployment_type', '')
                    row['Max. Endpoints'] = product.get('recommended_endpoints', '')
                    row['CPU'] = product.get('cpu', '')
                    row['RAM'] = product.get('ram', '')
            
            row['EOL Datum'] = product.get('eos_date', '')
            row['Datasheet URL'] = product.get('datasheet_url', '')
            
            data.append(row)
        
        return data
    
    def _prepare_license_data(self, products: List[Dict]) -> List[Dict]:
        """Prepare license data for Excel export"""
        data = []
        
        for product in products:
            licenses = product.get('sku_licenses', {})
            if licenses:
                for license_type, sku in licenses.items():
                    data.append({
                        'Produkt': product.get('name', ''),
                        'Produkt SKU': product.get('sku_base', ''),
                        'Lizenz-Typ': license_type.replace('_', ' ').title(),
                        'Lizenz SKU': sku
                    })
        
        return data
    
    def _prepare_accessory_data(self, products: List[Dict]) -> List[Dict]:
        """Prepare accessory data for Excel export"""
        data = []
        
        for product in products:
            accessories = product.get('accessories', [])
            if accessories:
                for acc_id in accessories:
                    data.append({
                        'Produkt': product.get('name', ''),
                        'Produkt SKU': product.get('sku_base', ''),
                        'Zubehör ID': acc_id
                    })
        
        return data
    
    def _prepare_project_summary(self, project_name: str, items: List[Dict]) -> List[Dict]:
        """Prepare project summary"""
        # Category breakdown
        category_count = {}
        for item in items:
            cat = item.get('category', 'Sonstiges')
            category_count[cat] = category_count.get(cat, 0) + item.get('quantity', 1)
        
        summary = [
            {'Feld': 'Projektname', 'Wert': project_name},
            {'Feld': 'Erstellt am', 'Wert': datetime.now().strftime('%d.%m.%Y %H:%M')},
            {'Feld': 'Anzahl Positionen', 'Wert': len(items)},
            {'Feld': 'Gesamtmenge', 'Wert': sum(item.get('quantity', 1) for item in items)},
            {'Feld': '', 'Wert': ''},
            {'Feld': 'Kategorie-Übersicht', 'Wert': ''},
        ]
        
        for cat, count in category_count.items():
            summary.append({'Feld': f'  {cat}', 'Wert': count})
        
        return summary
    
    def _prepare_pdf_simple_table(self, products: List[Dict]) -> List[List[str]]:
        """Prepare simple product table for PDF"""
        data = [['Name', 'Kategorie', 'SKU', 'Status']]
        
        for product in products:
            data.append([
                product.get('name', ''),
                product.get('category', ''),
                product.get('sku_base', ''),
                product.get('status', '')
            ])
        
        return data
    
    def _prepare_pdf_detailed_table(self, products: List[Dict]) -> List[List[str]]:
        """Prepare detailed product table for PDF"""
        data = [['Name', 'Kategorie', 'SKU', 'Wichtige Specs', 'Status']]
        
        for product in products:
            # Category-specific key specs
            specs = ""
            if product.get('category') in ['MR', 'Catalyst AP']:
                specs = f"{product.get('wifi_standard', '')}, {product.get('poe_requirement', '')}"
            elif product.get('category') == 'MX':
                specs = f"FW: {product.get('firewall_throughput', '')}, VPN: {product.get('vpn_throughput', '')}"
            elif product.get('category') in ['MS', 'Catalyst Switch']:
                specs = f"{product.get('total_ports', '')} Ports, PoE: {product.get('poe_budget', '0W')}"
            elif product.get('category') == 'ISE':
                specs = f"{product.get('recommended_endpoints', '')}"
            
            data.append([
                product.get('name', ''),
                product.get('category', ''),
                product.get('sku_base', ''),
                specs,
                product.get('status', '')
            ])
        
        return data
    
    def _format_excel_worksheets(self, writer):
        """Format Excel worksheets with styling"""
        workbook = writer.book
        
        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            
            # Header formatting
            for cell in worksheet[1]:
                cell.font = cell.font.copy(bold=True, color='FFFFFF')
                cell.fill = cell.fill.copy(fgColor='0066CC', patternType='solid')
                cell.alignment = cell.alignment.copy(horizontal='center')
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _format_bom_worksheets(self, writer, project_name: str):
        """Format BOM worksheets"""
        self._format_excel_worksheets(writer)
        
        # Add project name to header
        workbook = writer.book
        if 'Stückliste' in workbook.sheetnames:
            worksheet = workbook['Stückliste']
            worksheet.insert_rows(1)
            worksheet['A1'] = f"Projekt: {project_name}"
            worksheet['A1'].font = worksheet['A1'].font.copy(bold=True, size=14)


# Global instance
def get_export_manager():
    """Get ExportManager instance"""
    return ExportManager()

