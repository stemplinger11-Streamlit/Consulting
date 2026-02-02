"""
Admin Tools Page
Web Scraping, Database Updates, Data Management
"""

import streamlit as st
from utils.auth import require_admin, get_current_user
from utils.scraper import get_scraper
from utils.product_loader import get_product_loader
import os

# Authentication required
require_admin(lambda: main())

def main():
    st.title("🔧 Admin Tools")
    st.markdown("Verwaltungswerkzeuge für Datenbank-Updates und Web Scraping")
    
    user = get_current_user()
    st.info(f"👤 Eingeloggt als: **{user['username']}** (Admin)")
    
    st.markdown("---")
    
    # Tabs for different admin functions
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Web Scraping",
        "📊 Datenbank Status",
        "🔄 Manuelle Updates",
        "⚙️ Einstellungen"
    ])
    
    # Tab 1: Web Scraping
    with tab1:
        st.header("🔍 Web Scraping")
        st.markdown("Automatisches Auslesen von offiziellen Cisco/Meraki Seiten")
        
        scraper = get_scraper()
        product_loader = get_product_loader()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("EOL Daten aktualisieren")
            st.markdown("Scrapt aktuelle End-of-Life Daten von Meraki")
            
            if st.button("🔄 EOL Daten scrapen", key="scrape_eol"):
                with st.spinner("Scraping läuft..."):
                    updated = scraper.update_product_database_with_eol(product_loader)
                st.success(f"✅ {updated} Produkte aktualisiert!")
        
        with col2:
            st.subheader("MR Datasheets scrapen")
            st.markdown("Scrapt alle MR Access Point Spezifikationen")
            
            if st.button("📄 MR Datasheets scrapen", key="scrape_mr"):
                with st.spinner("Scraping läuft... (kann mehrere Minuten dauern)"):
                    updated = scraper.scrape_all_mr_datasheets(product_loader)
                st.success(f"✅ {updated} MR Produkte aktualisiert!")
        
        st.markdown("---")
        
        st.subheader("Einzelnes Produkt scrapen")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category = st.selectbox(
                "Kategorie",
                ["MR", "MX", "MS", "MV"],
                key="scrape_category"
            )
        
        with col2:
            model = st.text_input("Modell (z.B. MR46)", key="scrape_model")
        
        with col3:
            st.write("")  # Spacing
            st.write("")
            if st.button("🔍 Scrape", key="scrape_single"):
                if model:
                    with st.spinner(f"Scraping {model}..."):
                        specs = scraper.scrape_product_datasheet(category, model)
                    
                    if specs:
                        st.success("✅ Erfolgreich!")
                        st.json(specs)
                else:
                    st.warning("⚠️ Bitte Modell eingeben")
        
        st.markdown("---")
        
        st.info("""
        **⚠️ Hinweise zum Web Scraping:**
        - Respektiere Cisco's robots.txt und Rate Limits
        - Scraping kann mehrere Minuten dauern
        - Prüfe gescrapte Daten immer manuell
        - Bei Fehlern: Manuelles Update nutzen
        """)
    
    # Tab 2: Database Status
    with tab2:
        st.header("📊 Datenbank Status")
        
        product_loader = get_product_loader()
        
        # Statistics
        all_products = product_loader.get_all_products()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gesamt Produkte", len(all_products))
        
        with col2:
            active = len([p for p in all_products if p.get('status') == 'Active'])
            st.metric("Aktive Produkte", active)
        
        with col3:
            eol = len([p for p in all_products if p.get('status') == 'EOL Announced'])
            st.metric("EOL Announced", eol)
        
        with col4:
            accessories = len(product_loader.accessories)
            st.metric("Zubehör", accessories)
        
        st.markdown("---")
        
        # Category breakdown
        st.subheader("Produkte pro Kategorie")
        
        category_stats = {}
        for product in all_products:
            cat = product.get('category', 'Unknown')
            category_stats[cat] = category_stats.get(cat, 0) + 1
        
        category_df = {
            'Kategorie': list(category_stats.keys()),
            'Anzahl': list(category_stats.values())
        }
        
        st.bar_chart(category_df, x='Kategorie', y='Anzahl')
        
        st.markdown("---")
        
        # Recent updates (mock - would need timestamp tracking)
        st.subheader("Letzte Aktualisierungen")
        st.info("ℹ️ Feature in Entwicklung - zeigt zukünftig letzte Änderungen")
    
    # Tab 3: Manual Updates
    with tab3:
        st.header("🔄 Manuelle Updates")
        
        st.subheader("Produkt bearbeiten")
        
        product_loader = get_product_loader()
        all_products = product_loader.get_all_products()
        
        # Product selector
        product_names = [f"{p.get('name', '')} ({p.get('id', '')})" for p in all_products]
        selected_product = st.selectbox("Produkt auswählen", product_names)
        
        if selected_product:
            # Extract ID from selection
            product_id = selected_product.split('(')[-1].replace(')', '')
            product = product_loader.get_product_by_id(product_id)
            
            if product:
                with st.expander("📝 Produkt bearbeiten", expanded=True):
                    # Create edit form
                    with st.form("edit_product_form"):
                        name = st.text_input("Name", value=product.get('name', ''))
                        category = st.text_input("Kategorie", value=product.get('category', ''))
                        sku_base = st.text_input("SKU", value=product.get('sku_base', ''))
                        
                        status = st.selectbox(
                            "Status",
                            ["Active", "EOL Announced", "End of Sale"],
                            index=["Active", "EOL Announced", "End of Sale"].index(product.get('status', 'Active'))
                        )
                        
                        eol_announced = st.date_input(
                            "EOL Announced",
                            value=None
                        )
                        
                        eos_date = st.date_input(
                            "End of Sale Date",
                            value=None
                        )
                        
                        datasheet_url = st.text_input(
                            "Datasheet URL",
                            value=product.get('datasheet_url', '')
                        )
                        
                        submitted = st.form_submit_button("💾 Speichern")
                        
                        if submitted:
                            # Update product
                            product['name'] = name
                            product['category'] = category
                            product['sku_base'] = sku_base
                            product['status'] = status
                            product['eol_announced'] = eol_announced.isoformat() if eol_announced else None
                            product['eos_date'] = eos_date.isoformat() if eos_date else None
                            product['datasheet_url'] = datasheet_url
                            
                            # Save
                            cat_key = product.get('_category_file', category.lower())
                            product_loader.save_product(cat_key, product)
                            
                            st.success("✅ Produkt aktualisiert!")
                            st.rerun()
    
    # Tab 4: Settings
    with tab4:
        st.header("⚙️ Einstellungen")
        
        st.subheader("Scraper Einstellungen")
        
        scraper = get_scraper()
        
        rate_limit = st.slider(
            "Rate Limit (Sekunden zwischen Requests)",
            min_value=1,
            max_value=10,
            value=scraper.rate_limit_delay,
            help="Verhindert zu viele Requests an Cisco Server"
        )
        
        if st.button("💾 Einstellungen speichern"):
            scraper.rate_limit_delay = rate_limit
            st.success("✅ Einstellungen gespeichert!")
        
        st.markdown("---")
        
        st.subheader("Datenbank Export/Import")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Export**")
            if st.button("📥 Alle Daten exportieren"):
                st.info("ℹ️ Feature in Entwicklung")
        
        with col2:
            st.markdown("**Import**")
            uploaded_file = st.file_uploader("JSON Datei hochladen", type=['json'])
            if uploaded_file:
                st.info("ℹ️ Feature in Entwicklung")
        
        st.markdown("---")
        
        st.subheader("Gefährliche Aktionen")
        st.warning("⚠️ Diese Aktionen können nicht rückgängig gemacht werden!")
        
        if st.button("🗑️ Cache leeren", type="secondary"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("✅ Cache geleert!")


if __name__ == "__main__":
    main()
