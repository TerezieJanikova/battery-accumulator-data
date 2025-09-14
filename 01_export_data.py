import requests
import pandas as pd

hs_codes = [
    '16850610', '16850630', '16850640', '16850650', '16850660', '16850680', '16850690',
    '16850710', '16850720', '16850730', '16850740', '16850750', '16850760', '16850780', '16850790'
]

years = [2018, 2019, 2020, 2021, 2022, 2023]

base_url = "https://api-v2.oec.world/tesseract/data.jsonrecords"

all_records = []

def fetch_data(hs, year, cube):
    params = {
        'cube': cube,
        'drilldowns': 'Exporter Country,Year',
        'measures': 'Trade Value',
        'HS6': hs,
        'Year': year,
        'limit': 1000,
        'offset': 0,
        'locale': 'en'
    }
    records = []
    while True:
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Chyba {response.status_code} pro HS6={hs} Rok={year} cube={cube}")
            break
        json_data = response.json()
        total = json_data['page']['total']
        data = json_data.get('data', [])
        if not data:
            break
        records.extend(data)
        params['offset'] += params['limit']
        if params['offset'] >= total:
            break
    return records

for hs in hs_codes:
    for year in years:
        data = fetch_data(hs, year, 'trade_i_baci_a_96')
        if not data:
            # Pokud není data v hlavním cube, zkus alternativní
            data = fetch_data(hs, year, 'trade_i_baci_a_12')
            cube_used = 'trade_i_baci_a_12'
        else:
            cube_used = 'trade_i_baci_a_96'
        if data:
            for rec in data:
                rec['HS6'] = hs
                rec['Cube'] = cube_used
            all_records.extend(data)
            print(f"Staženo {len(data)} záznamů HS6={hs} Rok={year} Cube={cube_used}")
        else:
            print(f"Žádná data HS6={hs} Rok={year}")

df = pd.DataFrame(all_records)
df.to_csv('oec_all_data_combined.csv', index=False)
print("Hotovo. Data uložena do oec_all_data_combined.csv")
