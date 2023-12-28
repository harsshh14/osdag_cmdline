"""

@Author:    Rutvik Joshi - Osdag Team, IIT Bombay [(P) rutvikjoshi63@gmail.com / 30005086@iitb.ac.in]

@Module - Plate Girder- Welded

@Reference(s): 1) IS 800: 2007, General construction in steel - Code of practice (Third revision)
               2) IS 808: 1989, Dimensions for hot rolled steel beam, column, channel, and angle sections and
                                it's subsequent revision(s)
               3) Design of Steel Structures by N. Subramanian (Fifth impression, 2019, Chapter 15)
               4) Limit State Design of Steel Structures by S K Duggal (second edition, Chapter 11)
                     
other          8) 
references     9)

"""
import logging
import math
import numpy as np
from Common import *
# from design_type.connection.moment_connection import MomentConnection
from utils.common.material import *
from utils.common.load import Load
from utils.common.component import ISection, Material
from utils.common.component import *
from design_type.member import Member
from Report_functions import *
from design_report.reportGenerator_latex import CreateLatex
from utils.common.common_calculation import *
from design_type.tension_member import *
from utils.common.Section_Properties_Calculator import BBAngle_Properties
from utils.common import is800_2007
from utils.common.component import *
from utils.common.Section_Properties_Calculator import I_sectional_Properties
from design_type.flexural_member.flexure import Flexure

class Custom_Girder():#Material
    # def __new__(self,design_dictionary):
    def __init__(self, design_dictionary):
        # super(Custom_Girder,self).__init__()#material_grade
        print("Girder Object Initialised")
        self.flange_thickness = float(design_dictionary[KEY_tf])
        self.depth = float(design_dictionary[KEY_dw]) + 2* self.flange_thickness
        self.flange_width = float(design_dictionary[KEY_bf])
        self.web_thickness = float(design_dictionary[KEY_tw])
        self.flange_slope = 90
        self.root_radius = 0
        self.toe_radius = 0
        self.mass = round(I_sectional_Properties().calc_Mass(self.depth,self.flange_width,self.web_thickness,self.flange_thickness,self.flange_slope,self.root_radius,self.toe_radius)*10**1)
        self.area = round(I_sectional_Properties().calc_Area(self.depth,self.flange_width,self.web_thickness,self.flange_thickness,self.flange_slope,self.root_radius,self.toe_radius)*10**2)
        self.mom_inertia_z = round(I_sectional_Properties().calc_MomentOfAreaZ(self.depth,self.flange_width,self.web_thickness,self.flange_thickness,self.flange_slope,self.root_radius,self.toe_radius)*10**4)
        self.mom_inertia_y = round(I_sectional_Properties().calc_MomentOfAreaY(self.depth,self.flange_width,self.web_thickness,self.flange_thickness,self.flange_slope,self.root_radius,self.toe_radius)*10**4)
        self.rad_of_gy_z = round(I_sectional_Properties().calc_RogZ(self.depth,self.flange_width,self.web_thickness,self.flange_thickness,self.flange_slope,self.root_radius,self.toe_radius)*10**1)
        self.rad_of_gy_y = round(I_sectional_Properties().calc_RogY(self.depth,self.flange_width,self.web_thickness,self.flange_thickness,self.flange_slope,self.root_radius,self.toe_radius)*10**1)
        self.elast_sec_mod_z = round(I_sectional_Properties().calc_ElasticModulusZz(self.depth,self.flange_width,self.web_thickness,self.flange_thickness,self.flange_slope,self.root_radius,self.toe_radius)*10**3)
        self.elast_sec_mod_y = round(I_sectional_Properties().calc_ElasticModulusZy(self.depth,self.flange_width,self.web_thickness,self.flange_thickness,self.flange_slope,self.root_radius,self.toe_radius)*10**3)
        self.plast_sec_mod_z = round(I_sectional_Properties().calc_PlasticModulusZpz(self.depth,self.flange_width,self.web_thickness,self.flange_thickness,self.flange_slope,self.root_radius,self.toe_radius)*10**3)
        self.plast_sec_mod_y = round(I_sectional_Properties().calc_PlasticModulusZpy(self.depth,self.flange_width,self.web_thickness,self.flange_thickness,self.flange_slope,self.root_radius,self.toe_radius)*10**3)
        # print(self.flange_thickness)

    def __str__(self) -> str:
        return "Customised Girder generated"
class PlateGirderWelded(Member):

    def __init__(self):
        super(PlateGirderWelded, self).__init__()

    ###############################################
    # Design Preference Functions Start
    ###############################################
    def tab_list(self):
        """

        :return: This function returns the list of tuples. Each tuple will create a tab in design preferences, in the
        order they are appended. Format of the Tuple is:
        [Tab Title, Type of Tab, function for tab content)
        Tab Title : Text which is displayed as Title of Tab,
        Type of Tab: There are Three types of tab layouts.
            Type_TAB_1: This have "Add", "Clear", "Download xlsx file" "Import xlsx file"
            TYPE_TAB_2: This contains a Text box for side note.
            TYPE_TAB_3: This is plain layout
        function for tab content: All the values like labels, input widgets can be passed as list of tuples,
        which will be displayed in chosen tab layout

        """
        tabs = []
        # t1 = ("Under Development", TYPE_TAB_1, self.tab_section)
        # tabs.append(t1)
        # t2 = ("Under Development", TYPE_TAB_2, self.optimization_tab_plate_girder_design)
        # tabs.append(t2)

        t5 = ("Under Development", TYPE_TAB_2, self.optimization_tab_plate_girder_design)
        tabs.append(t5)
        # t1 = (KEY_DISP_COLSEC, TYPE_TAB_1, self.tab_section)
        # tabs.append(t1)
        
        # t2 = ("Optimization", TYPE_TAB_2, self.optimization_tab_flexure_design)
        # tabs.append(t2)

        # t5 = ("Design", TYPE_TAB_2, self.design_values)
        # tabs.append(t5)

        return tabs
    def tab_value_changed(self):
        change_tab = []
        return change_tab
    def input_dictionary_design_pref(self):
        """

        :return: This function is used to choose values of design preferences to be saved to design dictionary.

         It returns list of tuple which contains, tab name, input widget type of keys, keys whose values to be saved,

         [(Tab Name, input widget type of keys, [List of keys to be saved])]
        TODO : Material pop-up
         """
        design_input = []

        t2 = ("Under Development", TYPE_TEXTBOX, [ KEY_EFFECTIVE_AREA_PARA, KEY_LENGTH_OVERWRITE, KEY_BEARING_LENGTH]) #, KEY_STEEL_COST
        design_input.append(t2)

        t2 = ("Under Development", TYPE_COMBOBOX, [KEY_ALLOW_CLASS, KEY_LOAD]) #, KEY_STEEL_COST
        design_input.append(t2)
        t6 = ("Design", TYPE_COMBOBOX, [KEY_DP_DESIGN_METHOD])
        design_input.append(t6)

        return design_input
    def input_dictionary_without_design_pref(self):

        design_input = []
        t2 = (None, [KEY_DP_DESIGN_METHOD], '')
        design_input.append(t2)
        
        t2 = (None, [KEY_ALLOW_CLASS, KEY_EFFECTIVE_AREA_PARA, KEY_LENGTH_OVERWRITE,KEY_BEARING_LENGTH, KEY_LOAD, KEY_DP_DESIGN_METHOD], '')
        design_input.append(t2)

        return design_input
    
    def get_values_for_design_pref(self, key, design_dictionary):
        if design_dictionary[KEY_MATERIAL] != 'Select Material':
            material = Material(design_dictionary[KEY_MATERIAL], 41)
            fu = material.fu
            fy = material.fy
        else:
            fu = ''
            fy = ''

        val = {
            KEY_ALLOW_CLASS: 'Yes',
            KEY_EFFECTIVE_AREA_PARA: '1.0',
            KEY_LENGTH_OVERWRITE :'NA',
            KEY_BEARING_LENGTH : 'NA',
            KEY_LOAD : 'Normal',
            KEY_DP_DESIGN_METHOD: "Limit State Design",
            KEY_ShearBucklingOption: KEY_DISP_SB_Option[0],
        }[key]

        return val
    ####################################
    # Design Preference Functions End
    ####################################

    # Setting up logger and Input and Output Docks
    ####################################
    def module_name(self):
        # self.mainmodule = KEY_PLATE_GIRDER_MAIN_MODULE
        return KEY_DISP_PLATE_GIRDER_WELDED

    def set_osdaglogger(key):
        """
        Set logger for Column Design Module.
        """
        global logger
        logger = logging.getLogger('Osdag')

        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        handler = logging.FileHandler('logging_text.log')

        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        if key is not None:
            handler = OurLog(key)
            formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    def customized_input(self):

        c_lst = []

        return c_lst
    def input_values(self):

        self.module = PlateGirderWelded.module_name(self)
        options_list = []

        t1 = (KEY_MODULE, self.module, TYPE_MODULE, None, True, "No Validator")
        options_list.append(t1)

        t1 = (KEY_SECTION_PROFILE, KEY_SECTION_DATA, TYPE_TITLE, None, True, 'No Validator')
        options_list.append(t1)

        t2 = (KEY_SEC_PROFILE, KEY_DISP_Plate_Girder_PROFILE, TYPE_NOTE, KEY_PLATE_GIRDER_MAIN_MODULE, True, 'No Validator') #'Beam and Column'
        options_list.append(t2)

        t1 = (KEY_tf, KEY_DISP_tf, TYPE_TEXTBOX, None, True, 'Int Validator')
        options_list.append(t1)
        t1 = (KEY_tw, KEY_DISP_tw, TYPE_TEXTBOX, None, True, 'Int Validator')
        options_list.append(t1)
        t1 = (KEY_dw, KEY_DISP_dw, TYPE_TEXTBOX, None, True, 'Int Validator')
        options_list.append(t1)
        t1 = (KEY_bf, KEY_DISP_bf, TYPE_TEXTBOX, None, True, 'Int Validator')
        options_list.append(t1)
        
        t4 = (KEY_MATERIAL, KEY_DISP_MATERIAL, TYPE_COMBOBOX, VALUES_MATERIAL, True, 'No Validator')
        options_list.append(t4)
        t5 = (KEY_LENGTH, KEY_DISP_LENGTH_BEAM, TYPE_TEXTBOX, None, True, 'Int Validator')
        options_list.append(t5)

        t7 = (None, DISP_TITLE_FSL, TYPE_TITLE, None, True, 'No Validator')
        options_list.append(t7)

        t8 = (KEY_MOMENT, KEY_DISP_MOMENT, TYPE_TEXTBOX, None, True, 'No Validator')
        options_list.append(t8)

        t8 = (KEY_SHEAR, KEY_DISP_SHEAR, TYPE_TEXTBOX, None, True, 'No Validator')
        options_list.append(t8)

        t8 = (KEY_IntermediateStiffener, KEY_DISP_IntermediateStiffener, TYPE_COMBOBOX, ['Yes','No'], True, 'No Validator')
        options_list.append(t8)

        t8 = (KEY_IntermediateStiffener_spacing, KEY_DISP_IntermediateStiffener_spacing, TYPE_TEXTBOX, None, True, 'Int Validator')
        options_list.append(t8)

        t8 = (KEY_BUCKLING_STRENGTH, KEY_DISP_BUCKLING_STRENGTH, TYPE_COMBOBOX, ['Yes','No'], True, 'No Validator')
        options_list.append(t8)

        t8 = (KEY_WEB_CRIPPLING, KEY_DISP_CRIPPLING_STRENGTH, TYPE_COMBOBOX, ['Yes','No'], True, 'No Validator')
        options_list.append(t8)
        return options_list

    def input_value_changed(self):

        lst = []
        t3 = ([KEY_MATERIAL], KEY_MATERIAL, TYPE_CUSTOM_MATERIAL, self.new_material)
        lst.append(t3)
        return lst

    def output_values(self, flag):

        out_list = []
        t1 = (None, DISP_TITLE_STRUT_SECTION, TYPE_TITLE, None, True)

        out_list.append(t1)
        t2 = (KEY_betab_constatnt, KEY_DISP_betab_constatnt, TYPE_TEXTBOX,
              'NA', True)
        out_list.append(t2)
        return out_list

    def func_for_validation(self, design_dictionary):
        print(f"func_for_validation here")
        all_errors = []
        self.design_status = False
        flag = False
        flag1 = False
        flag2 = False
        flag3 = False
        option_list = self.input_values(self)
        missing_fields_list = []
        print(f'func_for_validation option_list {option_list}'
            f"\n  design_dictionary {design_dictionary}"
              )
        for option in option_list:
            # print(option_list)
            if option[2] == TYPE_TEXTBOX and option[0] == KEY_LENGTH or option[0] == KEY_SHEAR or option[0] == KEY_MOMENT:
                if design_dictionary[option[0]] == '':
                    missing_fields_list.append(option[1])
                    continue
                if option[0] == KEY_LENGTH:
                    if float(design_dictionary[option[0]]) <= 0.0:
                        print("Input value(s) cannot be equal or less than zero.")
                        error = "Input value(s) cannot be equal or less than zero."
                        all_errors.append(error)
                    else:
                        flag1 = True
                elif option[0] == KEY_SHEAR:
                    if float(design_dictionary[option[0]]) < 0.0:
                        print("Input value(s) cannot be less than zero.")
                        error = "Input value(s) cannot be less than zero."
                        all_errors.append(error)
                    else:
                        flag2 = True
                elif option[0] == KEY_MOMENT:
                    if float(design_dictionary[option[0]]) < 0.0:
                        print("Input value(s) cannot be less than zero.")
                        error = "Input value(s) cannot be less than zero."
                        all_errors.append(error)
                    else:
                        flag3 = True
            # if option[0] == KEY_tf or option[0] == KEY_tw or option[0] == KEY_dw or option[0] == KEY_bf:
            #     if design_dictionary[option[0]]
  
        if len(missing_fields_list) > 0:
            error = self.generate_missing_fields_error_string(self, missing_fields_list)
            all_errors.append(error)
        else:
            flag = True

        if flag and flag1 and flag2 and flag3:
            print(f"\n design_dictionary{design_dictionary}")
            self.set_input_values(self, design_dictionary)
        else:
            return all_errors
    def isfloat(input_list):
        for i in range(1,5):
            try:
                print(input_list[i])
                yield isinstance(float(input_list[i]),float)
            except:
                yield False
    # Setting inputs from the input dock GUI
    def set_input_values(self, design_dictionary):
        # out_list = []
        ### INPUT FROM INPUT DOCK ####
        self.length = float(design_dictionary[KEY_LENGTH])*10**3 #m -> mm
        self.material = design_dictionary[KEY_MATERIAL]
        self.load = Load(0,design_dictionary[KEY_SHEAR],design_dictionary[KEY_MOMENT],unit_kNm=True) #KN -> N
        self.temp_section_list = list(design_dictionary.values())#[1,4]
        self.section_list = [i for i in self.isfloat(self.temp_section_list)]
        # self.material = design_dictionary[KEY_MATERIAL]
        self.sec_profile = design_dictionary[KEY_SEC_PROFILE]
        # safety factors
        self.gamma_m0 = IS800_2007.cl_5_4_1_Table_5["gamma_m0"]["yielding"]
        self.gamma_m1 = IS800_2007.cl_5_4_1_Table_5["gamma_m1"]["ultimate_stress"]
        self.material_property = Material(material_grade=self.material, thickness=0)
 

        ### INPUT FROM DESIGN PREFERENCE ###
        # self.latex_efp = design_dictionary[KEY_LENGTH_OVERWRITE]
        # self.effective_area_factor = float(design_dictionary[KEY_EFFECTIVE_AREA_PARA])
        # self.allowable_utilization_ratio = 1.0
        # self.optimization_parameter = "Utilization Ratio"
        # self.allow_class = design_dictionary[KEY_ALLOW_CLASS]  # if 'Semi-Compact' is available
        # self.steel_cost_per_kg = 50
        # # Step 2 - computing the design compressive stress for web_buckling & web_crippling
        # self.bearing_length = design_dictionary[KEY_BEARING_LENGTH]
        # #TAKE from Design Dictionary
        # self.allowed_sections = []
        # if self.allow_class == "Yes":
        #     self.allowed_sections == "Semi-Compact"

        #############
        # LATEX VARIABLES
        #############

        def design(design_dictionary):
            # Assign custom section def to calulate properties
            self.Girder_SectionProperty(self)
            
            
            
    
        return design(design_dictionary)

    def Girder_SectionProperty(self):
        print(Custom_Girder)
        print(f'temp_section_list = {self.temp_section_list}')

        print(f'section_list = {self.section_list}')
        # if isinstance(float(design_dictionary[KEY_tf]),float) and 
        if all(self.section_list):
            self.optimization_tab_check(self)
            self.design = False
            self.section_property = Custom_Girder(design_dictionary)
            print(self.section_property.flange_thickness,
                self.section_property.depth,
                self.section_property.flange_width,
                self.section_property.web_thickness,
                self.section_property.flange_slope,
                self.section_property.root_radius,
                self.section_property.toe_radius,
                self.section_property.mass,
                self.section_property.area, #mm
                self.section_property.mom_inertia_z,
                self.section_property.mom_inertia_y,
                self.section_property.rad_of_gy_z,
                self.section_property.rad_of_gy_y,
                self.section_property.elast_sec_mod_z,
                self.section_property.elast_sec_mod_y,
                self.section_property.plast_sec_mod_z,
                self.section_property.plast_sec_mod_y)
        else:
            self.design = True

    def optimization_tab_check(self):
        print(f"\n Inside optimization_tab_check")
        # self.latex_tension_zone = False
        if (self.effective_area_factor <= 0.10) or (self.effective_area_factor > 1.0):
            logger.error(
                "The defined value of Effective Area Factor in the design preferences tab is out of the suggested range."
            )
            logger.info("Provide an appropriate input and re-design.")
            logger.warning("Assuming a default value of 1.0.")
            self.effective_area_factor = 1.0
            # self.design_status = False
            # self.design_status_list.append(self.design_status)
            self.optimization_tab_check(self)
        
    def results(self, design_dictionary):

        # sorting results from the dataset
        # if len(self.input_section_list) > 1:
        # results based on UR
        if self.optimization_parameter == "Utilization Ratio":
            filter_UR = filter(
                lambda x: x <= min(self.allowable_utilization_ratio, 1.0),
                self.optimum_section_ur
            )
            self.optimum_section_ur = list(filter_UR)

            self.optimum_section_ur.sort()
            # print(f"self.optimum_section_ur{self.optimum_section_ur}")
            # print(f"self.result_UR{self.result_UR}")

            # selecting the section with most optimum UR
            if len(self.optimum_section_ur) == 0:  # no design was successful
                logger.warning(
                    "The sections selected by the solver from the defined list of sections did not satisfy the Utilization Ratio (UR) "
                    "criteria"
                )
                logger.error(
                    "The solver did not find any adequate section from the defined list."
                )
                logger.info(
                    "Re-define the list of sections or check the Design Preferences option and re-design."
                )
                self.design_status = False
                # self.design_status_list.append(self.design_status)

            else:
                self.result_UR = self.optimum_section_ur[
                    -1
                ]  # optimum section which passes the UR check
                print(f"self.result_UR{self.result_UR}")
                self.design_status = True
                self.common_result(
                    self,
                    list_result=self.optimum_section_ur_results,
                    result_type=self.result_UR,
                )

        else:  # results based on cost
            self.optimum_section_cost.sort()

            # selecting the section with most optimum cost
            self.result_cost = self.optimum_section_cost[0]
            self.design_status = True
       
        self.design_status_list.append(self.design_status)
        for status in self.design_status_list:
            print('status list', status)
            if status is False:
                self.design_status = False
                break
            else:
                self.design_status = True

    ### start writing save_design from here!
    def save_design(self, popup_summary):
 
        self.report_input = \
            {#KEY_MAIN_MODULE: self.mainmodule,
                KEY_MODULE: self.module, #"Axial load on column "
            }

        print(sys.path[0])
        rel_path = str(sys.path[0])
        rel_path = rel_path.replace("\\", "/")
        fname_no_ext = popup_summary['filename']
        CreateLatex.save_latex(CreateLatex(), self.report_input, self.report_check, popup_summary, fname_no_ext,
                              rel_path, [], '', module=self.module) #



