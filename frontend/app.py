import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# --- 1. Global Page Configuration (Must be first) ---
st.set_page_config(
    page_title="Misinformation Analysis Dashboard",
    page_icon="favicon.png",
    layout="wide"
)

# --- 2. Configuration & Session State ---

API_URL = "http://localhost:8000" 

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['user_email'] = None
    st.session_state['page'] = 'login'

# --- 3. Authentication Functions ---

def login_user(email, password):
    try:
        response = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
        
        if response.status_code == 200:
            data = response.json()
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = data['user_id']
            st.session_state['user_email'] = email
            return True, "Success"
        
        elif response.status_code == 404:
            return False, "📧 Email not found. Please register first!"
            
        elif response.status_code == 401:
            return False, "🔑 Incorrect password. Please try again."
            
        else:
            return False, f"Login failed: {response.json().get('detail', 'Unknown error')}"
            
    except Exception as e:
        return False, f"Connection Error: {str(e)}"

def signup_user(email, password):
    try:
        response = requests.post(f"{API_URL}/signup", json={"email": email, "password": password})
        return response.status_code == 200
    except:
        return False

# --- 4. Login/Signup UI ---

if not st.session_state['logged_in']:
    if st.session_state['page'] == 'login':
        st.title("🔑 Misinfo Detector Account Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True, key="login_btn_main"):
            success, message = login_user(email, password)
            if success:
                st.success("Logged in!")
                st.rerun()
            else:
                st.error(message)
        
        if st.button("New user? Create account", key="signup_nav_btn"):
            st.session_state['page'] = 'signup'
            st.rerun()

    else:
        st.title("📝 Sign Up")
        new_email = st.text_input("New Email")
        new_pass = st.text_input("New Password", type="password")
        conf_pass = st.text_input("Confirm Password", type="password")
        
        if st.button("Register", use_container_width=True, key="reg_btn"):
            if new_pass != conf_pass:
                st.error("Passwords match error")
            elif signup_user(new_email, new_pass):
                st.success("Account created! Please login.")
                st.session_state['page'] = 'login'
                st.rerun()
            else:
                st.error("Email already exists")
                
        if st.button("Back to Login", key="back_login_btn"):
            st.session_state['page'] = 'login'
            st.rerun()

# --- 5. Main Dashboard (Protected) ---
else:
    st.sidebar.title("👤 Account")
    st.sidebar.write(f"Logged in: {st.session_state['user_email']}")
    if st.sidebar.button("Logout", key="logout_sidebar_btn"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title("🛡️ Misinformation Analysis Dashboard")

    try: 
        stats_r = requests.get(f"{API_URL}/stats?user_id={st.session_state['user_id']}", timeout=5) 
        if stats_r.status_code == 200: 
             stats = stats_r.json() 
             total = stats.get("total", 0) 
             fake_p = stats.get("fake_percent", 0) 
             real_p = stats.get("real_percent", 0) 
             uncertain_p = stats.get("uncertain_percent", 0) 

             st.markdown(""" 
                 <style> 
                 .delta-wrapper { 
                     display: inline-flex; 
                     align-items: center; 
                     padding: 2px 8px; 
                     border-radius: 0.5rem; 
                     font-size: 0.85rem; 
                     font-weight: 500; 
                     margin-top: -15px; 
                 } 
                 .delta-red { background-color: rgba(239, 85, 59, 0.2); color: #EF553B; } 
                 .delta-green { background-color: rgba(0, 204, 150, 0.2); color: #00CC96; } 
                 .delta-yellow { background-color: rgba(253, 180, 50, 0.2); color: #FDB432; } 
                 </style> 
                 """, unsafe_allow_html=True) 

             col_metrics, col_chart = st.columns([3, 1]) 

             with col_metrics: 
                 st.markdown("### Key Performance Metrics") 
                 m1, m2, m3, m4, m5 = st.columns(5) 
                 m1.metric("Total Analyzed", total) 
                 with m2: 
                     st.metric("Fake News", f"{fake_p}%") 
                     st.markdown(f'<div class="delta-wrapper delta-red">↑ {fake_p}%</div>', unsafe_allow_html=True) 
                 with m3: 
                     st.metric("Real News", f"{real_p}%") 
                     st.markdown(f'<div class="delta-wrapper delta-green">↑ {real_p}%</div>', unsafe_allow_html=True) 
                 with m4: 
                     st.metric("Uncertain", f"{uncertain_p}%") 
                     st.markdown(f'<div class="delta-wrapper delta-yellow">↑ {uncertain_p}%</div>', unsafe_allow_html=True) 
                 m5.metric("System Status", "Online ✅") 

             with col_chart: 
                 if total > 0: 
                     chart_df = pd.DataFrame({ 
                         "Category": ["Fake", "Real", "Uncertain"], 
                         "Percentage": [fake_p, real_p, uncertain_p] 
                     }) 
                     fig = px.pie(chart_df, values='Percentage', names='Category', hole=0.6,  
                                  color='Category', color_discrete_map={'Fake': '#EF553B', 'Real': '#00CC96', 'Uncertain': '#FDB432'}) 
                     fig.update_layout(margin=dict(l=0, r=50, t=0, b=0), height=200, showlegend=True,
                                       legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5)) 
                     st.plotly_chart(fig, use_container_width=True) 
        else: 
             st.info("No data available yet.") 
    except Exception as e: 
        st.warning("⚠️ Dashboard metrics unavailable.") 

    st.divider() 

    tab1, tab2, tab3 = st.tabs(["Analyze by URL", "Paste text", "History"]) 

    with tab1: 
        st.subheader("Analyze by URL") 
        url = st.chat_input("Paste news link here...", key="chat_u1") 
        if url: 
            with st.chat_message("user"): st.write(url) 
            with st.chat_message("assistant"): 
                with st.status("Processing URL...", expanded=True) as status: 
                    r = requests.post(f"{API_URL}/analyze_url", json={"url": url, "user_id": st.session_state['user_id']}) 
                    if r.status_code == 200: 
                        st.session_state['res1'] = r.json() 
                        status.update(label="Analysis Complete!", state="complete", expanded=False) 
                    else: 
                        status.update(label="Error fetching URL", state="error") 
        
        if 'res1' in st.session_state: 
            res = st.session_state['res1'] 
            if res.get("source") == "database": st.info("⚡ Instant Result: Loaded from cache.") 
            st.write(f"**Prediction:** {res.get('label')}") 
            st.write(f"**Confidence:** {res.get('confidence')}%") 
            st.write(f"**Explanation:** {res.get('explanation')}") 
            with st.expander("📝 Add Feedback", expanded=True): 
                fb1 = st.text_area("Comment:", key="f1", placeholder="Type your feedback...") 
                if st.button("Save Feedback", key="s1"): 
                    requests.post(f"{API_URL}/update_feedback", json={"id": res['id'], "feedback": fb1}) 
                    st.success("Feedback updated!") 
                    del st.session_state['res1'] 
                    st.rerun() 

    with tab2: 
        st.subheader("Analyze News Text") 
        text = st.chat_input("Paste news text here...", key="chat_u2") 
        if text: 
            with st.chat_message("user"): st.write(text[:200] + "...") 
            with st.chat_message("assistant"): 
                with st.status("Analyzing text...", expanded=True) as status: 
                    r = requests.post(f"{API_URL}/predict", json={"text": text, "user_id": st.session_state['user_id']}) 
                    if r.status_code == 200: 
                        st.session_state['res2'] = r.json() 
                        status.update(label="Analysis Complete!", state="complete", expanded=False) 
                    else: status.update(label="Model Error", state="error") 

        if 'res2' in st.session_state: 
            res = st.session_state['res2'] 
            st.write(f"**Prediction:** {res.get('label')}") 
            st.write(f"**Confidence:** {res.get('confidence')}%") 
            st.write(f"**Explanation:** {res.get('explanation')}") 
            with st.expander("📝 Add Feedback", expanded=True): 
                fb2 = st.text_area("Comment:", key="f2", placeholder="Type your feedback...") 
                if st.button("Save Feedback", key="s2"): 
                    requests.post(f"{API_URL}/update_feedback", json={"id": res['id'], "feedback": fb2}) 
                    st.success("Feedback updated!") 
                    del st.session_state['res2'] 
                    st.rerun()

    with tab3:
        st.subheader("Analysis History")
        try:
            r = requests.get(f"{API_URL}/history?user_id={st.session_state['user_id']}&limit=50")
            if r.status_code == 200:
                data = r.json()
                if data:
                    st.dataframe(pd.DataFrame(data), use_container_width=True, height=400)
                    st.divider()
                    with st.expander("🗑️ Clear My History"):
                        confirm = st.checkbox("Confirm deletion")
                        if st.button("🚨 Clear My Records", type="primary", disabled=not confirm, key="clear_hist_btn"):
                            requests.post(f"{API_URL}/clear_history", json={"user_id": st.session_state['user_id']})
                            st.rerun()
                else:
                    st.info("No records found.")
        except Exception: 
            st.error("Connection Error: Backend unreachable.")