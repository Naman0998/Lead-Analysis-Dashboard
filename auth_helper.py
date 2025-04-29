import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

def get_connection():
    return st.connection("gsheets", type=GSheetsConnection, ttl = 0)

def load_allowed_users():
    conn = get_connection()
    df = conn.read(worksheet="userbase")
    df = df.dropna(how="all")  # Removing completely empty rows 
    df["Email"] = df["Email"].astype(str).str.strip().str.lower() # strip spaces
    allowed_users = df[df["Active"] == 0]["Email"].tolist()
    return allowed_users

def login_user(email):
    allowed_emails = load_allowed_users()
    return email in allowed_emails
