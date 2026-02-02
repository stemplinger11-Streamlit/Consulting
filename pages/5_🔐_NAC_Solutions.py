"""
NAC Solutions Page
Compare Network Access Control solutions: ISE vs Meraki
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.product_loader import get_product_loader
import json

# Require authentication
require_auth(lambda: main())

def main():
    st.title("🔐 Network Access Control (NAC)")
    st.markdown("Vergleiche Cisco ISE und Meraki NAC-Lösungen für dein Netzwerk")
    
    # Load translations
    with open('data/translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    
    lang = st.session_state.get('language', 'de')
    t = translations[lang]
    
    st.markdown("---")
    
    # Main navigation
    nav = st.radio(
        "Navigation",
        ["🔍 Lösungsvergleich", "🎯 Empfehlungs-Assistent", "📊 Feature-Matrix", "🏗️ Architektur-Beispiele", "📚 Ressourcen"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if nav == "🔍 Lösungsvergleich":
        display_solution_comparison()
    
    elif nav == "🎯 Empfehlungs-Assistent":
        display_recommendation_wizard()
    
    elif nav == "📊 Feature-Matrix":
        display_feature_matrix()
    
    elif nav == "🏗️ Architektur-Beispiele":
        display_architecture_examples()
    
    elif nav == "📚 Ressourcen":
        display_resources()


def display_solution_comparison():
    """Display high-level solution comparison"""
    
    st.subheader("🔍 NAC-Lösungen im Überblick")
    
    # Quick comparison cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='border: 2px solid #0066cc; border-radius: 10px; padding: 20px; background-color: #f0f8ff;'>
            <h3 style='color: #0066cc;'>🔵 Cisco ISE</h3>
            <p><strong>Identity Services Engine</strong></p>
            <p>Enterprise NAC mit umfassenden Policy-Enforcement und Security-Features</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        
        st.markdown("**✅ Ideal für:**")
        st.markdown("- Enterprise-Umgebungen (>500 Endpoints)")
        st.markdown("- Hochkomplexe Policies")
        st.markdown("- Multi-Vendor Netzwerke")
        st.markdown("- TrustSec (SGT/SXP)")
        st.markdown("- Device Administration (TACACS+)")
        st.markdown("- Strenge Compliance-Anforderungen")
        
        st.markdown("")
        
        st.markdown("**⚡ Key Features:**")
        st.markdown("- 802.1X für Wired & Wireless")
        st.markdown("- Guest Portal & Sponsor Portal")
        st.markdown("- BYOD Onboarding")
        st.markdown("- Device Profiling")
        st.markdown("- TrustSec (Security Group Tags)")
        st.markdown("- pxGrid Integration")
        st.markdown("- Posture Assessment")
        st.markdown("- Device Admin (TACACS+)")
    
    with col2:
        st.markdown("""
        <div style='border: 2px solid #00c853; border-radius: 10px; padding: 20px; background-color: #f1f8f4;'>
            <h3 style='color: #00c853;'>🟢 Meraki Systems Manager</h3>
            <p><strong>Cloud-Managed NAC</strong></p>
            <p>Einfache, cloud-basierte NAC-Lösung mit Zero-Touch Deployment</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        
        st.markdown("**✅ Ideal für:**")
        st.markdown("- SMB bis Mid-Market (<1000 Endpoints)")
        st.markdown("- Cloud-First Strategie")
        st.markdown("- Einfache, schnelle Deployments")
        st.markdown("- Meraki-Only Netzwerke")
        st.markdown("- Minimaler Admin-Aufwand")
        st.markdown("- BYOD & Mobile Device Management")
        
        st.markdown("")
        
        st.markdown("**⚡ Key Features:**")
        st.markdown("- Cloud-basiertes Management")
        st.markdown("- 802.1X (einfache Config)")
        st.markdown("- Guest Access (integriert)")
        st.markdown("- MDM für iOS, Android, macOS, Windows")
        st.markdown("- Geofencing & Location Tracking")
        st.markdown("- App Management")
        st.markdown("- Compliance & Reporting")
        st.markdown("- Zero-Touch Deployment")
    
    st.markdown("---")
    
    # Decision helper
    st.subheader("🎯 Schnellentscheidung")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        endpoints = st.number_input("Anzahl Endpoints", min_value=10, max_value=100000, value=500, step=10)
    
    with col2:
        complexity = st.selectbox("Policy-Komplexität", ["Einfach", "Mittel", "Komplex"])
    
    with col3:
        vendor = st.selectbox("Netzwerk-Infrastruktur", ["Nur Meraki", "Multi-Vendor", "Gemischt"])
    
    # Simple recommendation
    if st.button("💡 Empfehlung anzeigen", use_container_width=True):
        recommendation = get_quick_recommendation(endpoints, complexity, vendor)
        
        if recommendation == "ISE":
            st.success("✅ **Empfehlung: Cisco ISE**")
            st.info("Basierend auf deinen Anforderungen (Enterprise-Scale, Policy-Komplexität, Multi-Vendor) ist ISE die bessere Wahl.")
        else:
            st.success("✅ **Empfehlung: Meraki Systems Manager**")
            st.info("Basierend auf deinen Anforderungen (SMB/Mid-Market, Cloud-First, Meraki-Netzwerk) ist Meraki SM die bessere Wahl.")


def display_recommendation_wizard():
    """Interactive recommendation wizard"""
    
    st.subheader("🎯 NAC Empfehlungs-Assistent")
    st.markdown("Beantworte ein paar Fragen, um die optimale NAC-Lösung zu finden")
    
    # Initialize wizard state
    if 'wizard_step' not in st.session_state:
        st.session_state['wizard_step'] = 1
    
    if 'wizard_answers' not in st.session_state:
        st.session_state['wizard_answers'] = {}
    
    step = st.session_state['wizard_step']
    answers = st.session_state['wizard_answers']
    
    # Progress bar
    progress = (step - 1) / 7
    st.progress(progress)
    st.caption(f"Schritt {step} von 8")
    
    st.markdown("---")
    
    # Step 1: Organization size
    if step == 1:
        st.markdown("### 1️⃣ Unternehmensgröße")
        
        org_size = st.radio(
            "Wie viele Endpoints (Geräte) müssen verwaltet werden?",
            ["< 100", "100 - 500", "500 - 2.000", "2.000 - 10.000", "> 10.000"],
            key="q1"
        )
        
        if st.button("Weiter →", key="next1"):
            answers['org_size'] = org_size
            st.session_state['wizard_step'] = 2
            st.rerun()
    
    # Step 2: Infrastructure
    elif step == 2:
        st.markdown("### 2️⃣ Netzwerk-Infrastruktur")
        
        infrastructure = st.radio(
            "Welche Netzwerk-Hardware wird verwendet?",
            ["100% Cisco Meraki", "Meraki + Catalyst", "Multi-Vendor (Cisco, HP, Aruba, etc.)", "Nur Catalyst/Traditional Cisco"],
            key="q2"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Zurück", key="back2"):
                st.session_state['wizard_step'] = 1
                st.rerun()
        with col2:
            if st.button("Weiter →", key="next2"):
                answers['infrastructure'] = infrastructure
                st.session_state['wizard_step'] = 3
                st.rerun()
    
    # Step 3: Use Cases
    elif step == 3:
        st.markdown("### 3️⃣ Primäre Use Cases")
        
        use_cases = st.multiselect(
            "Welche Features werden benötigt? (Mehrfachauswahl)",
            [
                "802.1X Authentication (Wired/Wireless)",
                "Guest Access Management",
                "BYOD Onboarding",
                "Device Profiling",
                "Network Segmentation (VLAN Assignment)",
                "Security Group Tagging (TrustSec)",
                "Posture Assessment (Compliance Check)",
                "Device Administration (TACACS+)",
                "Mobile Device Management (MDM)",
                "Threat Containment & Quarantine"
            ],
            default=["802.1X Authentication (Wired/Wireless)"],
            key="q3"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Zurück", key="back3"):
                st.session_state['wizard_step'] = 2
                st.rerun()
        with col2:
            if st.button("Weiter →", key="next3"):
                answers['use_cases'] = use_cases
                st.session_state['wizard_step'] = 4
                st.rerun()
    
    # Step 4: Complexity
    elif step == 4:
        st.markdown("### 4️⃣ Policy-Komplexität")
        
        complexity = st.radio(
            "Wie komplex sind die Zugriffs-Policies?",
            [
                "Einfach - Basis-Policies (Mitarbeiter/Gäste)",
                "Mittel - Rollenbasiert (mehrere User-Gruppen)",
                "Komplex - Granular (Device Type, Location, Time, Posture)"
            ],
            key="q4"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Zurück", key="back4"):
                st.session_state['wizard_step'] = 3
                st.rerun()
        with col2:
            if st.button("Weiter →", key="next4"):
                answers['complexity'] = complexity
                st.session_state['wizard_step'] = 5
                st.rerun()
    
    # Step 5: IT Resources
    elif step == 5:
        st.markdown("### 5️⃣ IT-Ressourcen")
        
        it_resources = st.radio(
            "Wie ist das IT-Team aufgestellt?",
            [
                "Klein - 1-2 Admins, wenig NAC-Erfahrung",
                "Mittel - Dediziertes Team, Basis-Erfahrung",
                "Groß - Erfahrenes Security-Team, ISE-Know-how"
            ],
            key="q5"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Zurück", key="back5"):
                st.session_state['wizard_step'] = 4
                st.rerun()
        with col2:
            if st.button("Weiter →", key="next5"):
                answers['it_resources'] = it_resources
                st.session_state['wizard_step'] = 6
                st.rerun()
    
    # Step 6: Deployment Model
    elif step == 6:
        st.markdown("### 6️⃣ Deployment-Präferenz")
        
        deployment = st.radio(
            "Bevorzugtes Deployment-Modell?",
            [
                "Cloud - Keine On-Prem Hardware, Cloud-Managed",
                "On-Premises - Volle Kontrolle, lokale Appliances",
                "Hybrid - Mix aus Cloud & On-Prem"
            ],
            key="q6"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Zurück", key="back6"):
                st.session_state['wizard_step'] = 5
                st.rerun()
        with col2:
            if st.button("Weiter →", key="next6"):
                answers['deployment'] = deployment
                st.session_state['wizard_step'] = 7
                st.rerun()
    
    # Step 7: Compliance
    elif step == 7:
        st.markdown("### 7️⃣ Compliance & Audit")
        
        compliance = st.radio(
            "Compliance-Anforderungen?",
            [
                "Keine besonderen Anforderungen",
                "Standard - Basis-Reporting ausreichend",
                "Streng - Detaillierte Audits erforderlich (GDPR, HIPAA, PCI-DSS)"
            ],
            key="q7"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Zurück", key="back7"):
                st.session_state['wizard_step'] = 6
                st.rerun()
        with col2:
            if st.button("Weiter →", key="next7"):
                answers['compliance'] = compliance
                st.session_state['wizard_step'] = 8
                st.rerun()
    
    # Step 8: Results
    elif step == 8:
        st.markdown("### 8️⃣ Ergebnis & Empfehlung")
        
        # Calculate recommendation
        result = calculate_wizard_recommendation(answers)
        
        # Display result
        if result['solution'] == 'ISE':
            st.success("## ✅ Empfehlung: Cisco ISE")
            st.markdown(f"**Confidence Score:** {result['confidence']}%")
        else:
            st.success("## ✅ Empfehlung: Meraki Systems Manager")
            st.markdown(f"**Confidence Score:** {result['confidence']}%")
        
        st.markdown("---")
        
        # Reasoning
        st.markdown("### 💡 Begründung")
        for reason in result['reasons']:
            st.markdown(f"- {reason}")
        
        st.markdown("---")
        
        # Next steps
        st.markdown("### 🚀 Nächste Schritte")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**1. Sizing durchführen**")
            if st.button("🧮 Zum Sizing Calculator", use_container_width=True):
                st.switch_page("pages/3_🧮_Sizing_Calculator.py")
        
        with col2:
            st.markdown("**2. Produkte anschauen**")
            if st.button("📦 Zum Produktkatalog", use_container_width=True):
                st.switch_page("pages/1_📦_Product_Catalog.py")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Zurück", key="back8"):
                st.session_state['wizard_step'] = 7
                st.rerun()
        with col2:
            if st.button("🔄 Neu starten", key="restart"):
                st.session_state['wizard_step'] = 1
                st.session_state['wizard_answers'] = {}
                st.rerun()


def display_feature_matrix():
    """Display detailed feature comparison matrix"""
    
    st.subheader("📊 Feature-Vergleichsmatrix")
    st.markdown("Detaillierter Vergleich aller NAC-Features")
    
    import pandas as pd
    
    # Feature categories
    categories = {
        "🔐 Authentication & Authorization": [
            ("802.1X (Wired)", "✅ Full Support", "✅ Supported"),
            ("802.1X (Wireless)", "✅ Full Support", "✅ Supported"),
            ("MAB (MAC Auth Bypass)", "✅ Full Support", "✅ Supported"),
            ("Web Authentication", "✅ Full Support", "✅ Supported"),
            ("External Auth (AD/LDAP)", "✅ Full Support", "✅ Supported"),
            ("Multi-Factor Authentication", "✅ Full Support (SAML, RADIUS)", "✅ Supported (SAML)"),
            ("Certificate-Based Auth", "✅ Advanced (EAP-TLS, PEAP)", "✅ Basic"),
        ],
        
        "👥 Guest & BYOD": [
            ("Guest Portal", "✅ Full Featured (Sponsor, Self-Reg)", "✅ Integrated"),
            ("Sponsor Portal", "✅ Advanced", "✅ Basic"),
            ("Guest Self-Registration", "✅ Supported", "✅ Supported"),
            ("Social Login", "✅ Supported", "✅ Supported"),
            ("SMS-based Onboarding", "✅ Supported", "✅ Supported"),
            ("BYOD Device Onboarding", "✅ MyDevices Portal", "✅ Native MDM"),
            ("Dual SSID (Personal/Corporate)", "✅ Supported", "✅ Supported"),
        ],
        
        "🛡️ Security & Compliance": [
            ("Device Profiling", "✅ Advanced (1000+ profiles)", "✅ Basic"),
            ("Posture Assessment", "✅ Full (Agent & Agentless)", "✅ MDM Compliance"),
            ("Threat Containment", "✅ pxGrid + ANC", "✅ Basic Quarantine"),
            ("TrustSec (SGT/SXP)", "✅ Full Support", "❌ Not Supported"),
            ("Security Group Tags", "✅ Full", "❌ Not Supported"),
            ("Network Segmentation", "✅ VLAN + SGT", "✅ VLAN Assignment"),
            ("Compliance Reporting", "✅ Advanced", "✅ Standard"),
        ],
        
        "🔧 Management & Operations": [
            ("Deployment Model", "On-Prem Appliances", "Cloud-Only"),
            ("Zero-Touch Provisioning", "⚠️ Requires Config", "✅ Native"),
            ("GUI Complexity", "Complex (Enterprise)", "Simple (Intuitive)"),
            ("API Availability", "✅ Full REST API", "✅ REST API"),
            ("Multi-Tenancy", "✅ Supported", "✅ Per-Org"),
            ("High Availability", "✅ Active-Standby", "✅ Cloud HA"),
            ("Scalability", "Up to 500k endpoints", "Up to 10k endpoints"),
        ],
        
        "🔌 Integration": [
            ("pxGrid", "✅ Full Support", "❌ Not Supported"),
            ("TACACS+ (Device Admin)", "✅ Full Support", "❌ Not Supported"),
            ("SIEM Integration", "✅ Syslog, pxGrid", "✅ Syslog, API"),
            ("MDM Integration", "✅ Via pxGrid", "✅ Native MDM"),
            ("Threat Intelligence", "✅ pxGrid (Firepower, etc.)", "⚠️ Limited"),
            ("Third-Party NAC", "✅ Via RADIUS Proxy", "❌ Not Applicable"),
        ],
        
        "💰 Licensing & Cost": [
            ("License Model", "Perpetual or Subscription", "Subscription Only"),
            ("License Tiers", "Base / Plus / Apex", "Systems Manager"),
            ("Per-Endpoint Pricing", "✅ Yes", "✅ Yes"),
            ("Hardware Cost", "Appliances Required", "Cloud (No Hardware)"),
            ("Total TCO (5 years, 1000 EP)", "$$$$$ High", "$$$ Medium"),
        ],
    }
    
    # Display each category
    for category, features in categories.items():
        with st.expander(f"**{category}**", expanded=True):
            df_data = []
            for feature, ise_support, meraki_support in features:
                df_data.append({
                    'Feature': feature,
                    'Cisco ISE': ise_support,
                    'Meraki SM': meraki_support
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)


def display_architecture_examples():
    """Display architecture diagrams and examples"""
    
    st.subheader("🏗️ Architektur-Beispiele")
    
    # Architecture selector
    arch_type = st.selectbox(
        "Wähle ein Szenario",
        ["ISE - Distributed Deployment", "ISE - Small Deployment", "Meraki - Cloud NAC", "Hybrid - ISE + Meraki"]
    )
    
    st.markdown("---")
    
    if arch_type == "ISE - Distributed Deployment":
        st.markdown("### 🏢 ISE Distributed Deployment (Enterprise)")
        
        st.markdown("""
        **Use Case:** Große Enterprise mit mehreren Standorten (>5.000 Endpoints)
        
        **Architektur:**
        - **2x PAN (Policy Admin Nodes):** Primary + Secondary für HA
        - **2x MnT (Monitoring & Troubleshooting):** Logging & Reporting
        - **Nx PSN (Policy Service Nodes):** Verteilte RADIUS/TACACS+ Services
        
        **Vorteile:**
        - ✅ Maximale Skalierbarkeit (bis 500k Endpoints)
        - ✅ High Availability auf allen Ebenen
        - ✅ Performance durch verteilte PSNs
        - ✅ Zentrale Policy-Verwaltung
        
        **Komponenten:**
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Data Center (HQ):**")
            st.markdown("- 2x ISE-3395 (PAN Primary/Secondary)")
            st.markdown("- 2x ISE-3395 (MnT Primary/Secondary)")
            st.markdown("- 2x ISE-3355 (PSN)")
        
        with col2:
            st.markdown("**Remote Sites:**")
            st.markdown("- Site A: 2x ISE-3315 (PSN)")
            st.markdown("- Site B: 2x ISE-3315 (PSN)")
            st.markdown("- Site C: 2x ISE-3315 (PSN)")
        
        st.info("💡 **Best Practice:** Mindestens 2 PSNs pro geografischer Region für Redundanz und Performance")
    
    elif arch_type == "ISE - Small Deployment":
        st.markdown("### 🏪 ISE Small Deployment (SMB/Branch)")
        
        st.markdown("""
        **Use Case:** Einzelner Standort, bis 5.000 Endpoints
        
        **Architektur:**
        - **2x ISE Appliances:** Standalone oder HA-Pair
        - Jede Appliance übernimmt alle Rollen (PAN, MnT, PSN)
        
        **Vorteile:**
        - ✅ Einfaches Setup
        - ✅ Redundanz durch HA
        - ✅ Niedrigere Kosten
        - ✅ Alle ISE-Features verfügbar
        
        **Komponenten:**
        """)
        
        st.markdown("**Empfohlene Appliances:**")
        st.markdown("- 2x ISE-3315 (bis 5k Endpoints) - HA Pair")
        st.markdown("- 2x ISE-3355 (bis 50k Endpoints) - HA Pair")
        
        st.warning("⚠️ **Hinweis:** Auch Small Deployments profitieren von HA (2 Appliances)")
    
    elif arch_type == "Meraki - Cloud NAC":
        st.markdown("### ☁️ Meraki Cloud NAC")
        
        st.markdown("""
        **Use Case:** SMB bis Mid-Market, Meraki-Netzwerk, Cloud-First
        
        **Architektur:**
        - **Cloud Dashboard:** Zentrale Verwaltung (cloud.meraki.com)
        - **Meraki APs/Switches:** Lokale Authentifizierung
        - **Systems Manager:** MDM & Device Management
        - **No On-Prem Hardware:** Alles Cloud-basiert
        
        **Vorteile:**
        - ✅ Zero-Touch Deployment
        - ✅ Keine Appliances erforderlich
        - ✅ Automatische Updates
        - ✅ Integriertes MDM
        - ✅ Einfache Verwaltung
        
        **Komponenten:**
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Cloud Services:**")
            st.markdown("- Meraki Dashboard (Cloud)")
            st.markdown("- Systems Manager (MDM)")
            st.markdown("- RADIUS (Cloud)")
            st.markdown("- Guest Portal (Cloud)")
        
        with col2:
            st.markdown("**On-Site:**")
            st.markdown("- Meraki MR Access Points")
            st.markdown("- Meraki MS Switches")
            st.markdown("- MX Security Appliances")
            st.markdown("- (Kein NAC-Server erforderlich)")
        
        st.success("✅ **Ideal für:** Organisationen, die schnelle Deployments ohne IT-Overhead bevorzugen")
    
    elif arch_type == "Hybrid - ISE + Meraki":
        st.markdown("### 🔄 Hybrid Deployment (ISE + Meraki)")
        
        st.markdown("""
        **Use Case:** Zentrale mit ISE, Branches mit Meraki
        
        **Architektur:**
        - **Headquarter:** Cisco ISE für komplexe Policies
        - **Branch Offices:** Meraki für einfaches Management
        - **Integration:** ISE als RADIUS-Server für Meraki
        
        **Vorteile:**
        - ✅ Best of Both Worlds
        - ✅ Zentrale Policy-Enforcement (ISE)
        - ✅ Einfache Branch-Verwaltung (Meraki)
        - ✅ Einheitliche Identity Source
        
        **Setup:**
        """)
        
        st.markdown("**HQ (ISE):**")
        st.markdown("- Cisco Catalyst Switches/APs")
        st.markdown("- ISE für 802.1X, TrustSec, Posture")
        st.markdown("- Komplexe Policies")
        
        st.markdown("**Branches (Meraki):**")
        st.markdown("- Meraki MR/MS/MX")
        st.markdown("- RADIUS-Authentifizierung zu ISE")
        st.markdown("- VLAN Assignment von ISE")
        
        st.info("💡 **Best Practice:** ISE als zentraler RADIUS-Server, Meraki für einfache Branch-Verwaltung")


def display_resources():
    """Display useful resources and documentation"""
    
    st.subheader("📚 Ressourcen & Dokumentation")
    
    # ISE Resources
    st.markdown("### 🔵 Cisco ISE Ressourcen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Offizielle Dokumentation:**")
        st.markdown("- [ISE Installation Guide](https://www.cisco.com/c/en/us/support/security/identity-services-engine/products-installation-guides-list.html)")
        st.markdown("- [ISE Configuration Guides](https://www.cisco.com/c/en/us/support/security/identity-services-engine/products-installation-and-configuration-guides-list.html)")
        st.markdown("- [ISE Ordering Guide](https://www.cisco.com/c/en/us/products/collateral/security/identity-services-engine/guide-c07-656177.html)")
        st.markdown("- [ISE Community Forum](https://community.cisco.com/t5/network-access-control/bd-p/discussions-nac)")
    
    with col2:
        st.markdown("**Lizenzierung:**")
        st.markdown("- [ISE Licensing Guide](https://www.cisco.com/c/en/us/products/collateral/security/identity-services-engine/guide-c07-656177.html)")
        st.markdown("- **Base:** 802.1X, Basic Profiling")
        st.markdown("- **Plus:** +Guest, BYOD, Advanced Profiling")
        st.markdown("- **Apex:** +TrustSec, TACACS+, pxGrid")
    
    st.markdown("---")
    
    # Meraki Resources
    st.markdown("### 🟢 Meraki Systems Manager Ressourcen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Offizielle Dokumentation:**")
        st.markdown("- [Systems Manager Documentation](https://documentation.meraki.com/SM)")
        st.markdown("- [Meraki Authentication Best Practices](https://documentation.meraki.com/MR/Encryption_and_Authentication)")
        st.markdown("- [Guest Access Setup](https://documentation.meraki.com/MR/Guest_Access)")
        st.markdown("- [Meraki Community](https://community.meraki.com/)")
    
    with col2:
        st.markdown("**Video Tutorials:**")
        st.markdown("- [Meraki SM Overview (YouTube)](https://www.youtube.com)")
        st.markdown("- [802.1X Configuration](https://www.youtube.com)")
        st.markdown("- [Guest Portal Setup](https://www.youtube.com)")
    
    st.markdown("---")
    
    # Comparison Documents
    st.markdown("### 📊 Vergleichsdokumente")
    
    st.markdown("**Cisco-Eigene Vergleiche:**")
    st.markdown("- [ISE vs Meraki: Choosing the Right NAC](https://www.cisco.com) (Placeholder)")
    st.markdown("- [NAC Solution Selector Tool](https://www.cisco.com) (Placeholder)")
    
    st.markdown("---")
    
    # Training
    st.markdown("### 🎓 Training & Zertifizierung")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**ISE Training:**")
        st.markdown("- Cisco ISE Essentials (SISE)")
        st.markdown("- Implementing Cisco ISE (300-715 SISE)")
        st.markdown("- ISE TrustSec Training")
    
    with col2:
        st.markdown("**Meraki Training:**")
        st.markdown("- Meraki Foundations Certification")
        st.markdown("- Meraki Webinars (Free)")
        st.markdown("- Meraki Virtual Labs")


# Helper functions

def get_quick_recommendation(endpoints, complexity, vendor):
    """Quick recommendation based on simple criteria"""
    
    score_ise = 0
    score_meraki = 0
    
    # Endpoints
    if endpoints > 2000:
        score_ise += 3
    elif endpoints > 500:
        score_ise += 1
        score_meraki += 1
    else:
        score_meraki += 2
    
    # Complexity
    if complexity == "Komplex":
        score_ise += 3
    elif complexity == "Mittel":
        score_ise += 1
        score_meraki += 1
    else:
        score_meraki += 2
    
    # Vendor
    if vendor == "Multi-Vendor":
        score_ise += 3
    elif vendor == "Nur Meraki":
        score_meraki += 3
    else:
        score_ise += 1
        score_meraki += 1
    
    return "ISE" if score_ise > score_meraki else "Meraki"


def calculate_wizard_recommendation(answers):
    """Calculate detailed recommendation from wizard answers"""
    
    score_ise = 0
    score_meraki = 0
    reasons = []
    
    # Org size
    org_size = answers.get('org_size', '')
    if "> 10.000" in org_size or "2.000 - 10.000" in org_size:
        score_ise += 20
        reasons.append("✅ Enterprise-Scale (>2k Endpoints) → ISE skaliert besser")
    elif "500 - 2.000" in org_size:
        score_ise += 10
        score_meraki += 5
    else:
        score_meraki += 15
        reasons.append("✅ SMB-Scale (<500 Endpoints) → Meraki ausreichend")
    
    # Infrastructure
    infrastructure = answers.get('infrastructure', '')
    if "Multi-Vendor" in infrastructure:
        score_ise += 25
        reasons.append("✅ Multi-Vendor Netzwerk → ISE unterstützt alle Hersteller")
    elif "100% Cisco Meraki" in infrastructure:
        score_meraki += 25
        reasons.append("✅ Pure Meraki Umgebung → Meraki SM nahtlos integriert")
    elif "Nur Catalyst" in infrastructure:
        score_ise += 15
    
    # Use cases
    use_cases = answers.get('use_cases', [])
    if "Security Group Tagging (TrustSec)" in use_cases:
        score_ise += 30
        reasons.append("✅ TrustSec (SGT) benötigt → Nur ISE unterstützt")
    if "Device Administration (TACACS+)" in use_cases:
        score_ise += 25
        reasons.append("✅ TACACS+ Device Admin → Nur ISE unterstützt")
    if "Mobile Device Management (MDM)" in use_cases:
        score_meraki += 15
        reasons.append("✅ Native MDM-Integration → Meraki SM Vorteil")
    if "Posture Assessment (Compliance Check)" in use_cases:
        score_ise += 10
    
    # Complexity
    complexity = answers.get('complexity', '')
    if "Komplex" in complexity:
        score_ise += 20
        reasons.append("✅ Komplexe Policies → ISE flexibler")
    elif "Einfach" in complexity:
        score_meraki += 15
        reasons.append("✅ Einfache Policies → Meraki einfacher zu managen")
    
    # IT Resources
    it_resources = answers.get('it_resources', '')
    if "Groß" in it_resources and "ISE-Know-how" in it_resources:
        score_ise += 15
        reasons.append("✅ Erfahrenes Team mit ISE-Know-how → ISE sinnvoll")
    elif "Klein" in it_resources:
        score_meraki += 20
        reasons.append("✅ Kleines Team ohne NAC-Erfahrung → Meraki einfacher")
    
    # Deployment
    deployment = answers.get('deployment', '')
    if "Cloud" in deployment:
        score_meraki += 20
        reasons.append("✅ Cloud-First Strategie → Meraki Cloud-Native")
    elif "On-Premises" in deployment:
        score_ise += 15
    
    # Compliance
    compliance = answers.get('compliance', '')
    if "Streng" in compliance:
        score_ise += 15
        reasons.append("✅ Strikte Compliance → ISE detailliertere Audits")
    
    # Calculate confidence
    total_score = score_ise + score_meraki
    if score_ise > score_meraki:
        confidence = int((score_ise / total_score) * 100)
        solution = "ISE"
    else:
        confidence = int((score_meraki / total_score) * 100)
        solution = "Meraki"
    
    return {
        'solution': solution,
        'confidence': confidence,
        'reasons': reasons
    }


if __name__ == "__main__":
    main()
