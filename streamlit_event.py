import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ページ設定
st.set_page_config(page_title="ScoutLab Pro Analyzer", layout="wide")

# --- 共通関数：データ座標系に合わせたサッカーコートの描画 ---
def draw_pitch(ax):
    """
    CSVデータの座標系 (-52.5 to 52.5, -34 to 34) に合わせたコートを作成
    """
    pitch_color = '#1a472a' # 濃い緑
    line_color = "white"
    ax.set_facecolor(pitch_color)
    
    # フィールドサイズ (データ基準: 横105m / 縦68m)
    x_max, y_max = 52.5, 34
    
    # 1. 外枠 (タッチライン・ゴールライン)
    ax.plot([-x_max, x_max, x_max, -x_max, -x_max], 
            [-y_max, -y_max, y_max, y_max, -y_max], color=line_color, lw=2, zorder=1)
    
    # 2. センターライン
    ax.axvline(0, color=line_color, lw=2, zorder=1)
    
    # 3. センターサークル (半径9.15m)
    center_circle = patches.Circle((0, 0), 9.15, color=line_color, fill=False, lw=2, zorder=1)
    ax.add_patch(center_circle)
    ax.scatter(0, 0, color=line_color, s=20, zorder=1)
    
    # 4. ペナルティエリア
    # 右側
    ax.plot([x_max - 16.5, x_max, x_max, x_max - 16.5, x_max - 16.5], 
            [-20.15, -20.15, 20.15, 20.15, -20.15], color=line_color, lw=2, zorder=1)
    # 左側
    ax.plot([-x_max + 16.5, -x_max, -x_max, -x_max + 16.5, -x_max + 16.5], 
            [-20.15, -20.15, 20.15, 20.15, -20.15], color=line_color, lw=2, zorder=1)
    
    # 5. ゴールエリア
    # 右側
    ax.plot([x_max - 5.5, x_max, x_max, x_max - 5.5, x_max - 5.5], 
            [-9.15, -9.15, 9.15, 9.15, -9.15], color=line_color, lw=2, zorder=1)
    # 左側
    ax.plot([-x_max + 5.5, -x_max, -x_max, -x_max + 5.5, -x_max + 5.5], 
            [-9.15, -9.15, 9.15, 9.15, -9.15], color=line_color, lw=2, zorder=1)
    
    # 6. ペナルティアーク
    arc_right = patches.Arc((x_max - 11, 0), 18.3, 18.3, theta1=128, theta2=232, color=line_color, lw=2, zorder=1)
    ax.add_patch(arc_right)
    arc_left = patches.Arc((-x_max + 11, 0), 18.3, 18.3, theta1=308, theta2=52, color=line_color, lw=2, zorder=1)
    ax.add_patch(arc_left)

    # 7. ゴールポスト（視覚的な強調）
    ax.plot([x_max, x_max+1], [-3.66, 3.66], color="red", lw=4, zorder=2)
    ax.plot([-x_max, -x_max-1], [-3.66, 3.66], color="red", lw=4, zorder=2)

    ax.set_xlim(-58, 58)
    ax.set_ylim(-38, 38)
    ax.axis('off')

# --- サイドバーメニュー ---
st.sidebar.title("⚽ ScoutLab Pro")
menu = st.sidebar.radio("メニューを選択", ["試合分析", "リーグ分析 (100year J2J3)"])

# ==========================================
# 1. 試合分析メニュー
# ==========================================
if menu == "試合分析":
    st.header("🏃 Match Analysis Dashboard")
    
    uploaded_file = st.sidebar.file_uploader("試合CSVをアップロード", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    else:
        try:
            # サーバー上のデフォルトファイル
            df = pd.read_csv('2026-02-14_-_FC_Machida_Zelvia_v_Mito_Hollyhock_dynamic_events.csv')
        except:
            st.warning("CSVファイルをアップロードしてください。")
            st.stop()

    if df is not None:
        team = st.sidebar.selectbox("チームを選択", df['team_shortname'].unique())
        df_t = df[df['team_shortname'] == team].copy()
        
        # シュートデータの抽出
        df_shots = df_t[
            (df_t['lead_to_shot'] == True) & 
            (df_t['x_start'].notna()) & 
            (df_t['y_start'].notna())
        ].copy()
        
        # KPI表示
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Shots", len(df_shots))
        with c2: st.metric("Goals", int(df_t['lead_to_goal'].sum()) if 'lead_to_goal' in df_t.columns else 0)
        with c3: st.metric("Avg Speed", f"{df_t['speed_avg'].mean() if 'speed_avg' in df_t.columns else 0:.2f} km/h")

        # --- シュートマップ ---
        st.subheader("🎯 Shoot Map")
        fig, ax = plt.subplots(figsize=(10, 7))
        draw_pitch(ax) # 関数名を統一しました
        
        if not df_shots.empty:
            for _, shot in df_shots.iterrows():
                is_goal = shot.get('lead_to_goal', False)
                # xthreat をサイズとして利用
                xt = shot.get('xthreat', 0.05)
                if pd.isna(xt) or xt <= 0: xt = 0.05
                size = (xt * 3000) + 100 
                
                ax.scatter(
                    shot['x_start'], shot['y_start'], 
                    s=size, 
                    c="yellow" if is_goal else "white", 
                    edgecolors="black", 
                    marker="*" if is_goal else "o",
                    alpha=0.8,
                    zorder=5
                )
            st.caption("🌟: Goal / ●: Shot (Size reflects xThreat)")
        else:
            st.info("この条件に該当するシュートデータはありません。")

        st.pyplot(fig)
        plt.close(fig)

        # 選手別統計テーブルの追加（詳細化）
        st.subheader("👤 Player Stats (Top 10 xT)")
        player_stats = df_t.groupby('player_name').agg({
            'xthreat': 'sum',
            'speed_avg': 'max',
            'event_id': 'count'
        }).rename(columns={'event_id': 'Events', 'speed_avg': 'Max Speed'}).sort_values('xthreat', ascending=False)
        st.table(player_stats.head(10))

# ==========================================
# 2. リーグ分析メニュー (100year J2J3)
# ==========================================
elif menu == "リーグ分析 (100year J2J3)":
    st.header("🏆 League Analysis: 100year J2J3")
    
    # リーグデータ読み込みの準備
    league_file = st.sidebar.file_uploader("リーグCSVをアップロード", type="csv", key="league")
    
    if league_file:
        df_league = pd.read_csv(league_file)
        st.success("リーグデータを読み込みました")
        st.dataframe(df_league.head())
    else:
        st.info("「100year J2J3」のリーグ全体データをアップロード、または設定してください。")
        st.write("### 分析予定項目:")
        st.write("- チーム別勝ち点・得失点ランキング")
        st.write("- リーグ全体の走行距離・インテンシティ比較")
        st.write("- 昇格争いシミュレーション")
