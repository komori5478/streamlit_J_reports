import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- ページ設定 ---
st.set_page_config(page_title="ScoutLab Pro", layout="wide")

# --- 共通関数：サッカーコートの描画 ---
def draw_pitch(ax):
    # 背景色と線の色
    pitch_color = "#1a472a"
    line_color = "white"
    ax.set_facecolor(pitch_color)
    
    # ピッチ外枠 (横105m: -52.5 to 52.5, 縦68m: -34 to 34)
    ax.plot([-52.5, 52.5, 52.5, -52.5, -52.5], [-34, -34, 34, 34, -34], color=line_color, lw=2)
    # センターライン
    ax.axvline(0, color=line_color, lw=2)
    # センターサークル
    center_circle = patches.Circle((0, 0), 9.15, color=line_color, fill=False, lw=2)
    ax.add_patch(center_circle)
    
    # ペナルティエリア (右)
    ax.plot([36, 52.5, 52.5, 36, 36], [-20.15, -20.15, 20.15, 20.15, -20.15], color=line_color, lw=2)
    # ペナルティエリア (左)
    ax.plot([-36, -52.5, -52.5, -36, -36], [-20.15, -20.15, 20.15, 20.15, -20.15], color=line_color, lw=2)
    
    # ゴール位置の強調（赤線）
    ax.plot([52.5, 53.5, 53.5, 52.5], [-3.66, -3.66, 3.66, 3.66], color="red", lw=3)
    ax.plot([-52.5, -53.5, -53.5, -52.5], [-3.66, -3.66, 3.66, 3.66], color="red", lw=3)

    # 表示範囲の設定
    ax.set_xlim(-58, 58)
    ax.set_ylim(-38, 38)
    ax.set_aspect('equal') # アスペクト比を固定してコートを正しく表示
    ax.axis('off')

# --- サイドバーメニュー ---
st.sidebar.title("⚽ ScoutLab Pro")
menu = st.sidebar.radio("メニューを選択", ["試合分析", "リーグ分析 (100year J2J3)"])

if menu == "試合分析":
    st.header("🏃 Match Analysis Dashboard")
    
    uploaded_file = st.sidebar.file_uploader("試合CSVをアップロード", type="csv")
    
    df = None
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
        df_t = df[df['team_shortname'] == team].copy()
        
        # シュートデータの抽出（欠損値を除去）
        df_shots = df_t[
            (df_t['lead_to_shot'] == True) & 
            (df_t['x_start'].notna()) & 
            (df_t['y_start'].notna())
        ].copy()
        
        # KPI
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Shots", len(df_shots))
        with c2: st.metric("Goals", int(df_t['lead_to_goal'].sum()) if 'lead_to_goal' in df_t.columns else 0)
        with c3: st.metric("Avg Speed", f"{df_t['speed_avg'].mean() if 'speed_avg' in df_t.columns else 0:.2f} km/h")

        # --- シュートマップの描画セクション ---
        st.subheader("🎯 Shoot Map")
        
        # 1. まず Figure と Axes を作成
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # 2. コートを描画（常に実行）
        draw_pitch(ax)
        
        # 3. データがある場合のみ、コートの上に点をプロット
        if not df_shots.empty:
            for _, shot in df_shots.iterrows():
                is_goal = shot.get('lead_to_goal', False)
                xt = shot.get('xthreat', 0.1)
                if pd.isna(xt): xt = 0.1
                size = (xt * 2000) + 100 
                
                ax.scatter(
                    shot['x_start'], shot['y_start'], 
                    s=size, 
                    c="yellow" if is_goal else "white", 
                    edgecolors="black", 
                    marker="*" if is_goal else "o",
                    alpha=0.8,
                    zorder=5 # コートの線より上に表示
                )
            st.caption("🌟: Goal / ●: Shot")
        else:
            st.info("表示できるシュートデータがありません。")

        # 4. 最後に st.pyplot でまとめて表示（これが重要！）
        st.pyplot(fig)
        plt.close(fig)

elif menu == "リーグ分析 (100year J2J3)":
    st.header("🏆 League Analysis")
    st.write("準備中...")


pip install statsbombpy mplsoccer
from statsbombpy import sb
from mplsoccer import Pitch
import matplotlib.pyplot as plt

# 1. 無料公開されている試合一覧から「2022 W杯決勝」のIDを取得
# 43はW杯のcompetition_id、106は2022年のseason_idです
df_events = sb.events(match_id=3869685)

# 2. アルゼンチンのシュートデータだけを抽出
team_name = 'Argentina'
shots = df_events[(df_events.type == 'Shot') & (df_events.team == team_name)].copy()

# 3. 座標データ (location) を x と y に分ける
shots[['x', 'y']] = shots['location'].apply(pd.Series)

# 4. ピッチの描画
pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
fig, ax = pitch.draw(figsize=(13, 8))

# 5. シュートをプロット（ゴールは大きく、それ以外は小さく）
for i, row in shots.iterrows():
    if row.shot_outcome == 'Goal':
        pitch.scatter(row.x, row.y, s=300, edgecolors='black', c='#ad993c', marker='*', ax=ax, label='Goal')
    else:
        pitch.scatter(row.x, row.y, s=100, edgecolors='white', c='#ea6969', alpha=0.7, ax=ax)

plt.title(f'{team_name} Shot Map (WC 2022 Final)', fontsize=20, color='white')
plt.show()
