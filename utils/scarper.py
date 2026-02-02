"""
Web Scraper for Cisco and Meraki Product Information
Automatically fetches product specs, EOL dates, and SKUs from official sources
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
import time
import streamlit as st

class CiscoMerakiScraper:
    """Scrape product information from official Cisco and Meraki websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Base URLs
        self.base_urls = {
            'meraki_docs': 'https://documentation.meraki.com',
            'meraki_eol': 'https://documentation.meraki.com/General_Administration/Other_Topics/Meraki_End-of-Life_(EOL)_Product_Dates',
            'cisco_eol': 'https://www.cisco.com/c/en/us/products/eos-eol-listing.html',
            'meraki_datasheet_base': 'https://documentation.meraki.com/{category}/Product_Information/Overviews_and_Datasheets',
        }
        
        self.rate_limit_delay = 2  # seconds between requests
    
    def scrape_meraki_eol_dates(self) -> Dict[str, Dict]:
        """
        Scrape EOL dates from Meraki documentation
        
        Returns:
        {
            'product_model': {
                'eol_announced': 'YYYY-MM-DD',
                'eos_date': 'YYYY-MM-DD',
                'status': 'Active' | 'EOL Announced' | 'End of Sale'
            }
        }
        """
        st.info("🔍 Scraping Meraki EOL Daten...")
        
        try:
            response = self.session.get(self.base_urls['meraki_eol'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            eol_data = {}
            
            # Find EOL tables
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        product = cols[0].get_text(strip=True)
                        eol_announced = cols[1].get_text(strip=True)
                        eos_date = cols[2].get_text(strip=True)
                        
                        # Parse dates
                        eol_announced_parsed = self._parse_date(eol_announced)
                        eos_date_parsed = self._parse_date(eos_date)
                        
                        # Determine status
                        status = self._determine_status(eol_announced_parsed, eos_date_parsed)
                        
                        # Extract model number
                        model = self._extract_model_number(product)
                        
                        if model:
                            eol_data[model.lower()] = {
                                'eol_announced': eol_announced_parsed,
                                'eos_date': eos_date_parsed,
                                'status': status,
                                'full_name': product
                            }
            
            st.success(f"✅ {len(eol_data)} EOL Einträge gefunden")
            time.sleep(self.rate_limit_delay)
            
            return eol_data
        
        except Exception as e:
            st.error(f"❌ Fehler beim Scrapen der EOL Daten: {str(e)}")
            return {}
    
    def scrape_product_datasheet(self, category: str, model: str) -> Optional[Dict]:
        """
        Scrape product specifications from datasheet pages
        
        Args:
            category: 'MR', 'MX', 'MS', etc.
            model: Product model (e.g., 'MR46')
        
        Returns:
            Dict with product specifications or None
        """
        st.info(f"🔍 Scraping Datasheet für {model}...")
        
        try:
            # Construct datasheet URL
            datasheet_url = f"{self.base_urls['meraki_docs']}/{category}/Product_Information/Overviews_and_Datasheets/{model}_Datasheet"
            
            response = self.session.get(datasheet_url, timeout=10)
            
            if response.status_code == 404:
                st.warning(f"⚠️ Datasheet nicht gefunden: {datasheet_url}")
                return None
            
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            specs = {
                'model': model,
                'datasheet_url': datasheet_url,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract specifications from tables
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['th', 'td'])
                    if len(cols) >= 2:
                        key = cols[0].get_text(strip=True)
                        value = cols[1].get_text(strip=True)
                        
                        # Map common spec names
                        spec_key = self._map_spec_name(key)
                        if spec_key:
                            specs[spec_key] = value
            
            # Extract SKUs
            skus = self._extract_skus_from_page(soup, model)
            if skus:
                specs['sku_base'] = skus.get('hardware')
                specs['sku_licenses'] = skus.get('licenses', {})
            
            st.success(f"✅ Datasheet für {model} erfolgreich gescraped")
            time.sleep(self.rate_limit_delay)
            
            return specs
        
        except Exception as e:
            st.error(f"❌ Fehler beim Scrapen von {model}: {str(e)}")
            return None
    
    def scrape_meraki_mr_models(self) -> List[str]:
        """
        Scrape list of current MR models from Meraki documentation
        
        Returns:
            List of model names (e.g., ['MR20', 'MR28', 'MR46'])
        """
        st.info("🔍 Scraping MR Produktliste...")
        
        try:
            url = f"{self.base_urls['meraki_docs']}/MR/Product_Information"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            models = set()
            
            # Find all links mentioning MR models
            links = soup.find_all('a', href=True)
            
            for link in links:
                text = link.get_text()
                # Match MR followed by digits (MR20, MR46, etc.)
                match = re.search(r'MR\d+[A-Z]*', text)
                if match:
                    models.add(match.group(0))
            
            models_list = sorted(list(models))
            st.success(f"✅ {len(models_list)} MR Modelle gefunden")
            time.sleep(self.rate_limit_delay)
            
            return models_list
        
        except Exception as e:
            st.error(f"❌ Fehler beim Scrapen der MR Modelle: {str(e)}")
            return []
    
    def scrape_cisco_ise_models(self) -> List[Dict]:
        """
        Scrape ISE appliance models and specs from Cisco website
        
        Returns:
            List of ISE model specifications
        """
        st.info("🔍 Scraping ISE Modelle...")
        
        try:
            url = "https://www.cisco.com/c/en/us/products/security/identity-services-engine/models-comparison.html"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            models = []
            
            # Find comparison table
            tables = soup.find_all('table', class_='comparison-table')
            
            for table in tables:
                rows = table.find_all('tr')
                headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]
                
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= len(headers):
                        model_data = {}
                        for i, col in enumerate(cols):
                            if i < len(headers):
                                model_data[headers[i]] = col.get_text(strip=True)
                        
                        models.append(model_data)
            
            st.success(f"✅ {len(models)} ISE Modelle gefunden")
            time.sleep(self.rate_limit_delay)
            
            return models
        
        except Exception as e:
            st.error(f"❌ Fehler beim Scrapen der ISE Modelle: {str(e)}")
            return []
    
    def update_product_database_with_eol(self, product_loader) -> int:
        """
        Update local product database with scraped EOL information
        
        Args:
            product_loader: ProductLoader instance
        
        Returns:
            Number of products updated
        """
        st.info("🔄 Aktualisiere Produktdatenbank mit EOL Daten...")
        
        eol_data = self.scrape_meraki_eol_dates()
        
        if not eol_data:
            st.warning("⚠️ Keine EOL Daten zum Aktualisieren gefunden")
            return 0
        
        updated_count = 0
        
        for category in ['mr', 'mx', 'ms', 'mv']:
            products = product_loader.get_products_by_category(category)
            
            for product in products:
                product_id = product.get('id', '').lower()
                model_name = product.get('name', '').split()[-1].lower()  # Get last part (e.g., "MR46" from "Meraki MR46")
                
                # Check if EOL data exists
                eol_info = eol_data.get(product_id) or eol_data.get(model_name)
                
                if eol_info:
                    # Update product
                    product['eol_announced'] = eol_info.get('eol_announced')
                    product['eos_date'] = eol_info.get('eos_date')
                    product['status'] = eol_info.get('status')
                    
                    # Save updated product
                    product_loader.save_product(category, product)
                    updated_count += 1
                    
                    st.success(f"✅ {product.get('name')}: Status aktualisiert auf '{eol_info.get('status')}'")
        
        st.success(f"🎉 {updated_count} Produkte aktualisiert!")
        return updated_count
    
    def scrape_all_mr_datasheets(self, product_loader) -> int:
        """
        Scrape all MR product datasheets and update database
        
        Returns:
            Number of products updated
        """
        models = self.scrape_meraki_mr_models()
        
        if not models:
            st.warning("⚠️ Keine MR Modelle zum Scrapen gefunden")
            return 0
        
        updated_count = 0
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, model in enumerate(models):
            status_text.text(f"Scraping {i+1}/{len(models)}: {model}")
            progress_bar.progress((i + 1) / len(models))
            
            specs = self.scrape_product_datasheet('MR', model)
            
            if specs:
                # Find existing product or create new
                product_id = model.lower()
                existing_product = product_loader.get_product_by_id(product_id)
                
                if existing_product:
                    # Update existing
                    existing_product.update(specs)
                    product_loader.save_product('mr', existing_product)
                else:
                    # Create new product entry
                    new_product = {
                        'id': product_id,
                        'name': f'Meraki {model}',
                        'category': 'MR',
                        **specs
                    }
                    product_loader.save_product('mr', new_product)
                
                updated_count += 1
        
        progress_bar.empty()
        status_text.empty()
        
        st.success(f"🎉 {updated_count} MR Produkte aktualisiert!")
        return updated_count
    
    # Helper methods
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format (YYYY-MM-DD)"""
        if not date_str or date_str.lower() in ['n/a', 'tbd', '-']:
            return None
        
        try:
            # Try common formats
            for fmt in ['%B %d, %Y', '%m/%d/%Y', '%Y-%m-%d', '%d.%m.%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If all fails, return original
            return date_str
        except:
            return None
    
    def _determine_status(self, eol_announced: Optional[str], eos_date: Optional[str]) -> str:
        """Determine product status based on dates"""
        if not eos_date:
            return "Active"
        
        try:
            eos_dt = datetime.fromisoformat(eos_date)
            today = datetime.now()
            
            if eos_dt < today:
                return "End of Sale"
            elif eol_announced:
                return "EOL Announced"
            else:
                return "Active"
        except:
            return "Active"
    
    def _extract_model_number(self, product_name: str) -> Optional[str]:
        """Extract model number from product name"""
        # Match patterns like MR46, MX250, MS225-48FP, etc.
        match = re.search(r'(MR|MX|MS|MV|MT)\d+[A-Z]*(-\d+[A-Z]*)?', product_name)
        return match.group(0) if match else None
    
    def _map_spec_name(self, raw_name: str) -> Optional[str]:
        """Map scraped spec names to standardized field names"""
        mapping = {
            'Wi-Fi Standard': 'wifi_standard',
            'Maximum Data Rate': 'max_data_rate',
            'Spatial Streams': 'spatial_streams',
            'Frequency Bands': 'frequency_bands',
            'PoE Requirement': 'poe_requirement',
            'Power Consumption': 'max_power_consumption',
            'Ethernet Ports': 'ethernet_ports',
            'Dimensions': 'dimensions',
            'Weight': 'weight',
            'Operating Temperature': 'operating_temp',
            'Firewall Throughput': 'firewall_throughput',
            'VPN Throughput': 'vpn_throughput',
            'Recommended Users': 'recommended_users',
            'Total Ports': 'total_ports',
            'PoE Budget': 'poe_budget',
            'Switching Capacity': 'switching_capacity',
        }
        
        for key, value in mapping.items():
            if key.lower() in raw_name.lower():
                return value
        
        return None
    
    def _extract_skus_from_page(self, soup: BeautifulSoup, model: str) -> Optional[Dict]:
        """Extract SKUs from product page"""
        skus = {
            'hardware': None,
            'licenses': {}
        }
        
        # Look for SKU mentions in text
        text = soup.get_text()
        
        # Hardware SKU pattern (e.g., MR46-HW)
        hw_match = re.search(rf'{model}-HW', text, re.IGNORECASE)
        if hw_match:
            skus['hardware'] = hw_match.group(0).upper()
        
        # License SKU patterns (e.g., LIC-ENT-1YR, LIC-MX67-SEC-3YR)
        license_matches = re.findall(r'LIC-[A-Z0-9-]+', text)
        
        for lic_sku in license_matches:
            # Determine license type from SKU
            if 'ENT' in lic_sku:
                if '1YR' in lic_sku:
                    skus['licenses']['1_year_ent'] = lic_sku
                elif '3YR' in lic_sku:
                    skus['licenses']['3_year_ent'] = lic_sku
                elif '5YR' in lic_sku:
                    skus['licenses']['5_year_ent'] = lic_sku
            elif 'SEC' in lic_sku or 'ADV' in lic_sku:
                if '1YR' in lic_sku:
                    skus['licenses']['1_year_adv'] = lic_sku
                elif '3YR' in lic_sku:
                    skus['licenses']['3_year_adv'] = lic_sku
                elif '5YR' in lic_sku:
                    skus['licenses']['5_year_adv'] = lic_sku
        
        return skus if skus['hardware'] or skus['licenses'] else None
    
    def export_scraped_data(self, data: Dict, filename: str):
        """Export scraped data to JSON file"""
        try:
            with open(f"data/scraped/{filename}", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            st.success(f"✅ Daten exportiert nach: data/scraped/{filename}")
        except Exception as e:
            st.error(f"❌ Fehler beim Exportieren: {str(e)}")


# Global instance
def get_scraper():
    """Get CiscoMerakiScraper instance"""
    return CiscoMerakiScraper()

