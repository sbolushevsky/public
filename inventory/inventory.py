import os
import pandas as pd
from IPython.display import display

print("Local database is being loaded...")


class Auth:

    def __init__(self):
        list_1 = ["DSI Barcode", "MW", "Liquid Stock Box Name", "Liquid Stock Location", "Chemist Name", "Assay Date"]
        data1 = pd.read_excel(
            r"Chemical inventory\SYN.xlsx",
            sheet_name="Sheet2", usecols=list_1, dtype=object)

        self.data1_copy = data1.copy()[list_1].rename(
            columns={"DSI Barcode": "DSI-#", "Liquid Stock Box Name": "LS Box",
                     "Liquid Stock Location": "LS Location",
                     "Chemist Name": "Chemist"})

        data2 = pd.read_excel(
            r"Chemical inventory\TAU.xlsx",
            sheet_name="Sheet1", usecol=list_1, dtype=object)
        self.data2_copy = data2.copy()[list_1].rename(
            columns={"DSI Barcode": "DSI-#", "Liquid Stock Box Name": "LS Box",
                     "Liquid Stock Location": "LS Location",
                     "Chemist Name": "Chemist"})

        list_2 = ["DSI-#", "Location"]
        data3 = pd.read_excel(
            r"ChemicalSYN.xlsx",
            sheet_name="Final Compound Storage Location", usecols=list_2, dtype=object)

        self.data3_copy = data3.copy().rename(columns={"Location": "SS Location"})

        data4 = pd.read_excel(
            r"ChemicalTU.xlsx",
            sheet_name="Final Compound Storage Location", usecols=list_2, dtype=object)
        self.data4_copy = data4.copy().rename(columns={"Location": "SS Location"})

        data5 = pd.read_excel(
            r"Chemical SYN.xlsx",
            sheet_name="Biolab Syn Locations", usecols=["DSI-#", "Location", "Comment_1", "Comment_2"], dtype=object)
        self.data5_copy = data5.copy().rename(columns={"Location": "IND Location"})

        data6 = pd.read_excel(
            r"Chemical inventoryTAU.xlsx",
            sheet_name="Biolab tau locations", usecols=["DSI-#", "Location", "Comment"], dtype=object)
        self.data6_copy = data6.copy().rename(columns={"Location": "IND Location"})


class SearchResults:

    def __init__(self, IND, data):

        self.data = data
        self.IND = IND
        self.search_in_SYN_LS = data.data1_copy["DSI-#"].str.contains(IND, na=False)
        self.search_in_TAU_LS = data.data2_copy["DSI-#"].str.contains(IND, na=False)

        self.search_in_SYN_SS = data.data3_copy["DSI-#"].str.contains(IND, na=False)
        self.search_in_TAU_SS = data.data4_copy["DSI-#"].str.contains(IND, na=False)

        self.search_in_SYN_SS_bio = data.data5_copy["DSI-#"].str.contains(IND, na=False)
        self.search_in_TAU_SS_bio = data.data6_copy["DSI-#"].str.contains(IND, na=False)

    def show(self):

        if all([self.search_in_SYN_LS.any() != True, self.search_in_TAU_LS.any() != True,
                self.search_in_SYN_SS.any() != True,
                self.search_in_TAU_SS.any() != True, self.search_in_SYN_SS_bio.any() != True,
                self.search_in_TAU_SS_bio.any() != True]):
            print("Not found")

        else:

            df_list = [self.data.data1_copy[self.search_in_SYN_LS], self.data.data2_copy[self.search_in_TAU_LS],
                       self.data.data3_copy[
                           self.search_in_SYN_SS], self.data.data4_copy[self.search_in_TAU_SS],
                       self.data.data5_copy[self.search_in_SYN_SS_bio],
                       self.data.data6_copy[self.search_in_TAU_SS_bio]]

            dfs = [i for i in df_list if i.empty == False]
            df_final = pd.concat([df.set_index('DSI-#') for df in dfs], axis=1, sort=False)
            # pd.concat([df.set_index('name') for df in dfs], axis=1, join='inner').reset_index()
            display(df_final)

    def alternate_output(self):

        print(
            f"\n {self.data.data1_copy[self.search_in_SYN_LS].set_index('DSI-#')}" if self.search_in_SYN_LS.any() else "")
        print(
            f"\n {self.data.data2_copy[self.search_in_TAU_LS].set_index('DSI-#')}" if self.search_in_TAU_LS.any() else "")
        print(
            f"\n {self.data.data3_copy[self.search_in_SYN_SS].set_index('DSI-#')}" if self.search_in_SYN_SS.any() else "")
        print(
            f"\n {self.data.data4_copy[self.search_in_TAU_SS].set_index('DSI-#')}" if self.search_in_TAU_SS.any() else "")
        print(
            f"\n {self.data.data5_copy[self.search_in_SYN_SS_bio].set_index('DSI-#')}" if self.search_in_SYN_SS_bio.any() else "")
        print(
            f"\n {self.data.data6_copy[self.search_in_TAU_SS_bio].set_index('DSI-#')}" if self.search_in_TAU_SS_bio.any() else "")

        if all([self.search_in_SYN_LS.any() != True, self.search_in_TAU_LS.any() != True,
                self.search_in_SYN_SS.any() != True,
                self.search_in_TAU_SS.any() != True, self.search_in_SYN_SS_bio.any() != True,
                self.search_in_TAU_SS_bio.any() != True]):
            print("Not found")


def main():
    """  """

    new_networked_directory = r'NONE'
    os.chdir(new_networked_directory)
    data = Auth()

    while True:

        ind = input("\nPut in IND#: ").upper().strip()
        note = "\nThere's something wrong with the value. Please, see alternate data output for this value:"

        try:
            search_results = SearchResults(ind, data)
            print("—" * 130)
            search_results.show()
            print("—" * 130)
        except ValueError:

            print(note)
            print("—" * int(len(note)))
            SearchResults(ind, data).alternate_output()
            print("—" * int(len(note)))



if __name__ == "__main__":
    main()
