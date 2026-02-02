"""
Projects Page
Manage network deployment projects with Bill of Materials (BOM)
"""

import streamlit as st
from utils.auth import require_auth, get_current_user
from utils.product_loader import get_product_loader
from utils.export import get_export_manager
from datetime import datetime
import json

# Require authentication
require_auth(lambda: main())

def main():
    st.title("📊 Projekt-Management")
    st.markdown("Erstelle und verwalte Netzwerk-Deployment-Projekte mit Stücklisten (BOM)")
    
    # Initialize
    product_loader = get_product_loader()
    
    # Initialize session state for projects
    if 'projects' not in st.session_state:
        st.session_state['projects'] = load_projects()
    
    if 'current_project' not in st.session_state:
        st.session_state['current_project'] = None
    
    st.markdown("---")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📋 Meine Projekte", "➕ Neues Projekt", "📦 Aktives Projekt"])
    
    with tab1:
        display_project_list()
    
    with tab2:
        create_new_project(product_loader)
    
    with tab3:
        if st.session_state['current_project']:
            display_active_project(product_loader)
        else:
            st.info("ℹ️ Kein aktives Projekt. Erstelle ein neues Projekt oder wähle ein bestehendes aus.")


def display_project_list():
    """Display list of all projects"""
    
    st.subheader("📋 Alle Projekte")
    
    projects = st.session_state.get('projects', [])
    
    if not projects:
        st.info("ℹ️ Noch keine Projekte erstellt. Erstelle dein erstes Projekt im Tab 'Neues Projekt'.")
        return
    
    # Sort options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("🔍 Projekt suchen", placeholder="Projektname, Kunde...")
    
    with col2:
        sort_by = st.selectbox("Sortieren", ["Neueste", "Name", "Kunde"])
    
    # Filter projects
    filtered_projects = projects
    if search_query:
        filtered_projects = [p for p in projects if 
                            search_query.lower() in p.get('name', '').lower() or
                            search_query.lower() in p.get('customer', '').lower()]
    
    # Sort projects
    if sort_by == "Neueste":
        filtered_projects.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    elif sort_by == "Name":
        filtered_projects.sort(key=lambda x: x.get('name', ''))
    elif sort_by == "Kunde":
        filtered_projects.sort(key=lambda x: x.get('customer', ''))
    
    st.markdown("---")
    
    # Display projects
    for project in filtered_projects:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"### {project.get('name', 'Unbenannt')}")
                st.caption(f"👤 {project.get('customer', 'N/A')} | 📅 {format_date(project.get('created_at', ''))}")
            
            with col2:
                st.metric("Positionen", len(project.get('items', [])))
            
            with col3:
                if st.button("📂 Öffnen", key=f"open_{project.get('id')}", use_container_width=True):
                    st.session_state['current_project'] = project
                    st.rerun()
            
            with col4:
                if st.button("🗑️ Löschen", key=f"delete_{project.get('id')}", use_container_width=True):
                    delete_project(project.get('id'))
                    st.rerun()
            
            # Quick preview
            if project.get('items'):
                item_summary = {}
                for item in project['items']:
                    cat = item.get('category', 'Sonstiges')
                    item_summary[cat] = item_summary.get(cat, 0) + item.get('quantity', 1)
                
                summary_text = " | ".join([f"{cat}: {count}" for cat, count in item_summary.items()])
                st.caption(f"📦 {summary_text}")
            
            st.markdown("---")


def create_new_project(product_loader):
    """Create new project form"""
    
    st.subheader("➕ Neues Projekt erstellen")
    
    with st.form("new_project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 Projekt-Informationen")
            
            project_name = st.text_input(
                "Projektname *",
                placeholder="z.B. Campus Network Expansion Q1/2026"
            )
            
            customer = st.text_input(
                "Kunde/Standort *",
                placeholder="z.B. Acme Corp München"
            )
            
            contact_person = st.text_input(
                "Ansprechpartner",
                placeholder="Max Mustermann"
            )
        
        with col2:
            st.markdown("### 🏢 Details")
            
            project_type = st.selectbox(
                "Projekt-Typ",
                ["Campus Network", "Branch Office", "Data Center", "Wireless Only", "Security Upgrade", "NAC Deployment", "Custom"]
            )
            
            deployment_date = st.date_input(
                "Geplantes Deployment",
                value=None
            )
            
            budget = st.number_input(
                "Budget (optional, EUR)",
                min_value=0,
                value=0,
                step=1000
            )
        
        st.markdown("---")
        
        # Description
        description = st.text_area(
            "Beschreibung / Notizen",
            placeholder="Projektdetails, Anforderungen, Besonderheiten...",
            height=100
        )
        
        # Template selection
        st.markdown("### 📋 Template (optional)")
        st.markdown("Starte mit einer Vorlage und passe sie an deine Bedürfnisse an")
        
        template = st.selectbox(
            "Template auswählen",
            ["Kein Template", "Small Office (10-50 Users)", "Medium Branch (50-250 Users)", 
             "Large Campus (500+ Users)", "Warehouse/Manufacturing", "ISE Deployment"]
        )
        
        if template != "Kein Template":
            st.info(f"ℹ️ Template '{template}' wird vorausgefüllt mit typischen Produkten für diesen Use Case")
        
        submitted = st.form_submit_button("✅ Projekt erstellen", use_container_width=True)
        
        if submitted:
            if not project_name or not customer:
                st.error("❌ Projektname und Kunde sind Pflichtfelder!")
            else:
                # Create new project
                new_project = {
                    'id': generate_project_id(),
                    'name': project_name,
                    'customer': customer,
                    'contact_person': contact_person,
                    'project_type': project_type,
                    'deployment_date': deployment_date.isoformat() if deployment_date else None,
                    'budget': budget if budget > 0 else None,
                    'description': description,
                    'created_at': datetime.now().isoformat(),
                    'created_by': get_current_user().get('username'),
                    'items': [],
                    'status': 'In Planung'
                }
                
                # Apply template if selected
                if template != "Kein Template":
                    new_project['items'] = get_template_items(template)
                
                # Add to projects
                st.session_state['projects'].append(new_project)
                save_projects(st.session_state['projects'])
                
                # Set as current project
                st.session_state['current_project'] = new_project
                
                st.success(f"✅ Projekt '{project_name}' erfolgreich erstellt!")
                st.rerun()


def display_active_project(product_loader):
    """Display and edit active project"""
    
    project = st.session_state['current_project']
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"📂 {project.get('name', 'Unbenannt')}")
        st.caption(f"👤 {project.get('customer', 'N/A')} | 🏷️ {project.get('project_type', 'N/A')}")
    
    with col2:
        if st.button("❌ Projekt schließen", use_container_width=True):
            st.session_state['current_project'] = None
            st.rerun()
    
    st.markdown("---")
    
    # Project tabs
    proj_tab1, proj_tab2, proj_tab3, proj_tab4 = st.tabs(["📦 Stückliste (BOM)", "➕ Produkte hinzufügen", "📊 Übersicht", "⚙️ Einstellungen"])
    
    with proj_tab1:
        display_bom(project, product_loader)
    
    with proj_tab2:
        add_products_to_project(project, product_loader)
    
    with proj_tab3:
        display_project_overview(project, product_loader)
    
    with proj_tab4:
        edit_project_settings(project)


def display_bom(project, product_loader):
    """Display Bill of Materials"""
    
    st.subheader("📦 Stückliste (Bill of Materials)")
    
    items = project.get('items', [])
    
    if not items:
        st.info("ℹ️ Noch keine Produkte in diesem Projekt. Füge Produkte im Tab 'Produkte hinzufügen' hinzu.")
        return
    
    # BOM actions
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.metric("📦 Positionen", len(items))
        total_qty = sum(item.get('quantity', 1) for item in items)
        st.caption(f"Gesamtmenge: {total_qty} Stück")
    
    with col2:
        if st.button("📥 Export Excel", use_container_width=True):
            export_bom_excel(project)
    
    with col3:
        if st.button("📄 Export PDF", use_container_width=True):
            export_bom_pdf(project)
    
    st.markdown("---")
    
    # Group by category
    grouped_items = {}
    for item in items:
        cat = item.get('category', 'Sonstiges')
        if cat not in grouped_items:
            grouped_items[cat] = []
        grouped_items[cat].append(item)
    
    # Display by category
    for category, cat_items in grouped_items.items():
        st.markdown(f"### {category}")
        
        for idx, item in enumerate(cat_items):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 2, 1])
                
                with col1:
                    st.markdown(f"**{item.get('product_name', 'N/A')}**")
                    st.caption(f"SKU: `{item.get('sku', 'N/A')}`")
                
                with col2:
                    # Editable quantity
                    new_qty = st.number_input(
                        "Menge",
                        min_value=1,
                        value=item.get('quantity', 1),
                        key=f"qty_{item.get('product_id')}_{idx}",
                        label_visibility="collapsed"
                    )
                    if new_qty != item.get('quantity', 1):
                        item['quantity'] = new_qty
                        save_current_project()
                
                with col3:
                    st.markdown("Stück")
                
                with col4:
                    # Comment
                    comment = st.text_input(
                        "Kommentar",
                        value=item.get('comment', ''),
                        key=f"comment_{item.get('product_id')}_{idx}",
                        placeholder="Optional...",
                        label_visibility="collapsed"
                    )
                    if comment != item.get('comment', ''):
                        item['comment'] = comment
                        save_current_project()
                
                with col5:
                    if st.button("🗑️", key=f"remove_{item.get('product_id')}_{idx}"):
                        project['items'].remove(item)
                        save_current_project()
                        st.rerun()
                
                st.markdown("---")
        
        st.markdown("")  # Spacing between categories


def add_products_to_project(project, product_loader):
    """Add products to project"""
    
    st.subheader("➕ Produkte hinzufügen")
    
    # Quick add from calculator results
    if 'project_items' in st.session_state and st.session_state['project_items']:
        st.markdown("### 🧮 Aus Sizing Calculator")
        
        with st.expander(f"📦 {len(st.session_state['project_items'])} Produkte aus Calculator"):
            for calc_item in st.session_state['project_items']:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{calc_item.get('product_name')}**")
                    st.caption(f"{calc_item.get('quantity')}x | {calc_item.get('category')}")
                
                with col2:
                    if st.button("➕ Hinzufügen", key=f"add_calc_{calc_item.get('product_id')}"):
                        add_item_to_project(project, calc_item)
                        st.success("✅ Hinzugefügt!")
                
                with col3:
                    if st.button("❌", key=f"remove_calc_{calc_item.get('product_id')}"):
                        st.session_state['project_items'].remove(calc_item)
                        st.rerun()
            
            if st.button("✅ Alle hinzufügen", use_container_width=True):
                for calc_item in st.session_state['project_items']:
                    add_item_to_project(project, calc_item)
                st.session_state['project_items'] = []
                st.success(f"✅ Alle Produkte hinzugefügt!")
                st.rerun()
        
        st.markdown("---")
    
    # Manual product selection
    st.markdown("### 🔍 Manuell hinzufügen")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Category filter
        categories = ["Alle", "MR", "MX", "MS", "Catalyst AP", "Catalyst Switch", "ISE", "Zubehör"]
        selected_category = st.selectbox("Kategorie", categories)
    
    with col2:
        # Search
        search = st.text_input("Suche", placeholder="Produktname, SKU...")
    
    # Get products
    if selected_category == "Alle":
        products = product_loader.get_all_products()
    elif selected_category == "Zubehör":
        products = []  # Show accessories
        st.info("ℹ️ Zubehör-Suche in Entwicklung")
    else:
        cat_key = selected_category.lower().replace(" ", "_")
        products = product_loader.get_products_by_category(cat_key)
    
    # Filter by search
    if search:
        products = [p for p in products if 
                   search.lower() in p.get('name', '').lower() or
                   search.lower() in p.get('sku_base', '').lower()]
    
    # Display products
    st.markdown("---")
    
    if products:
        for product in products[:10]:  # Show top 10
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{product.get('name', 'N/A')}**")
                    st.caption(f"{product.get('category')} | `{product.get('sku_base', 'N/A')}`")
                
                with col2:
                    qty = st.number_input(
                        "Menge",
                        min_value=1,
                        value=1,
                        key=f"add_qty_{product.get('id')}",
                        label_visibility="collapsed"
                    )
                
                with col3:
                    if st.button("➕ Hinzufügen", key=f"add_manual_{product.get('id')}"):
                        item = {
                            'product_id': product.get('id'),
                            'product_name': product.get('name'),
                            'sku': product.get('sku_base'),
                            'quantity': qty,
                            'category': product.get('category'),
                            'comment': ''
                        }
                        add_item_to_project(project, item)
                        st.success("✅ Hinzugefügt!")
                
                with col4:
                    if st.button("ℹ️", key=f"info_{product.get('id')}"):
                        st.info(f"Status: {product.get('status', 'N/A')}")
                
                st.markdown("---")
    else:
        st.info("🔍 Keine Produkte gefunden")


def display_project_overview(project, product_loader):
    """Display project overview and statistics"""
    
    st.subheader("📊 Projekt-Übersicht")
    
    items = project.get('items', [])
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Positionen", len(items))
    
    with col2:
        total_qty = sum(item.get('quantity', 1) for item in items)
        st.metric("🔢 Gesamtmenge", total_qty)
    
    with col3:
        unique_categories = len(set(item.get('category', 'N/A') for item in items))
        st.metric("🏷️ Kategorien", unique_categories)
    
    with col4:
        status = project.get('status', 'In Planung')
        st.metric("📋 Status", status)
    
    st.markdown("---")
    
    # Category breakdown
    st.markdown("### 📊 Kategorie-Übersicht")
    
    category_stats = {}
    for item in items:
        cat = item.get('category', 'Sonstiges')
        category_stats[cat] = category_stats.get(cat, 0) + item.get('quantity', 1)
    
    if category_stats:
        import pandas as pd
        
        df_cat = pd.DataFrame([
            {'Kategorie': cat, 'Anzahl': count}
            for cat, count in category_stats.items()
        ])
        
        st.bar_chart(df_cat.set_index('Kategorie'))
        
        # Table
        st.dataframe(df_cat, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Project details
    st.markdown("### 📝 Projekt-Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Kunde:** {project.get('customer', 'N/A')}")
        st.markdown(f"**Ansprechpartner:** {project.get('contact_person', 'N/A')}")
        st.markdown(f"**Projekt-Typ:** {project.get('project_type', 'N/A')}")
    
    with col2:
        st.markdown(f"**Erstellt am:** {format_date(project.get('created_at'))}")
        st.markdown(f"**Erstellt von:** {project.get('created_by', 'N/A')}")
        if project.get('deployment_date'):
            st.markdown(f"**Deployment:** {format_date(project.get('deployment_date'))}")
    
    if project.get('description'):
        st.markdown("---")
        st.markdown("**Beschreibung:**")
        st.markdown(project.get('description'))
    
    st.markdown("---")
    
    # Product details
    st.markdown("### 🔍 Produkt-Details")
    
    if items:
        for item in items:
            product = product_loader.get_product_by_id(item.get('product_id'))
            
            if product:
                with st.expander(f"{item.get('quantity')}x {item.get('product_name')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**SKU:** `{item.get('sku')}`")
                        st.markdown(f"**Kategorie:** {item.get('category')}")
                        st.markdown(f"**Status:** {product.get('status', 'N/A')}")
                    
                    with col2:
                        if item.get('comment'):
                            st.markdown(f"**Kommentar:** {item.get('comment')}")
                        
                        if product.get('datasheet_url'):
                            st.markdown(f"[📄 Datasheet]({product.get('datasheet_url')})")


def edit_project_settings(project):
    """Edit project settings"""
    
    st.subheader("⚙️ Projekt-Einstellungen")
    
    with st.form("edit_project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Projektname", value=project.get('name', ''))
            customer = st.text_input("Kunde", value=project.get('customer', ''))
            contact = st.text_input("Ansprechpartner", value=project.get('contact_person', ''))
        
        with col2:
            project_type = st.selectbox(
                "Projekt-Typ",
                ["Campus Network", "Branch Office", "Data Center", "Wireless Only", "Security Upgrade", "NAC Deployment", "Custom"],
                index=["Campus Network", "Branch Office", "Data Center", "Wireless Only", "Security Upgrade", "NAC Deployment", "Custom"].index(project.get('project_type', 'Custom'))
            )
            
            status = st.selectbox(
                "Status",
                ["In Planung", "In Bearbeitung", "Genehmigt", "Bestellt", "Deployed", "Abgeschlossen"],
                index=["In Planung", "In Bearbeitung", "Genehmigt", "Bestellt", "Deployed", "Abgeschlossen"].index(project.get('status', 'In Planung'))
            )
            
            deployment_date = st.date_input(
                "Geplantes Deployment",
                value=None
            )
        
        description = st.text_area(
            "Beschreibung",
            value=project.get('description', ''),
            height=100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 Speichern", use_container_width=True):
                project['name'] = name
                project['customer'] = customer
                project['contact_person'] = contact
                project['project_type'] = project_type
                project['status'] = status
                project['deployment_date'] = deployment_date.isoformat() if deployment_date else None
                project['description'] = description
                
                save_current_project()
                st.success("✅ Projekt aktualisiert!")
        
        with col2:
            if st.form_submit_button("❌ Abbrechen", use_container_width=True):
                st.rerun()


# Helper functions

def load_projects():
    """Load projects from file or session"""
    # In production: Load from database or file
    # For now: Use session state
    return []


def save_projects(projects):
    """Save projects to file or database"""
    # In production: Save to database or file
    st.session_state['projects'] = projects


def save_current_project():
    """Save current project"""
    if st.session_state.get('current_project'):
        project_id = st.session_state['current_project'].get('id')
        
        # Update in projects list
        for i, p in enumerate(st.session_state['projects']):
            if p.get('id') == project_id:
                st.session_state['projects'][i] = st.session_state['current_project']
                break
        
        save_projects(st.session_state['projects'])


def delete_project(project_id):
    """Delete project"""
    st.session_state['projects'] = [p for p in st.session_state['projects'] if p.get('id') != project_id]
    save_projects(st.session_state['projects'])


def generate_project_id():
    """Generate unique project ID"""
    import uuid
    return str(uuid.uuid4())[:8]


def format_date(date_str):
    """Format ISO date string to readable format"""
    if not date_str:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%d.%m.%Y")
    except:
        return date_str


def add_item_to_project(project, item):
    """Add item to project BOM"""
    # Check if item already exists
    existing = next((i for i in project['items'] if i.get('product_id') == item.get('product_id')), None)
    
    if existing:
        # Increase quantity
        existing['quantity'] = existing.get('quantity', 1) + item.get('quantity', 1)
    else:
        # Add new item
        project['items'].append(item)
    
    save_current_project()


def get_template_items(template_name):
    """Get pre-filled items for template"""
    
    templates = {
        "Small Office (10-50 Users)": [
            {'product_id': 'mr36', 'product_name': 'Meraki MR36', 'sku': 'MR36-HW', 'quantity': 3, 'category': 'MR', 'comment': 'Office WLAN'},
            {'product_id': 'mx75', 'product_name': 'Meraki MX75', 'sku': 'MX75-HW', 'quantity': 1, 'category': 'MX', 'comment': 'Firewall'},
            {'product_id': 'ms120-24p', 'product_name': 'Meraki MS120-24P', 'sku': 'MS120-24P-HW', 'quantity': 2, 'category': 'MS', 'comment': 'Access Switches'},
        ],
        
        "Medium Branch (50-250 Users)": [
            {'product_id': 'mr46', 'product_name': 'Meraki MR46', 'sku': 'MR46-HW', 'quantity': 8, 'category': 'MR', 'comment': ''},
            {'product_id': 'mx95', 'product_name': 'Meraki MX95', 'sku': 'MX95-HW', 'quantity': 2, 'category': 'MX', 'comment': 'HA Pair'},
            {'product_id': 'ms225-48fp', 'product_name': 'Meraki MS225-48FP', 'sku': 'MS225-48FP-HW', 'quantity': 4, 'category': 'MS', 'comment': ''},
            {'product_id': 'ms250-24', 'product_name': 'Meraki MS250-24', 'sku': 'MS250-24-HW', 'quantity': 1, 'category': 'MS', 'comment': 'Aggregation'},
        ],
        
        "Large Campus (500+ Users)": [
            {'product_id': 'mr56', 'product_name': 'Meraki MR56', 'sku': 'MR56-HW', 'quantity': 30, 'category': 'MR', 'comment': 'Indoor APs'},
            {'product_id': 'mr46e', 'product_name': 'Meraki MR46E', 'sku': 'MR46E-HW', 'quantity': 5, 'category': 'MR', 'comment': 'Outdoor APs'},
            {'product_id': 'mx250', 'product_name': 'Meraki MX250', 'sku': 'MX250-HW', 'quantity': 2, 'category': 'MX', 'comment': 'HA Pair'},
            {'product_id': 'ms350-24x', 'product_name': 'Meraki MS350-24X', 'sku': 'MS350-24X-HW', 'quantity': 2, 'category': 'MS', 'comment': 'Core'},
            {'product_id': 'ms390-48', 'product_name': 'Meraki MS390-48', 'sku': 'MS390-48-HW', 'quantity': 10, 'category': 'MS', 'comment': 'Distribution'},
        ],
        
        "ISE Deployment": [
            {'product_id': 'ise-3355', 'product_name': 'Cisco ISE-3355', 'sku': 'ISE-3355-K9', 'quantity': 2, 'category': 'ISE', 'comment': 'HA Pair'},
        ],
    }
    
    return templates.get(template_name, [])


def export_bom_excel(project):
    """Export BOM as Excel"""
    export_mgr = get_export_manager()
    
    with st.spinner("Export läuft..."):
        buffer = export_mgr.export_project_bom_to_excel(
            project_name=project.get('name'),
            project_items=project.get('items', []),
            include_summary=True
        )
        
        st.download_button(
            label="📥 Excel herunterladen",
            data=buffer,
            file_name=f"BOM_{project.get('name')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


def export_bom_pdf(project):
    """Export BOM as PDF"""
    export_mgr = get_export_manager()
    
    customer_info = {
        'name': project.get('customer', 'N/A'),
        'contact': project.get('contact_person', 'N/A'),
        'date': format_date(project.get('created_at'))
    }
    
    with st.spinner("Export läuft..."):
        buffer = export_mgr.export_project_bom_to_pdf(
            project_name=project.get('name'),
            project_items=project.get('items', []),
            customer_info=customer_info
        )
        
        st.download_button(
            label="📥 PDF herunterladen",
            data=buffer,
            file_name=f"BOM_{project.get('name')}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )


if __name__ == "__main__":
    main()
