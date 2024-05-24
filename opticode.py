import pandas as pd
from mip import Model, xsum, minimize, BINARY

# Load data
dienst = pd.read_excel("data/test_diensten.xlsx")
voertuig = pd.read_excel("data/test_voertuigen.xlsx")

# Extracting data from DataFrames
aantal_voertuigen = len(voertuig)
aantal_diensten = len(dienst)

dienst_dict = dienst.to_dict(orient='index')
voertuig_dict = voertuig.to_dict(orient='index')
print(dienst_dict)
print(voertuig_dict)

# Create a MIP model
m = Model("Voertuig-toewijzing")

# Decision variables: 1 if vehicle i is assigned to service j, else 0
x = [[m.add_var(var_type=BINARY) for _ in range(aantal_diensten)] for _ in range(aantal_voertuigen)]

# Objective: Minimize the sum of (dienst_km * voertuig_verbruik) for all assignments
m.objective = minimize(xsum(x[i][j] * dienst_dict[j]['km'] * voertuig_dict[i]['verbruik']
                            for i in range(aantal_voertuigen) for j in range(aantal_diensten)))

for i in range(aantal_voertuigen):
    m += xsum(x[i][j] for j in range(aantal_diensten)) <= 1
# Constraints
for j in range(aantal_diensten):
    # Each service is associated with a depot
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig_dict[i]['stelplaats'] == dienst_dict[j]['stelplaats']) == 1

    # Each service is covered by exactly one vehicle
    m += xsum(x[i][j] for i in range(aantal_voertuigen)) == 1

    # Vehicle must be available to cover the service
    m += xsum(x[i][j] * voertuig_dict[i]['beschikbaar'] for i in range(aantal_voertuigen)) == 1

    # Vehicle type and subtype must match service requirements
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig_dict[i]['type'] == dienst_dict[j]['type']) == 1
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig_dict[i]['subtype'] == dienst_dict[j]['subtype']) == 1

    # Vehicle range must be sufficient to cover the service distance
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig_dict[i]['rijbereik'] >= dienst_dict[j]['km']) == 1

    # Additional constraints (adjust as needed)

# Optimize the model
m.optimize()

# Extract assigned vehicles for each service
toegewezen_voertuig = [-1] * aantal_diensten
for j in range(aantal_diensten):
    for i in range(aantal_voertuigen):
        if x[i][j].x >= 0.99:
            toegewezen_voertuig[j] = voertuig_dict[i]['busnummer']

# Update the 'planning' DataFrame with assigned vehicles
planning = dienst.copy()
planning['voertuig'] = toegewezen_voertuig

# Output the planning to Excel
planning.to_excel("data/PLANNING.xlsx", index=False)
