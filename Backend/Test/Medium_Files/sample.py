"""Data Analysis Toolkit - Basic data analysis utilities"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Optional
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataAnalyzer:
    """A class for basic data analysis operations."""
    
    def __init__(self, name="unnamed_dataset"):
        self.data = None
        self.name = name
        self._models = {}
        logger.info(f"Initialized DataAnalyzer: {name}")
    
    def plot_histogram(self, column: str, bins: int = 30) -> None:
        """Plot a histogram for a specific column."""
        if self.data is None or column not in self.data.columns:
            raise ValueError("Invalid data or column.")
            
        plt.figure(figsize=(8, 5))
        self.data[column].plot(kind='hist', bins=bins)
        plt.title(f'Histogram of {column}')
        plt.show()
    
    def train_linear_model(self, target: str, features: List[str]) -> Dict:
        """Train a linear regression model."""
        if self.data is None:
            raise ValueError("No data loaded.")
            
        # Prepare data
        X = self.data[features]
        y = self.data[target]
        
        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        # Store results
        model_info = {
            'model': model,
            'r2_score': r2,
            'rmse': rmse,
            'coefficients': {feature: coef for feature, coef in zip(features, model.coef_)}
        }
        
        self._models[target] = model_info
        return model_info