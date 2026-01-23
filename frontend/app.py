import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.title("Misinformation Detector (PoC)")

tab1, tab2, tab3 = st.tabs(["Analyze by URL", "Paste text", "History"])

with tab1:
    st.subheader("Analyze by URL")
    url = st.text_input("Paste news link here", key="u1")
    if st.button("Fetch + Analyze URL", key="b1"):
        r = requests.post(f"{API_URL}/analyze_url", json={"url": url})
        if r.status_code == 200:
            st.session_state['res1'] = r.json()
    
    if 'res1' in st.session_state:
        res = st.session_state['res1']
        st.write(f"**Prediction:** {res['label']}")
        st.write(f"**Confidence:** {res['confidence']}")
        st.write(f"**Explanation:** {res['explanation']}")
        with st.expander("📝 Add Feedback"):
            fb1 = st.text_area("Comment:", key="f1")
            if st.button("Save Feedback", key="s1"):
                requests.post(f"{API_URL}/update_feedback", json={"id": res['id'], "feedback": fb1})
                st.success("Saved!")
                del st.session_state['res1']
                st.rerun()

with tab2:
    st.subheader("Analyze News Text")
    text = st.text_area("Paste news text here", height=200, key="u2")
    if st.button("Analyze Text", key="b2"):
        r = requests.post(f"{API_URL}/predict", json={"text": text})
        if r.status_code == 200:
            st.session_state['res2'] = r.json()

    if 'res2' in st.session_state:
        res = st.session_state['res2']
        st.write(f"**Prediction:** {res['label']}")
        st.write(f"**Confidence:** {res['confidence']}")
        st.write(f"**Explanation:** {res['explanation']}")
        with st.expander("📝 Add Feedback"):
            fb2 = st.text_area("Comment:", key="f2")
            if st.button("Save Feedback", key="s2"):
                requests.post(f"{API_URL}/update_feedback", json={"id": res['id'], "feedback": fb2})
                st.success("Saved!")
                del st.session_state['res2']
                st.rerun()

with tab3:
    st.subheader("History")
    try:
        r = requests.get(f"{API_URL}/history?limit=50")
        if r.status_code == 200:
            data = r.json()
            if data:
                st.dataframe(pd.DataFrame(data), use_container_width=True, height=500)
            else:
                st.info("No records yet.")
    except:
        st.error("Connection Error")
