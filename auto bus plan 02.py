import pandas as pd
from datetime import datetime
from mip import Model, xsum, minimize, BINARY

# Load the data
dienst = pd.read_excel("data/DIENSTEN.xlsx")
voertuig = pd.read_excel("data/voertuigen.xlsx")

# Combine dates and hours
dienst['startdatuur'] = dienst.apply(lambda row: datetime.combine(row['startdatum'], row['start']), axis=1)
dienst['einddatuur'] = dienst.apply(lambda row: datetime.combine(row['einddatum'], row['eind']), axis=1)

aantal_voertuigen = len(voertuig)
aantal_diensten = len(dienst)

voertuig_datum = []
voertuig_stelplaats = []
voertuig_nummer = []
voertuig_type = []
voertuig_subtype = []
voertuig_leeftijd = []
voertuig_diesel = []
voertuig_elektriciteit = []
voertuig_lez_ok = []
voertuig_prob_hoogte = []
voertuig_rijbereik = []
voertuig_verbruik = []
voertuig_beschikbaar = []

toegewezen_voertuig_datum = []
toegewezen_voertuig_stelplaats = []
toegewezen_voertuig_nummer = []
toegewezen_voertuig_type = []
toegewezen_voertuig_subtype = []
toegewezen_voertuig_leeftijd = []
toegewezen_voertuig_diesel = []
toegewezen_voertuig_elektriciteit = []
toegewezen_voertuig_lez_ok = []
toegewezen_voertuig_prob_hoogte = []
toegewezen_voertuig_rijbereik = []
toegewezen_voertuig_verbruik = []
toegewezen_voertuig_beschikbaar = []

toegewezen_voertuig = []

for x in range(len(voertuig)):
    voertuig_datum.append(voertuig.iloc[x, 0])
    voertuig_stelplaats.append(voertuig.iloc[x, 1])
    voertuig_nummer.append(voertuig.iloc[x, 2])
    voertuig_type.append(voertuig.iloc[x, 3])
    voertuig_subtype.append(voertuig.iloc[x, 4])
    voertuig_leeftijd.append(voertuig.iloc[x, 5])
    voertuig_diesel.append(voertuig.iloc[x, 6])
    voertuig_elektriciteit.append(voertuig.iloc[x, 7])
    voertuig_lez_ok.append(voertuig.iloc[x, 8])
    voertuig_prob_hoogte.append(voertuig.iloc[x, 9])
    voertuig_rijbereik.append(voertuig.iloc[x, 10])
    voertuig_verbruik.append(voertuig.iloc[x, 11])
    voertuig_beschikbaar.append(voertuig.iloc[x, 12])

# Create a MIP model
m = Model("Voertuig-toewijzing")

# Add decision variables (1 if vehicle i is assigned to service j, otherwise 0)
x = [[m.add_var(var_type=BINARY) for j in range(aantal_diensten)] for i in range(aantal_voertuigen)]

# Define weights for the objectives
weight_diesel = 0.5
weight_age = 0.5

# OBJECTIVE: Minimize diesel consumption and age
m.objective = minimize(
    weight_diesel * xsum(x[i][j] * dienst.loc[j, 'km'] * voertuig.loc[i, 'verbruik'] for i in range(aantal_voertuigen) for j in range(aantal_diensten)) +
    weight_age * xsum(x[i][j] * voertuig.loc[i, 'leeftijd'] for i in range(aantal_voertuigen) for j in range(aantal_diensten))
)
# CONSTRAINTS

# Constraint 1: The date of a service must match the date of a vehicle
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.loc[i, 'datum'] == dienst.loc[j, 'startdatum']) == 1

# Constraint 2: Depots must match
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.loc[i, 'stelplaats'] == dienst.loc[j, 'stelplaats']) == 1

# Constraint 3: Each vehicle is assigned to at most one service at a time, with a 2-hour gap
for i in range(aantal_voertuigen):
    for j1 in range(aantal_diensten):
        for j2 in range(aantal_diensten):
            if j1 != j2:
                # Check if services j1 and j2 are on the same date and have at least 2 hours gap
                if (dienst.loc[j1, 'startdatum'] == dienst.loc[j2, 'startdatum'] and
                        (dienst.loc[j2, 'startdatuur'] - dienst.loc[j1, 'einddatuur']).total_seconds() >= 1):
                    m += x[i][j1] + x[i][j2] <= 1

# Constraint 4: Each service must be assigned to exactly one vehicle
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen)) == 1

# Constraint 5: A vehicle must be available to be assigned to a service
for i in range(aantal_voertuigen):
    m += xsum(x[i][j] for j in range(aantal_diensten)) <= voertuig.loc[i, 'beschikbaar']

# Constraint 6: The type of a service must match the type of a vehicle
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.loc[i, 'type'] == dienst.loc[j, 'type']) == 1

# Constraint 7: The subtype of a service must match the subtype of a vehicle
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.loc[i, 'subtype'] == dienst.loc[j, 'subtype']) == 1

# Constraint 8: The range of a vehicle must be greater than the distance of a service
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.loc[i, 'rijbereik'] >= dienst.loc[j, 'km']) == 1

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

vehicle_datum_map = dict(zip(voertuig_nummer, voertuig_datum))
vehicle_stelplaats_map = dict(zip(voertuig_nummer, voertuig_stelplaats))
vehicle_type_map = dict(zip(voertuig_nummer, voertuig_type))
vehicle_subtype_map = dict(zip(voertuig_nummer, voertuig_subtype))
vehicle_leeftijd_map = dict(zip(voertuig_nummer, voertuig_leeftijd))
vehicle_diesel_map = dict(zip(voertuig_nummer, voertuig_diesel))
vehicle_elektriciteit_map = dict(zip(voertuig_nummer, voertuig_elektriciteit))
vehicle_lez_ok_map = dict(zip(voertuig_nummer, voertuig_lez_ok))
vehicle_prob_hoogte_map = dict(zip(voertuig_nummer, voertuig_prob_hoogte))
vehicle_rijbereik_map = dict(zip(voertuig_nummer, voertuig_rijbereik))
vehicle_verbruik_map = dict(zip(voertuig_nummer, voertuig_verbruik))
vehicle_beschikbaar_map = dict(zip(voertuig_nummer, voertuig_beschikbaar))

for vehicle_number in toegewezen_voertuig:
    if vehicle_number != -1:  # Only update if vehicle is assigned
  #      toegewezen_voertuig_subtype.append(voertuig_subtype[voertuig_nummer.index(vehicle_number)])
  # BEKIJK NOG EENS GOED OF JE TOCH NIET BOVENSTE WIL GEBRUIKEN
        toegewezen_voertuig_datum.append((vehicle_datum_map.get(vehicle_number,'Unknown')))
        toegewezen_voertuig_stelplaats.append(vehicle_stelplaats_map.get(vehicle_number, 'Unknown'))
        toegewezen_voertuig_type.append(vehicle_type_map.get(vehicle_number, 'Unknown'))
        toegewezen_voertuig_subtype.append(vehicle_subtype_map.get(vehicle_number, 'Unknown'))
        toegewezen_voertuig_leeftijd.append(vehicle_leeftijd_map.get(vehicle_number, 'Unknown'))
        toegewezen_voertuig_diesel.append(vehicle_diesel_map.get(vehicle_number, 'Unknown'))
        toegewezen_voertuig_elektriciteit.append(vehicle_elektriciteit_map.get(vehicle_number, 'Unknown'))
        toegewezen_voertuig_lez_ok.append(vehicle_lez_ok_map.get(vehicle_number, 'Unknown'))
        toegewezen_voertuig_prob_hoogte.append(vehicle_prob_hoogte_map.get(vehicle_number, 'Unknown'))
        toegewezen_voertuig_rijbereik.append(vehicle_rijbereik_map.get(vehicle_number, 'Unknown'))
        toegewezen_voertuig_verbruik.append(vehicle_verbruik_map.get(vehicle_number, 'Unknown'))
        toegewezen_voertuig_beschikbaar.append(vehicle_beschikbaar_map.get(vehicle_number, 'Unknown'))

planning['bus'] = toegewezen_voertuig
planning['bus_datum'] = toegewezen_voertuig_datum
planning['bus_stelplaats'] = toegewezen_voertuig_stelplaats
planning['bus_type'] = toegewezen_voertuig_type
planning['bus_subtype'] = toegewezen_voertuig_subtype
planning['bus_leeftijd'] = toegewezen_voertuig_leeftijd
planning['bus_diesel'] = toegewezen_voertuig_diesel
planning['bus_elektriciteit'] = toegewezen_voertuig_elektriciteit
planning['bus_lez_ok'] = toegewezen_voertuig_lez_ok
planning['bus_prob_hoogte'] = toegewezen_voertuig_prob_hoogte
planning['bus_rijbereik'] = toegewezen_voertuig_rijbereik
planning['bus_verbruik'] = toegewezen_voertuig_verbruik
planning['bus_beschikbaar'] = toegewezen_voertuig_beschikbaar

planning.to_excel("data/PLANNING_02.xlsx", index=False)
