import pandas as pd
import numpy as np
import streamlit as strl
import streamlit_authenticator as stauth

from streamlit_extras.buy_me_a_coffee import button
from streamlit_extras.badges import badge
from streamlit_extras.colored_header import colored_header

from datetime import date, timedelta
import datetime

from functions import aws_crypto_api, colored_metric, bounded_metric, bull_bear_classifier, ML_date_finder, ML_XY_dataselector, ML_model_traintest, ML_model_predict, ML_bull_bear_plot, soft_vote_ML, soft_vote_plot 
from functions_auth import sidebar_auth, load_config, access_warning

#Sets page configuration
strl.set_page_config(layout="wide", page_title="₿trends - Machine Learning", page_icon = "⚙️")

# Title
strl.image("ML.jpg", use_column_width = True)

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
strl.caption("Customized indicator powered by Python Analytics")

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
normalize_bool = True
df_data = aws_crypto_api(aws_api_url, metric, price_bool, normalize_bool, api_key,date_today)

# Machine learning--------------------------------------------------------------    
#Creates columns and sets buttons
# strl.header("Machine learning")
col_MLinputs, col_MLgraphs = strl.columns([1, 3])

with col_MLinputs:
    strl.subheader("Select features:")
    
    #Creates metrics buttons to select
        #Technical
    strl.write("Technical")
    varML_timechannel = strl.checkbox('Time channel', key = 'Time channel_ML', value = True)
    varML_MAlograt = strl.checkbox('MA log rat', key = 'MA log rat_ML', value = True)

        #Onchain
    strl.write("On-chain")
    varML_nupl = strl.checkbox('NUPL', key = 'NUPL_ML', value = True)
    varML_mvrvz = strl.checkbox('MVRV-Z', key = 'MVRV-Z_ML', value = True)
    varML_puellmultiple = strl.checkbox('Puell Multiple', key = 'Puell Multiple_ML', value = True)
    varML_thermocap = strl.checkbox('Thermocap rat.', key = 'Thermocap rat._ML', value = True)
    varML_supplyprofit = strl.checkbox('Supply in profit', key = 'Supply in profit_ML', value = True)

        #Sentiment
    strl.write("Sentiment")
    varML_fg = strl.checkbox('Fear and Greed', key = 'Fear and Greedl_ML', value = False)
    varML_fgMA = strl.checkbox('Fear and Greed MA', key = 'Fear and Greed MA_ML', value = False)

    strl.markdown("""---""")

#Defines metrics to create average
dict_varML_bool = {"NUPL":varML_nupl,
                 'MVRV-Z':varML_mvrvz,
                 'Puell Multiple':varML_puellmultiple,
                 'Thermocap rat.':varML_thermocap,
                 'Supply in profit':varML_supplyprofit,
                 'Time channel':varML_timechannel,
                 'MA log rat':varML_MAlograt,
                 'Fear and Greed':varML_fg,
                 'Fear and Greed MA':varML_fgMA
                 }

#Creates a list of variables that are selected true
selected_variables = []
for metric in dict_varML_bool:

    if dict_varML_bool[metric] == True:
        selected_variables.extend([metric])

#Defines inputs for Machine learning
    #Defines bear bull periods (Y variable)
bull_bear_map = ["17 07 2010 bot bull",
                "08 06 2011 top bear",
                "18 11 2011 bot bull",
                "09 04 2013 top bear",
                "06 07 2013 bot bull",
                "04 12 2013 top bear",
                "14 01 2015 bot bull",
                "16 12 2017 top bear",
                "15 12 2018 bot bull",
                # "26 06 2019 top bear",#COVID as black swan
                # "12 03 2020 bot bull",#COVID as black swan
                "13 04 2021 top bear",
                "20 07 2021 bot bull",
                # "08 11 2021 top bear",#Max data mapped within y variable
                ]

    #Maps the bear bull periods in the data frame (Y variable)
df_classified = bull_bear_classifier(df_data,bull_bear_map)

    #Defines analysis dates
start_date = ML_date_finder(df_classified, selected_variables)
end_date = "2021-07-20" # Comes from the max variable mapped in the classification

ts_start = datetime.datetime.strptime(start_date,'%Y-%m-%d')
ts_end = datetime.datetime.strptime(end_date,'%Y-%m-%d')
ts_mid_init = ts_start + (ts_end-ts_start)*3/5

    #Time slider for input
with col_MLinputs:
    strl.subheader("Select date to split data")    
    ts_mid = strl.slider("Training/Test split date",
                                    value = ts_mid_init,
                                    min_value = ts_start,
                                    max_value = ts_end
                                    )
    
    #Changes datetime input into string with correct format
    mid_date = ts_mid.strftime("%Y-%m-%d")

with col_MLgraphs:
    # strl.subheader("Single model classification")

    expander_MLSingleModel = strl.expander(label='Classify with single model vote', expanded=False)
    with expander_MLSingleModel:   
        model_type = strl.selectbox('Machine learning model type',
                                    ("Neural Network",'Random Forest', "Decision Tree", 'Support Vector Machine', 'K-NN', 'Naive Bayes', "Logistic Regression"))
                   
#Splits the data
X_train, y_train, X_test, y_test, split_dates_list = ML_XY_dataselector(df_classified, selected_variables, "bull_bear", start_date, mid_date, end_date)

start_date = split_dates_list[0]
mid_date = split_dates_list[1]
end_date = split_dates_list[2]

#Trains the model
model, accuracy, accuracy_all = ML_model_traintest(X_train, y_train, X_test, y_test, mod_type = model_type)

# Uses the model with new data to predict 
df_new = ML_model_predict(model, df_classified, selected_variables, start_date)

with col_MLgraphs:

    with expander_MLSingleModel:
        #Plots prediction
        title = model_type + " confidence: " + str(round((accuracy*100), 2)) + " %"
        access_warning()
        strl.plotly_chart(ML_bull_bear_plot(df_new, start_date, mid_date, end_date, title, interactive = render), use_container_width=True, config = render_config)

    # strl.markdown("""---""")
    #Soft voting area ============================
    # strl.subheader("Soft voting algorithm")

    expander_soft_vote= strl.expander(label='Classify with multiple models vote', expanded=True)
    with expander_soft_vote:  
        #Soft vote estimation
        model_type_list = strl.multiselect('Select voting models',
                                        ["Neural Network",'Random Forest', "Decision Tree", 'Support Vector Machine', 'K-NN', 'Naive Bayes', "Logistic Regression", ],
                                        ["Neural Network",'Random Forest', 'Support Vector Machine', 'K-NN', "Logistic Regression", ])
        
        conf_threshold = strl.number_input('Confidence threshold for acceptance (%)', min_value = 50, max_value = 100, value = 85, help = "Defines the value under which the vote is discarded due to reduced consensus in all the voting models. It defines an area where the algorithm accuracy is too low to take any action according to our chosen preferences.")

        rolling_window = strl.number_input('Days in rolling voting window', min_value = 1, max_value = 90, value = 7, help = "Defines the time window where all the votes are averaged together. Bigger windows will show smoother data, but will suffer from a bigger time lag from the market events.")
        strl.caption("Number of votes on a single day is equal to the votes for all the models for each day in the rolling window: nos.models x nos.daysWindow = " + str(len(model_type_list)* rolling_window) + " votes.")

        #Creates soft vote df
        df_soft_vote, df_accuracy = soft_vote_ML(df_classified, selected_variables, model_type_list, start_date, mid_date, end_date, rolling_vote_window = rolling_window)

        #Plots soft vote
        access_warning()
        strl.plotly_chart(soft_vote_plot(df_soft_vote, start_date, mid_date, end_date, conf_threshold = conf_threshold/100, interactive = render), use_container_width=True, config = render_config)

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