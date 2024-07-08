import streamlit as st
import pandas as pd
import json
import os

# Function to display statistics
def display_stats(df, col):
    st.write(f"**Total Rows:** {len(df)}")
    st.write(f"**Data Type:** {df[col].dtype}")
    st.write(f"**Unique Values:** {df[col].nunique()}")
    st.write(f"**Number of NaNs:** {df[col].isna().sum()}")
    st.write(f"**Top 5 Value Counts:**")
    st.write(df[col].value_counts().head(5))

# Function to save vetted data to JSON
def save_to_json(vetted_data):
    with open('./vetted.json', 'w') as f:
        json.dump(vetted_data, f, indent=4)

# Load existing vetted data if available
vetted_data = []
if os.path.exists('./vetted.json'):
    with open('./vetted.json', 'r') as f:
        vetted_data = json.load(f)

# Dark mode setting
st.set_page_config(page_title="DataFrame Column Vetting App", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
    .reportview-container {
        background: #262730;
        color: white;
    }
    .sidebar .sidebar-content {
        background: #1c1e24;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("DataFrame Column Vetting App")

# Optional encoding input
encoding = st.sidebar.text_input("Enter encoding method (e.g., ISO-8859-1) or leave blank for default:", value="")

# File upload
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

# Session state to track the current column index
if "col_index" not in st.session_state:
    st.session_state.col_index = 0

if uploaded_file:
    try:
        # Use the specified encoding if provided, otherwise default to 'utf-8'
        encoding_to_use = encoding if encoding else 'utf-8'
        df = pd.read_csv(uploaded_file, encoding=encoding_to_use)

        # Ensure the column index is within valid range
        col_index = st.session_state.col_index
        col_index = col_index % len(df.columns)
        col_to_display = df.columns[col_index]

        # Sidebar - Select column
        st.sidebar.selectbox("Select Column", df.columns, index=col_index)

        # Main content layout
        col1, col2, col3 = st.columns([1, 1, 1])

        # Display the column's data in the leftmost column
        with col1:
            st.write(f"### Column: {col_to_display}")
            st.dataframe(df[[col_to_display]])

        # Display column stats in the middle column
        with col2:
            st.write(f"### Statistics for {col_to_display}")
            display_stats(df, col_to_display)

        # Rightmost column for actions
        with col3:
            st.write(f"### Actions for {col_to_display}")
            drop_col = st.checkbox("Drop Column", key=f"drop_{col_index}")
            
            new_name = st.text_input("New Name", value="", key=f"new_name_{col_index}")
            parse_col = st.selectbox("Parse as", ["None", "to_datetime", "to_numeric"], index=0, key=f"parse_{col_index}")
            save_parsed = st.checkbox("Save Parsed Column", key=f"save_parsed_{col_index}")
            
            # Update vetted data when POST is hit
            if st.button("POST"):
                column_vetting = {
                    "col_name": col_to_display,
                    "new_name": new_name if new_name else None,
                    "drop": drop_col,
                    "new_dtype": parse_col if parse_col != "None" else None
                }
                
                # Check if column has already been vetted
                col_found = False
                for idx, item in enumerate(vetted_data):
                    if item["col_name"] == col_to_display:
                        vetted_data[idx] = column_vetting
                        col_found = True
                        break
                
                if not col_found:
                    vetted_data.append(column_vetting)
                    
                save_to_json(vetted_data)
                st.success(f"Column '{col_to_display}' vetted successfully!")

                # Move to the next column
                st.session_state.col_index += 1
                if st.session_state.col_index >= len(df.columns):
                    st.session_state.col_index = 0  # Reset to the first column if it reaches the end
                
                st.experimental_rerun()  # Rerun the app to update the display for the next column
                
            # Show current vetted data
            st.write("### Current Vetted Data")
            st.json(vetted_data)
    except Exception as e:
        st.error(f"An error occurred while loading the CSV file: {e}")
else:
    st.write("Please upload a CSV file to begin vetting.")
