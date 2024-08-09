import streamlit as st
import pandas as pd
from datetime import datetime

# Function to load attendance data from CSV
def load_attendance_data(csv_file):
    try:
        df = pd.read_csv(csv_file)
        return df
    except FileNotFoundError:
        st.error(f"Error: {csv_file} not found.")
        return None

# Main function to run the Streamlit app
def main():
    st.title('Attendance Details')

    date = st.date_input("Select Date", datetime.now())
    formatted_date = date.strftime("%d-%m-%Y")


    st.header('Student Attendance')
    staff_csv_file = 'students_attendance.csv'
    staff_df = load_attendance_data(staff_csv_file)
    if staff_df is not None:
        st.dataframe(staff_df)

    # Display staff attendance
    st.header('Staff Attendance')
    staff_csv_file = 'staff_attendance.csv'
    staff_df = load_attendance_data(staff_csv_file)
    if staff_df is not None:
        st.dataframe(staff_df)

if __name__ == '__main__':
    main()
