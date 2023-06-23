import streamlit as strl
import streamlit_authenticator as stauth
from streamlit_extras.switch_page_button import switch_page
from st_files_connection import FilesConnection

import yaml
import json
import boto3
import os

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from email_validator import validate_email, EmailNotValidError

#Load config
@strl.cache_data
def load_config():
    
     # Create connection object and retrieve file contents.
    conn = strl.experimental_connection('s3', type=FilesConnection)
    json_config = conn.read(strl.secrets["BUCKET"]+"/config.json", input_format = "json", ttl=600)
    
    #Saves config info as yaml
    with open('.streamlit/config.yaml', 'w') as yaml_file:
        yaml.dump(json_config, yaml_file)

    return json_config

# Save the config.yaml file
def save_config(config):
    with open('.streamlit/config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

    save_config_aws()
    print("AWS Userbase data updated")

def credentials_email(recipient_email, sender_email = "admin@bitcointrends.app", sender_password = "bizdjqedmqqiownf", user_name = None, new_password = None):
    
    # SMTP server configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Email content
    if new_password is None:
        subject = 'Secure Username Delivery'
        body = f'Hi, \n \n Thanks for using the credentials recovery from Bitcointrends.app \n The username associated with this email is: {user_name}'

    else:
        subject = 'Secure Password Delivery'
        body = f'Hi, \n \n Thanks for using the credentials recovery from Bitcointrends.app \n The username associated with this email is: {user_name} \n Your temporary password is: {new_password} \n Please log in to your account and change the temporary password for a new one.'

    # Create a multipart email message
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient_email

    # Attach the email body as plain text
    message.attach(MIMEText(body, 'plain'))

    try:
        # Establish a secure connection to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        # Login to the SMTP server
        server.login(sender_email, sender_password)
        # Send the email
        server.sendmail(sender_email, recipient_email, message.as_string())
        # Close the SMTP connection
        server.quit()
        print('Email sent successfully.')
  
    except Exception as e:
        print(f'Error occurred while sending the email: {e}')

# # Example usage
# sender_email = 'bitcointrends.app@gmail.com'
# sender_password = "hqvstxhwmsiejvuu"
# recipient_email = 'juandavid7777@gmail.com'
# send_password_email(sender_email, sender_password, recipient_email)

def validate_useremail(email):

    try:

        # Check that the email address is valid. Turn on check_deliverability
        # for first-time validations like on account creation pages (but not
        # login pages).
        emailinfo = validate_email(email, check_deliverability=True)

        # After this point, use only the normalized form of the email address,
        # especially before going to a database query.
        email = emailinfo.normalized
        
        message = "Successful email {" + email + "} validation"
        
        return email, True, message,

    except EmailNotValidError as e:

        # The exception message is human-readable explanation of why it's
        # not a valid (or deliverable) email address.
        
        message = str(e)
        
        return email, False, message,
    
# #Usage    
# email = "admin$,$s@bitcointrends.appa"    
# validate_useremail(email)

def sidebar_auth(auth_out = False):

    # Load the config.yaml file
    config = load_config()

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
                                        )

    # If user is connected     
    if strl.session_state["authentication_status"]:

        #Add logout button
        with strl.sidebar:
            strl.write(f'Welcome *{strl.session_state["name"]}*') 
            authenticator.logout('Logout', 'main', key='unique_key')

    else:
        login_button = strl.sidebar.button("Login")
        if login_button:
            switch_page("Account-Login")

    if auth_out == True:
        return authenticator, config

def auth_connected(authenticator, name, authentication_status, username, config):

    #Passsword reset
    expander_resetPassword= strl.expander(label='Reset password', expanded=False)
    with expander_resetPassword:
        if authentication_status:
            try:
                if authenticator.reset_password(username, 'Reset Password'):
                    
                    save_config(config)
                    strl.success('Password modified successfully')

            except Exception as e:
                strl.error(e)

    #Update user details
    expander_updateUser= strl.expander(label='Update user details', expanded=False)
    with expander_updateUser:
        if authentication_status:
            try:
                if authenticator.update_user_details(username, 'Update user details'):

                    strl.success('Entries updated successfully')
                    save_config(config)
                    
            except Exception as e:
                strl.error(e)

def auth_disconnected(authenticator, config):
    #If the user is not connected
    if strl.session_state["authentication_status"] != True:
       
        # User registration
        expander_registerUser= strl.expander(label='User Registration', expanded=False)
        with expander_registerUser:
            try:
                if authenticator.register_user('', preauthorization=False):

                    strl.success('User registered successfully')
                    save_config(config)
                    
            except Exception as e:
                strl.error(e)

        # Forgot password
        expander_forgotPassword= strl.expander(label='Forgot Password', expanded=False)
        with expander_forgotPassword:
            try:
                username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('')
                if username_forgot_pw:

                    strl.success('New password sent securely')
                    credentials_email(email_forgot_password, user_name = username_forgot_pw, new_password = random_password)
                    save_config(config)
                    
                else:
                    
                    if username_forgot_pw in config["credentials"]["usernames"].keys(): 
                        strl.info('Valid username')
                    
                    elif username_forgot_pw == None:
                        # strl.info('Valid username')
                        pass

                    else:
                        strl.error('Username not found')
            except Exception as e:
                strl.error(e)

        # Forgot username
        expander_forgotUsername= strl.expander(label='Forgot username', expanded=False)
        with expander_forgotUsername:
            try:
                username_forgot_username, email_forgot_username = authenticator.forgot_username('')
                strl.write(email_forgot_username, 1) 
                # strl.write(config["credentials"][username_forgot_username]["email"], 2)
                if username_forgot_username:

                    strl.success('Username sent securely to registered email')
                    credentials_email(email_forgot_username, user_name = username_forgot_username)
                    
                else:
                    
                    if email_forgot_username == None:
                        strl.info('Please enter a valid email')
                        pass
                    else:
                        strl.error('Email not found: '+ email_forgot_username)

            except Exception as e:
                strl.error(e)

def access_warning():
    if strl.session_state["authentication_status"] != True:
        strl.warning("To access our exclusive content please register or login to your free account.")

def yaml_to_json():

    with open('.streamlit/config.yaml', 'r') as file:
        configuration = yaml.safe_load(file)

    with open('.streamlit/config.json', 'w') as json_file:
        json.dump(configuration, json_file)
        
    print("yaml converted to json")

def json_to_yaml():
    with open('.streamlit/config.json', 'r') as file:
        configuration = json.load(file)

    with open('.streamlit/config.yaml', 'w') as yaml_file:
        yaml.dump(configuration, yaml_file)

    print("yaml converted to json")

def save_config_aws():

    #Saves config back to json
    yaml_to_json()
    #Loads config file to aws
    #Sets AWS client connection
    s3 = boto3.client(
            service_name="s3",
            region_name= strl.secrets["AWS_DEFAULT_REGION"],
            aws_access_key_id=strl.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=strl.secrets["AWS_SECRET_ACCESS_KEY"],
        )

    name_file = "config.json"
    bucket = strl.secrets["BUCKET"]

    s3.upload_file(
        Filename = ".streamlit/config.json",
        Bucket = bucket,
        Key = name_file
    )

    # from streamlit import caching
    strl.cache_data.clear()
    strl.experimental_rerun()
    
    os.remove(".streamlit/config.json") 
