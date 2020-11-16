import requests
import pandas as pd


def return_list():
    link = r"c:\Users\sbolushevsky\Documents\cmpds\locations_syn.csv"
    b = pd.read_csv(link, names=['DSI#', 'Location', 'Stock', 'Comment', 'SS Location'])
    a = b["DSI#"].str.extract(r"(IND-[0-9]{7})(.{6})")

    dsi_data2 = pd.concat([b.copy(), a], axis=1)
    dsi_data2["IND#"] = dsi_data2[0]
    dsi_data2["Batch Name"] = dsi_data2[1]

    dsi_data_result0 = dsi_data2[dsi_data2["DSI#"].str.contains("IND", regex=True) == True]

    dsi_data_result = dsi_data_result0.copy()
    dsi_data_result = dsi_data_result.rename(columns={"IND#": "Molecule Name"})

    return dsi_data_result[["Molecule Name", "Batch Name", "Location", "Stock", "Comment", "SS Location"]]


class Upd:

    def __init__(self, index):
        db = return_list()

        self.index = index
        self.ind = db.loc[self.index, 'Molecule Name']
        self.batch = db.loc[self.index, 'Batch Name']
        self.liqloc = db.loc[self.index, 'Location']
        self.conc = db.loc[self.index, 'Stock']
        self.comm = db.loc[self.index, 'Comment']
        self.sllock = db.loc[self.index, 'SS Location']

        # ind_reex = re.findall(r'(IND-)([0-9]{7})', self.ind)
        # self.ind_number = ind_reex[0][1]


class Cdd(Upd):

    def __init__(self, index):
        super().__init__(index)
        self.index = index
        self.ind = Upd(self.index).ind

        url = Auth().base_url + "molecules"

        params = {'names': self.ind}
        response = requests.request("GET", url, params=params, headers=Auth().headers)

        # to view the detailed JSON return content:
        self.obj = response.json()
        self.data = self.obj.get('objects')[0]

    def show_batches(self, ind_batch_number):

        show_batches = [(batch['name'], batch['id']) for batch in Cdd(self.index).data.get('batches')]

        batch_id = []
        for batch_tuple in show_batches:
            if ind_batch_number in batch_tuple:
                batch_id.append(batch_tuple[1])

        if len(batch_id) == 0:
            print(f"{self.ind}: batch {ind_batch_number} is not found on CDD")

        else:
            return batch_id[0]


class Auth:

    def __init__(self):
        self.base_url = "https://app.collaborativedrug.com/api/v1/vaults/3370/"
        api_key_wr = "MTI2M3xsUUJxbkJ5ZFVLaE1ST2p3WXliN09mSnZxeGVyMGg5ZjRmb20veXdVRTB5M2lsUVFaQT09"
        api_key_r = "MTI1N3xqOGhMMnpnUnpwelVNTUxFYUlVTzlKQU83ZS9PSnFVdmdTQ2FRVkI0VTRFakc3UUxsdz09"
        self.headers = {'X-CDD-token': api_key_wr}


def main():
    b = return_list()

    for i in b.index:
        ind = Upd(i).ind
        ind_batch_number = Upd(i).batch

        d_new_temp = {'IND Location DMSO': b.loc[i, "Location"], 'Solid Stock Location': b.loc[i, "SS Location"],
                      'Note': b.loc[i, "Comment"], 'BATCH_COMMENT': b.loc[i, "Stock"]}

        d_upd = {key: val for key, val in d_new_temp.items() if pd.Series(val).notna().all()}
        # print(d_upd)

        try:
            Cdd(i).data
        except IndexError:
            print(f'\nCompound {ind} is not on CDD\n')
            continue

        batch_id = Cdd(i).show_batches(ind_batch_number)
        batch_info = [batch.get('batch_fields') for batch in Cdd(i).data.get('batches') if
                      batch_id in batch.values()]

        keys = ['IND Location DMSO', 'Solid Stock Location', 'Note', 'BATCH_COMMENT']

        try:
            d_cdd = {key: batch_info[0][key] for key in keys if key in batch_info[0].keys()}
        except IndexError:
            continue

        final = {k: v for k, v in d_upd.items()}
        # print(final)
        print('-' * 50)
        print(f'{ind + ind_batch_number}:')

        if 'BATCH_COMMENT' in d_cdd.keys() and 'BATCH_COMMENT' in d_upd.keys():
            print(f"- old stock comment: {d_cdd['BATCH_COMMENT']}")
            final.pop('BATCH_COMMENT')
        elif 'BATCH_COMMENT' not in d_cdd.keys() and 'BATCH_COMMENT' in d_upd.keys():
            final['BATCH_COMMENT'] = d_upd['BATCH_COMMENT']
            print(f"- new stock comment for BATCH_COMMENT ---> {d_upd['BATCH_COMMENT']}")

        update_list = [i for i in d_upd.keys() if i != 'BATCH_COMMENT']

        for key in update_list:
            if key not in d_cdd.keys():
                d_cdd[key] = d_upd[key]
                print(f'- new value for {key}: {d_upd[key]}')
            else:
                final[key] = d_cdd[key] + '; ' + d_upd[key]
                print(f'- more than one value for {key}: {final[key]}')

        # print(f'final{final}')
        print('-' * 50)

        url_molecule = Auth().base_url + "batches/" + str(batch_id)
        molecule_params = {'batch_fields': final}

        requests.request("PUT", url_molecule, json=molecule_params, headers=Auth().headers)


if __name__ == "__main__":
    main()
