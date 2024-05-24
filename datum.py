import pandas as pd
from datetime import datetime

dienst = pd.read_excel("data/TEST_DIENSTEN.xlsx")

# Converteer de 'datum' kolom naar datetime als dat nog niet is gebeurd
dienst['startdatum'] = pd.to_datetime(dienst['startdatum'])
dienst['einddatum'] = pd.to_datetime(dienst['einddatum'])

# Combineer 'datum' en 'start' kolommen
dienst['startdatuur'] = dienst.apply(lambda row: datetime.combine(row['startdatum'], row['start']), axis=1)
dienst['einddatuur'] = dienst.apply(lambda row: datetime.combine(row['einddatum'], row['eind']), axis=1)
dienst['delta'] = (dienst['einddatuur']-dienst['startdatuur'])
dienst['verschil_in_seconden'] = (dienst['einddatuur'] - dienst['startdatuur']).dt.total_seconds()

print(dienst)
