"""
Product Loader Utility
Loads and manages product data from JSON files
"""

import json
import os
from typing import List, Dict, Optional
import streamlit as st

class ProductLoader:
    def __init__(self):
        self.data_dir = "data"
        self.products = {}
        self.accessories = []
        self.load_all_products()
        self.load_accessories()
    
    @st.cache_data
    def load_json_file(_self, filename: str) -> dict:
        """Load JSON file from data directory"""
        filepath = os.path.join(_self.data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            st.warning(f"⚠️ Datei nicht gefunden: {filename}")
            return {"products": []} if "products" in filename else {"accessories": []}
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON Fehler in {filename}: {str(e)}")
            return {"products": []} if "products" in filename else {"accessories": []}
    
    def load_all_products(self):
        """Load all product JSON files"""
        product_files = [
            "products_mr.json",
            "products_mx.json",
            "products_ms.json",
            "products_mv.json",
            "products_mt.json",
            "products_catalyst_ap.json",
            "products_catalyst_switch.json",
            "products_ise.json"
        ]
        
        for filename in product_files:
            data = self.load_json_file(filename)
            if "products" in data:
                category_key = filename.replace("products_", "").replace(".json", "")
                self.products[category_key] = data["products"]
    
    def load_accessories(self):
        """Load accessories data"""
        data = self.load_json_file("accessories.json")
        if "accessories" in data:
            self.accessories = data["accessories"]
    
    def get_all_products(self) -> List[Dict]:
        """Get all products from all categories"""
        all_products = []
        for category, products in self.products.items():
            for product in products:
                product['_category_file'] = category
                all_products.append(product)
        return all_products
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Get products by category (MR, MX, MS, etc.)"""
        return self.products.get(category.lower(), [])
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get single product by ID"""
        for products in self.products.values():
            for product in products:
                if product.get('id') == product_id:
                    return product
        return None
    
    def get_accessories_by_product(self, product_id: str) -> List[Dict]:
        """Get compatible accessories for a product"""
        compatible = []
        for accessory in self.accessories:
            if product_id in accessory.get('compatible_products', []):
                compatible.append(accessory)
        return compatible
    
    def get_accessory_by_id(self, accessory_id: str) -> Optional[Dict]:
        """Get single accessory by ID"""
        for accessory in self.accessories:
            if accessory.get('id') == accessory_id:
                return accessory
        return None
    
    def search_products(self, query: str) -> List[Dict]:
        """Search products by name, ID, or SKU"""
        query = query.lower()
        results = []
        
        for product in self.get_all_products():
            if (query in product.get('name', '').lower() or
                query in product.get('id', '').lower() or
                query in product.get('sku_base', '').lower() or
                query in product.get('category', '').lower()):
                results.append(product)
        
        return results
    
    def filter_products(self, filters: Dict) -> List[Dict]:
        """
        Filter products based on multiple criteria
        
        filters example:
        {
            'category': 'MR',
            'subcategory': 'Indoor',
            'wifi_standard': 'Wi-Fi 6',
            'poe_requirement': '802.3at',
            'status': 'Active'
        }
        """
        results = self.get_all_products()
        
        for key, value in filters.items():
            if value and value != "All":
                results = [p for p in results if p.get(key) == value]
        
        return results
    
    def get_unique_values(self, field: str, category: Optional[str] = None) -> List[str]:
        """Get unique values for a field (for filter dropdowns)"""
        products = self.get_products_by_category(category) if category else self.get_all_products()
        values = set()
        
        for product in products:
            value = product.get(field)
            if value:
                values.add(value)
        
        return sorted(list(values))
    
    def get_products_by_status(self, status: str = "Active") -> List[Dict]:
        """Get products by EOL status"""
        return [p for p in self.get_all_products() if p.get('status') == status]
    
    def get_eol_products(self) -> List[Dict]:
        """Get products with EOL announced"""
        return [p for p in self.get_all_products() 
                if p.get('eol_announced') is not None]
    
    def save_product(self, category: str, product: Dict):
        """Save/update a product to JSON file"""
        filename = f"products_{category.lower()}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        # Load current data
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update or add product
        product_exists = False
        for i, p in enumerate(data['products']):
            if p['id'] == product['id']:
                data['products'][i] = product
                product_exists = True
                break
        
        if not product_exists:
            data['products'].append(product)
        
        # Save back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Reload products
        self.load_all_products()
    
    def delete_product(self, category: str, product_id: str):
        """Delete a product from JSON file"""
        filename = f"products_{category.lower()}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        # Load current data
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Remove product
        data['products'] = [p for p in data['products'] if p['id'] != product_id]
        
        # Save back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Reload products
        self.load_all_products()


# Global instance
@st.cache_resource
def get_product_loader():
    """Get cached ProductLoader instance"""
    return ProductLoader()

