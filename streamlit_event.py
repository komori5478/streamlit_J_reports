import streamlit as st
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns

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
    """サッカーコートを描画するヘルパー関数"""
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

    ax.set_xlim(-55, 55)
    ax.set_ylim(-36, 36)
    ax.axis('off')

# サイドバー設定
st.sidebar.title("📊 ScoutLab Advanced")
uploaded_file = st.sidebar.file_uploader("試合データ(CSV)をアップロードしてください", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # チーム選択
    teams = df['team_shortname'].unique()
    selected_team = st.sidebar.selectbox("分析対象チーム", teams)
    df_t = df[df['team_shortname'] == selected_team].copy()
    
    # 基本情報の表示
    st.title(f"🏃 {selected_team} Performance Insights")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("総イベント数", len(df_t))
    col2.metric("シュート起点数", len(df_t[df_t['lead_to_shot'] == True]))
    col3.metric("平均期待脅威(xT)", f"{df_t['xthreat'].mean():.4f}")
    col4.metric("パス成功率", f"{(len(df_t[df_t['pass_outcome']=='successful']) / len(df_t[df_t['pass_outcome'].notna()]) * 100):.1f}%")

    # メインビジュアライゼーション
    tab1, tab2 = st.tabs(["戦術マップ分析", "選手パフォーマンス"])

    with tab1:
        st.subheader("📍 プレーの価値とチャンス構築の可視化")
        vis_mode = st.radio("表示するデータを選択", ["High xThreat Actions (決定機への貢献)", "Difficult Successful Passes (高難易度パス)"], horizontal=True)
        
        fig, ax = plt.subplots(figsize=(10, 7), facecolor='#0e1117')
        draw_pro_pitch(ax)

        if "xThreat" in vis_mode:
            # xTが高い上位アクションをプロット
            top_xt = df_t.sort_values(by='xthreat', ascending=False).head(30)
            for _, row in top_xt.iterrows():
                lw = row['xthreat'] * 50 # 数値に応じて線を太く
                ax.annotate("", xy=(row['x_end'], row['y_end']), xytext=(row['x_start'], row['y_start']),
                            arrowprops=dict(arrowstyle="->", color="#00ffcc", lw=lw, alpha=0.6))
            st.info("💡 矢印が太いほど、そのプレーで得点の可能性が大きく高まったことを示します。")
        else:
            # 難易度が高いが成功したパス
            hard_passes = df_t[(df_t['pass_outcome'] == 'successful') & (df_t['xpass_completion'] < 0.6)].sort_values(by='xthreat', ascending=False).head(20)
            for _, row in hard_passes.iterrows():
                ax.annotate("", xy=(row['x_end'], row['y_end']), xytext=(row['x_start'], row['y_start']),
                            arrowprops=dict(arrowstyle="->", color="#ff007f", lw=2, alpha=0.8))
            st.info("💡 ピンクの矢印は、成功率期待値が低い「通すのが難しいパス」を成功させたシーンです。")
        
        st.pyplot(fig)

    with tab2:
        st.subheader("👤 選手別スタッツ・プロット")
        
        # 選手ごとの集計
        player_stats = df_t.groupby('player_name').agg({
            'xthreat': 'sum',
            'speed_avg': 'max',
            'event_id': 'count'
        }).reset_index()
        player_stats.columns = ['選手名', '累計xThreat', '最高速度(km/h)', 'アクション数']

        col_left, col_right = st.columns(2)
        
        with col_left:
            st.write("### 期待脅威 (xT) ランキング")
            st.dataframe(player_stats.sort_values('累計xThreat', ascending=False).style.background_gradient(subset=['累計xThreat'], cmap='Greens'))

        with col_right:
            st.write("### アクション数 vs 貢献度(xT)")
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            sns.scatterplot(data=player_stats, x='アクション数', y='累計xThreat', size='最高速度(km/h)', hue='最高速度(km/h)', sizes=(100, 500), ax=ax2, palette='viridis')
            
            # 選手名のラベル付け
            for i in range(len(player_stats)):
                ax2.text(player_stats['アクション数'][i]+0.5, player_stats['累計xThreat'][i], player_stats['選手名'][i], fontsize=9)
            
            st.pyplot(fig2)
            st.caption("円が大きいほど最高速度が速い選手です。右上に行くほど『多くのプレーに関与し、かつ決定的なチャンスを作っている』選手になります。")

else:
    st.title("⚽ Tactical Scout Pro")
    st.info("左のサイドバーから、解析対象のCSVファイルをアップロードしてください。")
