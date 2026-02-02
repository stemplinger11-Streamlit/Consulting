"""
Authentication and Authorization Functions
"""

import streamlit as st
import bcrypt
from datetime import datetime, timedelta
from utils.firebase_config import get_db

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def check_account_locked(user_doc):
    """Check if account is locked due to failed login attempts"""
    locked_until = user_doc.get('locked_until')
    
    if locked_until:
        if datetime.now() < locked_until:
            remaining = (locked_until - datetime.now()).seconds // 60
            return True, remaining
        else:
            # Unlock account
            db = get_db()
            user_ref = db.collection('users').document(user_doc.id)
            user_ref.update({
                'login_attempts': 0,
                'locked_until': None
            })
    
    return False, 0

def increment_login_attempts(user_id: str):
    """Increment failed login attempts and lock if threshold reached"""
    db = get_db()
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    
    if user_doc.exists:
        attempts = user_doc.to_dict().get('login_attempts', 0) + 1
        
        update_data = {'login_attempts': attempts}
        
        # Lock account after 5 failed attempts for 30 minutes
        if attempts >= 5:
            update_data['locked_until'] = datetime.now() + timedelta(minutes=30)
        
        user_ref.update(update_data)
        
        return attempts

def reset_login_attempts(user_id: str):
    """Reset login attempts after successful login"""
    db = get_db()
    user_ref = db.collection('users').document(user_id)
    user_ref.update({
        'login_attempts': 0,
        'locked_until': None
    })

def login(username: str, password: str) -> tuple:
    """
    Authenticate user
    Returns: (success: bool, user_data: dict, message: str)
    """
    db = get_db()
    users_ref = db.collection('users')
    
    # Find user by username
    user_query = users_ref.where('username', '==', username).limit(1).get()
    
    if not user_query:
        return False, None, "Benutzername oder Passwort falsch"
    
    user_doc = user_query[0]
    user_data = user_doc.to_dict()
    
    # Check if account is locked
    is_locked, remaining_minutes = check_account_locked(user_doc)
    if is_locked:
        return False, None, f"Account gesperrt. Versuche es in {remaining_minutes} Minuten erneut."
    
    # Verify password
    if verify_password(password, user_data['password']):
        # Reset login attempts
        reset_login_attempts(user_doc.id)
        
        # Set session with 10-hour expiration
        st.session_state['authenticated'] = True
        st.session_state['user'] = {
            'id': user_doc.id,
            'username': user_data['username'],
            'role': user_data['role'],
            'email': user_data.get('email', ''),
            'language': user_data.get('language', 'de')
        }
        st.session_state['login_time'] = datetime.now()
        
        return True, st.session_state['user'], "Login erfolgreich"
    else:
        # Increment failed attempts
        attempts = increment_login_attempts(user_doc.id)
        remaining_attempts = 5 - attempts
        
        if remaining_attempts > 0:
            return False, None, f"Benutzername oder Passwort falsch. Noch {remaining_attempts} Versuche übrig."
        else:
            return False, None, "Account wurde für 30 Minuten gesperrt (5 Fehlversuche)."

def logout():
    """Clear session state"""
    for key in ['authenticated', 'user', 'login_time']:
        if key in st.session_state:
            del st.session_state[key]

def check_session_timeout():
    """Check if session has expired (10 hours)"""
    if 'login_time' in st.session_state:
        elapsed = datetime.now() - st.session_state['login_time']
        if elapsed > timedelta(hours=10):
            logout()
            return True
    return False

def is_authenticated():
    """Check if user is authenticated and session is valid"""
    if check_session_timeout():
        return False
    return st.session_state.get('authenticated', False)

def is_admin():
    """Check if current user is admin"""
    if is_authenticated():
        return st.session_state.get('user', {}).get('role') == 'admin'
    return False

def get_current_user():
    """Get current logged-in user"""
    return st.session_state.get('user', None)

def require_auth(func):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            st.warning("⚠️ Bitte melde dich an, um fortzufahren.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorator to require admin role"""
    def wrapper(*args, **kwargs):
        if not is_admin():
            st.error("🚫 Diese Funktion erfordert Admin-Rechte.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def change_password(user_id: str, new_password: str):
    """Change user password"""
    db = get_db()
    user_ref = db.collection('users').document(user_id)
    
    hashed_pw = hash_password(new_password)
    user_ref.update({'password': hashed_pw})
    
    return True

