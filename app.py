import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Z-score Fear & Greed", layout="centered")
st.title("📈 주식 시장 심리 분석기 (Z-score)")

@st.cache_data(ttl=3600)
def get_cnn_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = "https://production.dataviz.cnn.io/index/feargreed/static/data"
    r = requests.get(url, headers=headers)
    data = r.json()
    strength = pd.DataFrame(data['indicators']['stock_price_strength']['data']).rename(columns={'x': 'date', 'y': 'strength'})
    breadth = pd.DataFrame(data['indicators']['stock_price_breadth']['data']).rename(columns={'x': 'date', 'y': 'breadth'})
    df = pd.merge(strength, breadth, on='date')
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    return df.tail(20)

try:
    df_recent = get_cnn_data().copy()
    df_recent['z_strength'] = (df_recent['strength'] - df_recent['strength'].mean()) / df_recent['strength'].std()
    df_recent['z_breadth'] = (df_recent['breadth'] - df_recent['breadth'].mean()) / df_recent['breadth'].std()

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.axvspan(-3, 0, 0.5, 1, alpha=0.1, color='orange')
    ax.axvspan(0, 3, 0.5, 1, alpha=0.1, color='green')
    ax.axvspan(-3, 0, 0, 0.5, alpha=0.1, color='red')
    ax.axvspan(0, 3, 0, 0.5, alpha=0.1, color='blue')
    
    ax.scatter(df_recent['z_breadth'][:-1], df_recent['z_strength'][:-1], c='gray', alpha=0.4)
    ax.scatter(df_recent['z_breadth'].iloc[-1], df_recent['z_strength'].iloc[-1], c='red', s=250, edgecolors='black')
    
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)
    ax.set_xlabel('Stock Price Breadth (Z-score)')
    ax.set_ylabel('Stock Price Strength (Z-score)')
    st.pyplot(fig)
    st.info(f"마지막 데이터 기준일: {df_recent['date'].iloc[-1].strftime('%Y-%m-%d')}")
except:
    st.error("데이터 로딩 실패")
