
import streamlit as strl
import streamlit_authenticator as stauth

from functions_auth import load_config, auth_connected, auth_disconnected, sidebar_auth

# Load the config.yaml file
config = load_config()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

strl.title('User account')

if strl.session_state["authentication_status"] != True:
    strl.warning("To access our exclusive content please register or login to your account.")

else:

    strl.success(f'Hi *{strl.session_state["name"]}*')
    strl.success(f' You are logged in as: *{strl.session_state["username"]}*', icon="✅")
    strl.success(f' Your  registered email is: *{config["credentials"]["usernames"][strl.session_state["username"]]["email"]}*', icon="📧") 
    
name, authentication_status, username = authenticator.login('Login for advanced metrics access', 'main')

sidebar_auth(authenticator)
auth_connected(authenticator, name, authentication_status, username, config)
auth_disconnected(authenticator, config)