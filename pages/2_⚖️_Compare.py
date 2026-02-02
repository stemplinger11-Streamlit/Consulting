"""
Compare Page
Side-by-side comparison of products with detailed specifications
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.product_loader import get_product_loader
import pandas as pd
import json

# Require authentication
require_auth(lambda: main())

def main():
    st.title("⚖️ Produktvergleich")
    st.markdown("Vergleiche bis zu 4 Produkte nebeneinander")
    
    # Load translations
    with open('data/translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    
    lang = st.session_state.get('language', 'de')
    t = translations[lang]
    
    # Initialize
    product_loader = get_product_loader()
    
    # Initialize comparison list
    if 'comparison_list' not in st.session_state:
        st.session_state['comparison_list'] = []
    
    comparison_list = st.session_state['comparison_list']
    
    st.markdown("---")
    
    # Header actions
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.metric("📊 Produkte im Vergleich", len(comparison_list))
    
    with col2:
        if st.button("🗑️ Alle löschen", use_container_width=True):
            st.session_state['comparison_list'] = []
            st.rerun()
    
    with col3:
        if len(comparison_list) > 0:
            if st.button("📥 Export", use_container_width=True):
                st.session_state['show_compare_export'] = True
    
    st.markdown("---")
    
    # Product selector
    st.subheader("➕ Produkte hinzufügen")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Category filter for selection
        categories = ["Alle", "MR", "MX", "MS", "Catalyst AP", "Catalyst Switch", "ISE"]
        selected_category = st.selectbox(
            "Kategorie filtern",
            categories
        )
    
    with col2:
        # Get products for dropdown
        if selected_category == "Alle":
            available_products = product_loader.get_all_products()
        else:
            cat_key = selected_category.lower().replace(" ", "_")
            available_products = product_loader.get_products_by_category(cat_key)
        
        # Filter out already selected
        available_products = [p for p in available_products if p.get('id') not in comparison_list]
        
        product_names = [f"{p.get('name', '')} ({p.get('id', '')})" for p in available_products]
        
        if product_names:
            selected_product_name = st.selectbox(
                "Produkt auswählen",
                product_names
            )
        else:
            selected_product_name = None
            st.info("ℹ️ Keine weiteren Produkte verfügbar")
    
    with col3:
        st.write("")  # Spacing
        st.write("")
        if selected_product_name and st.button("➕ Hinzufügen", use_container_width=True):
            if len(comparison_list) < 4:
                product_id = selected_product_name.split('(')[-1].replace(')', '')
                st.session_state['comparison_list'].append(product_id)
                st.success(f"✅ Hinzugefügt!")
                st.rerun()
            else:
                st.warning("⚠️ Maximal 4 Produkte können verglichen werden")
    
    st.markdown("---")
    
    # Display comparison
    if len(comparison_list) == 0:
        st.info("ℹ️ Füge Produkte hinzu, um sie zu vergleichen. Du kannst auch aus dem Produktkatalog Produkte zum Vergleich hinzufügen.")
    
    elif len(comparison_list) == 1:
        st.warning("⚠️ Füge mindestens 2 Produkte hinzu für einen Vergleich")
        display_single_product(comparison_list[0], product_loader)
    
    else:
        # Compare view type selector
        view_type = st.radio(
            "Vergleichsansicht",
            ["Übersicht", "Detailliert", "Nebeneinander"],
            horizontal=True
        )
        
        if view_type == "Übersicht":
            display_overview_comparison(comparison_list, product_loader)
        elif view_type == "Detailliert":
            display_detailed_comparison(comparison_list, product_loader)
        else:  # Nebeneinander
            display_side_by_side_comparison(comparison_list, product_loader)
    
    # Export dialog
    if st.session_state.get('show_compare_export', False):
        show_export_dialog(comparison_list, product_loader)


def display_single_product(product_id, product_loader):
    """Display single product details"""
    product = product_loader.get_product_by_id(product_id)
    
    if not product:
        st.error("❌ Produkt nicht gefunden")
        return
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(product.get('name', 'N/A'))
        st.caption(f"{product.get('category', '')} / {product.get('subcategory', '')}")
    
    with col2:
        if st.button("🗑️ Entfernen", key=f"remove_{product_id}"):
            st.session_state['comparison_list'].remove(product_id)
            st.rerun()
    
    # Display key specs
    category = product.get('category', '')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Allgemein**")
        st.markdown(f"SKU: `{product.get('sku_base', 'N/A')}`")
        st.markdown(f"Status: {product.get('status', 'N/A')}")
    
    with col2:
        if category in ['MR', 'Catalyst AP']:
            st.markdown("**Wireless**")
            st.markdown(f"{product.get('wifi_standard', 'N/A')}")
            st.markdown(f"{product.get('max_data_rate', 'N/A')}")
        elif category == 'MX':
            st.markdown("**Performance**")
            st.markdown(f"FW: {product.get('firewall_throughput', 'N/A')}")
            st.markdown(f"VPN: {product.get('vpn_throughput', 'N/A')}")
        elif category in ['MS', 'Catalyst Switch']:
            st.markdown("**Ports**")
            st.markdown(f"Total: {product.get('total_ports', 'N/A')}")
            st.markdown(f"PoE: {product.get('poe_ports', 'N/A')}")
    
    with col3:
        st.markdown("**Dokumentation**")
        if product.get('datasheet_url'):
            st.markdown(f"[📄 Datasheet]({product.get('datasheet_url')})")
        if product.get('installation_guide_url'):
            st.markdown(f"[📖 Install Guide]({product.get('installation_guide_url')})")


def display_overview_comparison(comparison_list, product_loader):
    """Display quick overview comparison table"""
    
    # Get products
    products = [product_loader.get_product_by_id(pid) for pid in comparison_list]
    products = [p for p in products if p is not None]
    
    # Create comparison table
    data = []
    
    # Header row (product names)
    names_row = [''] + [p.get('name', 'N/A') for p in products]
    
    # Category row
    category_row = ['Kategorie'] + [p.get('category', 'N/A') for p in products]
    data.append(category_row)
    
    # Subcategory row
    subcategory_row = ['Einsatzbereich'] + [p.get('subcategory', 'N/A') for p in products]
    data.append(subcategory_row)
    
    # SKU row
    sku_row = ['SKU'] + [f"`{p.get('sku_base', 'N/A')}`" for p in products]
    data.append(sku_row)
    
    # Status row
    status_row = ['Status'] + [p.get('status', 'N/A') for p in products]
    data.append(status_row)
    
    # Category-specific rows
    if all(p.get('category') in ['MR', 'Catalyst AP'] for p in products):
        data.append(['Wi-Fi Standard'] + [p.get('wifi_standard', 'N/A') for p in products])
        data.append(['Max. Data Rate'] + [p.get('max_data_rate', 'N/A') for p in products])
        data.append(['PoE Requirement'] + [p.get('poe_requirement', 'N/A') for p in products])
        data.append(['Empf. Clients'] + [str(p.get('recommended_clients', 'N/A')) for p in products])
        data.append(['Coverage Area'] + [p.get('coverage_area', 'N/A') for p in products])
    
    elif all(p.get('category') == 'MX' for p in products):
        data.append(['FW Throughput'] + [p.get('firewall_throughput', 'N/A') for p in products])
        data.append(['VPN Throughput'] + [p.get('vpn_throughput', 'N/A') for p in products])
        data.append(['Max VPN Tunnels'] + [str(p.get('max_vpn_tunnels', 'N/A')) for p in products])
        data.append(['Empf. Users'] + [p.get('recommended_users', 'N/A') for p in products])
        data.append(['WAN Ports'] + [p.get('wan_ports', 'N/A') for p in products])
        data.append(['LAN Ports'] + [p.get('lan_ports', 'N/A') for p in products])
    
    elif all(p.get('category') in ['MS', 'Catalyst Switch'] for p in products):
        data.append(['Total Ports'] + [str(p.get('total_ports', 'N/A')) for p in products])
        data.append(['PoE Ports'] + [str(p.get('poe_ports', 'N/A')) for p in products])
        data.append(['PoE Budget'] + [p.get('poe_budget', 'N/A') for p in products])
        data.append(['Stacking'] + [str(p.get('stacking', 'N/A')) for p in products])
        data.append(['Layer 3'] + [p.get('layer3_features', 'N/A') for p in products])
    
    elif all(p.get('category') == 'ISE' for p in products):
        data.append(['Endpoints'] + [p.get('recommended_endpoints', 'N/A') for p in products])
        data.append(['Deployment'] + [p.get('deployment_type', 'N/A') for p in products])
        data.append(['CPU'] + [p.get('cpu', 'N/A') for p in products])
        data.append(['RAM'] + [p.get('ram', 'N/A') for p in products])
    
    # Physical specs (common)
    data.append(['Dimensions'] + [p.get('dimensions', 'N/A') for p in products])
    data.append(['Weight'] + [p.get('weight', 'N/A') for p in products])
    
    # Create DataFrame
    df = pd.DataFrame(data[1:], columns=['Spezifikation'] + [p.get('name', f'Produkt {i+1}') for i, p in enumerate(products)])
    
    # Display with styling
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Spezifikation": st.column_config.TextColumn("Spezifikation", width="medium")
        }
    )
    
    # Remove buttons
    st.markdown("---")
    cols = st.columns(len(products))
    for i, product in enumerate(products):
        with cols[i]:
            if st.button(f"🗑️ {product.get('name', '')[:20]}...", key=f"remove_overview_{i}", use_container_width=True):
                st.session_state['comparison_list'].remove(product.get('id'))
                st.rerun()


def display_detailed_comparison(comparison_list, product_loader):
    """Display detailed specification comparison"""
    
    # Get products
    products = [product_loader.get_product_by_id(pid) for pid in comparison_list]
    products = [p for p in products if p is not None]
    
    # Tabs for different spec categories
    tabs = st.tabs(["📊 Technische Specs", "🔌 Konnektivität", "💾 Hardware", "📜 Lizenzen", "🔧 Zubehör"])
    
    with tabs[0]:  # Technical Specs
        st.subheader("Technische Spezifikationen")
        
        data = []
        category = products[0].get('category', '')
        
        if category in ['MR', 'Catalyst AP']:
            specs = [
                ('Wi-Fi Standard', 'wifi_standard'),
                ('Max. Data Rate', 'max_data_rate'),
                ('Spatial Streams', 'spatial_streams'),
                ('Frequency Bands', 'frequency_bands'),
                ('Max. Power', 'max_power'),
                ('Antenna Type', 'antenna_type'),
                ('Empf. Clients', 'recommended_clients'),
                ('Coverage Area', 'coverage_area'),
                ('Bluetooth', 'bluetooth'),
            ]
        
        elif category == 'MX':
            specs = [
                ('Firewall Throughput', 'firewall_throughput'),
                ('VPN Throughput', 'vpn_throughput'),
                ('Adv. Security Throughput', 'advanced_security_throughput'),
                ('Max VPN Tunnels', 'max_vpn_tunnels'),
                ('Max Client VPN', 'max_client_vpn'),
                ('Empf. Users', 'recommended_users'),
                ('HTTPS Inspection', 'https_inspection'),
                ('IDS/IPS', 'ids_ips'),
            ]
        
        elif category in ['MS', 'Catalyst Switch']:
            specs = [
                ('Total Ports', 'total_ports'),
                ('Port Configuration', 'port_configuration'),
                ('PoE Ports', 'poe_ports'),
                ('PoE Budget', 'poe_budget'),
                ('PoE Standard', 'poe_standard'),
                ('Switching Capacity', 'switching_capacity'),
                ('Forwarding Rate', 'forwarding_rate'),
                ('Layer 3 Features', 'layer3_features'),
                ('Stacking', 'stacking'),
                ('Max Stack Members', 'max_stack_members'),
            ]
        
        elif category == 'ISE':
            specs = [
                ('Recommended Endpoints', 'recommended_endpoints'),
                ('Concurrent Sessions', 'recommended_concurrent_sessions'),
                ('Deployment Type', 'deployment_type'),
                ('CPU', 'cpu'),
                ('RAM', 'ram'),
                ('Storage', 'storage'),
                ('RAID', 'raid'),
                ('Max Nodes', 'max_nodes_distributed'),
            ]
        else:
            specs = []
        
        for label, key in specs:
            row = [label] + [p.get(key, 'N/A') for p in products]
            data.append(row)
        
        if data:
            df = pd.DataFrame(data, columns=['Spezifikation'] + [p.get('name', f'Produkt {i+1}') for i, p in enumerate(products)])
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tabs[1]:  # Connectivity
        st.subheader("Konnektivität & Ports")
        
        data = []
        category = products[0].get('category', '')
        
        if category in ['MR', 'Catalyst AP']:
            specs = [
                ('Ethernet Ports', 'ethernet_ports'),
                ('PoE Requirement', 'poe_requirement'),
                ('PoE Wattage', 'poe_wattage'),
                ('Console Port', 'console_port'),
            ]
        
        elif category == 'MX':
            specs = [
                ('WAN Ports', 'wan_ports'),
                ('LAN Ports', 'lan_ports'),
                ('PoE Support', 'poe_support'),
                ('Fiber Support', 'fiber_support'),
                ('Cellular Failover', 'cellular_failover'),
            ]
        
        elif category in ['MS', 'Catalyst Switch']:
            specs = [
                ('Total Ports', 'total_ports'),
                ('Uplink Ports', 'uplink_ports'),
                ('SFP Ports', 'sfp_ports'),
                ('SFP+ Ports', 'sfp_plus_ports'),
                ('SFP28 Ports', 'sfp28_ports'),
            ]
        else:
            specs = [
                ('Network Interfaces', 'network_interfaces'),
            ]
        
        for label, key in specs:
            row = [label] + [p.get(key, 'N/A') for p in products]
            data.append(row)
        
        if data:
            df = pd.DataFrame(data, columns=['Spezifikation'] + [p.get('name', f'Produkt {i+1}') for i, p in enumerate(products)])
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tabs[2]:  # Hardware
        st.subheader("Hardware & Physisch")
        
        data = [
            ['Form Factor'] + [p.get('form_factor', 'N/A') for p in products],
            ['Dimensions'] + [p.get('dimensions', 'N/A') for p in products],
            ['Weight'] + [p.get('weight', 'N/A') for p in products],
            ['Power Consumption'] + [p.get('power_consumption', p.get('max_power_consumption', 'N/A')) for p in products],
            ['Operating Temp'] + [p.get('operating_temp', 'N/A') for p in products],
            ['Dual Power Supply'] + [str(p.get('dual_power_supply', 'N/A')) for p in products],
            ['Fanless'] + [str(p.get('fanless', 'N/A')) for p in products],
        ]
        
        df = pd.DataFrame(data, columns=['Spezifikation'] + [p.get('name', f'Produkt {i+1}') for i, p in enumerate(products)])
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tabs[3]:  # Licenses
        st.subheader("Verfügbare Lizenzen")
        
        for i, product in enumerate(products):
            st.markdown(f"**{product.get('name', 'N/A')}**")
            
            licenses = product.get('sku_licenses', {})
            if licenses:
                license_data = []
                for lic_type, sku in licenses.items():
                    license_data.append({
                        'Typ': lic_type.replace('_', ' ').title(),
                        'SKU': sku
                    })
                
                df_lic = pd.DataFrame(license_data)
                st.dataframe(df_lic, use_container_width=True, hide_index=True)
            else:
                st.info("Keine Lizenzen verfügbar")
            
            if i < len(products) - 1:
                st.markdown("---")
    
    with tabs[4]:  # Accessories
        st.subheader("Kompatibles Zubehör")
        
        for i, product in enumerate(products):
            st.markdown(f"**{product.get('name', 'N/A')}**")
            
            accessories = product_loader.get_accessories_by_product(product.get('id'))
            
            if accessories:
                for acc in accessories:
                    st.markdown(f"- {acc.get('name', 'N/A')} (`{acc.get('sku', 'N/A')}`)")
            else:
                st.info("Kein Zubehör verfügbar")
            
            if i < len(products) - 1:
                st.markdown("---")
    
    # Remove buttons
    st.markdown("---")
    cols = st.columns(len(products))
    for i, product in enumerate(products):
        with cols[i]:
            if st.button(f"🗑️ Entfernen", key=f"remove_detailed_{i}", use_container_width=True):
                st.session_state['comparison_list'].remove(product.get('id'))
                st.rerun()


def display_side_by_side_comparison(comparison_list, product_loader):
    """Display products side-by-side in columns"""
    
    # Get products
    products = [product_loader.get_product_by_id(pid) for pid in comparison_list]
    products = [p for p in products if p is not None]
    
    # Create columns
    cols = st.columns(len(products))
    
    for i, product in enumerate(products):
        with cols[i]:
            display_product_column(product, product_loader, i)


def display_product_column(product, product_loader, index):
    """Display single product in a column"""
    
    st.markdown(f"### {product.get('name', 'N/A')}")
    
    # Remove button
    if st.button("🗑️ Entfernen", key=f"remove_sidebyside_{index}", use_container_width=True):
        st.session_state['comparison_list'].remove(product.get('id'))
        st.rerun()
    
    st.markdown("---")
    
    # Status badge
    status = product.get('status', 'Active')
    if status == 'Active':
        st.success(f"🟢 {status}")
    elif status == 'EOL Announced':
        st.warning(f"🟡 {status}")
    else:
        st.error(f"🔴 {status}")
    
    # Basic info
    st.markdown(f"**Kategorie:** {product.get('category', 'N/A')}")
    st.markdown(f"**SKU:** `{product.get('sku_base', 'N/A')}`")
    
    st.markdown("---")
    
    # Category-specific specs
    category = product.get('category', '')
    
    if category in ['MR', 'Catalyst AP']:
        st.markdown("**Wireless**")
        st.markdown(f"📡 {product.get('wifi_standard', 'N/A')}")
        st.markdown(f"⚡ {product.get('max_data_rate', 'N/A')}")
        st.markdown(f"🔌 {product.get('poe_requirement', 'N/A')}")
        st.markdown(f"👥 {product.get('recommended_clients', 'N/A')} Clients")
    
    elif category == 'MX':
        st.markdown("**Performance**")
        st.markdown(f"🔥 FW: {product.get('firewall_throughput', 'N/A')}")
        st.markdown(f"🔒 VPN: {product.get('vpn_throughput', 'N/A')}")
        st.markdown(f"🌐 Tunnels: {product.get('max_vpn_tunnels', 'N/A')}")
        st.markdown(f"👥 {product.get('recommended_users', 'N/A')} Users")
    
    elif category in ['MS', 'Catalyst Switch']:
        st.markdown("**Ports & PoE**")
        st.markdown(f"🔌 Ports: {product.get('total_ports', 'N/A')}")
        st.markdown(f"⚡ PoE: {product.get('poe_budget', 'N/A')}")
        st.markdown(f"🔗 Stack: {product.get('stacking', 'N/A')}")
        st.markdown(f"📶 L3: {product.get('layer3_features', 'N/A')}")
    
    elif category == 'ISE':
        st.markdown("**Kapazität**")
        st.markdown(f"📱 {product.get('recommended_endpoints', 'N/A')}")
        st.markdown(f"💻 {product.get('cpu', 'N/A')}")
        st.markdown(f"🧠 {product.get('ram', 'N/A')}")
    
    st.markdown("---")
    
    # Physical
    st.markdown("**Physisch**")
    st.markdown(f"📏 {product.get('dimensions', 'N/A')}")
    st.markdown(f"⚖️ {product.get('weight', 'N/A')}")
    
    st.markdown("---")
    
    # Links
    st.markdown("**Dokumentation**")
    if product.get('datasheet_url'):
        st.markdown(f"[📄 Datasheet]({product.get('datasheet_url')})")
    if product.get('installation_guide_url'):
        st.markdown(f"[📖 Install Guide]({product.get('installation_guide_url')})")


def show_export_dialog(comparison_list, product_loader):
    """Show export dialog for comparison"""
    
    with st.expander("📥 Vergleich exportieren", expanded=True):
        export_format = st.radio("Format", ["Excel", "PDF"], horizontal=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Exportieren"):
                from utils.export import get_export_manager
                export_mgr = get_export_manager()
                
                products = [product_loader.get_product_by_id(pid) for pid in comparison_list]
                products = [p for p in products if p is not None]
                
                with st.spinner("Export läuft..."):
                    if export_format == "Excel":
                        buffer = export_mgr.export_products_to_excel(
                            products,
                            include_specs=True,
                            include_licenses=True,
                            include_accessories=True
                        )
                        st.download_button(
                            label="📥 Excel herunterladen",
                            data=buffer,
                            file_name=f"produktvergleich_{len(products)}_produkte.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:  # PDF
                        buffer = export_mgr.export_products_to_pdf(
                            products,
                            title=f"Produktvergleich ({len(products)} Produkte)",
                            include_details=True
                        )
                        st.download_button(
                            label="📥 PDF herunterladen",
                            data=buffer,
                            file_name=f"produktvergleich_{len(products)}_produkte.pdf",
                            mime="application/pdf"
                        )
        
        with col2:
            if st.button("❌ Abbrechen"):
                st.session_state['show_compare_export'] = False
                st.rerun()


if __name__ == "__main__":
    main()
