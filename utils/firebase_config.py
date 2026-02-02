"""
Firebase Configuration and Initialization
"""

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import json

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Initialize with Streamlit secrets
        firebase_creds = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

def get_db():
    """Get Firestore database instance"""
    return firestore.client()

def create_initial_admin():
    """
    Create initial admin user in Firestore if not exists
    Called once during setup
    """
    db = get_db()
    users_ref = db.collection('users')
    
    # Check if admin exists
    admin_query = users_ref.where('username', '==', st.secrets["admin"]["username"]).limit(1).get()
    
    if not admin_query:
        import bcrypt
        
        # Hash password
        hashed_pw = bcrypt.hashpw(
            st.secrets["admin"]["password"].encode('utf-8'),
            bcrypt.gensalt()
        )
        
        # Create admin user
        admin_data = {
            'username': st.secrets["admin"]["username"],
            'password': hashed_pw.decode('utf-8'),
            'role': 'admin',
            'email': 'admin@example.com',
            'created_at': firestore.SERVER_TIMESTAMP,
            'login_attempts': 0,
            'locked_until': None,
            'language': 'de'
        }
        
        users_ref.add(admin_data)
        return True
    return False

