"""
Home Dashboard
Main landing page with widgets, quick actions, and news banner
"""

import streamlit as st
from utils.auth import require_auth, get_current_user, is_admin
from utils.product_loader import get_product_loader
from datetime import datetime, timedelta
import json

# Page config (must be first Streamlit command)
st.set_page_config(
    page_title="Cisco Product Catalog",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Require authentication
require_auth(lambda: main())

def main():
    # Load user
    user = get_current_user()
    
    # Header with welcome message
    col1, col2 = st.columns([3, 1])
    
    with col1:
        current_hour = datetime.now().hour
        if current_hour < 12:
            greeting = "Guten Morgen"
        elif current_hour < 18:
            greeting = "Guten Tag"
        else:
            greeting = "Guten Abend"
        
        st.title(f"{greeting}, {user.get('full_name', user.get('username'))}! 👋")
        st.markdown("Willkommen im **Cisco Meraki & Catalyst Produktkatalog**")
    
    with col2:
        st.markdown("")
        st.markdown("")
        current_date = datetime.now().strftime("%d.%m.%Y")
        current_time = datetime.now().strftime("%H:%M")
        st.markdown(f"📅 {current_date}")
        st.caption(f"🕐 {current_time} Uhr")
    
    st.markdown("---")
    
    # News Banner (Critical/Important news only)
    display_news_banner()
    
    # Quick Actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📦 Produktkatalog durchsuchen", use_container_width=True, type="primary"):
            st.switch_page("pages/1_📦_Product_Catalog.py")
    
    with col2:
        if st.button("🧮 Sizing berechnen", use_container_width=True):
            st.switch_page("pages/3_🧮_Sizing_Calculator.py")
    
    with col3:
        if st.button("📊 Projekt erstellen", use_container_width=True):
            st.switch_page("pages/4_📊_Projects.py")
    
    with col4:
        if st.button("🔐 NAC vergleichen", use_container_width=True):
            st.switch_page("pages/5_🔐_NAC_Solutions.py")
    
    st.markdown("---")
    
    # Main dashboard widgets
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_statistics_widget()
        st.markdown("")
        display_recent_activity_widget()
    
    with col2:
        display_eol_widget()
        st.markdown("")
        display_quick_links_widget()
    
    st.markdown("---")
    
    # Additional widgets
    col1, col2 = st.columns(2)
    
    with col1:
        display_product_categories_widget()
    
    with col2:
        display_popular_products_widget()
    
    # Admin section
    if is_admin():
        st.markdown("---")
        display_admin_section()
    
    # Footer
    display_footer()


def display_news_banner():
    """Display important news as banner"""
    
    # Load news
    if 'news_items' not in st.session_state:
        # Load default news
        from pages.page_news import load_news_items
        st.session_state['news_items'] = load_news_items()
    
    news_items = st.session_state.get('news_items', [])
    
    # Filter for banner-worthy news
    banner_news = [n for n in news_items 
                   if n.get('show_as_banner') and 
                   n.get('status') == 'published' and
                   datetime.fromisoformat(n.get('expires_at', datetime.now().isoformat())) > datetime.now()]
    
    if banner_news:
        # Show first critical/important news
        news = banner_news[0]
        priority = news.get('priority', 'info')
        
        if priority == 'critical':
            st.error(f"""
            🔴 **{news.get('title')}**
            
            {news.get('content')[:200]}...
            
            [📰 Mehr erfahren](#) | Kategorie: {news.get('category')}
            """)
        elif priority == 'important':
            st.warning(f"""
            🟡 **{news.get('title')}**
            
            {news.get('content')[:200]}...
            
            [📰 Mehr erfahren](#) | Kategorie: {news.get('category')}
            """)
        
        # Link to news page
        if st.button("📰 Alle News anzeigen", key="news_link"):
            st.switch_page("pages/6_📰_News.py")


def display_statistics_widget():
    """Display product statistics"""
    
    st.markdown("### 📊 Katalog-Statistiken")
    
    product_loader = get_product_loader()
    all_products = product_loader.get_all_products()
    
    # Calculate stats
    total_products = len(all_products)
    active_products = len([p for p in all_products if p.get('status') == 'Active'])
    eol_announced = len([p for p in all_products if p.get('status') == 'EOL Announced'])
    total_accessories = len(product_loader.accessories)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Gesamt Produkte",
            value=total_products,
            delta=None
        )
    
    with col2:
        st.metric(
            label="Aktive Produkte",
            value=active_products,
            delta=f"{(active_products/total_products*100):.0f}%"
        )
    
    with col3:
        st.metric(
            label="EOL Announced",
            value=eol_announced,
            delta=f"-{eol_announced}" if eol_announced > 0 else "0",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="Zubehör",
            value=total_accessories
        )
    
    # Category breakdown
    st.markdown("#### Produkte nach Kategorie")
    
    category_stats = {}
    for product in all_products:
        cat = product.get('category', 'Unknown')
        category_stats[cat] = category_stats.get(cat, 0) + 1
    
    # Display as columns
    categories = ['MR', 'MX', 'MS', 'Catalyst AP', 'Catalyst Switch', 'ISE']
    cols = st.columns(len(categories))
    
    for i, cat in enumerate(categories):
        with cols[i]:
            count = category_stats.get(cat, 0)
            st.metric(cat, count)


def display_recent_activity_widget():
    """Display recent user activity"""
    
    st.markdown("### 🕐 Letzte Aktivitäten")
    
    # Mock recent activities (in production: track from user sessions)
    activities = [
        {
            'icon': '📦',
            'action': 'Produktkatalog durchsucht',
            'details': 'Filter: Wi-Fi 6, Indoor APs',
            'time': datetime.now() - timedelta(minutes=15)
        },
        {
            'icon': '🧮',
            'action': 'Sizing Calculator verwendet',
            'details': 'Access Points für 500m² Office',
            'time': datetime.now() - timedelta(hours=2)
        },
        {
            'icon': '📊',
            'action': 'Projekt erstellt',
            'details': '"Campus Network Expansion"',
            'time': datetime.now() - timedelta(days=1)
        },
        {
            'icon': '⚖️',
            'action': 'Produkte verglichen',
            'details': 'MR46 vs MR56',
            'time': datetime.now() - timedelta(days=2)
        },
    ]
    
    for activity in activities[:5]:
        time_ago = format_time_ago(activity['time'])
        
        st.markdown(f"""
        <div style='padding: 8px; margin-bottom: 8px; border-left: 3px solid #0066cc; background-color: #f5f5f5;'>
            {activity['icon']} <strong>{activity['action']}</strong><br>
            <small>{activity['details']}</small><br>
            <small style='color: #666;'>{time_ago}</small>
        </div>
        """, unsafe_allow_html=True)


def display_eol_widget():
    """Display EOL announcements widget"""
    
    st.markdown("### ⚠️ EOL-Ankündigungen")
    
    product_loader = get_product_loader()
    all_products = product_loader.get_all_products()
    
    # Get EOL products
    eol_products = [p for p in all_products if p.get('eol_announced') is not None]
    eol_products.sort(key=lambda x: x.get('eol_announced', ''), reverse=True)
    
    if eol_products:
        for product in eol_products[:5]:
            eol_date = product.get('eol_announced', 'N/A')
            eos_date = product.get('eos_date', 'N/A')
            
            st.warning(f"""
            **{product.get('name')}**
            
            EOL: {eol_date}  
            EOS: {eos_date}
            """)
        
        if st.button("📋 Alle EOL Produkte", use_container_width=True):
            st.switch_page("pages/1_📦_Product_Catalog.py")
    else:
        st.success("✅ Keine aktuellen EOL-Ankündigungen")


def display_quick_links_widget():
    """Display quick links"""
    
    st.markdown("### 🔗 Schnellzugriff")
    
    links = [
        ("📦 Produktkatalog", "pages/1_📦_Product_Catalog.py"),
        ("⚖️ Vergleich", "pages/2_⚖️_Compare.py"),
        ("🧮 Sizing Calculator", "pages/3_🧮_Sizing_Calculator.py"),
        ("📊 Projekte", "pages/4_📊_Projects.py"),
        ("🔐 NAC Lösungen", "pages/5_🔐_NAC_Solutions.py"),
        ("📰 News", "pages/6_📰_News.py"),
    ]
    
    for name, page in links:
        if st.button(name, use_container_width=True, key=f"link_{page}"):
            st.switch_page(page)


def display_product_categories_widget():
    """Display product categories overview"""
    
    st.markdown("### 🏷️ Produkt-Kategorien")
    
    categories = [
        {
            'icon': '📡',
            'name': 'Meraki Access Points',
            'category': 'MR',
            'description': 'Cloud-Managed Wi-Fi 5/6/6E/7',
            'count': None
        },
        {
            'icon': '🔥',
            'name': 'Meraki Security Appliances',
            'category': 'MX',
            'description': 'SD-WAN & Security',
            'count': None
        },
        {
            'icon': '🔌',
            'name': 'Meraki Switches',
            'category': 'MS',
            'description': 'Cloud-Managed Switching',
            'count': None
        },
        {
            'icon': '📶',
            'name': 'Catalyst Access Points',
            'category': 'Catalyst AP',
            'description': 'Enterprise Wi-Fi',
            'count': None
        },
        {
            'icon': '🔀',
            'name': 'Catalyst Switches',
            'category': 'Catalyst Switch',
            'description': 'Enterprise Switching',
            'count': None
        },
        {
            'icon': '🔐',
            'name': 'Identity Services Engine',
            'category': 'ISE',
            'description': 'Network Access Control',
            'count': None
        },
    ]
    
    # Get product counts
    product_loader = get_product_loader()
    
    for cat in categories:
        cat_key = cat['category'].lower().replace(" ", "_")
        products = product_loader.get_products_by_category(cat_key)
        cat['count'] = len(products)
    
    # Display as grid
    for i in range(0, len(categories), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            cat = categories[i]
            display_category_card(cat)
        
        if i + 1 < len(categories):
            with col2:
                cat = categories[i + 1]
                display_category_card(cat)


def display_category_card(category):
    """Display single category card"""
    
    with st.container():
        st.markdown(f"""
        <div style='
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 16px;
            background-color: #fafafa;
            height: 120px;
        '>
            <div style='font-size: 32px;'>{category['icon']}</div>
            <div style='font-weight: bold; margin-top: 8px;'>{category['name']}</div>
            <div style='color: #666; font-size: 12px;'>{category['description']}</div>
            <div style='margin-top: 8px; color: #0066cc; font-weight: bold;'>{category['count']} Produkte</div>
        </div>
        """, unsafe_allow_html=True)


def display_popular_products_widget():
    """Display popular/recommended products"""
    
    st.markdown("### ⭐ Empfohlene Produkte")
    
    # Popular products (hardcoded - in production: track views/usage)
    popular = [
        {
            'id': 'mr46',
            'name': 'Meraki MR46',
            'category': 'MR',
            'reason': '🔥 Wi-Fi 6, Indoor, High-Density',
            'badge': 'Bestseller'
        },
        {
            'id': 'mx95',
            'name': 'Meraki MX95',
            'category': 'MX',
            'reason': '⚡ Mid-Size Branches, 2.5 Gbps FW',
            'badge': 'Beliebt'
        },
        {
            'id': 'ms225-48fp',
            'name': 'Meraki MS225-48FP',
            'category': 'MS',
            'reason': '🔌 48 Ports, Full PoE+, 740W Budget',
            'badge': 'Top-Seller'
        },
        {
            'id': 'ise-3355',
            'name': 'Cisco ISE-3355',
            'category': 'ISE',
            'reason': '🔐 NAC für bis zu 50k Endpoints',
            'badge': 'Enterprise'
        },
    ]
    
    for product in popular:
        with st.expander(f"{product['name']} - {product['badge']}"):
            st.markdown(f"**Kategorie:** {product['category']}")
            st.markdown(f"**Warum beliebt:** {product['reason']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Details", key=f"pop_details_{product['id']}"):
                    st.info(f"Details für {product['name']}")
            
            with col2:
                if st.button("⚖️ Vergleichen", key=f"pop_compare_{product['id']}"):
                    if 'comparison_list' not in st.session_state:
                        st.session_state['comparison_list'] = []
                    st.session_state['comparison_list'].append(product['id'])
                    st.success("✅ Zum Vergleich hinzugefügt!")


def display_admin_section():
    """Display admin quick actions"""
    
    st.markdown("### 🔧 Admin-Bereich")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 Web Scraper", use_container_width=True):
            st.switch_page("pages/8_🔧_Admin_Tools.py")
    
    with col2:
        if st.button("📰 News verwalten", use_container_width=True):
            st.switch_page("pages/6_📰_News.py")
    
    with col3:
        if st.button("👥 Benutzer verwalten", use_container_width=True):
            st.info("ℹ️ User Management in Entwicklung")
    
    with col4:
        if st.button("📊 Analytics", use_container_width=True):
            st.info("ℹ️ Analytics Dashboard in Entwicklung")
    
    # Admin stats
    st.markdown("#### 📈 System-Statistiken")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Aktive User", "8")
    
    with col2:
        st.metric("Gesamt Projekte", "23")
    
    with col3:
        st.metric("News-Einträge", "4")


def display_footer():
    """Display footer"""
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.caption("🔵 **Cisco Meraki & Catalyst Produktkatalog**")
        st.caption("Alle Produktdaten, SKUs und Specs für Cisco Meraki und Catalyst Produkte")
    
    with col2:
        st.caption("**Schnellzugriff**")
        st.caption("[Produktkatalog](#) | [Sizing](#) | [NAC](#)")
    
    with col3:
        st.caption("**Ressourcen**")
        st.caption("[Cisco.com](https://www.cisco.com) | [Meraki Docs](https://documentation.meraki.com)")
    
    st.caption("")
    st.caption(f"© 2026 | Version 1.0 | Letztes Update: {datetime.now().strftime('%d.%m.%Y')}")


# Helper functions

def format_time_ago(dt):
    """Format datetime to 'X ago' string"""
    
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        if diff.days == 1:
            return "vor 1 Tag"
        else:
            return f"vor {diff.days} Tagen"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"vor {hours} Stunde{'n' if hours > 1 else ''}"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"vor {minutes} Minute{'n' if minutes > 1 else ''}"
    else:
        return "gerade eben"


if __name__ == "__main__":
    main()
