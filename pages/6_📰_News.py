"""
News & Announcements Page
Display product updates, EOL announcements, and admin news management
"""

import streamlit as st
from utils.auth import require_auth, get_current_user, is_admin
from datetime import datetime, timedelta
import json

# Require authentication
require_auth(lambda: main())

def main():
    st.title("📰 News & Ankündigungen")
    st.markdown("Aktuelle Updates zu Cisco Produkten, EOL-Announcements und Feature-Releases")
    
    user = get_current_user()
    
    st.markdown("---")
    
    # Initialize news in session state
    if 'news_items' not in st.session_state:
        st.session_state['news_items'] = load_news_items()
    
    # Tabs
    if is_admin():
        tab1, tab2, tab3 = st.tabs(["📰 Alle News", "➕ News erstellen", "⚙️ Verwaltung"])
    else:
        tab1, tab2 = st.tabs(["📰 Alle News", "🔔 Meine Benachrichtigungen"])
    
    with tab1:
        display_news_feed()
    
    if is_admin():
        with tab2:
            create_news_item()
        
        with tab3:
            manage_news_items()
    else:
        with tab2:
            display_user_notifications()


def display_news_feed():
    """Display news feed with filtering"""
    
    st.subheader("📰 News Feed")
    
    news_items = st.session_state.get('news_items', [])
    
    # Filter options
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        category_filter = st.selectbox(
            "Kategorie",
            ["Alle", "Produkt-Update", "EOL-Ankündigung", "Neue Features", "Security Advisory", "Allgemein"]
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Priorität",
            ["Alle", "🔴 Kritisch", "🟡 Wichtig", "🟢 Info"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sortierung",
            ["Neueste", "Älteste"]
        )
    
    # Search
    search_query = st.text_input("🔍 Suche", placeholder="Stichwort, Produkt...")
    
    st.markdown("---")
    
    # Filter news
    filtered_news = news_items
    
    if category_filter != "Alle":
        filtered_news = [n for n in filtered_news if n.get('category') == category_filter]
    
    if priority_filter != "Alle":
        priority_map = {"🔴 Kritisch": "critical", "🟡 Wichtig": "important", "🟢 Info": "info"}
        filtered_news = [n for n in filtered_news if n.get('priority') == priority_map[priority_filter]]
    
    if search_query:
        filtered_news = [n for n in filtered_news 
                        if search_query.lower() in n.get('title', '').lower() or
                        search_query.lower() in n.get('content', '').lower()]
    
    # Sort
    if sort_by == "Neueste":
        filtered_news.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    else:
        filtered_news.sort(key=lambda x: x.get('published_at', ''))
    
    # Display news items
    if not filtered_news:
        st.info("🔍 Keine News gefunden.")
        return
    
    st.caption(f"Zeige {len(filtered_news)} News-Einträge")
    
    for news in filtered_news:
        display_news_card(news)


def display_news_card(news):
    """Display single news card"""
    
    # Priority badge
    priority = news.get('priority', 'info')
    if priority == 'critical':
        priority_badge = "🔴 **KRITISCH**"
        border_color = "#d32f2f"
    elif priority == 'important':
        priority_badge = "🟡 **WICHTIG**"
        border_color = "#ffa000"
    else:
        priority_badge = "🟢 Info"
        border_color = "#0066cc"
    
    # Category icon
    category_icons = {
        "Produkt-Update": "🔄",
        "EOL-Ankündigung": "⚠️",
        "Neue Features": "✨",
        "Security Advisory": "🔒",
        "Allgemein": "📢"
    }
    category_icon = category_icons.get(news.get('category', 'Allgemein'), "📰")
    
    with st.container():
        st.markdown(f"""
        <div style='
            border-left: 4px solid {border_color};
            padding: 16px;
            margin-bottom: 16px;
            background-color: {"#fafafa" if st.session_state.get("theme") == "light" else "#1e1e1e"};
            border-radius: 4px;
        '>
        """, unsafe_allow_html=True)
        
        # Header
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"### {category_icon} {news.get('title', 'Unbenannt')}")
            st.caption(f"{priority_badge} | {news.get('category', 'Allgemein')} | {format_date(news.get('published_at', ''))}")
        
        with col2:
            if is_admin():
                if st.button("✏️", key=f"edit_{news.get('id')}"):
                    st.session_state['editing_news'] = news.get('id')
                    st.rerun()
        
        # Content
        st.markdown(news.get('content', ''))
        
        # Affected products
        if news.get('affected_products'):
            st.markdown("**🔗 Betroffene Produkte:**")
            products_str = ", ".join(news.get('affected_products', []))
            st.markdown(f"`{products_str}`")
        
        # Links
        if news.get('links'):
            st.markdown("**📎 Weiterführende Links:**")
            for link in news.get('links', []):
                st.markdown(f"- [{link.get('title', 'Link')}]({link.get('url', '#')})")
        
        # Author
        st.caption(f"Erstellt von: {news.get('author', 'N/A')}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")


def create_news_item():
    """Create new news item (admin only)"""
    
    st.subheader("➕ Neue News erstellen")
    
    with st.form("create_news_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "Titel *",
                placeholder="z.B. MR36 End-of-Life angekündigt"
            )
            
            category = st.selectbox(
                "Kategorie *",
                ["Produkt-Update", "EOL-Ankündigung", "Neue Features", "Security Advisory", "Allgemein"]
            )
            
            priority = st.selectbox(
                "Priorität *",
                ["🟢 Info", "🟡 Wichtig", "🔴 Kritisch"]
            )
        
        with col2:
            publish_now = st.checkbox("Sofort veröffentlichen", value=True)
            
            if not publish_now:
                publish_date = st.date_input("Veröffentlichungsdatum")
                publish_time = st.time_input("Veröffentlichungszeit")
            
            display_duration = st.number_input(
                "Anzeige-Dauer (Tage)",
                min_value=1,
                max_value=365,
                value=30,
                help="Wie lange soll die News angezeigt werden?"
            )
        
        # Content
        st.markdown("### 📝 Inhalt")
        
        content = st.text_area(
            "News-Text *",
            height=200,
            placeholder="Beschreibe die Neuigkeit im Detail...",
            help="Markdown-Formatierung unterstützt"
        )
        
        # Affected products
        st.markdown("### 🔗 Betroffene Produkte (optional)")
        
        affected_products = st.text_input(
            "Produkt-IDs (kommagetrennt)",
            placeholder="mr36, mx75, ms225-48fp",
            help="Relevante Produkt-IDs aus dem Katalog"
        )
        
        # Links
        st.markdown("### 📎 Links (optional)")
        
        num_links = st.number_input("Anzahl Links", min_value=0, max_value=5, value=0)
        
        links = []
        for i in range(num_links):
            col1, col2 = st.columns(2)
            with col1:
                link_title = st.text_input(f"Link {i+1} Titel", key=f"link_title_{i}")
            with col2:
                link_url = st.text_input(f"Link {i+1} URL", key=f"link_url_{i}")
            
            if link_title and link_url:
                links.append({'title': link_title, 'url': link_url})
        
        # Banner option
        st.markdown("---")
        
        show_as_banner = st.checkbox(
            "Als Banner auf Startseite anzeigen",
            help="Wichtige News werden prominent auf der Startseite angezeigt"
        )
        
        submitted = st.form_submit_button("✅ News erstellen", use_container_width=True)
        
        if submitted:
            if not title or not content:
                st.error("❌ Titel und Inhalt sind Pflichtfelder!")
            else:
                # Create news item
                priority_map = {"🟢 Info": "info", "🟡 Wichtig": "important", "🔴 Kritisch": "critical"}
                
                new_news = {
                    'id': generate_news_id(),
                    'title': title,
                    'category': category,
                    'priority': priority_map[priority],
                    'content': content,
                    'affected_products': [p.strip() for p in affected_products.split(',')] if affected_products else [],
                    'links': links,
                    'author': get_current_user().get('username'),
                    'published_at': datetime.now().isoformat() if publish_now else f"{publish_date}T{publish_time}",
                    'expires_at': (datetime.now() + timedelta(days=display_duration)).isoformat(),
                    'show_as_banner': show_as_banner,
                    'status': 'published' if publish_now else 'scheduled'
                }
                
                # Add to news
                st.session_state['news_items'].insert(0, new_news)
                save_news_items(st.session_state['news_items'])
                
                st.success(f"✅ News '{title}' erfolgreich erstellt!")
                
                # Show banner preview
                if show_as_banner:
                    st.info("💡 Diese News wird als Banner auf der Startseite angezeigt:")
                    display_news_banner(new_news)
                
                st.rerun()


def manage_news_items():
    """Manage existing news items (admin only)"""
    
    st.subheader("⚙️ News-Verwaltung")
    
    news_items = st.session_state.get('news_items', [])
    
    if not news_items:
        st.info("📭 Noch keine News erstellt.")
        return
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📰 Gesamt", len(news_items))
    
    with col2:
        published = len([n for n in news_items if n.get('status') == 'published'])
        st.metric("✅ Veröffentlicht", published)
    
    with col3:
        scheduled = len([n for n in news_items if n.get('status') == 'scheduled'])
        st.metric("⏰ Geplant", scheduled)
    
    with col4:
        banners = len([n for n in news_items if n.get('show_as_banner')])
        st.metric("📌 Banner", banners)
    
    st.markdown("---")
    
    # News management table
    st.markdown("### 📋 Alle News")
    
    for news in news_items:
        with st.expander(f"{news.get('title', 'Unbenannt')} - {news.get('category', 'N/A')}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Titel:** {news.get('title')}")
                st.markdown(f"**Kategorie:** {news.get('category')}")
                st.markdown(f"**Priorität:** {news.get('priority')}")
                st.markdown(f"**Status:** {news.get('status')}")
            
            with col2:
                st.markdown(f"**Erstellt:** {format_date(news.get('published_at'))}")
                st.markdown(f"**Läuft ab:** {format_date(news.get('expires_at'))}")
                st.markdown(f"**Autor:** {news.get('author')}")
            
            with col3:
                if news.get('show_as_banner'):
                    st.success("📌 Banner: Ja")
                else:
                    st.info("📌 Banner: Nein")
                
                if st.button("✏️ Bearbeiten", key=f"edit_mgmt_{news.get('id')}"):
                    st.info("ℹ️ Bearbeiten-Funktion in Entwicklung")
                
                if st.button("🗑️ Löschen", key=f"delete_{news.get('id')}"):
                    delete_news_item(news.get('id'))
                    st.success("✅ News gelöscht!")
                    st.rerun()


def display_user_notifications():
    """Display user-specific notifications"""
    
    st.subheader("🔔 Meine Benachrichtigungen")
    
    # User notification settings
    st.markdown("### ⚙️ Benachrichtigungs-Einstellungen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("EOL-Ankündigungen", value=True, key="notif_eol")
        st.checkbox("Produkt-Updates", value=True, key="notif_updates")
        st.checkbox("Neue Features", value=False, key="notif_features")
    
    with col2:
        st.checkbox("Security Advisories", value=True, key="notif_security")
        st.checkbox("Allgemeine News", value=False, key="notif_general")
    
    if st.button("💾 Einstellungen speichern"):
        st.success("✅ Einstellungen gespeichert!")
    
    st.markdown("---")
    
    # Display relevant news
    st.markdown("### 📬 Deine News")
    
    news_items = st.session_state.get('news_items', [])
    
    # Filter based on user preferences (simplified)
    user_news = [n for n in news_items if n.get('status') == 'published']
    
    if user_news:
        for news in user_news[:5]:  # Show top 5
            display_news_card(news)
    else:
        st.info("📭 Keine neuen Benachrichtigungen")


def display_news_banner(news):
    """Display news as banner (for homepage)"""
    
    priority = news.get('priority', 'info')
    
    if priority == 'critical':
        banner_type = "error"
        icon = "🔴"
    elif priority == 'important':
        banner_type = "warning"
        icon = "🟡"
    else:
        banner_type = "info"
        icon = "🟢"
    
    # Get Streamlit's built-in banner function
    if banner_type == "error":
        st.error(f"{icon} **{news.get('title')}** - {news.get('content')[:100]}...")
    elif banner_type == "warning":
        st.warning(f"{icon} **{news.get('title')}** - {news.get('content')[:100]}...")
    else:
        st.info(f"{icon} **{news.get('title')}** - {news.get('content')[:100]}...")


# Helper functions

def load_news_items():
    """Load news items from storage"""
    # In production: Load from database or file
    # For now: Return default news items
    
    return [
        {
            'id': 'news-001',
            'title': 'MR36 End-of-Life angekündigt',
            'category': 'EOL-Ankündigung',
            'priority': 'important',
            'content': 'Cisco hat das End-of-Life für das Meraki MR36 Access Point angekündigt. End-of-Sale: 31.12.2026, End-of-Support: 31.12.2031.\n\nWir empfehlen ein Upgrade auf MR46 oder MR56 für bessere Wi-Fi 6 Performance.',
            'affected_products': ['mr36'],
            'links': [
                {'title': 'Offizielle EOL-Ankündigung', 'url': 'https://documentation.meraki.com'},
                {'title': 'Migration Guide zu MR46', 'url': 'https://documentation.meraki.com'}
            ],
            'author': 'admin',
            'published_at': (datetime.now() - timedelta(days=2)).isoformat(),
            'expires_at': (datetime.now() + timedelta(days=90)).isoformat(),
            'show_as_banner': True,
            'status': 'published'
        },
        {
            'id': 'news-002',
            'title': 'Neue Wi-Fi 7 Access Points verfügbar',
            'category': 'Neue Features',
            'priority': 'info',
            'content': 'Cisco Meraki hat die neue MR57 Serie mit Wi-Fi 7 Support vorgestellt. Verfügbar ab Q2/2026.\n\nKey Features:\n- Wi-Fi 7 (802.11be)\n- Bis zu 9.6 Gbps\n- Multi-Link Operation (MLO)\n- 6 GHz Support',
            'affected_products': ['mr57'],
            'links': [
                {'title': 'MR57 Datasheet', 'url': 'https://documentation.meraki.com/MR/MR57_Datasheet'}
            ],
            'author': 'admin',
            'published_at': (datetime.now() - timedelta(days=7)).isoformat(),
            'expires_at': (datetime.now() + timedelta(days=60)).isoformat(),
            'show_as_banner': False,
            'status': 'published'
        },
        {
            'id': 'news-003',
            'title': 'Security Advisory: ISE Patch verfügbar',
            'category': 'Security Advisory',
            'priority': 'critical',
            'content': '🔒 KRITISCHES SECURITY UPDATE\n\nCisco hat ein Security-Update für ISE veröffentlicht (CVE-2026-XXXX). Betroffen: ISE 3.1, 3.2.\n\n**Empfohlene Aktion:** Sofortiges Update auf neueste Patch-Version.\n\n**Severity:** High (CVSS 8.1)',
            'affected_products': ['ise-3315', 'ise-3355', 'ise-3395'],
            'links': [
                {'title': 'Security Advisory', 'url': 'https://sec.cloudapps.cisco.com'},
                {'title': 'Patch Download', 'url': 'https://software.cisco.com'}
            ],
            'author': 'security-team',
            'published_at': (datetime.now() - timedelta(hours=6)).isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
            'show_as_banner': True,
            'status': 'published'
        },
        {
            'id': 'news-004',
            'title': 'Dashboard Firmware Update v1.34',
            'category': 'Produkt-Update',
            'priority': 'info',
            'content': 'Neues Meraki Dashboard Firmware Update verfügbar.\n\n**Neue Features:**\n- Verbessertes Reporting\n- API v1.41 Support\n- Bugfixes für MS Switches\n\nUpdate wird automatisch ausgerollt.',
            'affected_products': [],
            'links': [
                {'title': 'Release Notes', 'url': 'https://documentation.meraki.com'}
            ],
            'author': 'admin',
            'published_at': (datetime.now() - timedelta(days=14)).isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
            'show_as_banner': False,
            'status': 'published'
        },
    ]


def save_news_items(news_items):
    """Save news items to storage"""
    # In production: Save to database or file
    st.session_state['news_items'] = news_items


def delete_news_item(news_id):
    """Delete news item"""
    st.session_state['news_items'] = [n for n in st.session_state['news_items'] if n.get('id') != news_id]
    save_news_items(st.session_state['news_items'])


def generate_news_id():
    """Generate unique news ID"""
    import uuid
    return f"news-{str(uuid.uuid4())[:8]}"


def format_date(date_str):
    """Format ISO date string to readable format"""
    if not date_str:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(date_str)
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            if diff.seconds < 3600:
                return f"vor {diff.seconds // 60} Minuten"
            else:
                return f"vor {diff.seconds // 3600} Stunden"
        elif diff.days == 1:
            return "Gestern"
        elif diff.days < 7:
            return f"vor {diff.days} Tagen"
        else:
            return dt.strftime("%d.%m.%Y")
    except:
        return date_str


if __name__ == "__main__":
    main()
