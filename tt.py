# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 19:48:02 2024

@author: jiahui
"""

import pandas as pd

# Try reading the file with different encodings
try:
    data = pd.read_csv('data.csv', encoding='utf-8')
except UnicodeDecodeError:
    data = pd.read_csv('data.csv', encoding='latin1')
    
#print(data.head())  # Display the first few rows of the DataFrame
#print(data.info())  # Get information about the DataFrame, including data types and non-null counts
#print(data.describe())  # Get summary statistics for numerical columns

data['grand_total'] = data['Quantity'] * data['UnitPrice']
selected = data.loc[:, ['InvoiceNo', 'Description', 'Quantity', 'InvoiceDate', 'CustomerID', 'Country', 'grand_total']]

# Convert 'InvoiceDate' to datetime format
selected['InvoiceDate'] = pd.to_datetime(selected['InvoiceDate'])

# Extract date and time features
selected['DayOfWeek'] = selected['InvoiceDate'].dt.dayofweek
selected['Month'] = selected['InvoiceDate'].dt.month
selected['Year'] = selected['InvoiceDate'].dt.year
selected['Hour'] = selected['InvoiceDate'].dt.hour

# Example: Calculate total quantity per customer
customer_total_quantity = selected.groupby('CustomerID')['Quantity'].sum().reset_index()
customer_total_quantity.rename(columns={'Quantity': 'TotalQuantity'}, inplace=True)
selected = selected.merge(customer_total_quantity, on='CustomerID', how='left')

# Example: Perform one-hot encoding for the 'Country' column
country_dummies = pd.get_dummies(selected['Country'], prefix='Country')
selected = pd.concat([selected, country_dummies], axis=1)

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

# Define the features and target variable
features = ['Quantity', 'DayOfWeek', 'Month', 'Year', 'Hour', 'TotalQuantity', 'Country_United Kingdom']  
X = selected[features]
y = selected['grand_total']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Handle missing values (if any)
imputer = SimpleImputer(strategy='mean')
X_train_imputed = imputer.fit_transform(X_train)
X_test_imputed = imputer.transform(X_test)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_imputed)
X_test_scaled = scaler.transform(X_test_imputed)

# Create and train the linear regression model
model = LinearRegression()
model.fit(X_train_scaled, y_train)

# Make predictions
y_pred = model.predict(X_test_scaled)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print('Mean Squared Error:', mse)
print('R-squared:', r2)










