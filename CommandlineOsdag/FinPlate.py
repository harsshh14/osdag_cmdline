import logging
import sys

import yaml

import prettytable
import colorama
from colorama import Fore
from CommandlineOsdag.design_type_v2.connection.fin_plate_connection import FinPlateConnection

from Common import *
from utils.common.other_standards import PATH_TO_DATABASE
import pandas as pd
colorama.init(autoreset=True)
class FinPlate(FinPlateConnection):
    def __init__(self,**kwargs):
        super().__init__()
        self.design_dict={}

        self.design_pref_inputs={}
        self.design_pref()
        self.input_dock_inputs = self.input_values()
        # self.designPrefDialog = DesignPreferences(input_dictionary=self.input_dock_inputs)

        self.input()
        # fin.show_design_dict()

        self.set_inputs()
        self.output()
    def workbook(self):
        import pandas as pd

        df = pd.read_excel("inputStructure.xlsx")
        df = pd.DataFrame(df)
        self.design_dict['']
        print(df["Connectivity"][2])

    def set_factored_loads(self):


        self.sherd_loads = input("Enter Shear Load")
        self.design_dict['Load.Shear'] = self.sherd_loads
        self.axial_force = input("Enter Axial Force")
        self.design_dict['Load.Axial'] = self.axial_force

    def set_bolt(self):
        print()
        print()
        print(Fore.GREEN+"Enter bolt details")
        print(Fore.GREEN+'1.', 'Bolt Type')
        print(Fore.GREEN+'2.', 'Bolt Diameter')
        print(Fore.GREEN+'3.', 'Bolt Grade')
        bolt_option = input(Fore.BLUE+'Enter Bolt Option (If entered all press 0): ')
        if bolt_option == '1':
            print(Fore.CYAN+"Select Bolt Type")
            print(Fore.CYAN+'1.', 'Bearing Bolt')
            print(Fore.CYAN+'2.', 'Friction Grip Bolt')

            bolt_type = input(Fore.BLUE+'Enter Bolt Type: ')
            if bolt_type == '1':
                self.bolt_type = 'Bearing Bolt'
                self.design_dict['Bolt.Type'] = self.bolt_type
            elif bolt_type == '2':
                self.bolt_type = 'Friction Grip Bolt'
                self.design_dict['Bolt.Type'] = self.bolt_type

            else:
                colorama.colorama_text('Invalid Input')
                self.set_bolt()
                return

            self.set_bolt()
            return
        elif bolt_option == '2':
            conn = sqlite3.connect(PATH_TO_DATABASE)
            cursor = conn.cursor()
            cursor.execute("Select * from Bolt")
            print(prettytable.from_db_cursor(cursor))
            cursor.execute("Select Bolt_diameter from Bolt")
            all_bolt = cursor.fetchall()


            print(Fore.GREEN+'Enter Bolt Diameter, (If want to select all grades, enter "All", else enter them in space separated manner)')

            bolt_diameter = list(input(Fore.BLUE+'Enter Bolt Diameter: ').split())
            if bolt_diameter[0] == 'All' or bolt_diameter[0] == 'all':
                self.bolt_diameter = 'All'
                self.design_dict['Bolt.Diameter'] = self.bolt_diameter

            else:
                for bolt in bolt_diameter:
                    if (bolt,) not in all_bolt:
                        print(Fore.RED+'Invalid Input')
                        self.set_bolt()
                        break
                self.bolt_diameter = bolt_diameter
                self.design_dict['Bolt.Diameter'] = bolt_diameter
                print(Fore.YELLOW+'', *bolt_diameter)
            self.set_bolt()
            return
        elif bolt_option == '3':
            bolt_grades = ['3.6', '4.6', '4.8', '5.6', '5.8', '6.8', '8.8', '9.8', '10.9', '12.9']
            print(*bolt_grades)
            print(Fore.GREEN+'Select Bolt Grade, (If want to select all grades, enter "All", else enter them in space separated manner)')
            bolt_grade = list(input(Fore.BLUE+'Enter Bolt Grade: ').split())
            if bolt_grade[0] in ["all",'All']:
                self.bolt_grade = 'All'
                self.design_dict['Bolt.Grade'] = self.bolt_grade

            else:
                for grade in bolt_grade:
                    if grade not in bolt_grades:
                        print('Invalid Bolt Grade')
                        self.set_bolt()
                        return
                self.bolt_grade = bolt_grade
                print(Fore.CYAN+'Bolt Grade Selected')
                x = prettytable.PrettyTable(['Bolt Grade'])
                x.add_rows([[grade] for grade in bolt_grade])
                print(Fore.YELLOW+'',x)
                self.design_dict['Bolt.Grade'] = bolt_grade
            self.set_bolt()
            return

    def set_plate(self, plate_thickness='All'):
        print(PLATE_THICKNESS_SAIL)
        print(Fore.GREEN+"Enter Plate Thickness (If want to select all, enter 'All', else enter them in space separated manner)")
        plate_thickness = list(input(Fore.BLUE+'Enter Plate Thickness: ').split())
        if plate_thickness[0] == 'All' or plate_thickness[0] == 'all':
            self.plate_thickness = 'All'
            self.design_dict['Plate.Thickness'] = self.plate_thickness

        else:
            for thickness in plate_thickness:
                if thickness not in PLATE_THICKNESS_SAIL:
                    print(Fore.RED+'Invalid Plate Thickness')
                    self.set_plate()
                    return
            self.plate_thickness = plate_thickness
            self.design_dict['Connector.Plate.Thickness_List'] = self.plate_thickness

    def design_pref(self):
        option_list = self.input_values()
        new_list = self.customized_input()
        updated_list = self.input_value_changed()
        out_list = self.output_values(False)
        data = {}
        last_design_folder = os.path.join('ResourceFiles', 'last_designs')
        last_design_file = str(self.module_name()).replace(' ', '') + ".osi"
        last_design_file = os.path.join(last_design_folder, last_design_file)
        last_design_dictionary = {}
        if not os.path.isdir(last_design_folder):
            os.mkdir(last_design_folder)
        if os.path.isfile(last_design_file):
            with open(str(last_design_file), 'r') as last_design:
                last_design_dictionary = yaml.safe_load(last_design)
        if isinstance(last_design_dictionary, dict):
            self.setDictToUserInputs(last_design_dictionary, option_list, data, new_list)
            if "out_titles_status" in last_design_dictionary.keys():
                title_status = last_design_dictionary["out_titles_status"]
                print("titles", title_status)
                title_count = 0
                out_titles = []
                title_repeat = 1
                for out_field in out_list:
                    if out_field[2] == TYPE_TITLE:
                        title_name = out_field[1]
                        if title_name in out_titles:
                            title_name += str(title_repeat)
                            title_repeat += 1
                        # self.output_title_fields[title_name][0].setVisible(title_status[title_count])
                        title_count += 1
                        out_titles.append(title_name)
        self.ui_loaded = True

    def design_fn(self, op_list, data_list):
        design_dictionary = {}
        self.input_dock_inputs = {}
        for op in op_list:
            # widget = self.dockWidgetContents.findChild(QtWidgets.QWidget, op[0])
            if op[2] == TYPE_COMBOBOX:
                # des_val = widget.currentText()
                des_val = self.design_dict[op[0]]
                d1 = {op[0]: des_val}
            elif op[2] == TYPE_MODULE:
                des_val = op[0]
                module = op[1]
                d1 = {op[0]: module}
            elif op[2] == TYPE_COMBOBOX_CUSTOMIZED:
                if op[0] in self.design_dict.keys():
                    des_val = self.design_dict[op[0]]
                    d1 = {op[0]: des_val}
                else:
                    des_val = data_list[op[0]]
                    d1 = {op[0]: des_val}
            elif op[2] == TYPE_TEXTBOX:
                des_val = self.design_dict[op[0]]
                d1 = {op[0]: des_val}
            elif op[2] == TYPE_NOTE:
                # widget = self.dockWidgetContents.findChild(QtWidgets.QWidget, op[0] + "_note")
                # des_val = widget.text()
                d1 = {op[0]: self.design_dict[op[0]]}
            else:
                d1 = {}
            design_dictionary.update(d1)
            self.input_dock_inputs.update(d1)

        for design_pref_key in self.design_pref_inputs.keys():
            if design_pref_key not in self.input_dock_inputs.keys():
                self.input_dock_inputs.update({design_pref_key: self.design_pref_inputs[design_pref_key]})
        if 0:
            pass
        # if self.designPrefDialog.flag:
        #     print('flag true')
        #
        #     des_pref_input_list = self.input_dictionary_design_pref()
        #     edit_tabs_list = self.edit_tabs()
        #     edit_tabs_remove = list(filter(lambda x: x[2] == TYPE_REMOVE_TAB, edit_tabs_list))
        #     remove_tab_name = [x[0] for x in edit_tabs_remove]
        #     # remove_tabs = list(filter(lambda x: x[0] in remove_tab_name, des_pref_input_list))
        #     #
        #     # remove_func_name = edit_tabs_remove[3]
        #     result = None
        #     for edit in self.edit_tabs():
        #         (tab_name, input_dock_key_name, change_typ, f) = edit
        #         remove_tabs = list(filter(lambda x: x[0] in remove_tab_name, des_pref_input_list))
        #
        #         input_dock_key = self.dockWidgetContents.findChild(QtWidgets.QWidget, input_dock_key_name)
        #         result = list(filter(lambda get_tab:
        #                              self.designPrefDialog.ui.findChild(QtWidgets.QWidget, get_tab[0]).objectName() !=
        #                              f(input_dock_key.currentText()), remove_tabs))
        #
        #     if result is not None:
        #         des_pref_input_list_updated = [i for i in des_pref_input_list if i not in result]
        #     else:
        #         des_pref_input_list_updated = des_pref_input_list
        #
        #     for des_pref in des_pref_input_list_updated:
        #         tab_name = des_pref[0]
        #         input_type = des_pref[1]
        #         input_list = des_pref[2]
        #         tab = self.designPrefDialog.ui.findChild(QtWidgets.QWidget, tab_name)
        #         for key_name in input_list:
        #             key = tab.findChild(QtWidgets.QWidget, key_name)
        #             if key is None:
        #                 continue
        #             if input_type == TYPE_TEXTBOX:
        #                 val = key.text()
        #                 design_dictionary.update({key_name: val})
        #             elif input_type == TYPE_COMBOBOX:
        #                 val = key.currentText()
        #                 design_dictionary.update({key_name: val})
        else:
            print('flag false')

            for without_des_pref in self.input_dictionary_without_design_pref():
                input_dock_key = without_des_pref[0]
                input_list = without_des_pref[1]
                input_source = without_des_pref[2]
                for key_name in input_list:
                    if input_source == 'Input Dock':
                        design_dictionary.update({key_name: design_dictionary[input_dock_key]})
                    else:
                        val = self.get_values_for_design_pref(key_name, design_dictionary)
                        design_dictionary.update({key_name: val})

            # for dp_key in self.design_pref_inputs.keys():
            #     design_dictionary[dp_key] = self.design_pref_inputs[dp_key]

        self.design_inputs = design_dictionary
        self.design_inputs = design_dictionary

    def update_material_db(self, grade, material):

        fy_20 = int(material.fy_20)
        fy_20_40 = int(material.fy_20_40)
        fy_40 = int(material.fy_40)
        fu = int(material.fu)
        elongation = 0

        if fy_20 > 350:
            elongation = 20
        elif 250 < fy_20 <= 350:
            elongation = 22
        elif fy_20 <= 250:
            elongation = 23

        conn = sqlite3.connect(PATH_TO_DATABASE)
        c = conn.cursor()
        c.execute('''INSERT INTO Material (Grade,[Yield Stress (< 20)],[Yield Stress (20 -40)],
        [Yield Stress (> 40)],[Ultimate Tensile Stress],[Elongation ]) VALUES (?,?,?,?,?,?)''',
                  (grade, fy_20, fy_20_40, fy_40, fu, elongation))
        conn.commit()
        c.close()
        conn.close()

    def setDictToUserInputs(self, uiObj, op_list, data, new):

        self.load_input_error_message = "Invalid Inputs Found! \n"

        for uiObj_key in uiObj.keys():
            if str(uiObj_key) in [KEY_SUPTNGSEC_MATERIAL, KEY_SUPTDSEC_MATERIAL, KEY_SEC_MATERIAL,
                                  KEY_CONNECTOR_MATERIAL,
                                  KEY_BASE_PLATE_MATERIAL]:
                material = uiObj[uiObj_key]
                material_validator = MaterialValidator(material)
                if material_validator.is_already_in_db():
                    pass
                elif material_validator.is_format_custom():
                    if material_validator.is_valid_custom():
                        self.update_material_db(grade=material, material=material_validator)
                        input_dock_material = []
                        input_dock_material.clear()
                        for item in connectdb("Material"):
                            input_dock_material.append(item)
                    else:
                        self.load_input_error_message += \
                            str(uiObj_key) + ": (" + str(material) + ") - Default Value Considered! \n"
                        continue
                else:
                    self.load_input_error_message += \
                        str(uiObj_key) + ": (" + str(material) + ") - Default Value Considered! \n"
                    continue

            if uiObj_key not in [i[0] for i in op_list]:
                self.design_pref_inputs.update({uiObj_key: uiObj[uiObj_key]})

        # for op in op_list:
        #     key_str = op[0]
        #     key = self.dockWidgetContents.findChild(QtWidgets.QWidget, key_str)
        #     if op[2] == TYPE_COMBOBOX:
        #         if key_str in uiObj.keys():
        #             index = key.findText(uiObj[key_str], QtCore.Qt.MatchFixedString)
        #             if index >= 0:
        #                 key.setCurrentIndex(index)
        #             else:
        #                 if key_str in [KEY_SUPTDSEC, KEY_SUPTNGSEC]:
        #                     self.load_input_error_message += \
        #                         str(key_str) + ": (" + str(uiObj[key_str]) + ") - Select from available Sections! \n"
        #                 else:
        #                     self.load_input_error_message += \
        #                         str(key_str) + ": (" + str(uiObj[key_str]) + ") - Default Value Considered! \n"
        #     elif op[2] == TYPE_TEXTBOX:
        #         if key_str in uiObj.keys():
        #             if key_str == KEY_SHEAR or key_str == KEY_AXIAL or key_str == KEY_MOMENT:
        #                 if uiObj[key_str] == "":
        #                     pass
        #                 elif float(uiObj[key_str]) >= 0:
        #                     pass
        #                 else:
        #                     self.load_input_error_message += \
        #                         str(key_str) + ": (" + str(uiObj[key_str]) + ") - Load should be positive integer! \n"
        #                     uiObj[key_str] = ""
        #
        #             key.setText(uiObj[key_str] if uiObj[key_str] != 'Disabled' else "")
        #     elif op[2] == TYPE_COMBOBOX_CUSTOMIZED:
        #         if key_str in uiObj.keys():
        #             for n in new:
        #
        #                 if n[0] == key_str and n[0] == KEY_SECSIZE:
        #                     if set(uiObj[key_str]) != set(n[1]([self.dockWidgetContents.findChild(QtWidgets.QWidget,
        #                                                                                           KEY_SEC_PROFILE).currentText()])):
        #                         key.setCurrentIndex(1)
        #                     else:
        #                         key.setCurrentIndex(0)
        #                     data[key_str + "_customized"] = uiObj[key_str]
        #
        #                 elif n[0] == key_str and n[0] != KEY_SECSIZE:
        #                     if set(uiObj[key_str]) != set(n[1]()):
        #                         key.setCurrentIndex(1)
        #                     else:
        #                         key.setCurrentIndex(1)
        #                     data[key_str + "_customized"] = uiObj[key_str]
        #
        #     else:
        #         pass

        if self.load_input_error_message != "Invalid Inputs Found! \n":
            logging.log(self.load_input_error_message)

    def show_error_msg(self, error):
          # show only first error message.
        logging.error(error,)


    def column_flange_beam_web(self):
        print("Connectivity : ",self.connectivity)
        print('1. Enter Beam Section Properties')
        self.input_beam(0)
        print()
        print('2. Enter Column Section Properties')
        self.input_column()
        print()
        print('3. Enter Material Properties')
        self.input_material()
        print()
        print('4. Enter Bolt Properties')
        self.set_bolt()
        print()
        print('5. Enter Plate Properties')
        self.set_plate()
        print()
        print('6. Enter Factored Loads')
        self.set_factored_loads()
        print()
    def column_web_beam_web(self):
        print("Connectivity : ",self.connectivity)
        print('1. Enter Beam Section Properties')
        self.input_beam(0)
        print()
        print('2. Enter Column Section Properties')
        self.input_column()
        print()
        print('3. Enter Material Properties')
        self.input_material()
        print()
        print('4. Enter Bolt Properties')
        self.set_bolt()
        print()
        print('5. Enter Plate Properties')
        self.set_plate()
        print()
        print('6. Enter Factored Loads')
        self.set_factored_loads()
        print()
    def design_prefernces(self):
        print("Enter Materail Properties")

    def beam_beam(self):
        print("Connectivity : ",self.connectivity)
        print('1. Enter Beam Section Properties')
        self.input_beam(0)
        print()
        print('2. Enter Column Section Properties')
        self.input_beam(1)
        print()
        print('3. Enter Material Properties')
        self.input_material()
        print()
        print('4. Enter Bolt Properties')
        self.set_bolt()
        print()
        print('5. Enter Plate Properties')
        self.set_plate()
        print()
        print('6. Enter Factored Loads')
        self.set_factored_loads()
        print()


    def input(self):
        print(Fore.LIGHTMAGENTA_EX+'------------------Input------------------')
        print(Fore.GREEN+"Select Connectivity")
        CONN_CFBW = 'Column Flange-Beam Web'
        CONN_CWBW = 'Column Web-Beam Web'
        CONN_BB = 'Beam-Beam'
        print(Fore.GREEN+"Select Connectivity")
        print(Fore.GREEN+'1.', CONN_CFBW)
        print(Fore.GREEN+'2.', CONN_CWBW)
        print(Fore.GREEN+'3.', CONN_BB)

        conn = input('Enter Connectivity: ')
        if conn == '1':
            self.connectivity = CONN_CFBW
            self.design_dict['Connectivity'] = self.connectivity

            while True:
                try:
                    self.column_flange_beam_web()
                    break
                except Exception as e:
                    print(e)
                    print(Fore.RED+'Please enter valid inputs')
                    continue


        elif conn == '2':

            self.connectivity = CONN_CFBW
            self.design_dict['Connectivity'] = self.connectivity

            while True:
                try:
                    self.column_web_beam_web()
                    break
                except Exception as e:
                    print(e)
                    print(Fore.RED+'Please enter valid inputs')
                    continue
        elif conn == '3':
            self.connectivity = CONN_BB
            self.design_dict['Connectivity'] = self.connectivity

            while True:
                try:
                    self.beam_beam()
                    break
                except Exception as e:
                    print(e)
                    print(Fore.RED + 'Please enter valid inputs')
                    continue
        else:
            print(Fore.RED+'Please enter valid inputs')
            self.input()
        self.design_dict['Member.Supporting_Section.Designation'] = self.ColumnSection
        self.design_dict['Member.Supported_Section.Designation']= self.BeamSection
        self.design_dict['Material'] = self.material
        # Connectivity Column Flange-Beam Web
    def input_beam(self,flag):
        if flag==0: #primary beam / default
            conn = sqlite3.connect(PATH_TO_DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT Id, Designation FROM Beams")
            beam = prettytable.from_db_cursor(cursor)
            print(Fore.GREEN+"Enter Beam Section Id (If want to see all available beams, type 'all')")
            beam_id = input(Fore.BLUE+'Beam Section Id: ')
            if beam_id == 'all':
                print(beam)
                beam_id = input(Fore.BLUE+'Beam Section Id: ')
                cursor.execute("SELECT Designation FROM Beams WHERE Id = ?", (beam_id,))
                self.BeamSection = cursor.fetchone()[0]
            else:
                cursor.execute("SELECT Designation FROM Beams WHERE Id = ?", (beam_id,))
                self.BeamSection = cursor.fetchone()[0]
            print(Fore.YELLOW+self.BeamSection)
            cursor.close()
        else:
            conn = sqlite3.connect(PATH_TO_DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT Id, Designation FROM Beams")
            beam = prettytable.from_db_cursor(cursor)
            print(Fore.GREEN+"Enter Beam Section Id (If want to see all available beams, type 'all')")
            beam_id = input(Fore.BLUE+'Beam Section Id: ')
            if beam_id == 'all':
                print(beam)
                beam_id = input(Fore.BLUE+'Beam Section Id: ')
                cursor.execute("SELECT Designation FROM Beams WHERE Id = ?", (beam_id,))
                self.ColumnSection = cursor.fetchone()[0] # using column Section varible as secondary beam
            else:
                cursor.execute("SELECT Designation FROM Beams WHERE Id = ?", (beam_id,))
                self.ColumnSection = cursor.fetchone()[0]
            print(Fore.YELLOW+self.ColumnSection)
            cursor.close()

    def input_column(self):
        conn = sqlite3.connect(PATH_TO_DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT Id, Designation FROM Columns")
        column = prettytable.from_db_cursor(cursor)
        print(Fore.GREEN+"Enter Column Section Id (If want to see all available columns, type 'all')")
        column_id = input(Fore.BLUE+'Column Section Id: ')
        if column_id == 'all':
            print(column)
            column_id = input(Fore.BLUE+'Column Section Id: ')
            cursor.execute("SELECT Designation FROM Columns WHERE Id = ?", (column_id,))
            self.ColumnSection = cursor.fetchone()[0]
        else:
            cursor.execute("SELECT Designation FROM Columns WHERE Id = ?", (column_id,))
            self.ColumnSection = cursor.fetchone()[0]
        print(Fore.YELLOW+self.ColumnSection)
        cursor.close()

    def input_material(self):
        conn = sqlite3.connect(PATH_TO_DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT Grade FROM Material")

        material = cursor.fetchall()
        materials = []
        c=1
        for i in material:
            materials.append([c,i[0]])
            c+=1

        table = prettytable.PrettyTable(['S.No.','Grade'])
        for i in materials:
            table.add_row(i)
        print(Fore.GREEN+"Enter Material Id (If want to see all available materials, type 'all')")
        material_id = input(Fore.BLUE+'Material Id: ')
        if material_id == 'all':
            print(table)
            try:
                material_id = int(input(Fore.BLUE+'Material Id: '))
            except:
                print(Fore.RED+'Invalid Input')
            for i in materials:
                if i[0] == material_id:
                    self.material = i[1]
                    break

        else:
            material_id=int(material_id)
            for i in materials:
                print(i)
                if i[0] == material_id:
                    self.material = i[1]
                    break
        self.design_dict['Material']= self.material
        print(Fore.YELLOW+self.material)
        cursor.close()

    def show_design_dict(self):
        print(Fore.GREEN+"Design Dictionary")
        x = prettytable.PrettyTable(['Field', 'Value'])
        for key, value in self.design_inputs.items():
            x.add_row([key, value])
        print(x)

    def set_inputs(self):
        option_list = self.input_values()
        new_list = self.customized_input()

        data = {}

        if len(new_list) > 0:
            for i in new_list:
                data_key = i[0]
                data[data_key] = [all_val for all_val in i[1]()]
        # fin.design_input is design dictionary
        self.design_fn(option_list, data)
        self.set_input_values(self.design_inputs)

    def output(self):
        print()

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
            self.show_output()
            self.output()
            return
        elif output == '2':
            self.save_design_report()
            self.output()
            return
        elif output == '3':
            # self.save_output_to_excel()
            self.output()
            return
        elif output == '4':
            self.show_design_dict()
            self.output()
            return
        else:
            print(Fore.RED + 'Invalid Input')
            self.output()
    def show_output(self):
        print(Fore.GREEN+"Output")
        outputs= self.output_values(self.design_status)
        tabu = prettytable.PrettyTable(['Field', 'Value'])
        for output in outputs:
            if output[2]=='Title':
                tabu.add_row([Fore.CYAN+output[1],'------------------------------'])
            elif output[2]=='TextBox':
                tabu.add_row([Fore.YELLOW+str(output[1]),Fore.YELLOW+str(output[3])])
        print(tabu)
    def save_design_report(self):
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
        companyName = input(Fore.BLUE+'Enter Company Name (Leave Empty if want to): ')
        companyLogo = input(Fore.BLUE+'Enter Path of Company Logo (Leave Empty if want to): ')
        teamName = input(Fore.BLUE+'Enter Team Name (Leave Empty if want to): ')
        designer = input(Fore.BLUE+'Enter Designer Name (Leave Empty if want to): ')


        profile_summary['CompanyName']=companyName
        profile_summary['CompanyLogo']=companyLogo
        profile_summary['Group/TeamName']=teamName
        profile_summary['Designer']=designer
        popup_summary['ProfileSummary']=profile_summary

        print(Fore.CYAN+"Design Summary")
        ProjectName = input(Fore.BLUE+'Enter Project Name (Leave Empty if want to): ')
        subtitle = input(Fore.BLUE+'Enter Subtitle (Leave Empty if want to): ')
        jobNumber = input(Fore.BLUE+'Enter Job Number (Leave Empty if want to): ')

        popup_summary['ProjectTitle']=ProjectName
        popup_summary['Subtitle']=subtitle
        popup_summary['JobNumber']=jobNumber
        popup_summary['AdditionalComments']=''

        Client = input(Fore.BLUE+'Enter Client Name (Leave Empty if want to): ')

        filename = input(Fore.BLUE+'Enter File Path with name to save (Leave Empty if want to): ')

        popup_summary['Client']=Client
        popup_summary['filename']=filename
        popup_summary['does_design_exist']=self.design_status
        popup_summary['logger_messages']=''

        self.save_design(popup_summary)


