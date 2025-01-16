# Utility Dashboard

## Description
A web-based application designed to help users analyse their utility billing data and track monthly costs and usage to gain actionable insights into their energy usage.

## Features
- **Secure User Authentication**: Allows users to log in and view their own billing data securely.
- **Billing Data Analysis**: Visualises monthly billing costs and usage patterns.
- **Export Options**: Enables users to export reports as PDFs or CSV files.
- **Interactive Visualisations**: Displays dynamic graphs powered by Plotly.
- **Responsive Design**: Optimised for desktop using Bootstrap.

## Technologies Used
- **Backend**: Python (Flask)
- **Database**: PostgreSQL
- **Data Visualisation**: Plotly
- **PDF Export**: ReportLab
- **Data Handling**: Pandas

## Installation and Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/SamanthaMT/Utility-Dashboard.git
   cd Utility-Dashboard

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Set Up Database**:
   Create a PostgreSQL database and update the __init__.py file with your database credentials

5. **Run Application**:
   ```bash
   flask run

6. **Access Application**:
   Open your browser and navigate to http://127.0.0.1:5000

10. **Usage**:
    **Log In**:
    - Register for an account or log in with your credentials.

    **View Insights**:
    - Navigate to /billing to access interactive dashboard to analyse billing trends.
   
    **Upload Billing Data**:
    - Navigate to billing/add_billing to add bills. Can be done manually or by uploading a file in csv format.
   
    **View Billing Data**:
    - Navigate to billing/view_billing to view all bills added. The data can be sorted or filtered. Use the appropriate buttons to download the data.
    
  ![image](https://github.com/user-attachments/assets/a6bf3c43-d12b-444e-a1eb-664a77cf3507)

  ![image](https://github.com/user-attachments/assets/edca014c-f449-4a37-a293-f3650a60b629)

  ![image](https://github.com/user-attachments/assets/e0bf64a0-3f1e-45c8-9f57-383468f089f9)




