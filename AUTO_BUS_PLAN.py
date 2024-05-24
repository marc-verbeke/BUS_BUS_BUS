import pandas as pd
from mip import Model, xsum, minimize, BINARY
import os

dienst_datum = []
dienst_stelplaats = []
dienst_nummer = []
dienst_type = []
dienst_subtype = []
dienst_start = []
dienst_eind = []
dienst_km = []
dienst_lez = []
dienst_elektriciteit = []
dienst_hoogte_nok = []

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

excel_file_path = "data/TEST_DIENSTEN.xlsx"
dienst = pd.read_excel(excel_file_path)
excel_file_path = "data/TEST_VOERTUIGEN.xlsx"
voertuig = pd.read_excel(excel_file_path)

aantal_voertuigen = len(voertuig)
aantal_diensten = len(dienst)

for x in range(len(dienst)):
    dienst_datum.append(dienst.iloc[x,0])
    dienst_stelplaats.append(dienst.iloc[x, 1])
    dienst_nummer.append(dienst.iloc[x, 2])
    dienst_type.append(dienst.iloc[x, 3])
    dienst_subtype.append(dienst.iloc[x, 4])
    dienst_start.append(dienst.iloc[x, 5])
    dienst_eind.append(dienst.iloc[x, 6])
    dienst_km.append(dienst.iloc[x, 7])
    dienst_lez.append(dienst.iloc[x, 8])
    dienst_elektriciteit.append(dienst.iloc[x, 9])
    dienst_hoogte_nok.append(dienst.iloc[x, 10])

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

# Maak een MIP-model
m = Model("Voertuig-toewijzing")

# Voeg beslissingsvariabelen toe (1 als voertuig i aan rit j wordt toegewezen, anders 0)
x = [[m.add_var(var_type=BINARY) for j in range(aantal_diensten)] for i in range(aantal_voertuigen)]


# OBJECTIEF
# VERBRUIK ZO MINIMAAL MOGELIJK MAZOUT
m.objective = minimize(xsum(x[i][j] * dienst_km[j] * voertuig_verbruik[i] for i in range(aantal_voertuigen) for j in range(aantal_diensten)))


# CONSTRAINT 01
# DE DATUM VAN EEN DIENST MOET GELIJK ZIJN AAN DE DATUM VAN EEN VOERTUIG
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.iloc[i, 0] == dienst.iloc[j, 0]) == 1

# CONSTRAINT 01
# IEDERE DIENST IS AAN EEN STELPLAATS GEKOPPELD
# IEDER VOERTUIG IS AAN EEN STELPLAATS GEKOPPELD
# DE STELPLAATSEN MOETEN GELIJK ZIJN
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.iloc[i, 1] == dienst.iloc[j, 1]) == 1

# elk voertuig wordt aan maximaal één dienst toegewezen
# DIT MOET NOG VERDER AANGEPAST WORDEN VOERTUIGEN KUNNEN WEL MEER DAN 1 DIENST RIJDEN
for i in range(aantal_voertuigen):
    m += xsum(x[i][j] for j in range(aantal_diensten)) <= 1

# CONSTRAINT 02
# ELKE DIENST MOET DOOR 1 VOERTUIG GEREDEN WORDEN
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen)) == 1

# CONSTRAINT 03
# EEN VOERTUIG MOET BESCHIKBAAR ZIJN OM AAN EEN DIENST TE KUNNEN TOEGEWEZEN WORDEN
for j in range(aantal_diensten):
    m += xsum(x[i][j] * voertuig_beschikbaar[i] for i in range(aantal_voertuigen)) == 1

# CONSTRAINT 04
# HET TYPE VAN EEN DIENST MOET GELIJK ZIJN AAN HET TYPE VAN EEN VOERTUIG
# type voertuig = type dienst => 1
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.iloc[i, 3] == dienst.iloc[j, 3]) == 1

# CONSTRAINT 05
# HET SUBTYPE VAN EEN DIENST MOET GELIJK ZIJN AAN HET SUBTYPE VAN EEN VOERTUIG
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.iloc[i, 4] == dienst.iloc[j, 4]) == 1

# CONSTRAINT 06
# HET RIJBEREIK VAN EEN VOERTUIG MOET GROTER ZIJN DAN HET AANTAL KM VAN EEN DIENST
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.iloc[i, 10] < dienst.iloc[j, 7]) == 0

# CONSTRAINT 07
# DIENSTEN IN LEZ ZONE MOET GEREDEN WORDEN DOOR VOERTUIGEN DIE LEZ OK ZIJN
for j in range(aantal_diensten):
    for i in range(aantal_voertuigen):
        if dienst_lez[j] == 1:
            m += x[i][j] <= voertuig_lez_ok[i]
        else:
            m += x[i][j] <= 1

# CONSTRAINT 08
# DIENSTEN MET EEN HOOGTE PROBLEEM (te lage tunnels) MOET GEREDEN WORDEN DOOR VOERTUIG ZON DER HOOGTE PROBLEEM
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.iloc[i, 9] == dienst.iloc[j, 10] == 1) == 0

# CONSTRAINT 09
# EEN DIENST DIE DOOR EEN ELEKTRISCH VOERTUIG VRAAGT MOET GEREDEN WORDEN DOOR EEN ELEKTRISCHE BUS GEREDEN WORDEN
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen) if voertuig.iloc[i, 7] < dienst.iloc[j, 9] ) == 0

# OPTIMALISEER HET MODEL
m.optimize()

# Toon de toegewezen voertuigen aan ritten
for j in range(aantal_diensten):
    for i in range(aantal_voertuigen):
        if x[i][j].x >= 0.99:
            toegewezen_voertuig.append(i + 1)

planning = dienst
planning['voertuig'] = toegewezen_voertuig

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

print(planning)
planning.to_excel("data/PLANNING.xlsx", index=False)