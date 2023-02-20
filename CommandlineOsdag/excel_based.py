import sys
from pathlib import Path

import pandas as pd
from colorama import Fore
from CommandlineOsdag.FinPlate import FinPlate
from CommandlineOsdag.common_fn import *
from CommandlineOsdag.EndPlate import EndPlate
from Common import *
from CommandlineOsdag.ColumnCoverPlate import BeamCoverPlateBolted
class Workbook():

    def __init__(self,filepath):
        if True:

            df = pd.DataFrame(pd.read_excel(filepath,header=[0,1,2]))
            df.dropna()
            print(df.head(1))
            df.values.astype(str)
            self.total_records=[]
            for index,series in df.iterrows():
                module = getModule(series)
                print(series.tolist())
                if module=="FinPlate":
                    self.total_records.append(FinPlate(0,series))
                elif module=="EndPlate":
                    pass
                    # self.total_records.append(EndPlate(series))
                elif module=="BBCoverPlateBolted":
                    self.total_records.append(BeamCoverPlateBolted(0,series))

            self.design_statuses = [record.design_status for record in self.total_records]

        # Print design Status

        print(Fore.LIGHTMAGENTA_EX + '----------------------------------------------------')
        for i,v in enumerate(self.total_records):
            if v.design_status:
                print(Fore.GREEN + str(i) +". " + v.module_name() +  " Design is Successful")
            else:
                print(Fore.RED + str(i) +". " + v.module_name() +  " Design is Not Successful")


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
        print(Fore.GREEN + '3.', 'Show Design Dictionary')
        print(Fore.GREEN + '4', 'Save Output to excel')
        print(Fore.GREEN + '5.', 'Exit')
        output = input(Fore.BLUE + 'Enter Output: ')
        if output == '1':
            try:

                self.show_outputs()
                self.output()
            except:
                print(Fore.RED+"Invalid Output")
                self.output()
            return
        elif output == '2':
            try:
                print(Fore.YELLOW+'Enter File Path to Save: ')
                file_path=input()
                self.design_reportInput()
                filepath = Path(file_path)
                filepath.parent.mkdir(parents=True, exist_ok=True)

                for i in range(len(self.total_records)):
                    self.total_records[i].save_design(
                        self.design_popup(self.design_statuses[i], file_path + self.file_name[i]))
                self.output()
                return
            except:
                print(Fore.RED+"Invalid File Path")
                self.output()



        elif output == '3':
            self.show_design_dicts()
            self.output()
            return
        elif output=='4':
            self.save_output_to_excel()
            self.output()
        elif output=='5':
            sys.exit()

        else:
            print(Fore.RED + 'Invalid Input')
            self.output()

    def show_outputs(self):
        for i in self.total_records:
            i.show_output()
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
        for i in self.total_records:
            i.show_design_dict()

    def save_output_to_excel(self):
        for i in self.total_records:

            print("Enter File Name : ")
            name = input()
            import pandas as pd
            out_list = i.output_values(i.design_status)
            in_list = i.design_inputs.items()
            to_Save = {}
            flag = 0
            for option in out_list:
                if option[0] is not None and option[2] == TYPE_TEXTBOX:
                    to_Save[option[0]] = option[3]
                    if str(option[3]):
                        flag = 1
                if option[2] == TYPE_OUT_BUTTON:
                    tup = option[3]
                    fn = tup[1]
                    for item in fn(i.design_status):
                        lable = item[0]
                        value = item[3]
                        if lable != None and value != None:
                            to_Save[lable] = value
            df = pd.DataFrame(i.design_inputs.items())
            # df.columns = ['label','value']
            # columns = [('input values','label'),('input values','value')]
            # df.columns = pd.MultiIndex.from_tuples(columns)

            df1 = pd.DataFrame(to_Save.items())
            # df1.columns = ['label','value']
            # df1.columns = pd.MultiIndex.from_product([["Output Values"], df1.columns])

            bigdata = pd.concat([df, df1], axis=1)
            bigdata.to_csv(name + ".csv", index=False, header=None)






