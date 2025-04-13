import streamlit as st
import sqlite3
import pandas as pd

# Database setup
DB_NAME = "customers.db"

def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CustomerData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            income REAL,
            credit_score INTEGER,
            loan_amount REAL,
            loan_term_months INTEGER,
            debt_to_income_ratio REAL,
            employment_years INTEGER,
            previous_defaults INTEGER,
            loan_purpose TEXT,
            education_level TEXT,
            age INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_to_database(data):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CustomerData (
                income, credit_score, loan_amount, loan_term_months,
                debt_to_income_ratio, employment_years, previous_defaults,
                loan_purpose, education_level, age
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        conn.commit()
        conn.close()
        return "✅ Customer data saved successfully."
    except Exception as e:
        return f"❌ Error: {e}"

def fetch_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM CustomerData", conn)
    conn.close()
    return df

def delete_customer_by_id(customer_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CustomerData WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()

def predict_default(data):
    income, credit_score, loan_amount, loan_term, dti, employment_years, previous_defaults, *_ = data

    reasons = []
    if dti > 0.4:
        reasons.append("High Debt-to-Income Ratio")
    if credit_score < 650:
        reasons.append("Low Credit Score")
    if income < 40000:
        reasons.append("Low Income")
    if employment_years < 3:
        reasons.append("Short Employment History")
    if loan_amount > income * 0.4:
        reasons.append("High Loan Amount Relative to Income")
    if previous_defaults > 0:
        reasons.append("History of Previous Defaults")

    if reasons:
        return "❌ Likely to DEFAULT", reasons
    else:
        return "✅ Likely to PAY BACK", []

# Streamlit UI
def main():
    st.set_page_config(page_title="Loan Default Predictor", layout="centered")
    st.title("💰 Loan Default Predictor")

    st.markdown("Enter customer details below:")

    with st.form("customer_form"):
        income = st.number_input("Income (USD)", min_value=0.0)
        credit_score = st.number_input("Credit Score", min_value=300, max_value=850)
        loan_amount = st.number_input("Loan Amount (USD)", min_value=0.0)
        loan_term = st.number_input("Loan Term (Months)", min_value=1, max_value=360)
        dti = st.slider("Debt-to-Income Ratio", 0.0, 1.0, step=0.01)
        employment_years = st.number_input("Employment Years", min_value=0)
        previous_defaults = st.number_input("Previous Defaults", min_value=0)
        loan_purpose = st.selectbox("Loan Purpose", ["Home Improvement", "Debt Consolidation", "Business", "Medical", "Education", "Car Repair"])
        education_level = st.selectbox("Education Level", ["High School", "Associates", "Bachelors", "Masters", "PhD"])
        age = st.number_input("Age", min_value=18, max_value=100)

        submitted = st.form_submit_button("Predict and Save")
        if submitted:
            data = (income, credit_score, loan_amount, loan_term, dti, employment_years, previous_defaults, loan_purpose, education_level, age)
            prediction, reasons = predict_default(data)
            st.markdown(f"### Prediction Result: {prediction}")
            if reasons:
                st.warning("Reasons:")
                for reason in reasons:
                    st.write(f"- {reason}")
            st.info(save_to_database(data))

    st.markdown("---")
    st.header("📋 Customer Records")

    df = fetch_data()
    if not df.empty:
        st.dataframe(df)

        selected_id = st.number_input("Enter Customer ID to Delete", min_value=1, step=1)
        if st.button("🗑️ Delete Customer"):
            delete_customer_by_id(selected_id)
            st.success(f"Customer with ID {selected_id} deleted.")
            st.rerun()
    else:
        st.info("No customer data found.")

if __name__ == "__main__":
    initialize_database()
    main()

