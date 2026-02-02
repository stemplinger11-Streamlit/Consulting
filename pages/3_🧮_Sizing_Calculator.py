"""
Sizing Calculator Page
Calculate optimal network infrastructure sizing based on requirements
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.product_loader import get_product_loader
from utils.calculations import SizingCalculator
import json

# Require authentication
require_auth(lambda: main())

def main():
    st.title("🧮 Sizing Calculator")
    st.markdown("Berechne die optimale Netzwerk-Infrastruktur für dein Projekt")
    
    # Load translations
    with open('data/translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    
    lang = st.session_state.get('language', 'de')
    t = translations[lang]
    
    # Initialize
    product_loader = get_product_loader()
    calculator = SizingCalculator()
    
    st.markdown("---")
    
    # Calculator type selector
    st.subheader("📐 Wähle den Berechnungstyp")
    
    calc_type = st.radio(
        "Was möchtest du dimensionieren?",
        ["🔵 Access Points (WLAN)", "🔴 Firewalls (MX)", "🟢 Switches (MS)", "🟡 ISE (Network Access Control)"],
        horizontal=False
    )
    
    st.markdown("---")
    
    # Initialize session state for results
    if 'sizing_results' not in st.session_state:
        st.session_state['sizing_results'] = None
    
    # Display calculator based on selection
    if calc_type == "🔵 Access Points (WLAN)":
        calculate_access_points(calculator, product_loader)
    
    elif calc_type == "🔴 Firewalls (MX)":
        calculate_firewalls(calculator, product_loader)
    
    elif calc_type == "🟢 Switches (MS)":
        calculate_switches(calculator, product_loader)
    
    elif calc_type == "🟡 ISE (Network Access Control)":
        calculate_ise(calculator, product_loader)


def calculate_access_points(calculator, product_loader):
    """Calculate Access Point requirements"""
    
    st.subheader("🔵 Access Point Sizing")
    st.markdown("Berechne die benötigte Anzahl und Modell-Empfehlungen für Access Points")
    
    with st.form("ap_sizing_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📏 Räumliche Anforderungen")
            
            area_sqm = st.number_input(
                "Abzudeckende Fläche (m²)",
                min_value=0,
                max_value=100000,
                value=500,
                step=50,
                help="Gesamte Fläche, die mit WLAN abgedeckt werden soll"
            )
            
            deployment_type = st.selectbox(
                "Deployment-Typ",
                ["Office", "Warehouse", "Hospital", "School", "Retail", "Stadium"],
                help="Beeinflusst die Reichweite pro AP"
            )
            
            high_density = st.checkbox(
                "High-Density Umgebung",
                help="Stadien, Konferenzräume, Auditorien mit vielen Clients auf engem Raum"
            )
        
        with col2:
            st.markdown("### 👥 Client-Anforderungen")
            
            client_count = st.number_input(
                "Anzahl Clients (gleichzeitig)",
                min_value=1,
                max_value=10000,
                value=100,
                step=10,
                help="Maximale Anzahl gleichzeitig verbundener Geräte"
            )
            
            wifi_standard = st.selectbox(
                "Gewünschter Wi-Fi Standard",
                ["Wi-Fi 5 (802.11ac)", "Wi-Fi 6 (802.11ax)", "Wi-Fi 6E (802.11ax 6GHz)", "Wi-Fi 7 (802.11be)"],
                index=1
            )
            
            outdoor_required = st.checkbox(
                "Outdoor APs benötigt",
                help="Für Außenbereiche, Parkplätze, etc."
            )
        
        st.markdown("---")
        
        # Additional requirements
        with st.expander("⚙️ Erweiterte Optionen"):
            col1, col2 = st.columns(2)
            
            with col1:
                poe_requirement = st.selectbox(
                    "PoE Verfügbarkeit",
                    ["PoE (802.3af - 15W)", "PoE+ (802.3at - 30W)", "UPOE (802.3bt - 60W+)"],
                    index=1
                )
                
                budget_constraint = st.selectbox(
                    "Budget-Orientierung",
                    ["Keine Beschränkung", "Mittelklasse bevorzugt", "Entry-Level bevorzugt"],
                    index=0
                )
            
            with col2:
                future_proof = st.checkbox(
                    "Zukunftssicher (20% Reserve)",
                    value=True,
                    help="Berücksichtigt zukünftiges Wachstum"
                )
                
                meraki_only = st.checkbox(
                    "Nur Meraki (kein Catalyst)",
                    value=False
                )
        
        submitted = st.form_submit_button("🧮 Berechnen", use_container_width=True)
        
        if submitted:
            with st.spinner("Berechnung läuft..."):
                # Calculate requirements
                results = calculator.calculate_ap_requirements(
                    area_sqm=area_sqm,
                    client_count=client_count,
                    deployment_type=deployment_type,
                    high_density=high_density
                )
                
                # Adjust for future-proofing
                if future_proof:
                    results['recommended_aps'] = int(results['recommended_aps'] * 1.2)
                
                # Filter recommendations based on criteria
                filtered_suggestions = filter_ap_recommendations(
                    results['ap_model_suggestions'],
                    wifi_standard,
                    outdoor_required,
                    poe_requirement,
                    budget_constraint,
                    meraki_only,
                    product_loader
                )
                
                results['filtered_suggestions'] = filtered_suggestions
                results['parameters'] = {
                    'area_sqm': area_sqm,
                    'client_count': client_count,
                    'deployment_type': deployment_type,
                    'high_density': high_density,
                    'wifi_standard': wifi_standard,
                    'outdoor_required': outdoor_required,
                    'future_proof': future_proof
                }
                
                st.session_state['sizing_results'] = results
    
    # Display results
    if st.session_state.get('sizing_results'):
        display_ap_results(st.session_state['sizing_results'], product_loader)


def calculate_firewalls(calculator, product_loader):
    """Calculate Firewall (MX) requirements"""
    
    st.subheader("🔴 Firewall Sizing")
    st.markdown("Dimensioniere die passende MX Security Appliance")
    
    with st.form("mx_sizing_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👥 Nutzer & Standort")
            
            user_count = st.number_input(
                "Anzahl Nutzer",
                min_value=1,
                max_value=50000,
                value=100,
                step=10
            )
            
            site_type = st.selectbox(
                "Standort-Typ",
                ["Small Branch (<50 Users)", "Medium Branch (50-250)", "Large Branch (250-500)", "Campus/HQ (>500)"],
                index=1
            )
            
            ha_required = st.checkbox(
                "High Availability (HA-Paar)",
                help="Redundanter Betrieb mit 2 MX Appliances"
            )
        
        with col2:
            st.markdown("### 🌐 Netzwerk-Anforderungen")
            
            bandwidth_mbps = st.number_input(
                "Internet-Bandbreite (Mbps)",
                min_value=10,
                max_value=10000,
                value=500,
                step=50,
                help="Gesamte Internet-Uplink Bandbreite"
            )
            
            vpn_tunnels = st.number_input(
                "Site-to-Site VPN Tunnel",
                min_value=0,
                max_value=5000,
                value=0,
                step=5,
                help="Anzahl VPN-Verbindungen zu anderen Standorten"
            )
            
            client_vpn_users = st.number_input(
                "Client VPN Nutzer",
                min_value=0,
                max_value=1000,
                value=0,
                step=5,
                help="Remote-User mit VPN-Zugang"
            )
        
        st.markdown("---")
        
        # Security features
        st.markdown("### 🔒 Security Features")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            advanced_security = st.checkbox(
                "Advanced Security",
                value=True,
                help="IDS/IPS, AMP, Content Filtering"
            )
        
        with col2:
            https_inspection = st.checkbox(
                "HTTPS DPI",
                value=False,
                help="Deep Packet Inspection für verschlüsselten Traffic"
            )
        
        with col3:
            sd_wan = st.checkbox(
                "SD-WAN Features",
                value=True,
                help="Intelligentes Load Balancing über mehrere Uplinks"
            )
        
        submitted = st.form_submit_button("🧮 Berechnen", use_container_width=True)
        
        if submitted:
            with st.spinner("Berechnung läuft..."):
                results = calculator.calculate_firewall_requirements(
                    user_count=user_count,
                    bandwidth_mbps=bandwidth_mbps,
                    vpn_tunnels=vpn_tunnels,
                    advanced_security=advanced_security
                )
                
                results['parameters'] = {
                    'user_count': user_count,
                    'bandwidth_mbps': bandwidth_mbps,
                    'vpn_tunnels': vpn_tunnels,
                    'client_vpn_users': client_vpn_users,
                    'ha_required': ha_required,
                    'advanced_security': advanced_security,
                    'https_inspection': https_inspection,
                    'sd_wan': sd_wan
                }
                
                st.session_state['sizing_results'] = results
    
    # Display results
    if st.session_state.get('sizing_results'):
        display_mx_results(st.session_state['sizing_results'], product_loader)


def calculate_switches(calculator, product_loader):
    """Calculate Switch requirements"""
    
    st.subheader("🟢 Switch Sizing")
    st.markdown("Berechne die benötigten Switches und Port-Konfiguration")
    
    with st.form("ms_sizing_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔌 Port-Anforderungen")
            
            access_ports = st.number_input(
                "Access Ports (für Endgeräte)",
                min_value=1,
                max_value=1000,
                value=48,
                step=8,
                help="Ports für PCs, Telefone, IoT-Geräte, etc."
            )
            
            uplink_speed = st.selectbox(
                "Uplink Geschwindigkeit",
                ["1 Gbps", "10 Gbps", "25 Gbps"],
                index=1
            )
            
            stacking_required = st.checkbox(
                "Stacking erforderlich",
                help="Mehrere Switches als eine Einheit verwalten"
            )
        
        with col2:
            st.markdown("### ⚡ PoE-Anforderungen")
            
            poe_devices = st.number_input(
                "Geräte mit PoE+ (30W)",
                min_value=0,
                max_value=1000,
                value=24,
                step=4,
                help="Access Points, IP-Telefone, Kameras"
            )
            
            upoe_devices = st.number_input(
                "Geräte mit UPOE (60W+)",
                min_value=0,
                max_value=500,
                value=0,
                step=4,
                help="Wi-Fi 6E/7 APs, PTZ Kameras, Digital Signage"
            )
            
            redundant_power = st.checkbox(
                "Redundante Stromversorgung",
                help="Dual Power Supply für kritische Switches"
            )
        
        st.markdown("---")
        
        # Layer 3 requirements
        st.markdown("### 📶 Erweiterte Features")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            layer3_routing = st.checkbox(
                "Layer 3 Routing",
                help="OSPF, BGP für Inter-VLAN Routing"
            )
        
        with col2:
            aggregation_needed = st.checkbox(
                "Aggregation Switch",
                help="Zentraler Core/Distribution Switch"
            )
        
        with col3:
            fiber_uplinks = st.checkbox(
                "Glasfaser-Uplinks",
                help="SFP/SFP+ Fiber-Verbindungen"
            )
        
        submitted = st.form_submit_button("🧮 Berechnen", use_container_width=True)
        
        if submitted:
            with st.spinner("Berechnung läuft..."):
                results = calculator.calculate_switch_requirements(
                    access_ports_needed=access_ports,
                    poe_devices=poe_devices,
                    upoe_devices=upoe_devices,
                    stacking_required=stacking_required
                )
                
                results['parameters'] = {
                    'access_ports': access_ports,
                    'poe_devices': poe_devices,
                    'upoe_devices': upoe_devices,
                    'uplink_speed': uplink_speed,
                    'stacking_required': stacking_required,
                    'layer3_routing': layer3_routing,
                    'aggregation_needed': aggregation_needed,
                    'fiber_uplinks': fiber_uplinks,
                    'redundant_power': redundant_power
                }
                
                st.session_state['sizing_results'] = results
    
    # Display results
    if st.session_state.get('sizing_results'):
        display_ms_results(st.session_state['sizing_results'], product_loader)


def calculate_ise(calculator, product_loader):
    """Calculate ISE requirements"""
    
    st.subheader("🟡 ISE Sizing")
    st.markdown("Dimensioniere Cisco Identity Services Engine")
    
    with st.form("ise_sizing_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📱 Endpoint-Anforderungen")
            
            endpoint_count = st.number_input(
                "Anzahl Endpoints",
                min_value=100,
                max_value=1000000,
                value=5000,
                step=100,
                help="Alle verwalteten Geräte (PCs, Phones, IoT)"
            )
            
            concurrent_sessions = st.number_input(
                "Gleichzeitige Sessions",
                min_value=100,
                max_value=500000,
                value=int(endpoint_count * 0.8),
                step=100,
                help="Typischerweise 60-80% der Endpoints"
            )
            
            guest_portal = st.checkbox(
                "Guest Portal benötigt",
                value=True,
                help="Self-Service Portal für Gäste"
            )
        
        with col2:
            st.markdown("### 🏢 Deployment-Szenario")
            
            deployment_scenario = st.selectbox(
                "Szenario",
                ["Single Site", "High Availability", "Distributed Multi-Site"],
                help="Beeinflusst Anzahl der benötigten Nodes"
            )
            
            use_cases = st.multiselect(
                "Use Cases",
                ["802.1X (Wired/Wireless)", "Guest Access", "BYOD", "Profiling", "TrustSec", "Device Admin (TACACS+)"],
                default=["802.1X (Wired/Wireless)", "Guest Access"]
            )
            
            compliance = st.checkbox(
                "Compliance Requirements",
                help="Audit-Logging, Reporting für Compliance"
            )
        
        st.markdown("---")
        
        # License tier
        st.markdown("### 📜 Lizenz-Tier")
        
        license_tier = st.radio(
            "ISE Lizenz",
            ["Base", "Plus", "Apex"],
            help="Base: 802.1X | Plus: +Guest, BYOD, Profiling | Apex: +TrustSec, Device Admin"
        )
        
        st.info(f"""
        **{license_tier} Lizenz beinhaltet:**
        - **Base:** 802.1X Authentication, Basic Posture
        - **Plus:** +Guest Portal, BYOD Onboarding, Device Profiling
        - **Apex:** +TrustSec (SGT), Device Administration (TACACS+), pxGrid
        """)
        
        submitted = st.form_submit_button("🧮 Berechnen", use_container_width=True)
        
        if submitted:
            with st.spinner("Berechnung läuft..."):
                results = calculator.calculate_ise_requirements(
                    endpoint_count=endpoint_count,
                    concurrent_sessions=concurrent_sessions,
                    deployment_scenario=deployment_scenario
                )
                
                results['parameters'] = {
                    'endpoint_count': endpoint_count,
                    'concurrent_sessions': concurrent_sessions,
                    'deployment_scenario': deployment_scenario,
                    'guest_portal': guest_portal,
                    'use_cases': use_cases,
                    'compliance': compliance,
                    'license_tier': license_tier
                }
                
                st.session_state['sizing_results'] = results
    
    # Display results
    if st.session_state.get('sizing_results'):
        display_ise_results(st.session_state['sizing_results'], product_loader)


# Result display functions

def display_ap_results(results, product_loader):
    """Display Access Point sizing results"""
    
    st.markdown("---")
    st.success("✅ Berechnung abgeschlossen!")
    
    # Summary
    st.subheader("📊 Zusammenfassung")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Empfohlene APs", results['recommended_aps'])
    
    with col2:
        st.metric("Fläche pro AP", f"{results['parameters']['area_sqm'] / results['recommended_aps']:.0f} m²")
    
    with col3:
        st.metric("Clients pro AP", f"{results['parameters']['client_count'] / results['recommended_aps']:.0f}")
    
    # Reasoning
    st.info(f"💡 **Begründung:** {results['reasoning']}")
    
    st.markdown("---")
    
    # Recommended products
    st.subheader("🎯 Empfohlene Produkte")
    
    if results.get('filtered_suggestions'):
        for model_id in results['filtered_suggestions'][:5]:  # Top 5
            product = product_loader.get_product_by_id(model_id.lower())
            
            if product:
                with st.expander(f"✅ {product.get('name', 'N/A')} - {product.get('wifi_standard', '')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**SKU:** `{product.get('sku_base', 'N/A')}`")
                        st.markdown(f"**Wi-Fi:** {product.get('wifi_standard', 'N/A')}")
                        st.markdown(f"**Data Rate:** {product.get('max_data_rate', 'N/A')}")
                    
                    with col2:
                        st.markdown(f"**PoE:** {product.get('poe_requirement', 'N/A')}")
                        st.markdown(f"**Clients:** {product.get('recommended_clients', 'N/A')}")
                        st.markdown(f"**Coverage:** {product.get('coverage_area', 'N/A')}")
                    
                    with col3:
                        if product.get('datasheet_url'):
                            st.markdown(f"[📄 Datasheet]({product.get('datasheet_url')})")
                        
                        if st.button(f"➕ Zu Projekt", key=f"add_ap_{product.get('id')}"):
                            add_to_project(product, results['recommended_aps'])
    else:
        st.warning("⚠️ Keine passenden Produkte gefunden. Passe die Kriterien an.")
    
    # Add to project button
    if st.button("💾 Konfiguration als Projekt speichern", use_container_width=True):
        st.info("ℹ️ Projekt-Funktion in Entwicklung - nutze 'Zu Projekt hinzufügen' bei einzelnen Produkten")


def display_mx_results(results, product_loader):
    """Display Firewall sizing results"""
    
    st.markdown("---")
    st.success("✅ Berechnung abgeschlossen!")
    
    # Summary
    st.subheader("📊 Zusammenfassung")
    
    col1, col2, col3 = st.columns(3)
    
    params = results['parameters']
    
    with col1:
        st.metric("Nutzer", params['user_count'])
    
    with col2:
        st.metric("Bandbreite", f"{params['bandwidth_mbps']} Mbps")
    
    with col3:
        st.metric("VPN Tunnel", params['vpn_tunnels'])
    
    # HA recommendation
    if results.get('ha_recommended') or params.get('ha_required'):
        st.warning("⚠️ **High Availability empfohlen:** 2x MX Appliances im HA-Paar")
    
    # Reasoning
    st.info(f"💡 **Begründung:** {results['reasoning']}")
    
    st.markdown("---")
    
    # Recommended products
    st.subheader("🎯 Empfohlene Modelle")
    
    for model_id in results['recommended_models']:
        product = product_loader.get_product_by_id(model_id.lower())
        
        if product:
            with st.expander(f"✅ {product.get('name', 'N/A')}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**SKU:** `{product.get('sku_base', 'N/A')}`")
                    st.markdown(f"**Form Factor:** {product.get('form_factor', 'N/A')}")
                    st.markdown(f"**Users:** {product.get('recommended_users', 'N/A')}")
                
                with col2:
                    st.markdown(f"**FW Throughput:** {product.get('firewall_throughput', 'N/A')}")
                    st.markdown(f"**VPN Throughput:** {product.get('vpn_throughput', 'N/A')}")
                    st.markdown(f"**Max VPN Tunnels:** {product.get('max_vpn_tunnels', 'N/A')}")
                
                with col3:
                    st.markdown(f"**WAN Ports:** {product.get('wan_ports', 'N/A')}")
                    st.markdown(f"**LAN Ports:** {product.get('lan_ports', 'N/A')}")
                    
                    if product.get('datasheet_url'):
                        st.markdown(f"[📄 Datasheet]({product.get('datasheet_url')})")
                
                # Quantity recommendation
                quantity = 2 if (results.get('ha_recommended') or params.get('ha_required')) else 1
                
                if st.button(f"➕ {quantity}x zu Projekt", key=f"add_mx_{product.get('id')}"):
                    add_to_project(product, quantity)


def display_ms_results(results, product_loader):
    """Display Switch sizing results"""
    
    st.markdown("---")
    st.success("✅ Berechnung abgeschlossen!")
    
    # Summary
    st.subheader("📊 Zusammenfassung")
    
    col1, col2, col3 = st.columns(3)
    
    params = results['parameters']
    
    with col1:
        st.metric("Access Ports", params['access_ports'])
    
    with col2:
        st.metric("PoE Budget", f"{results['total_poe_budget_needed']}W")
    
    with col3:
        total_switches = sum(s['quantity'] for s in results['recommended_switches'] if s.get('type') != 'stacking_cable')
        st.metric("Switches", total_switches)
    
    # Reasoning
    st.info(f"💡 **Begründung:** {results['reasoning']}")
    
    st.markdown("---")
    
    # Recommended switches
    st.subheader("🎯 Empfohlene Switch-Konfiguration")
    
    for item in results['recommended_switches']:
        if item.get('type') == 'stacking_cable':
            # Stacking cable
            accessory = product_loader.get_accessory_by_id(item['model'].lower())
            if accessory:
                st.markdown(f"➕ **{item['quantity']}x {accessory.get('name', 'N/A')}** (Stacking)")
        else:
            # Switch
            product = product_loader.get_product_by_id(item['model'].lower())
            
            if product:
                with st.expander(f"✅ {item['quantity']}x {product.get('name', 'N/A')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**SKU:** `{product.get('sku_base', 'N/A')}`")
                        st.markdown(f"**Ports:** {product.get('total_ports', 'N/A')}")
                        st.markdown(f"**PoE Ports:** {product.get('poe_ports', 'N/A')}")
                    
                    with col2:
                        st.markdown(f"**PoE Budget:** {product.get('poe_budget', 'N/A')}")
                        st.markdown(f"**Stacking:** {product.get('stacking', 'N/A')}")
                        st.markdown(f"**Layer 3:** {product.get('layer3_features', 'N/A')}")
                    
                    with col3:
                        if product.get('datasheet_url'):
                            st.markdown(f"[📄 Datasheet]({product.get('datasheet_url')})")
                        
                        if st.button(f"➕ {item['quantity']}x zu Projekt", key=f"add_ms_{product.get('id')}"):
                            add_to_project(product, item['quantity'])


def display_ise_results(results, product_loader):
    """Display ISE sizing results"""
    
    st.markdown("---")
    st.success("✅ Berechnung abgeschlossen!")
    
    # Summary
    st.subheader("📊 Zusammenfassung")
    
    col1, col2, col3 = st.columns(3)
    
    params = results['parameters']
    
    with col1:
        st.metric("Endpoints", f"{params['endpoint_count']:,}")
    
    with col2:
        st.metric("ISE Nodes", results['node_count'])
    
    with col3:
        st.metric("Lizenz", params['license_tier'])
    
    # Architecture
    st.info(f"🏗️ **Architektur:** {results['deployment_architecture']}")
    
    # Reasoning
    st.info(f"💡 **Begründung:** {results['reasoning']}")
    
    st.markdown("---")
    
    # Recommended appliance
    st.subheader("🎯 Empfohlenes ISE Appliance")
    
    product = product_loader.get_product_by_id(results['recommended_model'].lower())
    
    if product:
        with st.expander(f"✅ {results['node_count']}x {product.get('name', 'N/A')}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**SKU:** `{product.get('sku_base', 'N/A')}`")
                st.markdown(f"**Endpoints:** {product.get('recommended_endpoints', 'N/A')}")
                st.markdown(f"**Deployment:** {product.get('deployment_type', 'N/A')}")
            
            with col2:
                st.markdown(f"**CPU:** {product.get('cpu', 'N/A')}")
                st.markdown(f"**RAM:** {product.get('ram', 'N/A')}")
                st.markdown(f"**Storage:** {product.get('storage', 'N/A')}")
            
            with col3:
                st.markdown(f"**Form Factor:** {product.get('form_factor', 'N/A')}")
                
                if product.get('datasheet_url'):
                    st.markdown(f"[📄 Datasheet]({product.get('datasheet_url')})")
            
            # License SKUs
            st.markdown("---")
            st.markdown("**Benötigte Lizenzen:**")
            
            license_tier = params['license_tier'].lower()
            licenses = product.get('sku_licenses', {})
            
            # Show relevant licenses
            for duration in ['1yr', '3yr', '5yr']:
                license_key = f"{license_tier}_{duration}"
                if license_key in licenses:
                    st.markdown(f"- {duration.upper()}: `{licenses[license_key]}`")
            
            if st.button(f"➕ {results['node_count']}x zu Projekt", key=f"add_ise_{product.get('id')}"):
                add_to_project(product, results['node_count'])


# Helper functions

def filter_ap_recommendations(suggestions, wifi_standard, outdoor, poe_req, budget, meraki_only, product_loader):
    """Filter AP recommendations based on criteria"""
    
    filtered = []
    
    for model_id in suggestions:
        product = product_loader.get_product_by_id(model_id.lower())
        
        if not product:
            continue
        
        # Filter by Wi-Fi standard
        if wifi_standard:
            if wifi_standard not in product.get('wifi_standard', ''):
                continue
        
        # Filter by outdoor
        if outdoor and product.get('subcategory') != 'Outdoor':
            continue
        
        # Filter by Meraki only
        if meraki_only and product.get('category') == 'Catalyst AP':
            continue
        
        # Budget constraint (simple heuristic based on model number)
        if budget == "Entry-Level bevorzugt":
            model_num = ''.join(filter(str.isdigit, product.get('id', '')))
            if model_num and int(model_num) > 40:
                continue
        
        filtered.append(model_id)
    
    return filtered


def add_to_project(product, quantity):
    """Add product to project (placeholder)"""
    
    if 'project_items' not in st.session_state:
        st.session_state['project_items'] = []
    
    st.session_state['project_items'].append({
        'product_id': product.get('id'),
        'product_name': product.get('name'),
        'sku': product.get('sku_base'),
        'quantity': quantity,
        'category': product.get('category')
    })
    
    st.success(f"✅ {quantity}x {product.get('name')} zu Projekt hinzugefügt!")


if __name__ == "__main__":
    main()
