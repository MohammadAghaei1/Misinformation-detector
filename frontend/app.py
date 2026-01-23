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
    st.subheader("Analyze News Text")
    news_text = st.text_area("Paste news text here", height=200, key="news_text_area")

    if st.button("Analyze Text Content"):
        if news_text:
            with st.spinner("Analyzing text..."):
                r = requests.post(f"{API_URL}/predict", json={"text": news_text})
                if r.status_code == 200:
                    st.session_state['text_analysis'] = r.json()
                else:
                    st.error(f"Analysis failed: {r.text}")

    if 'text_analysis' in st.session_state:
        res_text = st.session_state['text_analysis']
        
        st.markdown("---")
        st.info(f"**Prediction:** {res_text['label']} | **Confidence:** {res_text['confidence']}")
        st.write(f"**Explanation:** {res_text.get('explanation', 'N/A')}")
        
        with st.expander("📝 Add Feedback for this Text"):
            text_fb = st.text_area("Your comment:", value="", key="text_fb_box")
            
            if st.button("Save Text Feedback"):
                feedback_payload = {
                    "id": res_text.get('id'), 
                    "feedback": text_fb
                }
                resp = requests.post(f"{API_URL}/update_feedback", json=feedback_payload)
                
                if resp.status_code == 200:
                    st.success("Feedback saved for this text record!")
                    del st.session_state['text_analysis']
                    st.rerun()
                else:
                    st.error("Could not update feedback in Excel.")
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
    st.subheader("History (Automated View)")
    
    r = requests.get(f"{API_URL}/history?limit=50")
    
    if r.status_code == 200:
        data = r.json()
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, height=500)
        else:
            st.info("No records yet.")
    else:
        st.error(f"Could not load history: {r.status_code}")
