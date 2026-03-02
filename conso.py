import streamlit as st
import pandas as pd
import io

# -------------- Utility Functions --------------

# Consolidation logic for combining CSV/Excel files or specific sheets
def consolidate_files(file_list, file_type):
    consolidated_data = pd.DataFrame()
    for uploaded_file in file_list:
        try:
            if file_type == 'csv':
                df = pd.read_csv(uploaded_file)
                df['Filename'] = uploaded_file.name
                consolidated_data = pd.concat([consolidated_data, df], ignore_index=True)
            elif file_type == 'excel':
                df = pd.read_excel(uploaded_file, engine='openpyxl')
                df['Filename'] = uploaded_file.name
                consolidated_data = pd.concat([consolidated_data, df], ignore_index=True)
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")
    return consolidated_data

def consolidate_sheets(file_list, selected_sheets):
    consolidated_data = pd.DataFrame()
    for uploaded_file in file_list:
        try:
            if uploaded_file.name in selected_sheets:
                for sheet in selected_sheets[uploaded_file.name]:
                    sheet_df = pd.read_excel(uploaded_file, sheet_name=sheet)
                    sheet_df['Filename'] = uploaded_file.name
                    sheet_df['Sheet Name'] = sheet
                    consolidated_data = pd.concat([consolidated_data, sheet_df], ignore_index=True)
        except Exception as e:
            st.error(f"Error with file {uploaded_file.name}: {e}")
    return consolidated_data

# -------------- Streamlit Web Interface --------------

st.title('Data Consolidation Tool')
st.info("The login requirement has been removed. You can now use the tool directly.")

# 1. Select File Type
st.header('File Consolidation')
file_type = st.selectbox("Choose the file type to be consolidated:", options=['excel', 'csv'], index=0)

# 2. Select Consolidation Type
consolidation_type = st.selectbox("Select consolidation type:", ["Consolidate data from files", "Consolidate data from sheets"])

# 3. Upload Files
uploaded_files = st.file_uploader(f"Upload {file_type.upper()} files", type=["xlsx", "csv"] if file_type == 'csv' else ["xlsx"], accept_multiple_files=True)

if uploaded_files:
    st.write(f"Total uploaded files: {len(uploaded_files)}")

    if consolidation_type == "Consolidate data from files":
        consolidated_data = consolidate_files(uploaded_files, file_type)
        if not consolidated_data.empty:
            st.write("Consolidated Data:")
            st.dataframe(consolidated_data)
            output_file_name = st.text_input("File name:", value="consolidated")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                consolidated_data.to_excel(writer, index=False)
            st.download_button(label="Download Consolidated File", data=output.getvalue(), file_name=f"{output_file_name}.xlsx")

    elif consolidation_type == "Consolidate data from sheets" and file_type == 'excel':
        # Simple sheet selection
        selected_sheets = {}
        for file in uploaded_files:
            sheet_names = pd.ExcelFile(file).sheet_names
            selected_sheets[file.name] = st.multiselect(f"Sheets in {file.name}:", options=sheet_names)
        
        if st.button("Consolidate Selected Sheets"):
            consolidated_data = consolidate_sheets(uploaded_files, selected_sheets)
            if not consolidated_data.empty:
                st.dataframe(consolidated_data)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    consolidated_data.to_excel(writer, index=False)
                st.download_button(label="Download", data=output.getvalue(), file_name="consolidated_sheets.xlsx")

# Footer
st.markdown("""
    <style>
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: white; text-align: center; padding: 10px; font-size: small; border-top: 1px solid #eaeaea; }
    </style>
    <div class="footer">By Ansh Gandhi | +91 75888 34433</div>
""", unsafe_allow_html=True)
