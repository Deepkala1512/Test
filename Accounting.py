import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize session state to hold transaction data
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=['Date', 'Description', 'Amount', 'Category', 'Account', 'Debit/Credit'])

# Function to add a transaction (double-entry)
def add_transaction(date, description, amount, category, account, entry_type):
    # Determine debit or credit based on entry_type
    if entry_type == 'Debit':
        debit_credit = 'Debit'
        opposite = 'Credit'
    else:
        debit_credit = 'Credit'
        opposite = 'Debit'
    
    # Add two entries: one for debit and one for credit
    # Create the transaction entries
    transaction_entry_1 = {
        'Date': date,
        'Description': description,
        'Amount': amount,
        'Category': category,
        'Account': account,
        'Debit/Credit': debit_credit
    }
    
    # Let's decide the opposite account based on category
    if category in ['Income', 'Expense']:
        opposite_account = 'Equity'  # Income or Expense closes to Equity (Retained Earnings)
    elif category in ['Asset']:
        opposite_account = 'Liability'  # Asset increases with Debit, Liability decreases with Credit
    else:
        opposite_account = 'Asset'  # Liabilities are balanced by Asset
    
    transaction_entry_2 = {
        'Date': date,
        'Description': description,
        'Amount': amount,
        'Category': category,
        'Account': opposite_account,
        'Debit/Credit': opposite
    }
    
    # Convert both entries to DataFrame to concatenate
    transaction_df_1 = pd.DataFrame([transaction_entry_1])
    transaction_df_2 = pd.DataFrame([transaction_entry_2])
    
    # Concatenate the new transactions to the existing DataFrame
    st.session_state.transactions = pd.concat([st.session_state.transactions, transaction_df_1, transaction_df_2], ignore_index=True)

# Function to calculate P&L
def calculate_pnl():
    income = st.session_state.transactions[st.session_state.transactions['Account'] == 'Income']['Amount'].sum()
    expenses = st.session_state.transactions[st.session_state.transactions['Account'] == 'Expense']['Amount'].sum()
    pnl = income - expenses
    return income, expenses, pnl

# Function to generate Balance Sheet
def generate_balance_sheet():
    assets = st.session_state.transactions[st.session_state.transactions['Account'] == 'Asset']['Amount'].sum()
    liabilities = st.session_state.transactions[st.session_state.transactions['Account'] == 'Liability']['Amount'].sum()
    equity = assets - liabilities
    return assets, liabilities, equity

# Function to generate Trial Balance
def generate_trial_balance():
    # Pivot the data to get the debit and credit values per account
    trial_balance = pd.pivot_table(st.session_state.transactions, values='Amount', index='Account', columns='Debit/Credit', aggfunc='sum', fill_value=0)
    
    # If the columns 'Debit' or 'Credit' do not exist, create them as 0
    if 'Debit' not in trial_balance.columns:
        trial_balance['Debit'] = 0
    if 'Credit' not in trial_balance.columns:
        trial_balance['Credit'] = 0
    
    # Calculate the balance for each account
    trial_balance['Total'] = trial_balance['Debit'] - trial_balance['Credit']
    return trial_balance

# Streamlit app interface
def main():
    st.title('Restaurant Accounting System')

    # Section for entering transaction details
    st.header('Enter Transaction')
    
    # Transaction Details
    date = st.date_input('Transaction Date', datetime.today())
    description = st.text_input('Description')
    amount = st.number_input('Amount', min_value=0.01, step=0.01)
    category = st.selectbox('Category', ['Income', 'Expense', 'Asset', 'Liability'])
    
    # Define possible accounts based on category
    accounts_dict = {
        'Income': ['Food Sales', 'Beverage Sales', 'Catering Sales', 'Delivery Sales'],
        'Expense': ['Food Purchases', 'Beverage Purchases', 'Salaries/Wages', 'Rent', 'Utilities', 'Marketing', 'Depreciation'],
        'Asset': ['Cash', 'Accounts Receivable', 'Inventory'],
        'Liability': ['Accounts Payable', 'Loans', 'Accrued Expenses']
    }

    account = st.selectbox('Account', accounts_dict[category])
    entry_type = st.radio('Debit or Credit?', ['Debit', 'Credit'])

    if st.button('Add Transaction'):
        add_transaction(date, description, amount, category, account, entry_type)
        st.success(f'Transaction for {description} added!')

    # Displaying the transaction table
    st.header('Transaction History')
    st.dataframe(st.session_state.transactions)

    # Displaying the P&L
    st.header('Profit and Loss (P&L) Statement')
    income, expenses, pnl = calculate_pnl()
    st.write(f"Total Income: ₹{income}")
    st.write(f"Total Expenses: ₹{expenses}")
    st.write(f"Net Profit/Loss: ₹{pnl}")

    # Displaying the Balance Sheet
    st.header('Balance Sheet')
    assets, liabilities, equity = generate_balance_sheet()
    st.write(f"Total Assets: ₹{assets}")
    st.write(f"Total Liabilities: ₹{liabilities}")
    st.write(f"Equity: ₹{equity}")

    # Displaying the Trial Balance
    st.header('Trial Balance')
    trial_balance = generate_trial_balance()
    st.write(trial_balance)

if __name__ == '__main__':
    main()
