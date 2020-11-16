
import requests
import pandas as pd
import re
from datetime import datetime
import json


def main():
    base_url = "NONE"
    api_key_wr = "NONE"
    headers = {'token': api_key_wr}

    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    file_name_date = str(now.strftime("%y%m%d"))
    new_data = {k: [] for k in
                ['', 'Compound Name', 'Compound Name2', 'Batch', 'amount used', 'amount remaining', 'location']}

    while True:

        try:
            ind = input("\nPut in IND#(w/batch). Hit ENTER when done: ")
            t = re.findall(r"(IND-[0-9]{7})(.{6})", ind.strip())
            ind_number, batch_number = t[0]
        except IndexError:
            break

        mol_url = base_url + "molecules"

        new_data.setdefault('').append(ind)
        new_data.setdefault('Compound Name').append(ind_number)
        new_data.setdefault('Compound Name2').append(ind_number)
        new_data.setdefault('Batch').append(batch_number)

        params = {'names': ind_number}
        response = requests.request("GET", mol_url, params=params, headers=headers)
        obj = response.json()
        data = obj.get('objects')[0]
        ind_id = data.get('id')

        show_batches = [(batch['name'], batch['id']) for batch in data.get('batches')]

        batch_id = []
        for batch_tuple in show_batches:
            if batch_number in batch_tuple:
                batch_id.append(batch_tuple[1])

        if len(batch_id) == 0:
            print(f"{ind_number}: batch {batch_number} doesn't exist on ...")

        url = base_url + "protocols/52414/data"
        params_api = {'molecules': ind_id}

        response = requests.request("GET", url, params=params_api, headers=headers)
        obj_api = response.json()
        data_api = obj_api.get('objects')

        batch_select = [data for data in data_api if batch_id[0] in data.values()]

        try:
            last_run = batch_select[len(batch_select) - 1]
            last_readout = last_run.get('readouts')

            # amount_used, amount_remaining, location = last_readout['596734'], last_readout['596733'], last_readout['600784']
            amount_remaining, location = last_readout['596733'], last_readout['600784']
            print(f'{ind}: Amount Remaining: {amount_remaining}, Location: {location}')

        except IndexError:
            print(f'{ind_number + batch_number} is not in API protocol')

        amount_used = str(input('Put in amount used (g): ')) + "g"
        amount_remaining_2 = str(float(amount_remaining.strip('g')) - float(amount_used.strip('g'))) + 'g'
        print(amount_remaining_2)

        new_data.setdefault('amount used').append(amount_used)
        new_data.setdefault('amount remaining').append(amount_remaining_2)
        new_data.setdefault('location').append(location)

    file_path = "C:\\Users\\sbolushevsky\\Documents\\inventory\\API\\" + file_name_date + "upload.csv"
    data = pd.DataFrame.from_dict(new_data)
    data.rename(columns={'Compound Name2': 'Compound Name'}, inplace=True)

    print(data)
    data.to_csv(file_path, index=False)

    url_upd = 'NONE'
    headers_upd = {"Token": api_key_wr}

    data = {'mapping_template': 15461, 'project': 11667, 'runs': {'run_date': str(current_date)}}
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url_upd, headers=headers_upd, data={'json': json.dumps(data)}, files=files)

    api_url = response.json().get('api_url')

    while True:
        state = requests.get(api_url, headers=headers_upd)

        if state.json().get('state') != "committed":
            continue
        else:
            print(f"\nDone")
            break


if __name__ == "__main__":
    main()
