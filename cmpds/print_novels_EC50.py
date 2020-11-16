import pandas as pd
import subprocess


def main():
    """Generates a list of labels to print from an assay file. The file needs to be renamed to
    "M83.xlsx" """

    df = pd.read_excel(r"\\Som001.som.ucsf.edu\IND$\Shared\Prusiner\DrugDiscovery\Medicinal Chemistry\cmpds manage\cmpds management@UCSF_ver3.3.xlsx")
    df2 = pd.read_excel("M83.xlsx")

    df2 = df2[df2["Note"].str.strip() == "novel"]
    print(f'There are {df2.shape[0]} novel compounds in the list')

    df_toprint = df[df["DSI+batch"].isin(df2.iloc[:, 4].to_list())]

    df_toprint.to_excel("to_print.xlsx", index=False)
    print(f'There are {df_toprint.shape[0]} labels were chosen for printing')

    if df2.shape[0] != df_toprint.shape[0]:
        missing = pd.concat([df2.iloc[:, 4], df2.iloc[:, 4].isin(df["DSI+batch"])], axis=1)
        print(missing)

    print("\nDone! Ready to print\n")

    return subprocess.run('start DSI_label_ver3.5.lbx', shell=True)


if __name__ == "__main__":
    main()