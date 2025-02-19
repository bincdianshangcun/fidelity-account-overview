import csv
from pathlib import Path


data_path = Path(__file__).parent.parent / 'data'
csv_path = data_path / 'history' / 'BrokerageLink-652837700_FXAIX.Feb-19-2025.csv'

Column_CurrentValue='Current Value'
Column_CostBasisTotal='Cost Basis Total'

lst_current_value = []
lst_cost_basis_total = []
with open(csv_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        lst_current_value.append(float(row[Column_CurrentValue]))
        lst_cost_basis_total.append(float(row[Column_CostBasisTotal]))


sum_current_value = sum(lst_current_value)
sum_cost_basis_total = sum(lst_cost_basis_total)
total_gain_loss = (sum_current_value - sum_cost_basis_total) / sum_cost_basis_total

print('% Total Gain/Loss', f'{total_gain_loss*100:.2f}')