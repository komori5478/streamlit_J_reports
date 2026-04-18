import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ページ設定
st.set_page_config(page_title="Tactical Scout Pro", layout="wide")

# UIカスタム
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1a1c24; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

def draw_pro_pitch(ax):
    pitch_color = '#1b3d2f'
    line_color = "#f0f0f0"
    ax.set_facecolor(pitch_color)
    x_max, y_max = 52.5, 34

    # 芝のストライプ
    for i in range(-52, 53, 10):
        ax.axvspan(i, i+5, color='#224433', alpha=0.3, zorder=0)

    # ライン描画
    ax.plot([-x_max, x_max, x_max, -x_max, -x_max], [-y_max, -y_max, y_max, y_max, -y_max], color=line_color, lw=2, alpha=0.8, zorder=1)
    ax.axvline(0, color=line_color, lw=2, alpha=0.8, zorder=1)
    ax.add_patch(patches.Circle((0, 0), 9.15, color=line_color, fill=False, lw=2, alpha=0.8, zorder=1))
    
    for side in [-1, 1]:
        ax.plot([side*x_max, side*(x_max-16.5), side*(x_max-16.5), side*x_max], [-20.15, -20.15, 20.15, 20.15], color=line_color, lw=2, zorder=1)
        ax.plot([side*x_max, side*(x_max-5.5), side*(x_max-5.5), side*x_max], [-9.15, -9.15, 9.15, 9.15], color=line_color, lw=2, zorder=1)
        arc = patches.Arc((side*(x_max-11), 0), 18.3, 18.3, theta1=128 if side==1 else 308, theta2=232 if side==1 else 52, color=line_color, lw=2, alpha=0.8)
        ax.add_patch(arc)

    # ゴール強調
    ax.plot([x_max, x_max], [-3.66, 3.66], color="#00ffcc", lw=4, zorder=3)
    ax.plot([-x_max, -x_max], [-3.66, 3.66], color="#00ffcc", lw=4, zorder=3)

    ax.set_xlim(-55, 55)
    ax.set_ylim(-36, 36)
    ax.axis('off')

# サイドバー
st.sidebar.title("📊 ScoutLab Advanced")
menu = st.sidebar.radio("Navigation", ["Match Analysis", "League Analysis (100year J2J3)"])

if menu == "Match Analysis":
    st.title("🏃 Match Performance Insights")
    
    try:
        df = pd.read_csv('2026-02-14_-_FC_Machida_Zelvia_v_Mito_Hollyhock_dynamic_events.csv')
    except:
        uploaded = st.sidebar.file_uploader("Upload CSV", type="csv")
        if uploaded: df = pd.read_csv(uploaded)
        else: st.stop()

    team = st.sidebar.selectbox("Analyzing Team", df['team_shortname'].unique())
    df_t = df[df['team_shortname'] == team].copy()
    
    # データクリーニング（x, y座標が空のデータを除外）
    df_t = df_t.dropna(subset=['x_start', 'y_start'])
    
    # シュートデータ抽出
    shots = df_t[df_t['lead_to_shot'] == True].copy()

    # KPI
    c1, c2, c3 = st.columns(3)
    c1.metric("TOTAL SHOTS", len(shots))
    c2.metric("GOALS", int(df_t['lead_to_goal'].sum()))
    c3.metric("AVG xT", f"{df_t['xthreat'].mean():.4f}")

    # シュートマップ
    st.markdown("### 🎯 Shot Distribution")
    
    # 描画の安全処理
    fig, ax = plt.subplots(figsize=(10, 7), facecolor='#0e1117')
    draw_pro_pitch(ax)

    # ここが修正ポイント：データがある場合のみ1つずつ描画（一括処理のエラーを防ぐ）
    if not shots.empty:
        for _, s in shots.iterrows():
            try:
                is_goal = s.get('lead_to_goal', False)
                xt = s.get('xthreat', 0.05)
                if pd.isna(xt): xt = 0.05
                
                size = (xt * 3000) + 150
                color = "#ffdd00" if is_goal else "white"
                
                ax.scatter(s['x_start'], s['y_start'], 
                           s=size, color=color, 
                           edgecolors="#333333", 
                           marker="*" if is_goal else "o", 
                           alpha=0.8, zorder=5)
            except:
                continue # 個別の描画エラーは無視して次へ
    
    # エラー回避のため最後に描画チェック
    if ax.collections or ax.patches:
        st.pyplot(fig)
    else:
        st.info("No data available for the plot.")
    plt.close(fig)

elif menu == "League Analysis (100year J2J3)":
    st.title("🏆 League Comparison")
    st.info("データの入力を待っています...")
