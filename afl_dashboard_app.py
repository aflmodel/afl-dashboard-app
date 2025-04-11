import streamlit as st
import os
import pandas as pd

st.set_page_config(page_title="Debug Loader", layout="wide")
st.title("🔧 Streamlit Cloud Debug")

# 1. Show current directory
st.markdown("### 📁 Current directory")
st.code(os.getcwd())

# 2. List files
st.markdown("### 📂 Files in repo")
st.code("\n".join(os.listdir()))

# 3. Try loading Excel files
st.markdown("### 📊 Try loading Excel files")

for file in ["Export.xlsx", "ExportDisposals.xlsx"]:
    try:
        df = pd.read_excel(file)
        st.success(f"✅ Loaded `{file}` with shape {df.shape}")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"❌ Failed to load `{file}`: {type(e).__name__} – {e}")
