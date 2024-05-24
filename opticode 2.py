import pandas as pd
from mip import Model, xsum, minimize, BINARY

# Load the data
dienst = pd.read_excel("data/test_diensten.xlsx")
voertuig = pd.read_excel("data/test_voertuigen.xlsx")

aantal_voertuigen = len(voertuig)
aantal_diensten = len(dienst)

# Create a MIP model
m = Model("Voertuig-toewijzing")

# Add decision variables (1 if vehicle i is assigned to service j, otherwise 0)
x = [[m.add_var(var_type=BINARY) for j in range(aantal_diensten)] for i in range(aantal_voertuigen)]

# OBJECTIVE: Minimize diesel consumption
m.objective = minimize(xsum(x[i][j] * dienst.loc[j, 'km'] * voertuig.loc[i, 'verbruik']
                            for i in range(aantal_voertuigen) for j in range(aantal_diensten)))

# CONSTRAINTS

# Constraint 1: The date of a service must match the date of a vehicle
for j in range(aantal_diensten):
    dienst_datum = dienst.loc[j, 'datum']
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.loc[i, 'datum'] == dienst_datum) == 1

# Constraint 2: Depots must match
for j in range(aantal_diensten):
    dienst_stelplaats = dienst.loc[j, 'stelplaats']
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.loc[i, 'stelplaats'] == dienst_stelplaats) == 1

# Constraint 3: Each vehicle is assigned to at most one service
for i in range(aantal_voertuigen):
    m += xsum(x[i][j] for j in range(aantal_diensten)) <= 1

# Constraint 4: Each service must be assigned to exactly one vehicle
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen)) == 1

# Constraint 5: A vehicle must be available to be assigned to a service
for i in range(aantal_voertuigen):
    m += xsum(x[i][j] for j in range(aantal_diensten)) <= voertuig.loc[i, 'beschikbaar']

# Constraint 6: The type of a service must match the type of a vehicle
for j in range(aantal_diensten):
    dienst_type = dienst.loc[j, 'type']
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.loc[i, 'type'] == dienst_type) == 1

# Constraint 7: The subtype of a service must match the subtype of a vehicle
for j in range(aantal_diensten):
    dienst_subtype = dienst.loc[j, 'subtype']
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.loc[i, 'subtype'] == dienst_subtype) == 1

# Constraint 8: The range of a vehicle must be greater than the distance of a service
for j in range(aantal_diensten):
    dienst_km = dienst.loc[j, 'km']
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.loc[i, 'rijbereik'] >= dienst_km) == 1

# Constraint 9: LEZ zones
for j in range(aantal_diensten):
    if dienst.loc[j, 'lez'] == 1:
        m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.loc[i, 'lez ok'] == 1) == 1

# Constraint 10: Height problem
for j in range(aantal_diensten):
    if dienst.loc[j, 'hoogte_nok'] == 1:
        m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.loc[i, 'prob hoogte'] == 0) == 1

# Constraint 11: Electric vehicles
for j in range(aantal_diensten):
    if dienst.loc[j, 'elektriciteit'] == 1:
        m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.loc[i, 'elektriciteit'] == 1) == 1

# Optimize the model
m.optimize()

# Assign vehicles to services
toegewezen_voertuig = [-1] * aantal_diensten
for j in range(aantal_diensten):
    for i in range(aantal_voertuigen):
        if x[i][j].x >= 0.99:
            toegewezen_voertuig[j] = voertuig.loc[i, 'nummer']
            break

# Create the planning DataFrame
planning = dienst.copy()
planning['voertuig_nummer'] = toegewezen_voertuig

# Add vehicle information to the planning DataFrame
voertuig_info = voertuig.set_index('nummer').to_dict(orient='index')
for col in ['Bdatum', 'Bstelplaats', 'Btype', 'Bsubtype', 'Bleeftijd',
            'Bdiesel', 'Belektriciteit', 'Blez ok', 'Bprob hoogte', 'Brijbereik',
            'Bverbruik', 'Bbeschikbaar']:
    planning[col] = planning['voertuig_nummer'].map(lambda x: voertuig_info.get(x, {}).get(col, 'Unknown'))

print(planning)
planning.to_excel("data/PLANNING.xlsx", index=False)
