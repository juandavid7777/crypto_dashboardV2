
import streamlit as strl
import streamlit_authenticator as stauth

from streamlit_extras.buy_me_a_coffee import button
from streamlit_extras.badges import badge
from streamlit_extras.colored_header import colored_header 

from functions_auth import load_config, auth_connected, auth_disconnected, sidebar_auth
from functions_visual import clean_image
from functions_analytics import inject_ga


strl.set_page_config(layout="wide", page_title="₿trends - Account", page_icon = "🗝️")
inject_ga()
clean_image()

authenticator, config = sidebar_auth(auth_out = True)

strl.title('User account')
if strl.session_state["authentication_status"] != True:
    strl.info("To access our exclusive content please register or login to your account.")

name, authentication_status, username = authenticator.login('Login for advanced metrics access', 'main')   
    
#Basic session rendering
if strl.session_state["authentication_status"]:
    strl.success(f'Hi *{strl.session_state["name"]}*')
    strl.success(f' You are logged in as: *{strl.session_state["username"]}*', icon="✅")
    strl.success(f' Your  registered email is: *{config["credentials"]["usernames"][strl.session_state["username"]]["email"]}*', icon="📧")
    authenticator.logout('Logout', 'main', key='unique_key2')

else:   
    if strl.session_state["authentication_status"] is False:
        strl.error('Username/password is incorrect')
    else:
        strl.warning('Please enter your username and password')

strl.markdown("""---""")
strl.header("Register / Forgot password / Forgot username")
auth_connected(authenticator, name, authentication_status, username, config)
auth_disconnected(authenticator, config)

#Final comments
colored_header(label = "", description = "", color_name="yellow-80")
strl.write("Have you found this useful? Your donation will support our research and pave the way for innovative solutions.")

col1, col2, col3, col4 = strl.columns([1.5, 1.5, 5, 4])

with col1:
    badge(type="twitter", name="barbosa83")
with col2:
    badge(type="buymeacoffee", name="juandavid7E")
with col3:
    strl.caption("₿: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34")

button(username="juandavid7E",
       text = "Buy me a coffee",
       bg_color = '#FFDD00',
    #    emoji = "🍺",
       floating=False, width=220)




