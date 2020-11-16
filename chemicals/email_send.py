import win32com.client as client
import pandas as pd
import cirpy
from PIL import Image
import io
import os


def main():

    chemicals = pd.read_excel(r"c:\Users\sbolushevsky\Documents\chemicals\Chemical_Orders_Receiving.xlsx",
                              usecols=["Person Ordering", "Chemical Name", "Hazard Designation"])

    delete_rows = chemicals[chemicals["Person Ordering"] == "Sergei Bolushevsky"].index
    chemicals = chemicals.drop(delete_rows)
    chemicals["Chemical Name"].str.strip()
    chemicals.drop_duplicates(inplace=True)
    chemicals['Person Ordering'] = chemicals['Person Ordering'].apply(lambda x: x.split()[0])
    chemicals.insert(loc=2, column='pic', value=['' for i in range(chemicals.shape[0])])

    os.chdir(r"C:\Users\sbolushevsky\Documents\chemicals\pic")

    name = 1
    for i in chemicals.index:

        try:
            f = cirpy.resolve_image(chemicals.loc[i, "Chemical Name"], fmt=u'gif', width=200, height=200,
                                    symbolfontsize=8)
            image = Image.open(io.BytesIO(f))
            image.save(f"image{name}.gif")
            chemicals.loc[i, "pic"] = f"image{name}.gif"
            name += 1
        except Exception as e:
            print(i, e)

    def path_to_image_html(path):
        return '<img src="' + path + '" width="150" >'

    url = {}
    for root, dirs, files in os.walk(r"C:\Users\sbolushevsky\Documents\chemicals\pic", topdown=False):
        for file in files:
            path = os.path.join(root, file)
            url[file] = path_to_image_html(path)

    for i in chemicals.index:
        if chemicals.loc[i, "pic"] in url.keys():
            chemicals.loc[i, "pic"] = url[chemicals.loc[i, "pic"]]
        else:
            chemicals.loc[i, "pic"] = '<p style="text-align: center;">no image</p>'

        if chemicals.loc[i, "Hazard Designation"] not in ["4°C", "-20°C"]:
            chemicals.loc[i, "Hazard Designation"] = '<p style="text-align: center;">rt</p>'

    chemicals.sort_values(by=['Person Ordering'], inplace=True)
    chemicals.rename(columns={'Person Ordering': 'Person', 'Hazard Designation': 'TS'}, inplace=True)

    if chemicals.shape[0] == 0:
        return print("No email sent")
    else:

        clist = 'Conrad, Jay <Jay.Conrad@ucsf.edu>; Gomes, Mellanie <Mellanie.Gomes@ucsf.edu>; Raikar, ' \
                'Sandeep <Sandeep.Raikar@ucsf.edu>; Ramirez, Cristian <Cristian.Ramirez@ucsf.edu>; Sin, ' \
                'Ny <Ny.Sin@ucsf.edu>; Viart, Helene <Helene.Viart@ucsf.edu>; West, John W <John.West@ucsf.edu> '

        outlook = client.Dispatch("Outlook.Application")
        message = outlook.CreateItem(0)

        message.Display()
        message.To = clist
        message.Subject = '~CHEMICALS READY FOR PICKUP~'

        message.HTMLBody = chemicals.to_html(index=False, escape=False)
        #message.Safe()
        #message.Send()

        return print("Email sent")


if __name__ == "__main__":
    main()
