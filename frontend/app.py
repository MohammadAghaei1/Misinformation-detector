import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.title("Misinformation Detector (PoC)")

tab1, tab2, tab3 = st.tabs(["Analyze by URL", "Paste text", "History"])

with tab1:
    st.subheader("Analyze by URL")
    url = st.text_input("Paste news link here", key="u_url")
    if st.button("Fetch + Analyze URL"):
        r = requests.post(f"{API_URL}/analyze_url", json={"url": url})
        if r.status_code == 200:
            st.session_state['url_res'] = r.json()
    
    if 'url_res' in st.session_state:
        res = st.session_state['url_res']
        st.write(f"**Prediction:** {res['label']}")
        st.write(f"**Explanation:** {res['explanation']}")
        with st.expander("📝 Feedback"):
            f_url = st.text_area("Comment:", key="f_url")
            if st.button("Save URL Feedback"):
                requests.post(f"{API_URL}/update_feedback", json={"id": res['id'], "feedback": f_url})
                st.success("Saved!")
                del st.session_state['url_res']
                st.rerun()

with tab2:
    st.subheader("Analyze News Text")
    text = st.text_area("Paste news text here", height=200, key="u_txt")
    if st.button("Analyze Text"):
        r = requests.post(f"{API_URL}/predict", json={"text": text})
        if r.status_code == 200:
            st.session_state['txt_res'] = r.json()

    if 'txt_res' in st.session_state:
        res = st.session_state['txt_res']
        st.write(f"**Prediction:** {res['label']}")
        st.write(f"**Explanation:** {res['explanation']}")
        with st.expander("📝 Feedback"):
            f_txt = st.text_area("Comment:", key="f_txt")
            if st.button("Save Text Feedback"):
                requests.post(f"{API_URL}/update_feedback", json={"id": res['id'], "feedback": f_txt})
                st.success("Saved!")
                del st.session_state['txt_res']
                st.rerun()

with tab3:
    st.subheader("History")

    try:
        r_hist = requests.get(f"{API_URL}/history?limit=50")
        if r_hist.status_code == 200:
            df = pd.DataFrame(r_hist.json())

            st.dataframe(df, use_container_width=True, height=500)
    except:
        st.error("Connection Error")