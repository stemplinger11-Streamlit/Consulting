"""
Filter Functions for Product Catalog
"""

import streamlit as st
from typing import List, Dict, Optional

def create_filter_sidebar(product_loader, category: Optional[str] = None) -> Dict:
    """
    Create filter sidebar for product catalog
    Returns dict of active filters
    """
    st.sidebar.markdown("### 🔍 Filter")
    
    filters = {}
    
    # Category Filter (if not pre-selected)
    if not category:
        categories = ["All", "MR", "MX", "MS", "Catalyst AP", "Catalyst Switch", "ISE"]
        filters['category'] = st.sidebar.selectbox(
            "Produktkategorie",
            categories,
            index=0
        )
    else:
        filters['category'] = category
    
    # Get products for current category
    if filters['category'] == "All":
        products = product_loader.get_all_products()
    else:
        cat_key = filters['category'].lower().replace(" ", "_")
        products = product_loader.get_products_by_category(cat_key)
    
    # Dynamic filters based on category
    if filters['category'] in ["MR", "Catalyst AP"]:
        # Wi-Fi Access Point Filters
        subcategories = product_loader.get_unique_values('subcategory', 
            None if filters['category'] == "All" else filters['category'].lower().replace(" ", "_"))
        if subcategories:
            filters['subcategory'] = st.sidebar.selectbox(
                "Einsatzbereich",
                ["All"] + subcategories,
                index=0
            )
        
        wifi_standards = product_loader.get_unique_values('wifi_standard',
            None if filters['category'] == "All" else filters['category'].lower().replace(" ", "_"))
        if wifi_standards:
            filters['wifi_standard'] = st.sidebar.selectbox(
                "Wi-Fi Standard",
                ["All"] + wifi_standards,
                index=0
            )
        
        poe_requirements = product_loader.get_unique_values('poe_requirement',
            None if filters['category'] == "All" else filters['category'].lower().replace(" ", "_"))
        if poe_requirements:
            filters['poe_requirement'] = st.sidebar.selectbox(
                "PoE Anforderung",
                ["All"] + poe_requirements,
                index=0
            )
    
    elif filters['category'] in ["MX"]:
        # Firewall Filters
        subcategories = product_loader.get_unique_values('subcategory', 'mx')
        if subcategories:
            filters['subcategory'] = st.sidebar.selectbox(
                "Deployment-Größe",
                ["All"] + subcategories,
                index=0
            )
        
        # Throughput slider
        st.sidebar.markdown("**Firewall Throughput (Gbps)**")
        throughput_min = st.sidebar.number_input(
            "Minimum (Gbps)",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.5
        )
        if throughput_min > 0:
            filters['min_throughput'] = throughput_min
    
    elif filters['category'] in ["MS", "Catalyst Switch"]:
        # Switch Filters
        subcategories = product_loader.get_unique_values('subcategory',
            'ms' if filters['category'] == "MS" else 'catalyst_switch')
        if subcategories:
            filters['subcategory'] = st.sidebar.selectbox(
                "Switch-Typ",
                ["All"] + subcategories,
                index=0
            )
        
        # Port count
        st.sidebar.markdown("**Port-Anzahl**")
        port_options = ["All", "8", "24", "48", "16", "32"]
        filters['port_count'] = st.sidebar.selectbox(
            "Ports",
            port_options,
            index=0
        )
        
        # PoE Support
        filters['poe_support'] = st.sidebar.selectbox(
            "PoE Unterstützung",
            ["All", "Ja", "Nein"],
            index=0
        )
        
        # Stacking
        filters['stacking'] = st.sidebar.selectbox(
            "Stacking",
            ["All", "Ja", "Nein"],
            index=0
        )
    
    elif filters['category'] == "ISE":
        # ISE Filters
        deployment_types = product_loader.get_unique_values('deployment_type', 'ise')
        if deployment_types:
            filters['deployment_type'] = st.sidebar.selectbox(
                "Deployment-Typ",
                ["All"] + deployment_types,
                index=0
            )
        
        # Endpoint count
        st.sidebar.markdown("**Max. Endpoints**")
        endpoint_options = ["All", "Up to 5,000", "Up to 50,000", "Up to 100,000", "Up to 200,000", "Up to 500,000"]
        filters['recommended_endpoints'] = st.sidebar.selectbox(
            "Empfohlene Endpoints",
            endpoint_options,
            index=0
        )
    
    # Common Filters
    st.sidebar.markdown("---")
    
    # Status Filter
    filters['status'] = st.sidebar.selectbox(
        "Status",
        ["All", "Active", "EOL Announced"],
        index=0
    )
    
    # Search
    st.sidebar.markdown("---")
    search_query = st.sidebar.text_input("🔎 Suche", placeholder="Name, SKU, ID...")
    if search_query:
        filters['search'] = search_query
    
    return filters


def apply_filters(products: List[Dict], filters: Dict) -> List[Dict]:
    """Apply filters to product list"""
    filtered = products.copy()
    
    # Category filter
    if filters.get('category') and filters['category'] != "All":
        filtered = [p for p in filtered if p.get('category') == filters['category']]
    
    # Subcategory filter
    if filters.get('subcategory') and filters['subcategory'] != "All":
        filtered = [p for p in filtered if p.get('subcategory') == filters['subcategory']]
    
    # Wi-Fi Standard filter
    if filters.get('wifi_standard') and filters['wifi_standard'] != "All":
        filtered = [p for p in filtered if p.get('wifi_standard') == filters['wifi_standard']]
    
    # PoE Requirement filter
    if filters.get('poe_requirement') and filters['poe_requirement'] != "All":
        filtered = [p for p in filtered if p.get('poe_requirement') == filters['poe_requirement']]
    
    # Throughput filter (MX)
    if filters.get('min_throughput'):
        filtered = [p for p in filtered 
                   if float(p.get('firewall_throughput', '0').replace(' Gbps', '').replace(' Mbps', '')) 
                   >= filters['min_throughput']]
    
    # Port count filter
    if filters.get('port_count') and filters['port_count'] != "All":
        port_count = int(filters['port_count'])
        filtered = [p for p in filtered if p.get('total_ports') == port_count]
    
    # PoE Support filter
    if filters.get('poe_support') and filters['poe_support'] != "All":
        has_poe = filters['poe_support'] == "Ja"
        filtered = [p for p in filtered 
                   if (p.get('poe_ports', 0) > 0) == has_poe or 
                   (p.get('poe_support') == "Yes") == has_poe]
    
    # Stacking filter
    if filters.get('stacking') and filters['stacking'] != "All":
        has_stacking = filters['stacking'] == "Ja"
        filtered = [p for p in filtered 
                   if (p.get('stacking') == "Yes") == has_stacking or
                   (p.get('stacking') is True) == has_stacking]
    
    # Deployment type filter (ISE)
    if filters.get('deployment_type') and filters['deployment_type'] != "All":
        filtered = [p for p in filtered if p.get('deployment_type') == filters['deployment_type']]
    
    # Endpoint count filter (ISE)
    if filters.get('recommended_endpoints') and filters['recommended_endpoints'] != "All":
        filtered = [p for p in filtered 
                   if p.get('recommended_endpoints') == filters['recommended_endpoints']]
    
    # Status filter
    if filters.get('status') and filters['status'] != "All":
        filtered = [p for p in filtered if p.get('status') == filters['status']]
    
    # Search filter
    if filters.get('search'):
        query = filters['search'].lower()
        filtered = [p for p in filtered 
                   if query in p.get('name', '').lower() or
                   query in p.get('id', '').lower() or
                   query in p.get('sku_base', '').lower()]
    
    return filtered

