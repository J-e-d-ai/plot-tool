import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="多文件快速绘图", layout="wide")
st.title("📊 多文件合并绘图工具")

with st.sidebar:
    st.header("设置面板")
    files = st.file_uploader("上传 CSV / XLSX", type=["csv", "xlsx"], accept_multiple_files=True)
    chart_type = st.selectbox("图表类型", ["折线图", "散点图", "柱状图"])
    x_label = st.text_input("X轴名称", "X")
    y_label = st.text_input("Y轴名称", "Y")
    max_y_cols = st.slider("单文件最多Y列", min_value=5, max_value=10, value=8)
    show_legend = st.checkbox("显示图例", True)
    show_grid = st.checkbox("显示网格", True)

file_data = {}
if files:
    for f in files:
        try:
            if f.name.endswith(".csv"):
                df = pd.read_csv(f)
            else:
                df = pd.read_excel(f)
            file_data[f.name] = df
        except Exception as e:
            st.error(f"{f.name} 读取失败：{e}")

fig = go.Figure()
if file_data:
    st.subheader("列选择（每个文件独立选X、Y）")
    conf = {}
    for name, df in file_data.items():
        cols = list(df.columns)
        st.markdown(f"**{name}**")
        x_sel = st.selectbox(f"[{name}] X列", cols, key=f"x_{name}")
        y_options = [c for c in cols if c != x_sel]
        y_sel = st.multiselect(
            f"[{name}] Y列，最多{max_y_cols}项",
            y_options,
            max_selections=max_y_cols,
            key=f"y_{name}"
        )
        conf[name] = {"df": df, "x": x_sel, "ys": y_sel}

    for fname, item in conf.items():
        df = item["df"]
        xc = item["x"]
        ylist = item["ys"]
        for yc in ylist:
            if chart_type == "折线图":
                fig.add_trace(go.Scatter(x=df[xc], y=df[yc], name=f"{fname}｜{yc}", mode="lines"))
            elif chart_type == "散点图":
                fig.add_trace(go.Scatter(x=df[xc], y=df[yc], name=f"{fname}｜{yc}", mode="markers"))
            elif chart_type == "柱状图":
                fig.add_trace(go.Bar(x=df[xc], y=df[yc], name=f"{fname}｜{yc}"))

    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        showlegend=show_legend,
        xaxis={"showgrid": show_grid},
        yaxis={"showgrid": show_grid},
        height=650
    )
    st.plotly_chart(fig, use_container_width=True)
    img = fig.to_image(format="png", width=1200, height=700, scale=2)
    st.download_button("下载 PNG", data=img, file_name="result_plot.png", mime="image/png")
else:
    st.info("在左侧上传文件，表头放在第一行")
