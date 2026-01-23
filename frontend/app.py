import streamlit as st
import requests
import pandas as pd

st.title("Misinformation Detector (PoC)")
API_URL = "http://127.0.0.1:8000"

tab1, tab2, tab3 = st.tabs(["Analyze by URL", "Paste text", "History"])

# Tab 1: Analyze by URL
with tab1:
    st.subheader("Analyze by URL")
    url = st.text_input("Paste news link here")

    if st.button("Fetch + Analyze URL"):
        r = requests.post(f"{API_URL}/analyze_url", json={"url": url})
        if r.status_code == 200:
            st.success("Done")
            st.json(r.json())
        else:
            st.error(r.json())


# Tab 2: Paste news text
'''with tab2:
    st.subheader("Paste news text")
    text = st.text_area("Paste news text here")

    if st.button("Analyze Text"):
        payload = {"text": text}
        r = requests.post(f"{API_URL}/predict", json=payload)
        if r.status_code == 200:
            result = r.json()
            st.write(f"**Prediction:** {result['label']}")  
            st.write(f"**Confidence:** {result['confidence']}")  
            st.write(f"**Explanation:** {result['explanation']}")  
        else:
            st.error(f"Error: {r.status_code} - {r.text}")'''

# Tab 2: Paste news text
with tab2:
    st.subheader("Analyze Text & Feedback")
    text_input = st.text_area("Paste news text here", key="text_input")

    if st.button("Analyze Text"):
        if text_input:
            r = requests.post(f"{API_URL}/predict", json={"text": text_input})
            if r.status_code == 200:
                st.session_state['last_analysis'] = r.json()
            else:
                st.error("Error in analysis")

    if 'last_analysis' in st.session_state:
        res = st.session_state['last_analysis']
        
        st.info(f"**Model Verdict:** {res['label']} ({res['confidence']}%)")
        
        with st.expander("📝 Add Reviewer Feedback to this record"):
            feedback_value = st.text_area("Your thoughts:", value="", key="fb_input")
            
            if st.button("Save Feedback to Excel"):
                update_data = {
                    "id": res['id'], 
                    "feedback": feedback_value
                }
                up_r = requests.post(f"{API_URL}/update_feedback", json=update_data)
                if up_r.status_code == 200:
                    st.success("Feedback added to the same row in Excel!")
                    del st.session_state['last_analysis']
                    st.rerun()
# Tab 3:
with tab3:
    st.subheader("History (from Excel)")
    r = requests.get(f"{API_URL}/history?limit=50")
    if r.status_code == 200:
        data = r.json()
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df)  
        else:
            st.info("No records yet.")
    else:
        st.error(f"Could not load history: {r.status_code} - {r.text}")

