import requests
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Misinformation Detector", layout="wide")

# Change this to your EC2 IP in production
API_URL = "http://127.0.0.1:8000" 

# DASHBOARD SECTION 
st.title("🛡️ Misinformation Analysis Dashboard")

try:
    stats_r = requests.get(f"{API_URL}/stats")
    if stats_r.status_code == 200:
        stats = stats_r.json()
        total = stats.get("total", 0)
        fake_p = stats.get("fake_percent", 0)
        real_p = stats.get("real_percent", 0)

        col_metrics, col_chart = st.columns([3, 1])

        with col_metrics:
            st.markdown("###  Key Performance Metrics")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Analyzed", total)
            m2.metric("Fake News Ratio", f"{fake_p}%", delta=f"{fake_p}%", delta_color="inverse")
            m3.metric("Real News Ratio", f"{real_p}%", delta=f"{real_p}%", delta_color="normal")
            m4.metric("System Status", "Online ✅")

        with col_chart:
            if total > 0:
                st.markdown("<div style='padding-top: 20px;'></div>", unsafe_allow_html=True)
                
                chart_df = pd.DataFrame({
                    "Category": ["Fake", "Real"],
                    "Percentage": [fake_p, real_p]
                })
                fig = px.pie(
                    chart_df, 
                    values='Percentage', 
                    names='Category', 
                    hole=0.6, 
                    color='Category',
                    color_discrete_map={'Fake': '#EF553B', 'Real': '#00CC96'}
                )
                
                fig.update_layout(
                    margin=dict(l=0, r=50, t=0, b=0),
                    height=200,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available yet.")
except Exception as e:
    st.warning("⚠️ Dashboard unavailable.")

st.divider()

# TABS SECTION
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
    st.subheader("Analysis History")
    try:
        r = requests.get(f"{API_URL}/history?limit=50")
        if r.status_code == 200:
            data = r.json()
            if data and len(data) > 0:
                st.dataframe(pd.DataFrame(data), use_container_width=True, height=400)
                
                # Danger Zone: Clear History
                st.divider()
                with st.expander("🗑️ Danger Zone"):
                    st.warning("This action will permanently delete all records!")
                    confirm = st.checkbox("Confirm deletion")
                    if st.button("🚨 Clear All Records"):
                        if confirm:
                            res = requests.post(f"{API_URL}/clear_history")
                            if res.status_code == 200:
                                st.success("Database cleared!")
                                st.rerun()
            else:
                st.info("No records found. The database is empty.")
    except:
        st.error("Connection Error with Backend")