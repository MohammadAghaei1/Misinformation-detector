import streamlit as st
import requests
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Misinformation Detector", layout="wide")

# Change this to your EC2 IP or domain in production
API_URL = "http://127.0.0.1:8000" 

# DASHBOARD SECTION 
st.title("🛡️ Misinformation Analysis Dashboard")

try:
    # Fetch real-time stats from the new endpoint
    stats_r = requests.get(f"{API_URL}/stats")
    if stats_r.status_code == 200:
        stats = stats_r.json()
        total = stats.get("total", 0)
        percent = stats.get("percent", 0)
        
        # Display as metric cards
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Analyzed", total)
        m2.metric("Fake News Ratio", f"{percent}%")
        m3.metric("System Status", "Online ✅")
        
        # Simple progress bar for visual impact
        st.write(f"**Fake Content Distribution ({percent}%)**")
        st.progress(percent / 100)
except:
    st.warning("⚠️ Dashboard stats temporarily unavailable (Check backend connection).")

st.divider()

# ORIGINAL TABS SECTION
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
        # Show if result came from cache
        if res.get("source") == "database":
            st.info("⚡ Instant Result: This was previously analyzed and loaded from cache.")
            
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
        # Show if result came from cache
        if res.get("source") == "database":
            st.info("⚡ Instant Result: This was previously analyzed and loaded from cache.")

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
    # Fetch records from backend
    try:
        r = requests.get(f"{API_URL}/history?limit=50")
        
        if r.status_code == 200:
            data = r.json()
            if data and len(data) > 0:
                # Only show the dataframe if there's actually data
                st.dataframe(pd.DataFrame(data), use_container_width=True, height=500)
                
                st.divider()
                with st.expander("🗑️ Danger Zone"):
                    st.warning("This action cannot be undone!")
                    confirm = st.checkbox("I confirm that I want to delete all history")
                    if st.button("🚨 Clear All Records"):
                        if confirm:
                            res = requests.post(f"{API_URL}/clear_history")
                            if res.status_code == 200:
                                st.success("Database cleared successfully!")
                                # Use st.rerun() to refresh the UI
                                st.rerun()
                            else:
                                st.error("Failed to clear database.")
                        else:
                            st.info("Please check the confirmation box first.")
            else:
                # This replaces the red error when the database is empty
                st.info("No records found. The database is empty.")
        else:
            st.error(f"Backend returned an error: {r.status_code}")

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend server. Is it running?")
    except Exception as e:
        # Only show other types of errors, not empty data
        st.error(f"An unexpected error occurred: {e}")