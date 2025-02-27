from connection import mycon
import streamlit as st
import random as rd
from datetime import date
import re
import time

conn = mycon()
cur = conn.cursor(buffered=True)

menu = ["-select-", "Transaction", "Balance", "Create User"]
choice = st.sidebar.selectbox("Selection", menu)

if "show_create_user" not in st.session_state:
    st.session_state["show_create_user"] = False

def create_user():
    st.title("Registration Form")
    st.image('sbi.png')

    account_num = rd.randint(100000, 999999)
    entered_name = st.text_input("Name: ", key="name_input")
    contact_number = st.text_input("Primary Mobile: ", key="mobile_input")
    address = st.text_input("Address: ", key="address_input")
    email = st.text_input("Email:", key="email_input")
    amount = st.text_input("Provide your opening amount:", key="amount_input")
    selected_date = st.date_input("Select a Date", value=date.today(), key="date_input")

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if st.button("Create"):
        if not entered_name or not contact_number or not email or not amount:
            st.error("All fields except Address are required!")
            return
        if not re.match(email_pattern, email):
            st.error("Invalid Email! Please enter a valid email address.")
            return
        try:
            amount = int(amount)
            if amount < 0:
                st.error("Amount cannot be negative!")
                return
        except ValueError:
            st.error("Please enter a valid numeric amount!")
            return
        try:
            query = "CALL create_client(%s,%s,%s,%s,%s,%s,%s)"
            values = (entered_name, contact_number, address, email, amount, selected_date, account_num)
            cur.execute(query, values)

            while cur.nextset():
                pass  

            conn.commit()
            st.success(f"Account successfully created! Username: {entered_name}, Account Number: {account_num}. Please take a screenshot for future reference.")
            time.sleep(25)
            st.session_state["show_create_user"] = False
            st.session_state["menu_selection"] = "-select-"  
            time.sleep(2)
            st.rerun()
        except Exception as e:
            while cur.nextset():
                pass  
            conn.rollback()
            st.error(f"An error occurred: {e}")

if choice == "Balance":
    st.image('sbi.png')
    s_acc = st.text_input("Enter Account Number:", key="s_acc")
    if s_acc:
        try:
            new_s_acc = int(s_acc)
            cur.execute("CALL new_select(%s)", (new_s_acc,))
            result = cur.fetchone()

            while cur.nextset():
                pass  

            if result:
                name = result[1]
                bal = result[5]
            else:
                name = "Unknown"
                bal = "N/A"
            if st.button("Check"):
                if result is None:
                    st.error("User Not Found")
                    time.sleep(2)
                    st.success("Below is your Registration form. We will be happy to have you.")
                    time.sleep(2)
                    st.session_state["show_create_user"] = True
                    st.rerun()
                else:
                    st.success("Processing...")
                    time.sleep(2)
                    st.success(f"Dear Customer, {name}, Your Account Balance is ₹{bal}")
        except Exception as e:
            while cur.nextset():
                pass  
            st.error(f"An error occurred: {e}")

def transaction():
    sender = st.text_input("Sender Account", key="sender")
    receiver = st.text_input("Receiver Account", key="receiver")
    amount = st.text_input("Enter Amount", key="trans_amount")
    if st.button("Pay"):
        try:
            cur.execute("CALL transaction_py(%s,%s,%s)", (sender, receiver, amount))

            while cur.nextset():
                pass  

            conn.commit()
            st.success("Payment Successful!")
        except Exception as e:
            while cur.nextset():
                pass  
            conn.rollback()
            st.error(f"Transaction failed: {e}")

if choice == "Transaction":
    transaction()

if choice == "-select-":
    st.markdown(
        """
        <style>
            .centered-text {
                text-align: center;
                color: blue;
                font-size: 50px;
                font-weight: bold;
            </style>
        <h1 class="centered-text">SBI</h1>
        """,
        unsafe_allow_html=True
    )
    st.image("sbi.png", width=700)

if choice == "Create User":
    create_user()
else:
    st.session_state["show_create_user"] = False
