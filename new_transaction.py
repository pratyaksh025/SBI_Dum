from connection import mycon
import bcrypt as b
import streamlit as st
import random as rd
from datetime import date
import re
import time

def hide_menu():
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

def connect_db():
    conn = mycon()
    return conn, conn.cursor(buffered=True)

def login_page():
    st.markdown("<h1 style='color: blue; text-align: center;'>SBI Login Page</h1>", unsafe_allow_html=True)
    st.image("sbi.png", width=800)
    user = st.text_input("Enter your username")
    pasw = st.text_input("Enter your password", type="password")
    
    if st.button("Login"):
        conn, cur = connect_db()
        cur.execute("SELECT pass FROM full_client WHERE client_name = %s", (user,))
        result = cur.fetchone()

        if result is None:
            st.error("User not found! Redirecting to registration...")
            time.sleep(2)
            st.session_state["menu_selection"] = "Create User"
            st.rerun()
        else:
            stored_pass = result[0]
            if b.checkpw(pasw.encode(), stored_pass):
                st.success("Login Successful!")
                st.session_state.update({"logged_in": True, "username": user, "is_admin": user == "admin", "menu_selection": "Home-page"})
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid Password!")
    st.write("###")
    st.markdown("<h2 style='color: blue; text-align: center;'>We Connect People</h2>", unsafe_allow_html=True)

def logout():
    st.session_state.clear()
    st.success("Logged out successfully!")
    time.sleep(1)
    st.rerun()

def front_page():
    st.title("SBI Bank")
    st.image("sbi.png", width=800)
    if st.button("Logout"): logout()

def balance_check():
    st.title("Balance Check")
    s_acc = st.text_input("Enter Account Number:")
    
    if s_acc and st.button("Check"):
        conn, cur = connect_db()
        cur.execute("SELECT account_holder_name ,balance FROM transaction WHERE account_number = %s", (s_acc,))
        result = cur.fetchone()
        
        if result:
            st.success(f"Dear {result[0]}, Your Account Balance is ₹{result[1]}")
        else:
            st.error("User Not Found")
            time.sleep(1)
            st.session_state["menu_selection"] = "Create User"
            st.rerun()

def transaction():
    st.title("Transaction")
    sender = st.text_input("Sender Account")
    receiver = st.text_input("Receiver Account")
    amount = st.text_input("Enter Amount")
    
    if st.button("Pay"):
        try:
            conn, cur = connect_db()
            cur.execute("SELECT balance FROM transaction WHERE account_number = %s", (sender,))
            sender_balance = cur.fetchone()
            
            if not sender_balance or int(amount) > sender_balance[0]:
                st.error("Insufficient funds or invalid account.")
                return
            
            cur.execute("UPDATE transaction SET balance = balance - %s WHERE account_number = %s", (amount, sender))
            cur.execute("UPDATE transaction SET balance = balance + %s WHERE account_number = %s", (amount, receiver))
            conn.commit()
            st.success("Transaction Successful!")
        except:
            conn.rollback()
            st.error("Transaction Failed!")

def menu():
    is_admin = st.session_state.get("is_admin", False)
    menu_options = ["Home-page", "Balance", "Transaction"]
    if is_admin:
        menu_options.append("Create User")
    return st.sidebar.selectbox("Menu", menu_options)

def main():
    hide_menu()
    
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        login_page()
    else:
        choice = menu()
        if choice == "Home-page": front_page()
        elif choice == "Balance": balance_check()
        elif choice == "Transaction": transaction()
        elif choice == "Create User" and st.session_state.get("is_admin", False): create_user()

main()
