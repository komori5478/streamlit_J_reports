import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap

# ページ設定
st.set_page_config(page_title="Tactical Scout Pro", layout="wide")

# --- UIカスタム（CSSでScoutLab風の重厚感を出す） ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1a1c24; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    div[data-testid="stExpander"] { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- プロ仕様のピッチ描画関数 ---
def draw_pro_pitch(ax):
    pitch_color = '#1b3d2f' # 深みのあるタクティカルグリーン
    line_color = "#f0f0f0"
    
    ax.set_facecolor(pitch_color)
    x_max, y_max = 52.5, 34

    # 芝のストライプ模様（視覚的なプロ感を演出）
    for i in range(-52, 53, 10):
        ax.axvspan(i, i+5, color='#224433', alpha=0.3, zorder=0)

    # 外枠・ライン
    ax.plot([-x_max, x_max, x_max, -x_max, -x_max], [-y_max, -y_max, y_max, y_max, -y_max], color=line_color, lw=2, alpha=0.8, zorder=1)
    ax.axvline(0, color=line_color, lw=2, alpha=0.8, zorder=1)
    
    # センターサークル
    ax.add_patch(patches.Circle((0, 0), 9.15, color=line_color, fill=False, lw=2, alpha=0.8, zorder=1))
    ax.scatter(0, 0, color=line_color, s=30, zorder=1)
    
    # ペナルティエリア（右・左）
    for side in [-1, 1]:
        ax.plot([side*x_max, side*(x_max-16.5), side*(x_max-16.5), side*x_max], [-20.15, -20.15, 20.15, 20.15], color=line_color, lw=2, zorder=1)
        ax.plot([side*x_max, side*(x_max-5.5), side*(x_max-5.5), side*x_max], [-9.15, -9.15, 9.15, 9.15], color=line_color, lw=2, zorder=1)
        # ペナルティアーク
        arc = patches.Arc((side*(x_max-11), 0), 18.3, 18.3, theta1=128 if side==1 else 308, theta2=232 if side==1 else 52, color=line_color, lw=2, alpha=0.8)
        ax.add_patch(arc)

    # ゴール（発光表現を模したライン）
    ax.plot([x_max, x_max], [-3.66, 3.66], color="#00ffcc", lw=4, zorder=3)
    ax.plot([-x_max, -x_max], [-3.66, 3.66], color="#00ffcc", lw=4, zorder=3)

    ax.set_xlim(-55, 55)
    ax.set_ylim(-36, 36)
    ax.axis('off')

# --- メインロジック ---
st.sidebar.title("📊 ScoutLab Advanced")
menu = st.sidebar.radio("Navigation", ["Match Analysis", "League Analysis (100year J2J3)"])

if menu == "Match Analysis":
    st.title("🏃 Match Performance Insights")
    
    # データ読み込み
    try:
        df = pd.read_csv('2026-02-14_-_FC_Machida_Zelvia_v_Mito_Hollyhock_dynamic_events.csv')
    except:
        uploaded = st.sidebar.file_uploader("Upload CSV", type="csv")
        if uploaded: df = pd.read_csv(uploaded)
        else: st.stop()

    team = st.sidebar.selectbox("Analyzing Team", df['team_shortname'].unique())
    df_t = df[df['team_shortname'] == team].copy()
    
    # 統計集計
    shots = df_t[df_t['lead_to_shot'] == True]
    goals = df_t['lead_to_goal'].sum()
    avg_xt = df_t['xthreat'].mean()

    # KPIデザイン
    cols = st.columns(3)
    cols[0].metric("TOTAL SHOTS", f"{len(shots)}", help="Total shooting attempts")
    cols[1].metric("GOALS", f"{int(goals)}", delta=f"{int(goals)} G")
    cols[2].metric("AVG xTHREAT", f"{avg_xt:.4f}", help="Average expected threat")

    # シュートマップ
    st.markdown("### 🎯 Shot Distribution & Quality")
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='#0e1117')
    draw_pro_pitch(ax)

    if not shots.empty:
        for _, s in shots.iterrows():
            is_goal = s.get('lead_to_goal', False)
            xt = s.get('xthreat', 0.05)
            # サイズと色の動的調整
            size = (xt * 4000) + 150
            color = "#ffdd00" if is_goal else "white"
            marker = "*" if is_goal else "o"
            glow = 0.6 if is_goal else 0.3
            
            # 発光効果（ダミー）
            ax.scatter(s['x_start'], s['y_start'], s=size*1.5, color=color, alpha=0.15, zorder=4)
            ax.scatter(s['x_start'], s['y_start'], s=size, color=color, edgecolors="#333333", marker=marker, alpha=0.9, zorder=5)

    st.pyplot(fig)

    # 選手データの詳細テーブル（ScoutLab風のリスト）
    with st.expander("🔍 Player Detailed Stats"):
        p_stats = df_t.groupby('player_name').agg({'xthreat':'sum', 'lead_to_shot':'sum', 'speed_avg':'max'}).sort_values('xthreat', ascending=False)
        st.table(p_stats.head(10).style.format("{:.3f}", subset=['xthreat']))

elif menu == "League Analysis (100year J2J3)":
    st.title("🏆 League Comparison: 100year J2J3")
    st.markdown("### 準備中: リーグ統計を待機...")
    st.info("ここに順位表、J2/J3比較スタッツ、昇格期待値を実装します。")
