import streamlit as st
import pandas as pd
import numpy as np

st.subheader("📐 CMM Inspection Report Analyzer")

# File Uploader Widget
uploaded_file = st.file_uploader("Upload CMM Excel File (.xlsx, .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Reset file pointer to avoid buffer errors
    uploaded_file.seek(0)
    
    try:
        # Determine engine based on file extension
        if uploaded_file.name.endswith('.xls'):
            df = pd.read_excel(uploaded_file, engine='xlrd')
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            
        st.success(f"Successfully loaded `{uploaded_file.name}`")
        
        st.write("### Raw Data Preview")
        st.dataframe(df.head())
        
        # Standardize column names (strip whitespace and handle casing)
        df.columns = [str(col).strip() for col in df.columns]
        
        # Expected CMM columns
        required_cols = ['Feature', 'Nominal', 'Actual', 'USL', 'LSL']
        
        # Check if required columns are present
        if all(col in df.columns for col in required_cols):
            # Convert values to numeric, coercing errors
            for col in ['Nominal', 'Actual', 'USL', 'LSL']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Calculate Deviation and Out-of-Tolerance Status
            df['Dev'] = df['Actual'] - df['Nominal']
            df['Status'] = np.where(
                (df['Actual'] > df['USL']) | (df['Actual'] < df['LSL']), 
                'OUT OF TOLERANCE', 
                'OK'
            )
            
            # Key Performance Metrics
            total_points = len(df)
            out_of_spec = len(df[df['Status'] == 'OUT OF TOLERANCE'])
            pass_rate = ((total_points - out_of_spec) / total_points) * 100 if total_points > 0 else 0
            
            # Metric Cards Display
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Inspection Points", total_points)
            col2.metric("Out of Tolerance Points", out_of_spec, delta_color="inverse")
            col3.metric("Pass Rate (FD Score)", f"{pass_rate:.1f}%")
            
            # Display Out of Tolerance Table
            if out_of_spec > 0:
                st.warning(f"⚠️ Found {out_of_spec} out-of-tolerance inspection points:")
                out_df = df[df['Status'] == 'OUT OF TOLERANCE'][['Feature', 'Nominal', 'Actual', 'LSL', 'USL', 'Dev']]
                st.dataframe(out_df.style.format({'Nominal': '{:.2f}', 'Actual': '{:.2f}', 'LSL': '{:.2f}', 'USL': '{:.2f}', 'Dev': '{:+.2f}'}))
            else:
                st.success("✅ All inspection points are within specified tolerances!")
                
        else:
            st.info("💡 **Excel Structure Tip:** To run automated tolerance checks, ensure your Excel column headers include: `Feature`, `Nominal`, `Actual`, `USL`, and `LSL`.")
            
    except Exception as e:
        st.error(f"Error parsing Excel file: {e}")
        
