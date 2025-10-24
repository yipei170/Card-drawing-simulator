import streamlit as st
import random
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import font_manager

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

font_path = 'fonts/msjh.ttc'
try:
    font_manager.fontManager.addfont(font_path)
    # 2. 獲取字體屬性，這會讀取字體檔案內建的家族名稱
    prop = font_manager.FontProperties(fname=font_path)
    font_family_name = prop.get_name() # 獲取字體檔案的實際家族名稱 (例如: 'Microsoft JhengHei')
    
    # 3. 使用實際的字體家族名稱來設定 Matplotlib
    plt.rcParams['font.family'] = font_family_name
    plt.rcParams['axes.unicode_minus'] = False
    
    # 診斷訊息 (可選，用於確認)
    # st.sidebar.success(f"Matplotlib 字體設定成功: {font_family_name}")

except Exception as e:
    # 如果檔案找不到或其他錯誤，退回預設
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="抽卡策略分析器", layout="wide")
st.title("🎮 互動式多次活動抽卡策略分析器")

# ------------------------------
# 輸入設定
st.sidebar.header("模擬設定")
n_players = st.sidebar.number_input("玩家數量", value=1000, step=100)
limit = st.sidebar.number_input("抽卡上限", value=50, step=1)
p_ssr_before = st.sidebar.slider("SSR 機率（活動前）", 0.0, 1.0, 0.02)
p_ssr_after = st.sidebar.slider("SSR 機率（活動後）", 0.0, 1.0, 0.03)
p_sr_before = st.sidebar.slider("SR 機率（活動前）", 0.0, 1.0, 0.18)
p_sr_after = st.sidebar.slider("SR 機率（活動後）", 0.0, 1.0, 0.17)
step = st.sidebar.number_input("保底累積", value=10)
bonus = st.sidebar.number_input("保底增加機率", value=0.01, step=0.01)
cost_per_pull = st.sidebar.number_input("每抽花費", value=100)
n_events = st.sidebar.number_input("模擬活動次數", value=50, step=1)

# ------------------------------
# 抽卡模擬函式
random.seed(1234)
np.random.seed(1234)
def draw(p_ssr, p_sr, step, bonus, limit):
    counter = 0
    current_p_ssr = p_ssr
    for i in range(1, limit + 1):
        r = random.random()
        if r < current_p_ssr:
            return i, 'SSR'
        elif r < current_p_ssr + p_sr:
            rarity = 'SR'
        else:
            rarity = 'R'
        counter += 1
        if counter % step == 0:
            current_p_ssr = min(current_p_ssr + bonus, 1.0)
    return limit, 'SSR'

def simulate(n_players, p_ssr, p_sr):
    results = [draw(p_ssr, p_sr, step, bonus, limit) for _ in range(n_players)]
    df = pd.DataFrame(results, columns=['pulls_needed', 'rarity'])
    df['cost'] = df['pulls_needed'] * cost_per_pull
    return df

# ------------------------------
# 蒙地卡羅模擬
all_summary_before = []
all_summary_after = []

for i in range(n_events):
    df_b = simulate(n_players, p_ssr_before, p_sr_before)
    df_a = simulate(n_players, p_ssr_after, p_sr_after)
    all_summary_before.append(df_b['cost'].mean())
    all_summary_after.append(df_a['cost'].mean())

summary_df = pd.DataFrame({
    'Event': range(1, n_events + 1),
    'Mean_Cost_Before': all_summary_before,
    'Mean_Cost_After': all_summary_after
})

# ------------------------------
# 信賴區間計算
def ci_95(series):
    mean = series.mean()
    std = series.std()
    lower = mean - 1.96 * std / np.sqrt(len(series))
    upper = mean + 1.96 * std / np.sqrt(len(series))
    return mean, lower, upper

mean_before, ci_lower_before, ci_upper_before = ci_95(summary_df['Mean_Cost_Before'])
mean_after, ci_lower_after, ci_upper_after = ci_95(summary_df['Mean_Cost_After'])

st.subheader("📊 多次活動平均成本統計（95% CI）")
st.write(f"活動前 : {mean_before:.2f} ({ci_lower_before:.2f} ~ {ci_upper_before:.2f})")
st.write(f"活動後 : {mean_after:.2f} ({ci_lower_after:.2f} ~ {ci_upper_after:.2f})")

# ------------------------------
# 成本分布圖
fig, ax = plt.subplots(figsize=(8, 4))
sns.kdeplot(summary_df['Mean_Cost_Before'], fill=True, color='skyblue', label='Before', ax=ax)
sns.kdeplot(summary_df['Mean_Cost_After'], fill=True, color='salmon', label='After', ax=ax)
ax.set_xlabel("平均成本")
ax.set_ylabel("機率密度")
ax.set_title("平均抽卡成本分布")
ax.legend()
st.pyplot(fig)

# 將圖表存成 BytesIO
img = BytesIO()
fig.savefig(img, format='png', bbox_inches='tight')
img.seek(0)

# ------------------------------
# 產生 PDF
def pdf():
    # 註冊中文字體
    pdfmetrics.registerFont(TTFont('msjh', 'fonts/msjh.ttc'))

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "msjh"
    styles["Title"].fontName = "msjh"
    elements = []

    elements.append(Paragraph("多次活動抽卡策略分析報告", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"玩家數量:{n_players}  抽卡上限:{limit} ", styles["Normal"]))
    elements.append(Paragraph(f"SSR機率(活動前):{p_ssr_before:.2f}  SSR機率(活動後):{p_ssr_after:.2f} ",styles["Normal"]))
    elements.append(Paragraph(f"SR 機率(活動前):{p_sr_before:.2f}  SR機率(活動後):{p_sr_after:.2f}",styles["Normal"]))
    elements.append(Paragraph(f"保底累積:{step}  保底增加機率:{bonus:.2f} "
                              f" 每抽花費:{cost_per_pull}  模擬活動次數:{n_events}", styles["Normal"]))
    elements.append(Paragraph(f"活動前平均成本(95%CI): {mean_before:.2f} ({ci_lower_before:.2f} ~ {ci_upper_before:.2f})", styles["Normal"]))
    elements.append(Paragraph(f"活動後平均成本(95%CI): {mean_after:.2f} ({ci_lower_after:.2f} ~ {ci_upper_after:.2f})", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # 插入圖表
    elements.append(Image(img, width=400, height=250))
    elements.append(Spacer(1, 12))

    doc.build(elements)
    buffer.seek(0)
    return buffer

pdf_data = pdf()
st.download_button(
    "下載 PDF 報告",
    data=pdf_data,
    file_name="抽卡分析報告.pdf",
    mime="application/pdf"
)

with pd.ExcelWriter("gacha_multi_event.xlsx") as writer: summary_df.to_excel(writer, sheet_name='Summary', index=False)
st.download_button(
    "下載 Excel 報表",
    data=open("gacha_multi_event.xlsx", "rb").read(),
    file_name="模擬報表.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)








