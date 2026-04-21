import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="J2/J3 100YEAR VISION 分析", layout="wide")

# 1. データの読み込み（Excelの各シートに対応するCSV）
@st.cache_data
def load_data():
    df_shot = pd.read_csv("2026_J2J3xlsx.xlsx - Shot.csv", header=1)
    df_pass = pd.read_csv("2026_J2J3xlsx.xlsx - Pass.csv")
    df_box = pd.read_csv("2026_J2J3xlsx.xlsx - BOX.csv", header=1)
    return df_shot, df_pass, df_box

df_shot, df_pass, df_box = load_data()

# 2. サイドバーでのチーム選択
st.sidebar.title("分析設定")
target_team = st.sidebar.selectbox("チームを選択", df_shot["East A "].dropna().unique())

# 3. メイン画面のタブ構成
tab1, tab2, tab3 = st.tabs(["シュート分析", "パス・ビルドアップ", "BOX進入・エリア"])

with tab1:
    st.header(f"{target_team} のシュートスタッツ")
    # 例：決定率と枠内率をゲージやグラフで表示
    team_shot = df_shot[df_shot["East A "] == target_team]
    st.metric("決定率", f"{team_shot['決定率\n(%)'].values[0]}%")
    
    # リーグ全体の分布の中での位置
    fig = px.histogram(df_shot, x="決定率\n(%)", title="リーグ全体の決定率分布")
    st.plotly_chart(fig)

with tab2:
    st.header("パス供給ルートの傾向")
    # Pass.csvのデータを使って、「DT(自陣)」「MT(中盤)」「AT(敵陣)」の割合を可視化
    # ...ここにグラフ作成コード...
