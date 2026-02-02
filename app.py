"""
Meraki & Cisco Sizing Tool
Main Application Entry Point
"""

import streamlit as st
from utils.firebase_config import initialize_firebase, create_initial_admin
from utils.auth import login, logout, is_authenticated, get_current_user
import json

# Page configuration
st.set_page_config(
    page_title="Meraki & Cisco Sizing Tool",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Firebase
try:
    db = initialize_firebase()
    # Create initial admin if not exists
    create_initial_admin()
except Exception as e:
    st.error(f"⚠️ Firebase Initialisierung fehlgeschlagen: {str(e)}")
    st.stop()

# Load translations
@st.cache_data
def load_translations():
    with open('data/translations.json', 'r', encoding='utf-8') as f:
        return json.load(f)

translations = load_translations()

# Initialize session state
if 'language' not in st.session_state:
    st.session_state['language'] = 'de'

if 'theme' not in st.session_state:
    st.session_state['theme'] = 'light'

def t(key):
    """Get translation for key"""
    return translations[st.session_state['language']].get(key, key)

# Custom CSS for Nordic Minimalist Design
def apply_custom_css():
    theme = st.session_state.get('theme', 'light')
    
    if theme == 'dark':
        bg_color = "#1a1a1a"
        text_color = "#e0e0e0"
        sidebar_bg = "#2d2d2d"
        card_bg = "#2d2d2d"
        border_color = "#404040"
        accent_color = "#4a9eff"
    else:
        bg_color = "#ffffff"
        text_color = "#2c2c2c"
        sidebar_bg = "#f5f5f5"
        card_bg = "#fafafa"
        border_color = "#e0e0e0"
        accent_color = "#0066cc"
    
    st.markdown(f"""
        <style>
        /* Main Background */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg};
        }}
        
        /* Cards and Containers */
        .stCard {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: {accent_color};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 24px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            opacity: 0.85;
            transform: translateY(-2px);
        }}
        
        /* Input Fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {{
            border-radius: 6px;
            border: 1px solid {border_color};
            background-color: {card_bg};
            color: {text_color};
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: {text_color};
            font-weight: 300;
            letter-spacing: -0.5px;
        }}
        
        /* Links */
        a {{
            color: {accent_color};
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        /* Tables */
        .dataframe {{
            border: 1px solid {border_color} !important;
            border-radius: 8px;
        }}
        
        .dataframe th {{
            background-color: {sidebar_bg} !important;
            color: {text_color} !important;
            font-weight: 500;
        }}
        
        .dataframe td {{
            background-color: {card_bg} !important;
            color: {text_color} !important;
        }}
        
        /* Remove extra padding */
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
        }}
        
        /* Metrics */
        [data-testid="stMetricValue"] {{
            color: {text_color};
        }}
        </style>
    """, unsafe_allow_html=True)

apply_custom_css()

# Login Page
def show_login_page():
    st.markdown(f"<h1 style='text-align: center;'>{t('app_title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: gray;'>{t('app_subtitle')}</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='stCard'>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input(t('username'), placeholder="admin")
            password = st.text_input(t('password'), type="password", placeholder="••••••••")
            
            submit = st.form_submit_button(t('login'), use_container_width=True)
            
            if submit:
                if username and password:
                    success, user_data, message = login(username, password)
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Bitte Benutzername und Passwort eingeben")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Dashboard Page
def show_dashboard():
    user = get_current_user()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {user['username']}")
        st.caption(f"Rolle: {user['role'].upper()}")
        
        st.markdown("---")
        
        # Language Toggle
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🇩🇪 DE", use_container_width=True, 
                        disabled=st.session_state['language']=='de'):
                st.session_state['language'] = 'de'
                st.rerun()
        with col2:
            if st.button("🇬🇧 EN", use_container_width=True,
                        disabled=st.session_state['language']=='en'):
                st.session_state['language'] = 'en'
                st.rerun()
        
        # Theme Toggle
        st.markdown("---")
        theme_label = "🌙 Dark Mode" if st.session_state['theme'] == 'light' else "☀️ Light Mode"
        if st.button(theme_label, use_container_width=True):
            st.session_state['theme'] = 'dark' if st.session_state['theme'] == 'light' else 'light'
            st.rerun()
        
        st.markdown("---")
        
        if st.button(f"🚪 {t('logout')}", use_container_width=True):
            logout()
            st.rerun()
    
    # Main Content
    st.title(f"👋 {t('welcome')}, {user['username']}!")
    
    st.markdown("---")
    
    # Stats Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Produkte", "350+")
    
    with col2:
        st.metric("📊 Projekte", "12")
    
    with col3:
        st.metric("⚖️ Vergleiche", "8")
    
    with col4:
        st.metric("👥 Benutzer", "5")
    
    st.markdown("---")
    
    # Quick Access
    st.subheader("⚡ Schnellzugriff")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("""
                <div class='stCard'>
                    <h3>📦 Produktkatalog</h3>
                    <p>Durchsuche alle Meraki & Cisco Produkte</p>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown("""
                <div class='stCard'>
                    <h3>🧮 Sizing Calculator</h3>
                    <p>Berechne die optimale Lösung für dein Projekt</p>
                </div>
            """, unsafe_allow_html=True)
    
    with col3:
        with st.container():
            st.markdown("""
                <div class='stCard'>
                    <h3>📊 Neues Projekt</h3>
                    <p>Starte ein neues Sizing-Projekt</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent Activity
    st.subheader("📰 Letzte Aktivitäten")
    st.info("ℹ️ Noch keine Aktivitäten vorhanden")

# Main App Logic
if not is_authenticated():
    show_login_page()
else:
    show_dashboard()

