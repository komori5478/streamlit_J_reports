import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ページ設定
st.set_page_config(page_title="ScoutLab Pro", layout="wide")

# --- 共通関数：サッカーコートの描画 ---
def draw_pitch(ax):
    pitch_color = "#1a472a"
    line_color = "white"
    ax.set_facecolor(pitch_color)
    
    # ピッチの外枠
    ax.plot([-52.5, 52.5, 52.5, -52.5, -52.5], [-34, -34, 34, 34, -34], color=line_color, lw=2)
    # センターライン
    ax.axvline(0, color=line_color, lw=2)
    # センターサークル
    center_circle = patches.Circle((0, 0), 9.15, color=line_color, fill=False, lw=2)
    ax.add_patch(center_circle)
    
    # ペナルティエリア
    ax.plot([36, 52.5, 52.5, 36, 36], [-20.15, -20.15, 20.15, 20.15, -20.15], color=line_color, lw=2)
    ax.plot([-36, -52.5, -52.5, -36, -36], [-20.15, -20.15, 20.15, 20.15, -20.15], color=line_color, lw=2)
    
    # ゴールライン上の印（赤）
    ax.plot([52.5, 53.5, 53.5, 52.5], [-3.66, -3.66, 3.66, 3.66], color="red", lw=3)
    ax.plot([-52.5, -53.5, -53.5, -52.5], [-3.66, -3.66, 3.66, 3.66], color="red", lw=3)

    ax.set_xlim(-58, 58)
    ax.set_ylim(-38, 38)
    ax.axis('off')

# --- サイドバーメニュー ---
st.sidebar.title("⚽ ScoutLab Pro")
menu = st.sidebar.radio("メニューを選択", ["試合分析", "リーグ分析 (100year J2J3)"])

if menu == "試合分析":
    st.header("🏃 Match Analysis Dashboard")
    
    uploaded_file = st.sidebar.file_uploader("試合CSVをアップロード", type="csv")
    
    # データ読み込み処理
    df = None
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    else:
        try:
            # デフォルトファイル名。なければエラー回避。
            df = pd.read_csv('2026-02-14_-_FC_Machida_Zelvia_v_Mito_Hollyhock_dynamic_events.csv')
        except:
            st.warning("Please upload a CSV file to begin.")
            st.stop()

    if df is not None:
        # チーム選択
        teams = df['team_shortname'].unique()
        team = st.sidebar.selectbox("チームを選択", teams)
        df_t = df[df['team_shortname'] == team]
        
        # シュートデータの抽出 (リード・トゥ・ショットがTrueのもの)
        df_shots = df_t[df_t['lead_to_shot'] == True].copy()
        
        # KPI表示
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Shots", len(df_shots))
        with c2:
            goals = int(df_t['lead_to_goal'].sum()) if 'lead_to_goal' in df_t.columns else 0
            st.metric("Goals", goals)
        with c3:
            avg_speed = df_t['speed_avg'].mean() if 'speed_avg' in df_t.columns else 0
            st.metric("Avg Speed", f"{avg_speed:.2f} km/h")

        # シュートマップの描画
        st.subheader("🎯 Shoot Map")
        
        fig, ax = plt.subplots(figsize=(10, 7))
        draw_pitch(ax)
        
        if not df_shots.empty:
            for _, shot in df_shots.iterrows():
                is_goal = shot.get('lead_to_goal', False)
                # xthreatがあればサイズに反映、なければデフォルト
                xt = shot.get('xthreat', 0.1)
                size = (xt * 2000) + 100 
                
                ax.scatter(
                    shot['x_start'], shot['y_start'], 
                    s=size, 
                    c="yellow" if is_goal else "white", 
                    edgecolors="black", 
                    marker="*" if is_goal else "o",
                    alpha=0.8,
                    zorder=5
                )
            st.pyplot(fig)
            st.caption("🌟: Goal / ●: Shot")
        else:
            # データがない場合はコートだけ表示
            st.pyplot(fig)
            st.info("No shot data available for the selected team.")

elif menu == "リーグ分析 (100year J2J3)":
    st.header("🏆 League Analysis: 100year J2J3")
    st.write("League data visualization is coming soon.")
