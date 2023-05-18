import pandas as pd
import numpy as np
import streamlit as strl

from streamlit_extras.buy_me_a_coffee import button
from streamlit_extras.badges import badge

from datetime import date, timedelta
import datetime

from functions import plot_graphsV2, aws_crypto_api

#Sets page configuration
strl.set_page_config(layout="wide", page_title="BTC metrics - Sentiment", page_icon = "📊")

# Title
strl.image("sentiment_strip.png", use_column_width = True)
strl.write("Have you found this useful? Consider donating - BTC: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34 or buy me a beer https://bmc.link/juandavid7E" )

# Summary
strl.markdown("""---""")
strl.caption("Indicator powered by Alternative.me and Python Analytics")


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
df_meta = df_metadata[df_metadata["type"].isin(["Sentiment"])]

#Plots selected metrics
col_bounded, col_colored= strl.columns(2)

with col_bounded:
    strl.subheader("Oscillators thresholds")
    plot_graphsV2(df_data, df_meta, colored = False)

with col_colored:
    strl.subheader("Colored distribution")
    plot_graphsV2(df_data, df_meta, colored = True)

#Final comments
strl.markdown("""---""")
strl.write("Have you found this useful? Your donation will support our research and pave the way for innovative solutions.")

col1, col2, col3, col4 = strl.columns([1, 1, 4, 6])

with col1:
    badge(type="twitter", name="barbosa83")
with col2:
    badge(type="buymeacoffee", name="juandavid7E")
with col3:
    strl.caption("₿: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34")


