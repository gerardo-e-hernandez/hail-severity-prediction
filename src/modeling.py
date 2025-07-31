import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error
import joblib
import os

def label_data(features_df: pd.DataFrame, spc_hail_reports: pd.DataFrame, time_window_minutes=15, distance_threshold_deg=0.5):
    """
    Labels storm cell data based on proximity to SPC hail reports.
    """
    features_df['hail_report'] = 0
    features_df['hail_size_in'] = 0.0
    
    features_df['scan_time'] = pd.to_datetime(features_df['scan_time'])
    spc_hail_reports['datetime'] = pd.to_datetime(spc_hail_reports['Date'].astype(str) + ' ' + spc_hail_reports['Time'].str.zfill(4))

    for idx, report in spc_hail_reports.iterrows():
        report_time = report['datetime']
        report_lat = report['Lat']
        report_lon = report['Lon']
        report_size = report['Size']

        time_diff = np.abs((features_df['scan_time'] - report_time).dt.total_seconds() / 60)
        lat_diff = np.abs(features_df['centroid_lat'] - report_lat)
        lon_diff = np.abs(features_df['centroid_lon'] - report_lon)

        matched_cells = (time_diff <= time_window_minutes) & \
                        (lat_diff <= distance_threshold_deg) & \
                        (lon_diff <= distance_threshold_deg)
        
        if np.any(matched_cells):
            features_df.loc[matched_cells, 'hail_report'] = 1
            features_df.loc[matched_cells, 'hail_size_in'] = features_df.loc[matched_cells, 'hail_size_in'].combine(report_size, max)

    return features_df

def train_classification_model(X, y, model_save_path):
    """
    Trains a classification model to predict the occurrence of hail.
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    classifier = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    classifier.fit(X_train, y_train)
    
    y_pred = classifier.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred))
    
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump(classifier, model_save_path)
    
    return classifier

def train_regression_model(X, y, model_save_path):
    """
    Trains a regression model to predict hail size, for storms that produced hail.
    """
    X_hail = X[y > 0]
    y_hail = y[y > 0]
    
    if len(X_hail) < 10:
        print("Not enough hail samples to train regression model.")
        return None

    X_train, X_test, y_train, y_test = train_test_split(X_hail, y_hail, test_size=0.2, random_state=42)
    
    regressor = RandomForestRegressor(n_estimators=100, random_state=42)
    regressor.fit(X_train, y_train)
    
    y_pred = regressor.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"Root Mean Squared Error (RMSE): {rmse:.4f} inches")
    
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump(regressor, model_save_path)
    
    return regressor