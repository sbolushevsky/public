import pandas as pd
import subprocess


def main():
    """Generates a list of labels to print from the list of full IND#s """

    df = pd.read_excel(NONE)

    IND_list = []

    while True:
        s = input("Scan in a IND#: ")
        if 'IND' in s:
            IND_list.append(s.strip())
        else:
            break

    IND_list = list(set(IND_list))
    print(IND_list)

    for i in range(len(IND_list)):
        if "" in IND_list:
            IND_list.remove("")

    print(f'\nThere are {len(IND_list)} novel compounds')
    df_toprint = df[df["DSI+batch"].isin(IND_list)]
    df_toprint.to_excel("to_print.xlsx", index=False)
    print(f'There are {df_toprint.shape[0]} labels to print')

    print("\nDone! Ready to print")

    return subprocess.run('start DSI_label_ver3.5.lbx', shell=True)


if __name__ == "__main__":
    main()
