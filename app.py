import os
from datetime import datetime

import streamlit as st
from pymongo import MongoClient

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Docker Calculator",
    page_icon="🧮",
    layout="centered"
)

# ---------------- MONGODB CONNECTION ----------------
@st.cache_resource
def get_database():
    mongo_uri = os.getenv(
        "MONGO_URI",
        "mongodb://mongodb:27017/"
    )

    client = MongoClient(mongo_uri)
    db = client["calculator_db"]

    return db


db = get_database()
calculations = db["calculations"]


# ---------------- CALCULATOR ----------------
st.title("🧮 Streamlit Calculator")
st.write("Docker + Streamlit + MongoDB")

st.divider()

col1, col2 = st.columns(2)

with col1:
    num1 = st.number_input(
        "Enter first number",
        value=0.0
    )

with col2:
    num2 = st.number_input(
        "Enter second number",
        value=0.0
    )

operation = st.selectbox(
    "Select Operation",
    [
        "Addition",
        "Subtraction",
        "Multiplication",
        "Division"
    ]
)


if st.button("Calculate", type="primary"):

    try:

        if operation == "Addition":
            result = num1 + num2
            symbol = "+"

        elif operation == "Subtraction":
            result = num1 - num2
            symbol = "-"

        elif operation == "Multiplication":
            result = num1 * num2
            symbol = "*"

        elif operation == "Division":
            if num2 == 0:
                st.error("Cannot divide by zero.")
                st.stop()

            result = num1 / num2
            symbol = "/"

        st.success(f"Result: {result}")

        # Save calculation to MongoDB
        calculation = {
            "number1": num1,
            "number2": num2,
            "operation": operation,
            "expression": f"{num1} {symbol} {num2}",
            "result": result,
            "created_at": datetime.utcnow()
        }

        calculations.insert_one(calculation)

        st.info("Calculation saved to MongoDB.")


    except Exception as e:
        st.error(f"Error: {e}")


# ---------------- HISTORY ----------------

st.divider()

st.subheader("📋 Calculation History")

history = list(
    calculations.find(
        {},
        {"_id": 0}
    ).sort(
        "created_at",
        -1
    ).limit(20)
)

if history:

    for item in history:

        st.write(
            f"**{item['expression']} = {item['result']}**"
        )

        st.caption(
            f"Operation: {item['operation']} | "
            f"Time: {item['created_at']}"
        )

        st.divider()

else:
    st.info("No calculations saved yet.")
