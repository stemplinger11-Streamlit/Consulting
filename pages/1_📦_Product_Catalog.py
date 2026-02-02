"""
Product Catalog Page
Browse, search, and filter all Cisco Meraki and Catalyst products
"""

import streamlit as st
from utils.auth import require_auth, get_current_user, is_admin
from utils.product_loader import get_product_loader
from utils.filters import create_filter_sidebar, apply_filters
from utils.export import get_export_manager
import json

# Require authentication
require_auth(lambda: main())

def main():
    st.title("📦 Produktkatalog")
    st.markdown("Durchsuche alle Cisco Meraki & Catalyst Produkte")
    
    # Load translations
    with open('data/translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    
    lang = st.session_state.get('language', 'de')
    t = translations[lang]
    
    # Initialize
    product_loader = get_product_loader()
    all_products = product_loader.get_all_products()
    
    # Sidebar filters
    filters = create_filter_sidebar(product_loader)
    
    # Apply filters
    filtered_products = apply_filters(all_products, filters)
    
    # Main content
    st.markdown("---")
    
    # Header with stats and actions
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.metric("📊 Gefundene Produkte", len(filtered_products))
    
    with col2:
        view_mode = st.selectbox(
            "Ansicht",
            ["Karten", "Tabelle", "Liste"],
            label_visibility="collapsed"
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sortieren",
            ["Name", "Kategorie", "Status"],
            label_visibility="collapsed"
        )
    
    with col4:
        export_mgr = get_export_manager()
        if st.button("📥 Export", use_container_width=True):
            st.session_state['show_export_dialog'] = True
    
    # Export dialog
    if st.session_state.get('show_export_dialog', False):
        with st.expander("📥 Export Optionen", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                include_specs = st.checkbox("Technische Specs einbeziehen", value=True)
                include_licenses = st.checkbox("Lizenzen einbeziehen", value=True)
            
            with col2:
                include_accessories = st.checkbox("Zubehör einbeziehen", value=False)
                export_format = st.radio("Format", ["Excel", "PDF"])
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("✅ Exportieren"):
                    with st.spinner("Export läuft..."):
                        if export_format == "Excel":
                            buffer = export_mgr.export_products_to_excel(
                                filtered_products,
                                include_specs=include_specs,
                                include_licenses=include_licenses,
                                include_accessories=include_accessories
                            )
                            st.download_button(
                                label="📥 Excel herunterladen",
                                data=buffer,
                                file_name=f"produktkatalog_{len(filtered_products)}_produkte.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:  # PDF
                            buffer = export_mgr.export_products_to_pdf(
                                filtered_products,
                                title=f"Produktkatalog ({len(filtered_products)} Produkte)",
                                include_details=include_specs
                            )
                            st.download_button(
                                label="📥 PDF herunterladen",
                                data=buffer,
                                file_name=f"produktkatalog_{len(filtered_products)}_produkte.pdf",
                                mime="application/pdf"
                            )
            
            with col2:
                if st.button("❌ Abbrechen"):
                    st.session_state['show_export_dialog'] = False
                    st.rerun()
    
    st.markdown("---")
    
    # Sort products
    if sort_by == "Name":
        filtered_products.sort(key=lambda x: x.get('name', ''))
    elif sort_by == "Kategorie":
        filtered_products.sort(key=lambda x: (x.get('category', ''), x.get('name', '')))
    elif sort_by == "Status":
        filtered_products.sort(key=lambda x: (x.get('status', ''), x.get('name', '')))
    
    # Display products
    if len(filtered_products) == 0:
        st.info("🔍 Keine Produkte gefunden. Passe die Filter an.")
    else:
        if view_mode == "Karten":
            display_card_view(filtered_products, product_loader)
        elif view_mode == "Tabelle":
            display_table_view(filtered_products)
        else:  # Liste
            display_list_view(filtered_products, product_loader)


def display_card_view(products, product_loader):
    """Display products as cards (3 per row)"""
    
    # Pagination
    items_per_page = 12
    total_pages = (len(products) - 1) // items_per_page + 1
    
    if 'catalog_page' not in st.session_state:
        st.session_state['catalog_page'] = 1
    
    page = st.session_state['catalog_page']
    
    # Page controls
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.markdown(f"**Seite {page} von {total_pages}**")
    
    # Get products for current page
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_products = products[start_idx:end_idx]
    
    # Display cards
    for i in range(0, len(page_products), 3):
        cols = st.columns(3)
        
        for j in range(3):
            if i + j < len(page_products):
                product = page_products[i + j]
                with cols[j]:
                    display_product_card(product, product_loader)
    
    # Pagination buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if page > 1:
            if st.button("◀ Zurück", use_container_width=True):
                st.session_state['catalog_page'] = page - 1
                st.rerun()
    
    with col3:
        if page < total_pages:
            if st.button("Weiter ▶", use_container_width=True):
                st.session_state['catalog_page'] = page + 1
                st.rerun()


def display_product_card(product, product_loader):
    """Display single product card"""
    
    # Status badge color
    status = product.get('status', 'Active')
    if status == 'Active':
        status_color = '🟢'
    elif status == 'EOL Announced':
        status_color = '🟡'
    else:
        status_color = '🔴'
    
    # Card container
    with st.container():
        st.markdown(f"""
        <div style='
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 16px;
            height: 320px;
            background-color: {'#fafafa' if st.session_state.get('theme') == 'light' else '#2d2d2d'};
        '>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown(f"### {product.get('name', 'N/A')}")
        st.caption(f"{status_color} {status}")
        
        # Category badge
        category = product.get('category', 'N/A')
        subcategory = product.get('subcategory', '')
        st.markdown(f"**`{category}`** {subcategory}")
        
        st.markdown("---")
        
        # Key specs (category-specific)
        if category in ['MR', 'Catalyst AP']:
            st.markdown(f"**Wi-Fi:** {product.get('wifi_standard', 'N/A')}")
            st.markdown(f"**PoE:** {product.get('poe_requirement', 'N/A')}")
            st.markdown(f"**Clients:** {product.get('recommended_clients', 'N/A')}")
        
        elif category == 'MX':
            st.markdown(f"**Throughput:** {product.get('firewall_throughput', 'N/A')}")
            st.markdown(f"**VPN:** {product.get('vpn_throughput', 'N/A')}")
            st.markdown(f"**Users:** {product.get('recommended_users', 'N/A')}")
        
        elif category in ['MS', 'Catalyst Switch']:
            st.markdown(f"**Ports:** {product.get('total_ports', 'N/A')}")
            st.markdown(f"**PoE:** {product.get('poe_budget', '0W')}")
            st.markdown(f"**Stacking:** {product.get('stacking', 'N/A')}")
        
        elif category == 'ISE':
            st.markdown(f"**Endpoints:** {product.get('recommended_endpoints', 'N/A')}")
            st.markdown(f"**Type:** {product.get('deployment_type', 'N/A')}")
        
        st.markdown("---")
        
        # Actions
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Details", key=f"details_{product.get('id')}", use_container_width=True):
                st.session_state['selected_product'] = product.get('id')
                st.session_state['show_product_details'] = True
        
        with col2:
            # Add to comparison
            if st.button("⚖️ Vergleich", key=f"compare_{product.get('id')}", use_container_width=True):
                if 'comparison_list' not in st.session_state:
                    st.session_state['comparison_list'] = []
                
                if product.get('id') not in st.session_state['comparison_list']:
                    st.session_state['comparison_list'].append(product.get('id'))
                    st.success(f"✅ {product.get('name')} zum Vergleich hinzugefügt")
                else:
                    st.info("ℹ️ Bereits im Vergleich")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Product details dialog
    if st.session_state.get('show_product_details') and st.session_state.get('selected_product') == product.get('id'):
        show_product_details_dialog(product, product_loader)


def display_table_view(products):
    """Display products as a data table"""
    
    import pandas as pd
    
    # Prepare table data
    table_data = []
    
    for product in products:
        row = {
            'Name': product.get('name', ''),
            'Kategorie': product.get('category', ''),
            'Unterkategorie': product.get('subcategory', ''),
            'SKU': product.get('sku_base', ''),
            'Status': product.get('status', '')
        }
        
        # Add category-specific columns
        category = product.get('category', '')
        
        if category in ['MR', 'Catalyst AP']:
            row['Wi-Fi'] = product.get('wifi_standard', '')
            row['PoE'] = product.get('poe_requirement', '')
        elif category == 'MX':
            row['FW Throughput'] = product.get('firewall_throughput', '')
            row['Users'] = product.get('recommended_users', '')
        elif category in ['MS', 'Catalyst Switch']:
            row['Ports'] = product.get('total_ports', '')
            row['PoE Budget'] = product.get('poe_budget', '')
        elif category == 'ISE':
            row['Endpoints'] = product.get('recommended_endpoints', '')
        
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    
    # Display with column configuration
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Kategorie": st.column_config.TextColumn("Kategorie", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small")
        }
    )


def display_list_view(products, product_loader):
    """Display products as a detailed list"""
    
    for product in products:
        with st.expander(f"**{product.get('name', 'N/A')}** - {product.get('category', '')} - {product.get('status', '')}"):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Kategorie:** {product.get('category', 'N/A')} / {product.get('subcategory', 'N/A')}")
                st.markdown(f"**SKU:** `{product.get('sku_base', 'N/A')}`")
                st.markdown(f"**Status:** {product.get('status', 'N/A')}")
                
                if product.get('eol_announced'):
                    st.warning(f"⚠️ EOL Announced: {product.get('eol_announced')}")
                if product.get('eos_date'):
                    st.error(f"🛑 End of Sale: {product.get('eos_date')}")
                
                # Key specs
                st.markdown("**Wichtige Spezifikationen:**")
                category = product.get('category', '')
                
                if category in ['MR', 'Catalyst AP']:
                    st.markdown(f"- Wi-Fi Standard: {product.get('wifi_standard', 'N/A')}")
                    st.markdown(f"- Max. Data Rate: {product.get('max_data_rate', 'N/A')}")
                    st.markdown(f"- PoE Requirement: {product.get('poe_requirement', 'N/A')}")
                    st.markdown(f"- Recommended Clients: {product.get('recommended_clients', 'N/A')}")
                
                elif category == 'MX':
                    st.markdown(f"- Firewall Throughput: {product.get('firewall_throughput', 'N/A')}")
                    st.markdown(f"- VPN Throughput: {product.get('vpn_throughput', 'N/A')}")
                    st.markdown(f"- Max VPN Tunnels: {product.get('max_vpn_tunnels', 'N/A')}")
                    st.markdown(f"- Recommended Users: {product.get('recommended_users', 'N/A')}")
                
                elif category in ['MS', 'Catalyst Switch']:
                    st.markdown(f"- Total Ports: {product.get('total_ports', 'N/A')}")
                    st.markdown(f"- PoE Ports: {product.get('poe_ports', 'N/A')}")
                    st.markdown(f"- PoE Budget: {product.get('poe_budget', 'N/A')}")
                    st.markdown(f"- Stacking: {product.get('stacking', 'N/A')}")
                
                elif category == 'ISE':
                    st.markdown(f"- Recommended Endpoints: {product.get('recommended_endpoints', 'N/A')}")
                    st.markdown(f"- Deployment Type: {product.get('deployment_type', 'N/A')}")
                    st.markdown(f"- CPU: {product.get('cpu', 'N/A')}")
                    st.markdown(f"- RAM: {product.get('ram', 'N/A')}")
            
            with col2:
                # Links
                st.markdown("**Dokumentation:**")
                
                if product.get('datasheet_url'):
                    st.markdown(f"[📄 Datasheet]({product.get('datasheet_url')})")
                
                if product.get('installation_guide_url'):
                    st.markdown(f"[📖 Installation Guide]({product.get('installation_guide_url')})")
                
                if product.get('ordering_guide_url'):
                    st.markdown(f"[🛒 Ordering Guide]({product.get('ordering_guide_url')})")
                
                st.markdown("---")
                
                # Accessories
                accessories = product_loader.get_accessories_by_product(product.get('id'))
                if accessories:
                    st.markdown(f"**🔧 Zubehör:** {len(accessories)} verfügbar")
                
                st.markdown("---")
                
                # Actions
                if st.button("📄 Alle Details", key=f"list_details_{product.get('id')}", use_container_width=True):
                    st.session_state['selected_product'] = product.get('id')
                    st.session_state['show_product_details'] = True
                
                if st.button("⚖️ Zum Vergleich", key=f"list_compare_{product.get('id')}", use_container_width=True):
                    if 'comparison_list' not in st.session_state:
                        st.session_state['comparison_list'] = []
                    
                    if product.get('id') not in st.session_state['comparison_list']:
                        st.session_state['comparison_list'].append(product.get('id'))
                        st.success("✅ Hinzugefügt")
                
                # Edit button for admins
                if is_admin():
                    if st.button("✏️ Bearbeiten", key=f"list_edit_{product.get('id')}", use_container_width=True):
                        st.info("ℹ️ Nutze Admin Tools zum Bearbeiten")


def show_product_details_dialog(product, product_loader):
    """Show detailed product information in a modal-like dialog"""
    
    st.markdown("---")
    st.markdown("## 📋 Produktdetails")
    
    # Close button
    if st.button("❌ Schließen"):
        st.session_state['show_product_details'] = False
        st.rerun()
    
    # Tabs for different information
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Spezifikationen", "🔧 Zubehör", "📜 Lizenzen", "📄 Dokumentation"])
    
    with tab1:
        st.subheader(product.get('name', 'N/A'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Allgemein")
            st.markdown(f"**Kategorie:** {product.get('category', 'N/A')}")
            st.markdown(f"**Unterkategorie:** {product.get('subcategory', 'N/A')}")
            st.markdown(f"**SKU:** `{product.get('sku_base', 'N/A')}`")
            st.markdown(f"**Status:** {product.get('status', 'N/A')}")
            
            if product.get('eol_announced'):
                st.markdown(f"**EOL Announced:** {product.get('eol_announced')}")
            if product.get('eos_date'):
                st.markdown(f"**End of Sale:** {product.get('eos_date')}")
        
        with col2:
            st.markdown("### Physisch")
            st.markdown(f"**Dimensions:** {product.get('dimensions', 'N/A')}")
            st.markdown(f"**Weight:** {product.get('weight', 'N/A')}")
            st.markdown(f"**Operating Temp:** {product.get('operating_temp', 'N/A')}")
            
            if product.get('form_factor'):
                st.markdown(f"**Form Factor:** {product.get('form_factor', 'N/A')}")
        
        st.markdown("---")
        
        # Category-specific specs
        category = product.get('category', '')
        
        if category in ['MR', 'Catalyst AP']:
            st.markdown("### Wireless Spezifikationen")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Wi-Fi Standard:** {product.get('wifi_standard', 'N/A')}")
                st.markdown(f"**Max Data Rate:** {product.get('max_data_rate', 'N/A')}")
                st.markdown(f"**Spatial Streams:** {product.get('spatial_streams', 'N/A')}")
                st.markdown(f"**Frequency Bands:** {product.get('frequency_bands', 'N/A')}")
            
            with col2:
                st.markdown(f"**PoE Requirement:** {product.get('poe_requirement', 'N/A')}")
                st.markdown(f"**Power Consumption:** {product.get('max_power_consumption', 'N/A')}")
                st.markdown(f"**Recommended Clients:** {product.get('recommended_clients', 'N/A')}")
                st.markdown(f"**Coverage Area:** {product.get('coverage_area', 'N/A')}")
        
        elif category == 'MX':
            st.markdown("### Firewall Spezifikationen")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Firewall Throughput:** {product.get('firewall_throughput', 'N/A')}")
                st.markdown(f"**VPN Throughput:** {product.get('vpn_throughput', 'N/A')}")
                st.markdown(f"**Adv. Security Throughput:** {product.get('advanced_security_throughput', 'N/A')}")
            
            with col2:
                st.markdown(f"**Max VPN Tunnels:** {product.get('max_vpn_tunnels', 'N/A')}")
                st.markdown(f"**Recommended Users:** {product.get('recommended_users', 'N/A')}")
                st.markdown(f"**WAN Ports:** {product.get('wan_ports', 'N/A')}")
                st.markdown(f"**LAN Ports:** {product.get('lan_ports', 'N/A')}")
        
        elif category in ['MS', 'Catalyst Switch']:
            st.markdown("### Switch Spezifikationen")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Total Ports:** {product.get('total_ports', 'N/A')}")
                st.markdown(f"**Port Configuration:** {product.get('port_configuration', 'N/A')}")
                st.markdown(f"**PoE Ports:** {product.get('poe_ports', 'N/A')}")
                st.markdown(f"**PoE Budget:** {product.get('poe_budget', 'N/A')}")
            
            with col2:
                st.markdown(f"**Switching Capacity:** {product.get('switching_capacity', 'N/A')}")
                st.markdown(f"**Stacking:** {product.get('stacking', 'N/A')}")
                st.markdown(f"**Layer 3 Features:** {product.get('layer3_features', 'N/A')}")
        
        elif category == 'ISE':
            st.markdown("### ISE Spezifikationen")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Recommended Endpoints:** {product.get('recommended_endpoints', 'N/A')}")
                st.markdown(f"**Concurrent Sessions:** {product.get('recommended_concurrent_sessions', 'N/A')}")
                st.markdown(f"**Deployment Type:** {product.get('deployment_type', 'N/A')}")
            
            with col2:
                st.markdown(f"**CPU:** {product.get('cpu', 'N/A')}")
                st.markdown(f"**RAM:** {product.get('ram', 'N/A')}")
                st.markdown(f"**Storage:** {product.get('storage', 'N/A')}")
    
    with tab2:
        st.subheader("🔧 Kompatibles Zubehör")
        
        accessories = product_loader.get_accessories_by_product(product.get('id'))
        
        if accessories:
            for acc in accessories:
                with st.container():
                    st.markdown(f"**{acc.get('name', 'N/A')}**")
                    st.caption(f"SKU: `{acc.get('sku', 'N/A')}` | Kategorie: {acc.get('category', 'N/A')}")
                    st.markdown(f"{acc.get('description', '')}")
                    st.markdown("---")
        else:
            st.info("ℹ️ Kein spezifisches Zubehör hinterlegt")
    
    with tab3:
        st.subheader("📜 Verfügbare Lizenzen")
        
        licenses = product.get('sku_licenses', {})
        
        if licenses:
            import pandas as pd
            
            license_data = []
            for lic_type, sku in licenses.items():
                license_data.append({
                    'Lizenz-Typ': lic_type.replace('_', ' ').title(),
                    'SKU': sku
                })
            
            df = pd.DataFrame(license_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Keine Lizenz-Informationen verfügbar")
    
    with tab4:
        st.subheader("📄 Dokumentation & Links")
        
        if product.get('datasheet_url'):
            st.markdown(f"[📄 **Datasheet**]({product.get('datasheet_url')})")
        
        if product.get('installation_guide_url'):
            st.markdown(f"[📖 **Installation Guide**]({product.get('installation_guide_url')})")
        
        if product.get('ordering_guide_url'):
            st.markdown(f"[🛒 **Ordering Guide**]({product.get('ordering_guide_url')})")
        
        if product.get('meraki_migration_guide'):
            st.markdown(f"[🔄 **Meraki Migration Guide**]({product.get('meraki_migration_guide')})")
        
        if not any([product.get('datasheet_url'), product.get('installation_guide_url'), 
                   product.get('ordering_guide_url')]):
            st.info("ℹ️ Keine Dokumentations-Links verfügbar")


if __name__ == "__main__":
    main()
