import streamlit as st
import requests
import pandas as pd

st.title("Misinformation Detector (PoC)")
API_URL = "http://127.0.0.1:8000"

tab1, tab2, tab3 = st.tabs(["Analyze by URL", "Paste text", "History"])

'''# Tab 1: Analyze by URL
with tab1:
    st.subheader("Analyze by URL")
    url = st.text_input("Paste news link here")

    if st.button("Fetch + Analyze URL"):
        r = requests.post(f"{API_URL}/analyze_url", json={"url": url})
        if r.status_code == 200:
            st.success("Done")
            st.json(r.json())
        else:
            st.error(r.json())'''

# Tab 1: Analyze by URL
with tab1:
    st.subheader("Analyze by URL")
    url = st.text_input("Paste news link here", key="url_input")

    if st.button("Fetch + Analyze URL"):
        with st.spinner("Scraping and Analyzing..."):
            r = requests.post(f"{API_URL}/analyze_url", json={"url": url})
            if r.status_code == 200:
                st.session_state['url_analysis'] = r.json()
            else:
                st.error("Failed to analyze URL.")

    if 'url_analysis' in st.session_state:
        res = st.session_state['url_analysis']
        
        st.markdown("---")
        st.success(f"**Prediction:** {res['label']}")
        st.write(f"**Confidence:** {res['confidence']}")
        st.write(f"**Explanation:** {res.get('explanation', 'N/A')}")
        
        with st.expander("📝 Add Reviewer Feedback for this URL"):
            url_fb = st.text_area("Your comment:", value="", key="url_fb_box")
            
            if st.button("Save URL Feedback"):
                payload = {
                    "id": res.get('id'), 
                    "feedback": url_fb
                }
                resp = requests.post(f"{API_URL}/update_feedback", json=payload)
                if resp.status_code == 200:
                    st.success("Feedback saved for this URL!")
                    del st.session_state['url_analysis']
                    st.rerun()
                else:
                    st.error("Error saving feedback.")


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
'''# Tab 3:
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
        st.error(f"Could not load history: {r.status_code} - {r.text}")'''

with tab3:
    st.subheader("History (from Excel)")
    if st.button("Refresh History"):
        r = requests.get(f"{API_URL}/history?limit=50")
        if r.status_code == 200:
            data = r.json()
            if data:
                df = pd.DataFrame(data)
                if 'timestamp' in df.columns:
                    df = df.sort_values(by='timestamp', ascending=False)
                
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No records yet.")
        else:
            st.error("Could not load history.")
