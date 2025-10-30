# app.py
import streamlit as st
import pandas as pd
import os
from google.cloud import storage
from google.cloud import aiplatform
from profiler import profile_dataframe
from pbl_generator import generate_pbl_for_column
from chat_agent import answer_question_about_df
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize GCP clients
def init_gcp():
    if os.getenv('GOOGLE_CLOUD_PROJECT'):
        storage_client = storage.Client()
        aiplatform.init(project=os.getenv('GOOGLE_CLOUD_PROJECT'))
        return storage_client
    return None

def save_to_gcs(bucket_name, file_path, content):
    """Save content to Google Cloud Storage"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.upload_from_string(content)
    return f"gs://{bucket_name}/{file_path}"

# Initialize GCP
storage_client = init_gcp()

st.set_page_config(page_title="Data Profiling AI Assistant", layout="wide")
st.title("Data Profiling AI Assistant")

# Add GCS bucket input if in cloud environment
if storage_client:
    gcs_bucket = st.text_input("GCS Bucket Name (optional)", 
                              value=os.getenv('DEFAULT_BUCKET', ''))

uploaded_file = st.file_uploader("Upload CSV / Excel file", type=['csv','xlsx'])
if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Preview (first 200 rows)")
    st.dataframe(df.head(200))

    st.subheader("Profiling Summary")
    profile = profile_dataframe(df)

    st.markdown("**Columns overview**")
    overview = {}
    for c, meta in profile['columns_overview'].items():
        overview[c] = {
            'dtype': meta.get('dtype'),
            'nulls': meta.get('nulls'),
            'distinct': meta.get('distinct'),
            'pattern': meta.get('pattern')
        }
    st.dataframe(pd.DataFrame(overview).T)

    st.markdown("**Top insights**")
    for insight in profile['top_insights'][:20]:
        st.write("- ", insight)

    if profile.get('correlations') is not None:
        st.subheader("Numeric Correlations (pearson)")
        st.dataframe(profile['correlations'])

    st.subheader("Generate Plain Business Logic (PBL)")
    col = st.selectbox("Pick a column to generate PBL", df.columns.tolist())
    if st.button("Generate PBL"):
        pbl = generate_pbl_for_column(df[col], col_name=col)
        st.markdown("**PBL for column:**")
        for i, rule in enumerate(pbl, 1):
            st.write(f"{i}. {rule}")

    st.subheader("Ask a question about the dataset")
    question = st.text_input("e.g., 'How many nulls in email?' or 'Which columns have outliers?'")
    if st.button("Ask"):
        with st.spinner("Analyzing..."):
            answer = answer_question_about_df(question, df, profile)
        st.markdown("**Answer:**")
        st.write(answer)
