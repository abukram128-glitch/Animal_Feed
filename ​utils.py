# utils.py
from fpdf import FPDF
import streamlit as st

def generate_sack_tag(data):
    # دالة تصميم الديباجة التي صممناها سابقاً
    return f"""
    <div style="border: 4px solid #1b5e20; padding: 25px; border-radius: 20px; background: #ffffff; text-align: center;">
        <h1>مجموعة تاور للأعلاف</h1>
        <p><b>القسم:</b> {data['animal']} | <b>البروتين:</b> {data['cp']}%</p>
        <p><b>رقم التشغيلة:</b> {data['batch']}</p>
        <p><b>التاريخ:</b> {data['date']}</p>
    </div>
    """
