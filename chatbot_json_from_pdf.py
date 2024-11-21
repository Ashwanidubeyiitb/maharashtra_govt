import streamlit as st
from pandasai.llm.openai import OpenAI
from pandasai import Agent
import pandas as pd
import json
import os

# Set the OpenAI API key
openai_api_key = "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"

# Set the PandasAI API key as an environment variable (Optional: only required for extended features)
os.environ["OPENAI_API_KEY"] = openai_api_key

# Streamlit page configuration
st.set_page_config(layout="wide", page_title="ChatJSON with Plotting", page_icon="📊")

# Function to load JSON data
def load_json(file):
    return json.load(file)

# Function to convert JSON to DataFrame
def json_to_dataframe(json_data):
    df_list = []
    for question, states in json_data.items():
        for state, values in states.items():
            for sector, value in values.items():
                df_list.append({"Question": question, "State": state, "Sector": sector, "Value": value})
    return pd.DataFrame(df_list)

# Function to chat with the JSON data
def chat_with_json(df, prompt):
    llm = OpenAI(api_token=openai_api_key)
    agent = Agent(df)  # Removed the incorrect 'api_key' parameter
    result = agent.chat(prompt)
    return result

# Streamlit UI
st.title("📊 ChatJSON with Plotting")
st.write("Upload your JSON file and interact with the health metrics data using natural language queries, including generating visualizations.")

# JSON File Upload
input_json = st.file_uploader("Upload your JSON file:", type=["json"])

if input_json is not None:
    col1, col2 = st.columns([1, 1])

    # Process JSON data
    with col1:
        st.info("✅ JSON Uploaded Successfully")
        json_data = load_json(input_json)
        df = json_to_dataframe(json_data)
        st.write("### Preview of Flattened Data:")
        st.dataframe(df, use_container_width=True)

    # Chat functionality
    with col2:
        st.info("💬 Chat with Your Data")
        input_text = st.text_area("Enter your query (you can ask for plots, trends, or maximum values):")

        if input_text:
            if st.button("Chat with JSON"):
                st.info(f"Your Query: {input_text}")

                # Enhanced prompt for plotting and analysis
                prompt = f"""
                You are a data assistant analyzing a dataset about health metrics in India. The dataset includes:
                1. **Questions (Metrics)**: Metrics like "{list(json_data.keys())[:5]}..." and others.
                2. **States**: Data for states like "Andhra Pradesh", "Bihar", "All India", etc.
                3. **Sectors**: Each state has data categorized into sectors such as "Total", "Public", "Private", "Urban", and "Rural".

                Based on the query: "{input_text}", your tasks are:
                - Understand the user's intent (e.g., maximum value, specific state, or plotting trends).
                - If the query involves plotting:
                  - Create a **bar chart** for comparisons (e.g., "Which state has the highest ANC registrations?").
                  - Create a **line chart** for trends across states or sectors (e.g., "Plot ANC registrations over all sectors for Bihar.").
                - Provide a clear textual response along with any plots, if applicable.
                - Example Queries and Responses:
                  - Query: "Which state has the highest number of ANC registrations?"
                    - Response: "The state with the highest number of ANC registrations is Uttar Pradesh with 337,804."
                    - Plot: A bar chart comparing all states.
                  - Query: "Plot the ANC registrations for all states in the public sector."
                    - Response: "Here is the plot for ANC registrations in the public sector."
                    - Plot: A bar chart showing values for all states.
                  - Query: "What are the trends for ANC registrations in Bihar?"
                    - Response: "The trends for ANC registrations in Bihar across sectors are shown below."
                    - Plot: A line chart showing trends across sectors.

                Analyze the query "{input_text}" and provide the best response with a plot, if relevant.
                """
                try:
                    result = chat_with_json(df, prompt)
                    st.success("💡 Response:")
                    st.write(result)

                    # Display generated plot
                    st.write("### Generated Plot (if applicable):")
                    st.pyplot()  # PandasAI-generated plots are displayed here
                except Exception as e:
                    st.error(f"🚨 An error occurred: {e}")

    # Additional Visualization
    st.write("---")
    st.write("### Interactive Data Exploration:")
    state_filter = st.selectbox("Select a state to filter data:", options=df["State"].unique())
    if state_filter:
        filtered_df = df[df["State"] == state_filter]
        st.write(f"Showing data for **{state_filter}**:")
        st.dataframe(filtered_df, use_container_width=True)
