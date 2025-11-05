


import pandas as pd
import sqlite3
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error
import joblib
import os
import csv

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database.sqlite')
MODEL_PATH = '/tmp/model.joblib'

def load_data():
	conn = sqlite3.connect(DB_PATH)
	query = "SELECT recency_7, frequency_7, monetary_value_7, monetary_value_30 FROM passenger_activity_after_registration"
	df = pd.read_sql_query(query, conn)
	conn.close()
	return df


def train_and_save_best_model():
	df = load_data()
	X = df[["recency_7", "frequency_7", "monetary_value_7"]]
	y = df["monetary_value_30"]
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

	models_and_params = {
		"LinearRegression": {
			"model": LinearRegression(),
			"params": {"fit_intercept": [True, False]}
		},
		"RandomForestRegressor": {
			"model": RandomForestRegressor(random_state=42),
			"params": {
				"n_estimators": [50, 100, 200],
				"max_depth": [None, 5, 10],
				"min_samples_split": [2, 5]
			}
		},
		"Ridge": {
			"model": Ridge(),
			"params": {"alpha": [0.1, 1.0, 10.0], "fit_intercept": [True, False]}
		}
	}


	best_model = None
	best_mse = float('inf')
	best_name = None
	best_params = None
	results = []

	for name, mp in models_and_params.items():
		print(f"\nGrid search for {name}...")
		grid = GridSearchCV(mp["model"], mp["params"], cv=3, scoring="neg_mean_squared_error", n_jobs=-1, error_score='raise')
		grid.fit(X_train, y_train)
		y_pred = grid.predict(X_test)
		mse = mean_squared_error(y_test, y_pred)
		print(f"{name} best params: {grid.best_params_}")
		print(f"{name} Test MSE: {mse:.2f}")
		results.append({
			"model": name,
			"best_params": grid.best_params_,
			"test_mse": mse
		})
		if mse < best_mse:
			best_mse = mse
			best_model = grid.best_estimator_
			best_name = name
			best_params = grid.best_params_

	# Save results to CSV
	results_csv_path = '/tmp/model_results.csv'
	with open(results_csv_path, 'w', newline='') as csvfile:
		fieldnames = ['model', 'best_params', 'test_mse']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for row in results:
			writer.writerow({
				'model': row['model'],
				'best_params': str(row['best_params']),
				'test_mse': row['test_mse']
			})
	print(f"\nModel results saved to {results_csv_path}")

	joblib.dump(best_model, MODEL_PATH)
	print(f"\nBest model: {best_name} (MSE: {best_mse:.2f})")
	print(f"Best params: {best_params}")
	print(f"Model saved to {MODEL_PATH}")

	# Test the best model on the test set
	y_pred = best_model.predict(X_test)
	mse = mean_squared_error(y_test, y_pred)
	print(f"\nFinal Test MSE for best model: {mse:.2f}")

if __name__ == "__main__":
	train_and_save_best_model()
