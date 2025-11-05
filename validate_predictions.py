import sqlite3
import pandas as pd
import joblib

# Load model
model = joblib.load('model.joblib')

# Get some test cases from database
conn = sqlite3.connect('database.sqlite')
query = '''
SELECT id, recency_7, frequency_7, monetary_value_7, monetary_value_30
FROM passenger_activity_after_registration
WHERE id IN (1, 8, 20, 100, 29162)
ORDER BY id
'''
df = pd.read_sql_query(query, conn)
conn.close()

print('Model Predictions vs Actual Values:')
print('=' * 50)
for _, row in df.iterrows():
    # Create input for model
    input_data = pd.DataFrame({
        'recency_7': [row['recency_7']],
        'frequency_7': [row['frequency_7']],
        'monetary_value_7': [row['monetary_value_7']]
    })

    prediction = model.predict(input_data)[0]
    actual = row['monetary_value_30']
    error = abs(prediction - actual)
    error_pct = (error / actual) * 100 if actual > 0 else 0

    print(f'Passenger {int(row["id"])}:')
    print(f'  Input: recency={row["recency_7"]}, freq={row["frequency_7"]}, spend_7d=${row["monetary_value_7"]:.2f}')
    print(f'  Predicted: ${prediction:.2f}')
    print(f'  Actual: ${actual:.2f}')
    print(f'  Error: ${error:.2f} ({error_pct:.1f}%)')
    print()