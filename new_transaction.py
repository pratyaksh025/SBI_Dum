from connection import mycon
import streamlit as st
import random as rd
from datetime import date
import re
import time

hide_menu = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

conn = mycon()
cur = conn.cursor(buffered=True)

menu = ["-select-", "Transaction", "Balance", "Create User"]
choice = st.sidebar.selectbox("Selection", menu)

if "show_create_user" not in st.session_state:
    st.session_state["show_create_user"] = False

def create_user():
    st.title("Registration Form")

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
            amount = int(amount)  # Convert amount to integer

            # Start a transaction
            cur.execute("START TRANSACTION")

            # Fetch sender's balance
            cur.execute("SELECT balance FROM transaction WHERE account_number = %s", (sender,))
            result = cur.fetchone()

            if not result:
                st.error("Sender account not found.")
                cur.execute("ROLLBACK")
                return

            sender_balance = result[0]

            # Check for sufficient balance
            if amount > sender_balance:
                st.error("Insufficient balance.")
                cur.execute("ROLLBACK")
                return

            # Deduct amount from sender
            cur.execute("UPDATE transaction SET balance = balance - %s WHERE account_number = %s", (amount, sender))

            # Add amount to receiver
            cur.execute("UPDATE transaction SET balance = balance + %s WHERE account_number = %s", (amount, receiver))

            # Commit transaction
            cur.execute("COMMIT")
            st.success("Payment Successful!")

        except ValueError:
            st.error("Invalid amount. Please enter a numeric value.")
        except Exception as e:
            cur.execute("ROLLBACK")
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

if choice == "Create User":
    create_user()
else:
    st.session_state["show_create_user"] = False
    if choice == "-select-":
        st.markdown(
            """
            <style>
                .centered-text {
                    text-align: center;
                    color: #1a73e8;
                    font-size: 50px;
                    font-weight: bold;
                    animation: fadeIn 2s ease-in-out;
                }
                @keyframes fadeIn {
                    0% { opacity: 0; }
                    100% { opacity: 1; }
                }
                .sub-text {
                    text-align: center;
                    color: #1a73e8;
                    font-size: 20px;
                    font-weight: bold;
                    animation: slideIn 2s ease-in-out;
                }
                @keyframes slideIn {
                    0% { transform: translateY(20px); opacity: 0; }
                    100% { transform: translateY(0); opacity: 1; }
                }
            </style>
            <h1 class="centered-text">Welcome to SBI</h1>
            <p class="sub-text">Your trusted banking partner</p>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <style>
                .button-container {
                    display: flex;
                    justify-content: center;
                    margin-top: 20px;
                }
                .custom-button {
                    background-color: #1a73e8;
                    color: white;
                    padding: 10px 20px;
                    font-size: 20px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }
                .custom-button:hover {
                    background-color: #0c5bbf;
                }
            </style>
            <div class="button-container">
                <button class="custom-button" onclick="window.location.href='/C:/Users/PC-6/Desktop/bank/new_transaction.py?choice=Create%20User'">Get Started</button>
            </div>
            """,
            unsafe_allow_html=True
        )
