import pandas as pd
import numpy as np
import streamlit as strl

from functions import  plot_graphs, aws_crypto_api


strl.set_page_config(layout="wide", page_title="BTC metrics - Technical", page_icon = "📈")

# Title
strl.image("technical_strip.png", use_column_width = True)
strl.write("Have you found this useful? Consider donating - BTC: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34")
# strl.markdown('<b style="color:darkgoldenrod ; font-size: 44px">Technical</b>', unsafe_allow_html=True)

# Summary
strl.markdown("""---""")
strl.caption("Customized indicator powered by Glassnode")

aws_api_url = strl.secrets["aws_api_url"]
api_key = strl.secrets["aws_api_token"]
metric = "Metadata"
price_bool = False
normalize_bool = False


df_metadata = aws_crypto_api(aws_api_url, metric, price_bool, normalize_bool, api_key)

strl.write(df_metadata)

df_thresholds = pd.read_csv("thresholds.csv")
df_meta = df_thresholds[df_thresholds["type"].isin(["Technical"])]

col_bounded, col_colored= strl.columns(2)

with col_bounded:
    strl.subheader("Oscillators thresholds")
    plot_graphs(df_meta, colored = False)

with col_colored:
    strl.subheader("Colored distribution")
    plot_graphs(df_meta, colored = True)
