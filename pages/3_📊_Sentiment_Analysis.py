import pandas as pd
import numpy as np
import streamlit as strl


from functions import plot_graphs

strl.set_page_config(layout="wide", page_title="BTC metrics - Sentiment", page_icon = "📊")

# Title
strl.image("sentiment_strip.png", use_column_width = True)
strl.write("Have you found this useful? Consider donating - BTC: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34")
# strl.markdown('<b style="color:darkgoldenrod ; font-size: 44px">Sentiment</b>', unsafe_allow_html=True)

# Summary
strl.markdown("""---""")
strl.caption("Powered by Alternative.me")

df_thresholds = pd.read_csv("thresholds.csv")
df_meta = df_thresholds[df_thresholds["type"].isin(["Sentiment"])]

col_bounded, col_colored= strl.columns(2)

with col_bounded:
    strl.subheader("Oscillators thresholds")
    plot_graphs(df_meta, colored = False)

with col_colored:
    strl.subheader("Colored distribution")
    plot_graphs(df_meta, colored = True)


