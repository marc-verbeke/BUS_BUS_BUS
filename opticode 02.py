import pandas as pd
from mip import Model, xsum, minimize, BINARY

# Load the dienst and voertuig data
dienst = pd.read_excel("data/test_diensten.xlsx")
voertuig = pd.read_excel("data/test_voertuigen.xlsx")

# Extract data from DataFrames
dienst_datum = dienst['datum'].tolist()
dienst_stelplaats = dienst['stelplaats'].tolist()
dienst_nummer = dienst['nummer'].tolist()
dienst_type = dienst['type'].tolist()
dienst_subtype = dienst['subtype'].tolist()
dienst_start = dienst['start'].tolist()
dienst_eind = dienst['eind'].tolist()
dienst_km = dienst['km'].tolist()
dienst_lez = dienst['lez'].tolist()
dienst_elektriciteit = dienst['elektriciteit'].tolist()
dienst_hoogte_nok = dienst['hoogte_nok'].tolist()

voertuig_datum = voertuig['datum'].tolist()
voertuig_stelplaats = voertuig['stelplaats'].tolist()
voertuig_nummer = voertuig['nummer'].tolist()
voertuig_type = voertuig['type'].tolist()
voertuig_subtype = voertuig['subtype'].tolist()
voertuig_leeftijd = voertuig['leeftijd'].tolist()
voertuig_diesel = voertuig['diesel'].tolist()
voertuig_elektriciteit = voertuig['elektriciteit'].tolist()
voertuig_lez_ok = voertuig['lez_ok'].tolist()
voertuig_prob_hoogte = voertuig['prob_hoogte'].tolist()
voertuig_rijbereik = voertuig['rijbereik'].tolist()
voertuig_verbruik = voertuig['verbruik'].tolist()
voertuig_beschikbaar = voertuig['beschikbaar'].tolist()

aantal_voertuigen = len(voertuig)
aantal_diensten = len(dienst)

# Create a MIP model
m = Model("Voertuig-toewijzing")

# Add decision variables
x = [[m.add_var(var_type=BINARY) for _ in range(aantal_diensten)] for _ in range(aantal_voertuigen)]

# Objective: Minimize fuel consumption
m.objective = minimize(xsum(x[i][j] * dienst_km[j] * voertuig_verbruik[i] for i in range(aantal_voertuigen) for j in range(aantal_diensten)))

# Constraints
for j in range(aantal_diensten):
    # Date constraint
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig_datum[i] == dienst_datum[j]) == 1

    # Depot constraint
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig_stelplaats[i] == dienst_stelplaats[j]) == 1

    # Each dienst must be assigned to one vehicle
    m += xsum(x[i][j] for i in range(aantal_voertuigen)) == 1

    # Vehicle availability
    m += xsum(x[i][j] * voertuig_beschikbaar[i] for i in range(aantal_voertuigen)) == 1

    # Type and subtype constraints
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig_type[i] == dienst_type[j]) == 1
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig_subtype[i] == dienst_subtype[j]) == 1

    # Range constraint
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig_rijbereik[i] < dienst_km[j]) == 0

    # LEZ constraint
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if dienst_lez[j] == 1 and not voertuig_lez_ok[i]) == 0

    # Height problem constraint
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if dienst_hoogte_nok[j] == 1 and voertuig_prob_hoogte[i] == 1) == 0

    # Electric vehicle constraint
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if dienst_elektriciteit[j] == 1 and voertuig_elektriciteit[i] == 0) == 0

# Ensure each vehicle is assigned to at most one dienst
for i in range(aantal_voertuigen):
    m += xsum(x[i][j] for j in range(aantal_diensten)) <= 1

# Optimize the model
m.optimize()

# Assign vehicles to services
toegewezen_voertuig = [-1] * aantal_diensten
for j in range(aantal_diensten):
    for i in range(aantal_voertuigen):
        if x[i][j].x >= 0.99:
            toegewezen_voertuig[j] = voertuig_nummer[i]

planning = dienst.copy()
planning['voertuig'] = toegewezen_voertuig

# Create mapping dictionaries for vehicle attributes
vehicle_attribute_maps = {
    'datum': dict(zip(voertuig_nummer, voertuig_datum)),
    'stelplaats': dict(zip(voertuig_nummer, voertuig_stelplaats)),
    'type': dict(zip(voertuig_nummer, voertuig_type)),
    'subtype': dict(zip(voertuig_nummer, voertuig_subtype)),
    'leeftijd': dict(zip(voertuig_nummer, voertuig_leeftijd)),
    'diesel': dict(zip(voertuig_nummer, voertuig_diesel)),
    'elektriciteit': dict(zip(voertuig_nummer, voertuig_elektriciteit)),
    'lez_ok': dict(zip(voertuig_nummer, voertuig_lez_ok)),
    'prob_hoogte': dict(zip(voertuig_nummer, voertuig_prob_hoogte)),
    'rijbereik': dict(zip(voertuig_nummer, voertuig_rijbereik)),
    'verbruik': dict(zip(voertuig_nummer, voertuig_verbruik)),
    'beschikbaar': dict(zip(voertuig_nummer, voertuig_beschikbaar))
}

# Add vehicle attributes to planning DataFrame
for attr, mapping in vehicle_attribute_maps.items():
    planning[f'bus_{attr}'] = planning['voertuig'].map(mapping).fillna('Unknown')

# Save the planning to an Excel file
planning.to_excel("data/PLANNING.xlsx", index=False)

print(planning)
