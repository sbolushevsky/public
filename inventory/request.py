import requests
import re


def cdd_request():
    base_url = "None"
    api_key_wr = "None"
    api_key_r = "None"

    headers = {'token': api_key_r}
    url = base_url + "molecules"

    ind = input("\nPut in IND: ").strip().upper()
    ind_number = re.findall('[0-9]{7}', ind)[0]

    params = {'names': ['IND' + '-' + ind_number]}
    response = requests.request("GET", url, params=params, headers=headers)

    # to view the detailed JSON return content:
    response.json()
    obj = response.json()

    if obj.get('count') == 0:
        print('\nCompound is not found on CDD\n')
    else:
        data = obj.get('objects')[0]
        batches = data.get('batches')
        # print(batches)
        owner = data.get('owner')
        print("—" * 155 + f"\nOwner: {owner}\n")

        for batch in batches:
            # print(batch)
            molecule_batch_identifier = batch.get('molecule_batch_identifier')
            batch_info = batch.get('batch_fields')
            mw = batch.get('formula_weight')
            IND_Location_DMSO = batch_info.get('IND Location DMSO')
            person = batch_info.get('Person')
            inventor = batch_info.get('Inventor')
            Solid_Stock_Location = batch_info.get('Solid Stock Location')
            BATCH_COMMENT = batch_info.get('BATCH_COMMENT')
            note = batch_info.get('Note')

            print(
                f"{molecule_batch_identifier}:\nMW = {mw}, LS: {IND_Location_DMSO}, SS: {Solid_Stock_Location}, p: {person}, i: {inventor}, c: {BATCH_COMMENT}, n: {note}\n")

    print("—" * 155)
    print("MW - molecular weight, LS - liquid stock, SS - solid stock, p - Person, i - Inventor, c - Batch comment, "
          "n - Note")


def main():
    """  """

    while True:
        try:
            cdd_request()
        except IndexError:
            print("\nPlease put in 7-digit number\n")


if __name__ == "__main__":
    main()
