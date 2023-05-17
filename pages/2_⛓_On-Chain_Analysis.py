import pandas as pd
import numpy as np
import streamlit as strl


from functions import plot_graphsV2, aws_crypto_api

#Sets page configuration
strl.set_page_config(layout="wide", page_title="BTC metrics - On Chain", page_icon = "⛓")

# Title
strl.image("onchain_strip.png", use_column_width = True)
strl.write("Have you found this useful? Consider donating - BTC: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34")

# Summary
strl.markdown("""---""")

#Sets API general parameters
aws_api_url = strl.secrets["aws_api_url"]
api_key = strl.secrets["aws_api_token"]

#Calls metadata
metric = "Metadata"
price_bool = False
normalize_bool = False
df_metadata = aws_crypto_api(aws_api_url, metric, price_bool, normalize_bool, api_key)

#Calls all data
metric = "All"
price_bool = True
normalize_bool = False
df_data = aws_crypto_api(aws_api_url, metric, price_bool, normalize_bool, api_key)

#Filters metadata to select metrics
df_meta = df_metadata[df_metadata["type"].isin(["Onchain"])]

#Plots selected metrics
col_bounded, col_colored= strl.columns(2)

with col_bounded:
    strl.subheader("Oscillators thresholds")
    plot_graphsV2(df_data, df_meta, colored = False)

with col_colored:
    strl.subheader("Colored distribution")
    plot_graphsV2(df_data, df_meta, colored = True)