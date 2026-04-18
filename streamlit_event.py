import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_pitch_from_csv_coords():
    """
    CSVデータの座標系 (-52.5 to 52.5, -34 to 34) に合わせたコートを作成
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 背景色（芝生）
    ax.set_facecolor('#2e7d32')
    
    # --- 基本設定 ---
    # フィールドサイズ (データ基準: 横105m / 縦68m)
    x_max, y_max = 52.5, 34
    line_color = "white"
    
    # 1. 外枠 (タッチライン・ゴールライン)
    ax.plot([-x_max, x_max, x_max, -x_max, -x_max], 
            [-y_max, -y_max, y_max, y_max, -y_max], color=line_color, lw=2, zorder=1)
    
    # 2. センターライン
    ax.axvline(0, color=line_color, lw=2, zorder=1)
    
    # 3. センターサークル (半径9.15m)
    center_circle = patches.Circle((0, 0), 9.15, color=line_color, fill=False, lw=2, zorder=1)
    ax.add_patch(center_circle)
    # センタースポット
    ax.scatter(0, 0, color=line_color, s=20, zorder=1)
    
    # 4. ペナルティエリア (16.5m × 40.3m)
    # 右側
    ax.plot([x_max - 16.5, x_max, x_max, x_max - 16.5, x_max - 16.5], 
            [-20.15, -20.15, 20.15, 20.15, -20.15], color=line_color, lw=2, zorder=1)
    # 左側
    ax.plot([-x_max + 16.5, -x_max, -x_max, -x_max + 16.5, -x_max + 16.5], 
            [-20.15, -20.15, 20.15, 20.15, -20.15], color=line_color, lw=2, zorder=1)
    
    # 5. ゴールエリア (5.5m × 18.3m)
    # 右側
    ax.plot([x_max - 5.5, x_max, x_max, x_max - 5.5, x_max - 5.5], 
            [-9.15, -9.15, 9.15, 9.15, -9.15], color=line_color, lw=2, zorder=1)
    # 左側
    ax.plot([-x_max + 5.5, -x_max, -x_max, -x_max + 5.5, -x_max + 5.5], 
            [-9.15, -9.15, 9.15, 9.15, -9.15], color=line_color, lw=2, zorder=1)
    
    # 6. ペナルティアーク (半径9.15m)
    # 右側 (中心点: ゴールから11m地点)
    arc_right = patches.Arc((x_max - 11, 0), 18.3, 18.3, theta1=128, theta2=232, color=line_color, lw=2, zorder=1)
    ax.add_patch(arc_right)
    # 左側
    arc_left = patches.Arc((-x_max + 11, 0), 18.3, 18.3, theta1=308, theta2=52, color=line_color, lw=2, zorder=1)
    ax.add_patch(arc_left)

    # 7. ゴールポスト（赤線で強調）
    ax.plot([x_max, x_max+1], [-3.66, -3.66], color="red", lw=2)
    ax.plot([x_max, x_max+1], [3.66, 3.66], color="red", lw=2)
    ax.plot([x_max+1, x_max+1], [-3.66, 3.66], color="red", lw=2)

    # 表示範囲の調整
    ax.set_xlim(-60, 60)
    ax.set_ylim(-40, 40)
    ax.axis('off') # 軸と枠線を隠す
    
    return fig, ax

# 実行例
fig, ax = create_pitch_from_csv_coords()
plt.show()

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
