import streamlit as st
import requests
import time , os

# FastAPI Backend URL
BACKEND_URL = os.environ.get("BACKEND_URL")

st.title("Google Cloud Server Manager")

# Initialize session state for refresh tracking
if "refresh" not in st.session_state:
    st.session_state.refresh = False

# Function to fetch list of servers with retry mechanism
def fetch_servers(retries=3, delay=2):
    for _ in range(retries):
        response = requests.get(f"{BACKEND_URL}/list-server")
        if response.status_code == 200:
            return response.json()
        time.sleep(delay)  # Wait before retrying
    st.error("Failed to fetch server list after multiple attempts")
    return []

# Function to trigger UI refresh
def trigger_refresh():
    st.session_state.refresh = not st.session_state.refresh  # Toggle refresh state

# Display available servers
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
            if status.lower() == "terminated":  # If stopped, show "Start" button
                if st.button(f"Start {instance_name}", key=f"start_{instance_name}"):
                    request_body = {"zone": zone, "instance_name": instance_name}
                    response = requests.post(f"{BACKEND_URL}/start-server", json=request_body)
                    if response.status_code == 200:
                        st.success(f"Started {instance_name}, refreshing...")
                        time.sleep(3)  # Give time for GCloud to update
                        trigger_refresh()  # Update UI
                    else:
                        st.error(f"Failed to start {instance_name}")

            elif status.lower() == "running":  # If running, show "Stop" button
                if st.button(f"Stop {instance_name}", key=f"stop_{instance_name}"):
                    request_body = {"zone": zone, "instance_name": instance_name}
                    response = requests.post(f"{BACKEND_URL}/end-server", json=request_body)
                    if response.status_code == 200:
                        st.success(f"Stopped {instance_name}, refreshing...")
                        time.sleep(3)  # Give time for GCloud to update
                        trigger_refresh()  # Update UI
                    else:
                        st.error(f"Failed to stop {instance_name}")

# Refresh button (alternative way to refresh)
if st.button("Refresh Server List"):
    trigger_refresh()
