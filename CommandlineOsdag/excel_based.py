from pathlib import Path

import pandas as pd
from colorama import Fore
from CommandlineOsdag.FinPlate import FinPlate
class Workbook():
    def __init__(self,filepath):
        df = pd.DataFrame(pd.read_excel(filepath,header=[0,1,2]))
        df.dropna()
        df.values.astype(str)
        self.total_records=[]
        for index,series in df.iterrows():
            self.total_records.append(FinPlate(0,series))
        self.design_statuses = [record.design_status for record in self.total_records]
        self.file_name=["report"+str(i) for i in range(len(self.total_records))]
        self.output()


    def apply(self,func,list):
        return map(func,list)
    def addSeriesOutput(self):
        return self.apply(FinPlate.return_output,self.total_records)
    def output(self):
        print()
        print(Fore.LIGHTMAGENTA_EX + '----------------------------------------------------')
        print(Fore.CYAN + "Output")
        print(Fore.GREEN + "Select Output")
        print(Fore.GREEN + '1.', 'Show Output')
        print(Fore.GREEN + '2.', 'Save Design Report')
        print(Fore.GREEN + '3.', 'Save Output to Excel')
        print(Fore.GREEN + '4.', 'Show Design Dictionary')
        print(Fore.GREEN + '5.', 'Exit')
        output = input(Fore.BLUE + 'Enter Output: ')
        if output == '1':
            self.show_outputs()
            self.output()
            return
        elif output == '2':
            print(Fore.YELLOW+'Enter File Path to Save: ')
            file_path=input()
            self.design_reportInput()
            filepath = Path(file_path)
            filepath.parent.mkdir(parents=True, exist_ok=True)


            for i in range(len(self.total_records)):
                self.total_records[i].save_design(self.design_popup(self.design_statuses[i],file_path+self.file_name[i]))
            self.output()
            return
        elif output == '3':
            self.save_output_to_excels()
            self.output()
            return
        elif output == '4':
            self.show_design_dicts()
            self.output()
            return
        elif output=='5':
            return
        else:
            print(Fore.RED + 'Invalid Input')
            self.output()

    def show_outputs(self):
        x = list(map(FinPlate.show_output,self.total_records))
        print(x)
    def design_reportInput(self):
        self.companyName = input(Fore.BLUE+'Enter Company Name (Leave Empty if want to): ')
        self.companyLogo = input(Fore.BLUE+'Enter Path of Company Logo (Leave Empty if want to): ')
        self.teamName = input(Fore.BLUE+'Enter Team Name (Leave Empty if want to): ')
        self.designer = input(Fore.BLUE+'Enter Designer Name (Leave Empty if want to): ')
        self.ProjectName = input(Fore.BLUE+'Enter Project Name (Leave Empty if want to): ')
        self.subtitle = input(Fore.BLUE+'Enter Subtitle (Leave Empty if want to): ')
        self.jobNumber = input(Fore.BLUE+'Enter Job Number (Leave Empty if want to): ')
        self.Client = input(Fore.BLUE+'Enter Client Name (Leave Empty if want to): ')

        # filename = input(Fore.BLUE+'Enter File Path with name to save (Leave Empty if want to): ')



    def design_popup(self,design_status,filename):
        popup_summary={}
        print(Fore.MAGENTA+"------------Save Design Report------------")
        print(Fore.GREEN+"Save Design Report")
        popup = {
            'ProfileSummary': {'CompanyName': '113', 'CompanyLogo': '', 'Group/TeamName': '', 'Designer': ''},
            'ProjectTitle': '', 'Subtitle': '', 'JobNumber': '', 'AdditionalComments': '', 'Client': '',
            'filename': '/home/sagar/Osdag/sagar', 'does_design_exist': True,
            'logger_messages': '2022-08-01 14:56:42 - Osdag - WARNING - : The value of factored shear force is less than the minimum recommended value. Setting the value of the shear force to 15% of the supported beam shear capacity or 40 kN, whichever is lesser [Ref. IS 800:2007, Cl.10.7].\n2022-08-01 14:56:42 - Osdag - INFO - === End Of Design ===\n2022-08-01 14:56:42 - Osdag - INFO - : The minimum recommended weld throat thickness suggested by IS 800:2007 is 3 mm, as per cl. 10.5.3.1. Weld throat thickness is not considered as per cl. 10.5.3.2. Please take necessary detailing precautions at site accordingly.'}

        print(Fore.CYAN+"Profile Summary")
        profile_summary={}



        profile_summary['CompanyName']=self.companyName
        profile_summary['CompanyLogo']=self.companyLogo
        profile_summary['Group/TeamName']=self.teamName
        profile_summary['Designer']=self.designer
        popup_summary['ProfileSummary']=profile_summary

        print(Fore.CYAN+"Design Summary")

        popup_summary['ProjectTitle']=self.ProjectName
        popup_summary['Subtitle']=self.subtitle
        popup_summary['JobNumber']=self.jobNumber
        popup_summary['AdditionalComments']=''


        popup_summary['Client']=self.Client
        popup_summary['filename']=filename
        popup_summary['does_design_exist']=design_status
        popup_summary['logger_messages']=''
        return popup_summary
    def show_design_dicts(self):
        x = list(map(FinPlate.show_design_dict,self.total_records))
        print(x)

    def save_output_to_excels(self):
        print(
            Fore.YELLOW+"Enter File Path"
        )
        file_path= r'C:\Users\sagar\OneDrive\Desktop\batch\abd.xlsx'
        seriesOutput = [map for map in self.apply(FinPlate.return_output,self.total_records)]

        df = pd.concat(seriesOutput)
        df.to_excel(file_path)



