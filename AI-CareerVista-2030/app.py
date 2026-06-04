import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AI CareerVista 2030",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI CareerVista 2030")
st.subheader("AI Impact on Jobs & Future Career Analytics")

df = pd.read_csv("data/AI_Impact_on_Jobs_2030.csv")

col1,col2,col3,col4 = st.columns(4)

with col1:
    st.metric("Employees", len(df))

with col2:
    st.metric("Avg Salary", f"${int(df['Average_Salary_USD'].mean())}")

with col3:
    st.metric("Avg AI Risk",
              round(df['AI_Replacement_Risk'].mean(),2))

with col4:
    st.metric("Avg Demand",
              round(df['Future_Demand_Score'].mean(),2))

st.image("https://images.unsplash.com/photo-1485827404703-89b55fcc595e")
