import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Z-score Fear & Greed", layout="centered")
st.title("📈 주식 시장 심리 분석기 (Z-score)")

# 데이터를 가져오는 가장 안정적인 함수
@st.cache_data(ttl=3600)
def get_cnn_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    url = "https://production.dataviz.cnn.io/index/feargreed/static/data"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
        
    data = response.json()
    
    # 지표별 데이터 추출
    strength_raw = data['indicators']['stock_price_strength']['data']
    breadth_raw = data['indicators']['stock_price_breadth']['data']
    
    df_s = pd.DataFrame(strength_raw).rename(columns={'x': 'date', 'y': 'strength'})
    df_b = pd.DataFrame(breadth_raw).rename(columns={'x': 'date', 'y': 'breadth'})
    
    # 날짜 기준으로 병합
    df = pd.merge(df_s, df_b, on='date')
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    return df.sort_values('date').tail(20)

df_recent = get_cnn_data()

if df_recent is not None:
    # Z-score 계산 (최근 20일 기준)
    df_recent['z_strength'] = (df_recent['strength'] - df_recent['strength'].mean()) / df_recent['strength'].std()
    df_recent['z_breadth'] = (df_recent['breadth'] - df_recent['breadth'].mean()) / df_recent['breadth'].std()

    # 그래프 생성
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # 사분면 배경 색상 및 라벨
    ax.axvspan(-3, 0, 0.5, 1, alpha=0.1, color='orange') # 2사분면: 혼조
    ax.axvspan(0, 3, 0.5, 1, alpha=0.1, color='green')  # 1사분면: 탐욕
    ax.axvspan(-3, 0, 0, 0.5, alpha=0.1, color='red')    # 3사분면: 공포
    ax.axvspan(0, 3, 0, 0.5, alpha=0.1, color='blue')   # 4사분면: 회복
    
    # 점 찍기
    ax.scatter(df_recent['z_breadth'][:-1], df_recent['z_strength'][:-1], c='gray', alpha=0.4, label='Last 19 Days')
    ax.scatter(df_recent['z_breadth'].iloc[-1], df_recent['z_strength'].iloc[-1], c='red', s=300, edgecolors='black', label='Today')
    
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)
    ax.set_xlabel('Stock Price Breadth (Z-score)')
    ax.set_ylabel('Stock Price Strength (Z-score)')
    ax.legend()
    
    st.pyplot(fig)
    st.success(f"최종 업데이트: {df_recent['date'].iloc[-1].strftime('%Y-%m-%d')}")
else:
    st.error("현재 CNN 서버에서 데이터를 가져올 수 없습니다. 잠시 후 다시 시도해 주세요.")
