### Returns repeats with more than one location

import requests
import pandas as pd
import re


def main():
    """The file needs to be renamed to
    "M83.xlsx" """

    base_url = "NONE"
    api_key_r = "NONE"
    headers = {'token': api_key_r}
    url = base_url + "molecules"

    df = pd.read_excel("M83.xlsx")
    df2 = df[df["Note"].str.strip() == "repeat"]
    repeats = df2['Unnamed: 4'].tolist()

    for repeat in repeats:
        t = re.findall(r"(IND-[0-9]{7})(.{6})", repeat)
        ind_number, batch_number = t[0]

        params = {'names': ind_number}
        response = requests.request("GET", url, params=params, headers=headers)
        obj = response.json()
        data = obj.get('objects')[0]

        show_batches = [(batch['name'], batch['id']) for batch in data.get('batches')]

        batch_id = []
        for batch_tuple in show_batches:
            if batch_number in batch_tuple:
                batch_id.append(batch_tuple[1])

        if len(batch_id) == 0:
            print(f"{ind_number}: batch {batch_number} doesn't exist on CDD")

        batch_info = [batch.get('batch_fields') for batch in data.get('batches') if batch_id[0] in batch.values()]
        ind_location = batch_info[0]['IND Location DMSO']

        if ";" in ind_location:
            print(f'\n{ind_number + batch_number}: ')
            print(f"Location: {ind_location}")

        try:
            note = batch_info[0]['Note']
            if "empty" in note:
                print(f"Note: empty tube! ---> {note}")
        except KeyError:
            continue


if __name__ == "__main__":
    main()
