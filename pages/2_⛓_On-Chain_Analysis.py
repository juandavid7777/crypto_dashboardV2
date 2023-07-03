import pandas as pd
import numpy as np
import streamlit as strl
import streamlit_authenticator as stauth

from streamlit_extras.buy_me_a_coffee import button
from streamlit_extras.badges import badge
from streamlit_extras.colored_header import colored_header

from datetime import date, timedelta
import datetime

from functions import plot_graphsV2, aws_crypto_api
from functions_auth import sidebar_auth, load_config, access_warning
from functions_visual import clean_image
from functions_analytics import inject_ga

#Sets page configuration
strl.set_page_config(layout="wide", page_title="₿trends - On Chain", page_icon = "⛓")
inject_ga()
clean_image()

# Title
strl.image("onchain_plain.png", use_column_width = True)
strl.title("On-Chain Analysis: Bitcoin blockchain movements and distribution")

# Donations
strl.write("Unlock the potential of data science and bitcoin analysis to create a brighter financial future for all. Stay tunned, and keep accumulating!")
col1, col2, col3, col4 = strl.columns([1.5, 1.5, 5, 4])

with col1:
    badge(type="twitter", name="barbosa83")
with col2:
    badge(type="buymeacoffee", name="juandavid7E")
with col3:
    strl.caption("₿: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34")

# Summary
colored_header(label = "", description = "", color_name="yellow-80")
strl.caption("Indicator powered by Python Analytics")

#Adds side authenticator
sidebar_auth()

#Basic session rendering if connected
render_config = {'staticPlot': not(strl.session_state["authentication_status"]),
                 'displaylogo': False} 
render = strl.session_state["authentication_status"]

#Sets API general parameters
aws_api_url = strl.secrets["aws_api_url"]
api_key = strl.secrets["aws_api_token"]
date_today = datetime.datetime.now().strftime("%Y-%m-%d")

#Calls metadata
metric = "Metadata"
price_bool = False
normalize_bool = False
df_metadata = aws_crypto_api(aws_api_url, metric, price_bool, normalize_bool, api_key, date_today)

#Calls all data
metric = "All"
price_bool = True
normalize_bool = False
df_data = aws_crypto_api(aws_api_url, metric, price_bool, normalize_bool, api_key, date_today)

#Filters metadata to select metrics
df_meta = df_metadata[df_metadata["type"].isin(["Onchain"])]

#Plots selected metrics
col_bounded, col_colored= strl.columns(2)

with col_bounded:
    strl.subheader("Oscillators thresholds")
    access_warning()
    plot_graphsV2(df_data, df_meta, render, render_config, colored = False)

with col_colored:
    strl.subheader("Colored distribution")
    access_warning()
    plot_graphsV2(df_data, df_meta, render, render_config, colored = True)

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