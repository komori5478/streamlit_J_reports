import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ページ設定
st.set_page_config(page_title="Tactical Scout Pro", layout="wide")

# UIカスタムスタイル
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
    for i in range(-52, 53, 10):
        ax.axvspan(i, i+5, color='#224433', alpha=0.3, zorder=0)
    ax.plot([-x_max, x_max, x_max, -x_max, -x_max], [-y_max, -y_max, y_max, y_max, -y_max], color=line_color, lw=2, alpha=0.8, zorder=1)
    ax.axvline(0, color=line_color, lw=2, alpha=0.8, zorder=1)
    ax.add_patch(patches.Circle((0, 0), 9.15, color=line_color, fill=False, lw=2, alpha=0.8, zorder=1))
    for side in [-1, 1]:
        ax.plot([side*x_max, side*(x_max-16.5), side*(x_max-16.5), side*x_max], [-20.15, -20.15, 20.15, 20.15], color=line_color, lw=2, zorder=1)
        ax.plot([side*x_max, side*(x_max-5.5), side*(x_max-5.5), side*x_max], [-9.15, -9.15, 9.15, 9.15], color=line_color, lw=2, zorder=1)
    ax.set_xlim(-55, 55)
    ax.set_ylim(-36, 36)
    ax.axis('off')

# サイドバー
uploaded_file = st.sidebar.file_uploader("CSVをアップロード", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    teams = df['team_shortname'].unique()
    selected_team = st.sidebar.selectbox("分析チーム", teams)
    df_t = df[df['team_shortname'] == selected_team].copy()

    # 背番号の代用処理（player_idの下2桁などを表示。正式な背番号列があればそれに差し替え）
    if 'jersey_number' not in df_t.columns:
        # player_idを文字列にして末尾2桁を取得（背番号の代わりとしてよく使われる手法）
        df_t['display_num'] = df_t['player_id'].astype(str).str[-2:]
    else:
        df_t['display_num'] = df_t['jersey_number']

    st.title(f"🏃 {selected_team} Scout Report")

    vis_mode = st.radio("表示モード", ["High xT Actions (貢献度)", "Difficult Passes (高難易度パス)"], horizontal=True)
    
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='#0e1117')
    draw_pro_pitch(ax)

    if "xT" in vis_mode:
        data_to_plot = df_t.sort_values(by='xthreat', ascending=False).head(25)
        color_main = "#00ffcc"
    else:
        data_to_plot = df_t[(df_t['pass_outcome'] == 'successful') & (df_t['xpass_completion'] < 0.6)].sort_values(by='xthreat', ascending=False).head(20)
        color_main = "#ff007f"

    for _, row in data_to_plot.iterrows():
        # 1. 矢印のプロット
        lw = row['xthreat'] * 60 if "xT" in vis_mode else 2
        ax.annotate("", xy=(row['x_end'], row['y_end']), xytext=(row['x_start'], row['y_start']),
                    arrowprops=dict(arrowstyle="->", color=color_main, lw=lw, alpha=0.5, zorder=4))
        
        # 2. 起点に背番号（またはID）をプロット
        # 円形の背景（視認性向上）
        ax.scatter(row['x_start'], row['y_start'], color="#1a1c24", s=400, edgecolors=color_main, lw=1.5, zorder=5)
        # 番号テキスト
        ax.text(row['x_start'], row['y_start'], str(row['display_num']), 
                color="white", fontsize=9, fontweight='bold', ha='center', va='center', zorder=6)

    st.pyplot(fig)
    st.info("💡 プロット内の数字は選手識別番号（player_id末尾）です。右上に行くほどゴール期待値の高いプレーです。")

    # 選手リスト（照合用）
    with st.expander("選手名と番号の照合リスト"):
        player_list = df_t[['player_name', 'display_num']].drop_duplicates()
        st.table(player_list)

else:
    st.info("CSVファイルをアップロードしてください。")
