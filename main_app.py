# main_app.py
import streamlit as st

st.title("✅ Kiểm tra Import từ 'modules/'")

# Kiểm tra import thử một hàm từ mỗi file
try:
    from modules.content_parser import clean_text
    st.success("✅ Đã import 'clean_text' từ 'modules.content_parser'")
except Exception as e:
    st.error(f"❌ Lỗi import 'clean_text': {e}")

try:
    from modules.firebase_config import init_firestore
    st.success("✅ Đã import 'init_firestore' từ 'modules.firebase_config'")
except Exception as e:
    st.error(f"❌ Lỗi import 'init_firestore': {e}")

try:
    from modules.session_manager import generate_session_id
    st.success("✅ Đã import 'generate_session_id' từ 'modules.session_manager'")
except Exception as e:
    st.error(f"❌ Lỗi import 'generate_session_id': {e}")
