import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("data/AI_Impact_on_Jobs_2030.csv")

st.title("🤖 AI Replacement Risk Analysis")

risk = df.groupby("Job_Title")["AI_Replacement_Risk"].mean().sort_values(ascending=False).head(10)

fig = px.bar(
    risk,
    x=risk.values,
    y=risk.index,
    orientation="h",
    title="Top 10 High Risk Jobs"
)

st.plotly_chart(fig,use_container_width=True)

fig2 = px.scatter(
    df,
    x="AI_Replacement_Risk",
    y="Average_Salary_USD",
    color="Industry",
    title="AI Risk vs Salary"
)

st.plotly_chart(fig2,use_container_width=True)

st.info("Insight: Jobs with high automation tend to show higher AI replacement risk.")
