import streamlit as st
import requests
import time, os

st.title("Google Cloud Server Manager")

if "auth_configured" not in st.session_state:
    st.session_state.auth_configured = False
if "receiver_email" not in st.session_state:
    st.session_state.receiver_email = ""

st.sidebar.header("Configuration")

if st.sidebar.button("Reset Configuration"):
    st.session_state.auth_configured = False
    st.session_state.receiver_email = ""
    st.sidebar.success("Configuration reset!")
    st.rerun()

BACKEND_URL = os.environ.get("BACKEND_URL")

if not st.session_state.auth_configured:
    st.subheader("Setup Required")

    uploaded_file = st.file_uploader("Upload Google Cloud Service Account JSON Key", type=['json'], help="Upload your Google Cloud service account credentials JSON file")

    receiver_email = st.text_input("Receiver Email Address", placeholder="notifications@example.com", help="Email address to receive start/stop notifications")
    
    if uploaded_file is not None and receiver_email:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        r = requests.post(f"{BACKEND_URL}/load_config", files=files, timeout=30)
        st.session_state.receiver_email = receiver_email
        st.session_state.auth_configured = True
        st.success("Configuration saved!")
    elif uploaded_file is not None:
        st.warning("Please enter a receiver email address.")
    elif receiver_email:
        st.warning("Please upload your service account JSON file.")

if st.session_state.auth_configured:
    st.sidebar.success("Configuration Active")
    st.sidebar.write(f"**Receiver:** {st.session_state.receiver_email}")
    
    def fetch_servers():
        try:
            response = requests.get(f"{BACKEND_URL}/list-server")
            if response.status_code == 200:
                return response.json()
            else:
                error_detail = response.json().get("detail", "Unknown error")
                st.error(f"Error: {error_detail}")
                return []
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
            return []    
    st.subheader("Available Servers")

    servers = fetch_servers()

    if not servers:
        st.write("No servers found.")
    else:
        for server in servers:
            instance_name = server["Instance Name"]
            zone = server["Zone"]
            status = server["Instance Status"]

            col1, col2, col3 = st.columns([3, 2, 2])

            with col1:
                st.write(f"**{instance_name}** ({zone})")
                
            with col2:
                st.write(f"Status: **{status}**")

            with col3:
                if status.lower() == "terminated":
                    if st.button(f"Start {instance_name}", key=f"start_{instance_name}"):
                        request_body = {"zone": zone, "instance_name": instance_name,"receiver":receiver_email}
                        response = requests.post(f"{BACKEND_URL}/start-server", json=request_body)
                        if response.status_code == 200:
                            st.success(f"Started {instance_name}")
                            time.sleep(3)
                            st.rerun()
                        else:
                            st.error(f"Failed to start {instance_name}")

                elif status.lower() == "running":
                    if st.button(f"Stop {instance_name}", key=f"stop_{instance_name}"):
                        request_body = {"zone": zone, "instance_name": instance_name, "receiver":receiver_email}
                        response = requests.post(f"{BACKEND_URL}/end-server", json=request_body)
                        if response.status_code == 200:
                            st.success(f"Stopped {instance_name}")
                            time.sleep(3) 
                            st.rerun()
                        else:
                            st.error(f"Failed to stop {instance_name}")

    if st.button("Refresh Server List"):
        st.rerun()