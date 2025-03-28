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
    st.markdown("<h1 style='text-align: center;'>SBI Bank</h1>", unsafe_allow_html=True)
    st.image("sbi.png", width=200, use_container_width=True)
    st.markdown("<h2 style='text-align: center;'>Welcome to the State Bank of India. We are here to serve you.</h2>", unsafe_allow_html=True)
    conn, cur = connect_db()
    cur.execute("SELECT * FROM full_client WHERE client_name = %s", (st.session_state["username"],))
    user_details = cur.fetchone()
    
    if user_details:
        st.write(f"Welcome {user_details[1]}!")
        st.write(f"Account Number: {user_details[7]}")
        st.write(f"Email: {user_details[4]}")
        st.write(f"Phone: {user_details[2]}")
        st.write(f"Address: {user_details[3]}")
    else:
        st.error("User details not found.")
    if st.button("Logout"): logout()

def balance_check():
    st.title("Balance Check")
    conn, cur = connect_db()
    
    if st.session_state.get("is_admin", False):
        s_acc = st.text_input("Enter Account Number:")
        if s_acc and st.button("Check"):
            cur.execute("select * from full_client where account_no=(%s)", (s_acc,))
            result = cur.fetchone()
            if result:
                st.success(f"Dear {result[1]}, Your Account Balance is ₹{result[5]}")
            else:
                st.error("User Not Found")
    else:
        s_acc = st.text_input("Enter Account Number:")
        if s_acc and st.button("Check"):
            cur.execute("select * from full_client where client_name=(%s) and account_no=(%s)", (st.session_state["username"],s_acc))
            result = cur.fetchone()
            if result:
                st.success(f"Dear {result[1]}, Your Account Balance is ₹{result[5]}")
            else:
                st.error("Balance details not found.")


def create_user():
    st.title("Registration Form")
    st.image("reg.png", width=250)

    account_num = rd.randint(100000, 999999)
    entered_name = st.text_input("Name:", key="name_input")
    contact_number = st.text_input("Primary Mobile:", key="mobile_input")
    address = st.text_input("Address:", key="address_input")
    email = st.text_input("Email:", key="email_input")
    password = st.text_input("Password:", type="password", key="password_input")
    amount = st.text_input("Provide your opening amount:", key="amount_input")
    selected_date = st.date_input("Select a Date", value=date.today(), key="date_input")

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 4])
    
    with col4:
        if st.button("Create Account"):  
            if not entered_name or not contact_number or not email or not password or not amount:
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
                conn= mycon()
                cur = conn.cursor(buffered=True)
                hashed_pw = b.hashpw(password.encode(), b.gensalt())
                query = "CALL create_client(%s,%s,%s,%s,%s,%s,%s,%s)"
                values = (entered_name, contact_number, address, email,  amount, selected_date, account_num, hashed_pw)
                cur.execute(query, values)
                conn.commit()
                
                while cur.nextset():
                    pass  # Clear any remaining results
                
                conn.commit()
                st.success(f"Account successfully created! Username: {entered_name}, Account Number: {account_num}. Please take a screenshot for future reference.")
                time.sleep(10)
                st.session_state["menu_selection"] = "login-Page"
                st.rerun()
            except Exception as e:
                while cur.nextset():
                    pass  # Clear any remaining results
                conn.rollback()
                st.error(f"An error occurred: {e}")

def delete_user():
    session_state = st.session_state
    if session_state.get("is_admin", False):
        st.title("Delete User")
        conn, cur = connect_db()
        cur.execute("SELECT client_name FROM full_client")
        users = [user[0] for user in cur.fetchall()]
        user_to_delete = st.selectbox("Select User to Delete", users)
        if st.button("Delete User"):
            cur.execute("DELETE FROM full_client WHERE client_name = %s", (user_to_delete,))
            conn.commit()
            st.success(f"User {user_to_delete} deleted successfully!")

def transaction():
    st.title("Transaction")
    conn= mycon()
    cur = conn.cursor(buffered=True)
    cur.execute("SELECT account_no,amount FROM full_client WHERE client_name = %s", (st.session_state["username"],))
    sender= cur.fetchone()[0]
    # sender_balance = cur.fetchone()[1]
    receiver = st.text_input("Receiver Account")
    transaction_amount = st.text_input("Enter transaction_amount")
    
    if st.button("Pay"):
        try:
            conn, cur = connect_db()
            cur.execute("SELECT amount FROM full_client WHERE account_no = %s", (sender,))
            sender_balance = cur.fetchone()
            
            if not sender_balance or int(transaction_amount) > sender_balance[0]:
                st.error("Insufficient funds or invalid account.")
                return
            
            cur.execute("UPDATE full_client SET amount = amount - %s WHERE account_no = %s", (transaction_amount, sender))
            cur.execute("UPDATE full_client SET amount = amount + %s WHERE account_no = %s", (transaction_amount, receiver))
            conn.commit()
            st.success(f"Transaction Successful! of ₹{transaction_amount}")
        except:
            conn.rollback()
            st.error("Transaction Failed!")

def edit_user():
    session_state = st.session_state

    if session_state.get("is_admin", False):
        st.title("Edit User")
        conn, cur = connect_db()

    
        cur.execute("SELECT client_name FROM full_client")
        users = [user[0] for user in cur.fetchall()]

        user_to_edit = st.selectbox("Select User to Edit", users, key="selected_user")
        

        if "edit_option" not in st.session_state:
            st.session_state.edit_option = "select"
        
        st.session_state.edit_option = st.selectbox("What is to be Updated", 
                                                    ["select", "Name", "Mobile", "Address", "Email", "Amount"], 
                                                    index=["select", "Name", "Mobile", "Address", "Email", "Amount"].index(st.session_state.edit_option))

        if st.session_state.edit_option == "Name":
            new_name = st.text_input("Enter New Name", key="new_name")
            if st.button("Update"):
                cur.execute("UPDATE full_client SET client_name = %s WHERE client_name = %s", 
                            (new_name, user_to_edit))
                conn.commit()
                st.success(f"User {user_to_edit} updated successfully!")
                st.session_state.edit_option = "select"  # Reset option after update

        elif st.session_state.edit_option == "Mobile":
            new_mobile = st.text_input("Enter New Mobile", key="new_mobile")
            if st.button("Update"):
                cur.execute("UPDATE full_client SET mobile = %s WHERE client_name = %s", 
                            (new_mobile, user_to_edit))
                conn.commit()
                st.success(f"User {user_to_edit} updated successfully!")
                st.session_state.edit_option = "select"

        elif st.session_state.edit_option == "Address":
            new_address = st.text_input("Enter New Address", key="new_address")
            if st.button("Update"):
                cur.execute("UPDATE full_client SET address = %s WHERE client_name = %s", 
                            (new_address, user_to_edit))
                conn.commit()
                st.success(f"User {user_to_edit} updated successfully!")
                st.session_state.edit_option = "select"

        elif st.session_state.edit_option == "Email":
            new_email = st.text_input("Enter New Email", key="new_email")
            if st.button("Update"):
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if re.match(email_pattern, new_email):
                    cur.execute("UPDATE full_client SET email = %s WHERE client_name = %s", 
                                (new_email, user_to_edit))
                    conn.commit()
                else:
                    st.error("Invalid Email! Please enter a valid email address.")
                    return
                
                st.success(f"User {user_to_edit} updated successfully!")
                st.session_state.edit_option = "select"

        elif st.session_state.edit_option == "Amount":
            new_amount = st.text_input("Enter New Amount", key="new_amount")
            if st.button("Update"):
                cur.execute("UPDATE full_client SET amount = %s WHERE client_name = %s", 
                            (new_amount, user_to_edit))
                conn.commit()
                st.success(f"User {user_to_edit} updated successfully!")
                st.session_state.edit_option = "select"


            

def menu():
    is_admin = st.session_state.get("is_admin", False)
    menu_options = ["Home-page", "Balance", "Transaction"]
    if is_admin:
        menu_options.append("Create User")
        menu_options.append("delete_user")
        menu_options.append("Edit User")
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
        elif choice == "Create User" and st.session_state.get("is_admin", False): 
            create_user()
        elif choice=="delete_user" and st.session_state.get("is_admin", False):
            delete_user()
        elif choice=="Edit User" and st.session_state.get("is_admin", False):
            edit_user()

main()
