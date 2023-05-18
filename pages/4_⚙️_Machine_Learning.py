import pandas as pd
import numpy as np
import streamlit as strl

from datetime import date, timedelta
import datetime

from functions import aws_crypto_api, colored_metric, bounded_metric, bull_bear_classifier, ML_date_finder, ML_XY_dataselector, ML_model_traintest, ML_model_predict, ML_bull_bear_plot 

#Sets page configuration
strl.set_page_config(layout="wide", page_title="BTC metrics - Machine Learning", page_icon = "⚙️")

# Title
strl.image("ML.jpg", use_column_width = True)
strl.write("Have you found this useful? Consider donating - BTC: 3EbH7JPSTGqSzyKKAijgva1ffXaY6JWk34 or buy me a beer https://bmc.link/juandavid7E" )

# Summary
strl.markdown("""---""")
strl.caption("Customized indicator powered by Python Analytics")

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

#Creates columns and sets buttons
col_buttons, col_graphs = strl.columns([1, 3])

with col_buttons:

    strl.header("Confluence risk")

    #Creates metrics buttons to select
        #Technical
    strl.subheader("Technical")
    var_timechannel = strl.checkbox('Time channel', value = True)
    var_MAlograt = strl.checkbox('MA log rat', value = True)

        #Onchain
    strl.subheader("On-chain")
    var_nupl = strl.checkbox('NUPL', value = True)
    var_mvrvz = strl.checkbox('MVRV-Z', value = True)
    var_puellmultiple = strl.checkbox('Puell Multiple', value = True)
    var_thermocap = strl.checkbox('Thermocap rat.', value = True)
    var_supplyprofit = strl.checkbox('Supply in profit', value = True)

        #Sentiment
    strl.subheader("Sentiment")
    var_fg = strl.checkbox('Fear and Greed', value = True)
    var_fgMA = strl.checkbox('Fear and Greed MA', value = True)

#Defines metrics to create average
dict_var_bool = {"NUPL":var_nupl,
                 'MVRV-Z':var_mvrvz,
                 'Puell Multiple':var_puellmultiple,
                 'Thermocap rat.':var_thermocap,
                 'Supply in profit':var_supplyprofit,
                 'Time channel':var_timechannel,
                 'MA log rat':var_MAlograt,
                 'Fear and Greed':var_fg,
                 'Fear and Greed MA':var_fgMA
                 }

#Creates a list of variables that are selected true
selected_cols_list = []
for metric in dict_var_bool:

    if dict_var_bool[metric] == True:
        selected_cols_list.extend([metric])

#Estimates average risk of selected columns
df_data['Confluence risk'] = df_data[selected_cols_list].mean(axis=1)

with col_graphs:

    #reports latest value
    last_cfrisk = df_data['Confluence risk'].iloc[-1]
    strl.header("Latest value: " + str(round(last_cfrisk,4)*100) + "%")

    # Plots   
    strl.plotly_chart(colored_metric(df_data, "Confluence risk", ".1%"), use_container_width=True)
    strl.plotly_chart(bounded_metric(df_data,"Confluence risk", [0,0.25, 0.75, 1], metric_format = ".1%", log_scale = False), use_container_width=True)


strl.markdown("""---""")

# Machine learning--------------------------------------------------------------    
#Creates columns and sets buttons
col_MLinputs, col_MLgraphs = strl.columns([1, 3])

with col_MLinputs:

    strl.header("Machine learning")
    
    #Creates metrics buttons to select
        #Technical
    strl.subheader("Technical")
    varML_timechannel = strl.checkbox('Time channel', key = 'Time channel_ML', value = True)
    varML_MAlograt = strl.checkbox('MA log rat', key = 'MA log rat_ML', value = True)

        #Onchain
    strl.subheader("On-chain")
    varML_nupl = strl.checkbox('NUPL', key = 'NUPL_ML', value = True)
    varML_mvrvz = strl.checkbox('MVRV-Z', key = 'MVRV-Z_ML', value = True)
    varML_puellmultiple = strl.checkbox('Puell Multiple', key = 'Puell Multiple_ML', value = True)
    varML_thermocap = strl.checkbox('Thermocap rat.', key = 'Thermocap rat._ML', value = True)
    varML_supplyprofit = strl.checkbox('Supply in profit', key = 'Supply in profit_ML', value = True)

        #Sentiment
    strl.subheader("Sentiment")
    varML_fg = strl.checkbox('Fear and Greed', key = 'Fear and Greedl_ML', value = False)
    varML_fgMA = strl.checkbox('Fear and Greed MA', key = 'Fear and Greed MA_ML', value = False)

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
    strl.markdown("""---""")    
    ts_mid = strl.slider("Training/Test split date",
                                    value = ts_mid_init,
                                    min_value = ts_start,
                                    max_value = ts_end
                                    )
    
    #Changes datetime input into string with correct format
    mid_date = ts_mid.strftime("%Y-%m-%d")
    
    model_type = strl.selectbox('Machine learning model type',
                                ('Random Forest', "Decision tree", 'Support Vector Machine', 'K-NN', 'Naive Bayes', "Logistic regression"))
                   
#Splits the data
X_train, y_train, X_test, y_test, split_dates_list = ML_XY_dataselector(df_classified, selected_variables, "bull_bear", start_date, mid_date, end_date)

start_date = split_dates_list[0]
mid_date = split_dates_list[1]
end_date = split_dates_list[2]

#Trains the model
model, accuracy = ML_model_traintest(X_train, y_train, X_test, y_test, mod_type = model_type)


# Uses the model with new data to predict 
df_new = ML_model_predict(model, df_classified, selected_variables, start_date)

with col_MLgraphs:

    #Reports accuracy
    strl.header("Mapping accuracy: " + str(round((accuracy*100), 2))  + "%")

    #Plots prediction
    strl.plotly_chart(ML_bull_bear_plot(df_new, start_date, mid_date, end_date, model_type), use_container_width=True)