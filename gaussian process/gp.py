import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.gaussian_process.kernels import RBF
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Load the dataset
data = pd.read_csv('system_info.csv')

scaler = StandardScaler()
X = data['Time stamp'].values.reshape(-1, 1)  
y_columns = ['CPU Usage', ['Memory Usage']#, 'Control command sent', 
            # 'Encoder position', 'CPU Temperature', 'Packets sent', 'Packets received']
Y = data[y_columns].values  

# Split data into training and testing sets
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

X_train_scaled = scaler.fit_transform(X_train)

X_test_scaled = scaler.fit_transform(X_test)

kernel = RBF()  # Radial Basis Function (RBF) kernel
gp_model = GaussianProcessRegressor(kernel=kernel, random_state=42)#, n_restarts_optimizer=10)


gp_model.fit(X_train_scaled, Y_train)


Y_pred, sigma = gp_model.predict(X_test_scaled, return_std=True)

mse = mean_squared_error(Y_test, Y_pred)
print("Mean Squared Error:", mse)

