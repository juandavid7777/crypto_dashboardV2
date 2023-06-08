import streamlit as strl
import streamlit_authenticator as stauth

import yaml

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from email_validator import validate_email, EmailNotValidError

#Load config
def load_config():
    with open('.streamlit/config.yaml') as file:
        config = yaml.safe_load(file)
    return config

# Save the config.yaml file
def save_config(config):
    with open('.streamlit/config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

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

def sidebar_auth(authenticator):
    # If user is connected
           
    if strl.session_state["authentication_status"]:

        #Add logout button
        with strl.sidebar:
            strl.write(f'Welcome *{strl.session_state["name"]}*') 
            authenticator.logout('Logout', 'main', key='unique_key')

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

                    save_config(config)
                    strl.success('Entries updated successfully')

            except Exception as e:
                strl.error(e)

def auth_disconnected(authenticator, config):
    #If the user is not connected
    if strl.session_state["authentication_status"] != True:
       
        # User registration
        expander_registerUser= strl.expander(label='User Registration', expanded=False)
        with expander_registerUser:
            try:
                if authenticator.register_user('', preauthorization=True):

                    save_config(config)
                    strl.success('User registered successfully')

            except Exception as e:
                strl.error(e)

        # Forgot password
        expander_forgotPassword= strl.expander(label='Forgot Password', expanded=False)
        with expander_forgotPassword:
            try:
                username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('')
                if username_forgot_pw:

                    credentials_email(email_forgot_password, user_name = username_forgot_pw, new_password = random_password)
                    save_config(config)
                    strl.success('New password sent securely')

                else:
                    strl.error('Username not found')
            except Exception as e:
                strl.error(e)

        # Forgot username
        expander_forgotUsername= strl.expander(label='Forgot username', expanded=False)
        with expander_forgotUsername:
            try:
                username_forgot_username, email_forgot_username = authenticator.forgot_username('')
                if username_forgot_username:

                    credentials_email(email_forgot_username, user_name = username_forgot_username)
                    strl.success('Username sent securely')
                    
                else:
                    strl.error('Email not found')
            except Exception as e:
                strl.error(e)

def access_warning():
    if strl.session_state["authentication_status"] != True:
        strl.warning("To access our exclusive content please register or login to your free account.")