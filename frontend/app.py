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

with tab2:
    st.subheader("Paste news text")
    text = st.text_area("Paste news text here", key="main_text_input")

    if st.button("Analyze Text"):
        payload = {"text": text}
        r = requests.post(f"{API_URL}/predict", json=payload)
        if r.status_code == 200:
            st.session_state['result'] = r.json()
            st.session_state['original_text'] = text
        else:
            st.error(f"Error: {r.status_code}")

    if 'result' in st.session_state:
        res = st.session_state['result']
        
        st.write("---")
        st.write(f"**Prediction:** {res['label']}")  
        st.write(f"**Confidence:** {res['confidence']}")  
        
        st.subheader("Reviewer Feedback")
        user_fb = st.text_area("Enter your feedback here:", value="", key="reviewer_fb_input")
        
        if st.button("Submit Final Record"):
            final_payload = {
                "text": st.session_state['original_text'],
                "label": res['label'],
                "confidence": res['confidence'],
                "explanation": res['explanation'],
                "reviewer_feedback": user_fb, 
                "input_type": "text"
            }
            resp = requests.post(f"{API_URL}/save_with_feedback", json=final_payload)
            if resp.status_code == 200:
                st.success("Saved successfully!")
                del st.session_state['result']
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

