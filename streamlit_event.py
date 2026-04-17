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
    
    ax.plot([-52.5, 52.5, 52.5, -52.5, -52.5], [-34, -34, 34, 34, -34], color=line_color, lw=2)
    ax.axvline(0, color=line_color, lw=2)
    center_circle = patches.Circle((0, 0), 9.15, color=line_color, fill=False, lw=2)
    ax.add_patch(center_circle)
    
    ax.plot([36, 52.5, 52.5, 36, 36], [-20.15, -20.15, 20.15, 20.15, -20.15], color=line_color, lw=2)
    ax.plot([-36, -52.5, -52.5, -36, -36], [-20.15, -20.15, 20.15, 20.15, -20.15], color=line_color, lw=2)
    
    ax.plot([52.5, 53.5, 53.5, 52.5], [-3.66, -3.66, 3.66, 3.66], color="red", lw=3)
    ax.plot([-52.5, -53.5, -53.5, -52.5], [-3.66, -3.66, 3.66, 3.66], color="red", lw=3)

    ax.set_xlim(-58, 58)
    ax.set_ylim(-38, 38)
    ax.axis('off')

# --- サイドバーメニュー ---
st.sidebar.title("⚽ ScoutLab Pro")
menu = st.sidebar.radio("メニューを選択", ["試合分析", "リーグ分析 (100year J2J3)"])

if menu == "試合分析":
    st.header("🏃 試合分析ダッシュボード")
    
    uploaded_file = st.sidebar.file_uploader("試合CSVをアップロード", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    else:
        try:
            df = pd.read_csv('2026-02-14_-_FC_Machida_Zelvia_v_Mito_Hollyhock_dynamic_events.csv')
        except:
            st.warning("CSVファイルをアップロードしてください。")
            st.stop()

    if df is not None:
        team = st.sidebar.selectbox("チームを選択", df['team_shortname'].unique())
        df_t = df[df['team_shortname'] == team]
        
        # シュートデータの抽出
        df_shots = df_t[df_t['lead_to_shot'] == True].copy()
        
        # KPI
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("総シュート数", len(df_shots))
        with c2: st.metric("ゴール数", int(df_t['lead_to_goal'].sum()))
        with c3: st.metric("平均速度", f"{df_t['speed_avg'].mean():.2f} km/h")

        # シュートマップ
        st.subheader("🎯 シュートマップ")
        
        # ここでデータの有無をチェック
        if not df_shots.empty:
            fig, ax = plt.subplots(figsize=(10, 7))
            draw_pitch(ax)
            
            # データがある場合のみ scatter を実行
            for _, shot in df_shots.iterrows():
                is_goal = shot.get('lead_to_goal', False)
                size = (shot.get('xthreat', 0.1) * 2000) + 100 
                
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
            st.caption("🌟: ゴール / ●: シュート")
        else:
            # データがない場合はコートだけ表示するか、メッセージを出す
            st.info("選択された条件で表示できるシュートデータがありません。")
            fig, ax = plt.subplots(figsize=(10, 7))
            draw_pitch(ax)
            st.pyplot(fig)

elif menu == "リーグ分析 (100year J2J3)":
    st.header("🏆 リーグ分析: 100year J2J3")
    st.write("リーグデータの読み込みと可視化を準備します。")