"""

@Author:    Rutvik Joshi - Osdag Team, IIT Bombay [(P) rutvikjoshi63@gmail.com / 30005086@iitb.ac.in]

@Module - Beam Design
           - Laterally Supported Beam [Moment + Shear]
           - Laterally Unsupported Beam [Moment + Shear]


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
from design_type.connection.moment_connection import MomentConnection
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


class Flexure(Member):

    def __init__(self):
        # print(f"Here10")
        super(Flexure, self).__init__()

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

        t1 = (KEY_DISP_COLSEC, TYPE_TAB_1, self.tab_section)
        tabs.append(t1)
        
        t2 = ("Optimization", TYPE_TAB_2, self.optimization_tab_flexure_design)
        tabs.append(t2)

        t5 = ("Design", TYPE_TAB_2, self.design_values)
        tabs.append(t5)

        return tabs

    def tab_value_changed(self):
        change_tab = []

        t1 = (KEY_DISP_COLSEC, [KEY_SEC_MATERIAL], [KEY_SEC_FU, KEY_SEC_FY], TYPE_TEXTBOX, self.get_fu_fy_I_section)
        change_tab.append(t1)

        t4 = (KEY_DISP_COLSEC, ['Label_1', 'Label_2', 'Label_3', 'Label_4', 'Label_5'],
              ['Label_11', 'Label_12', 'Label_13', 'Label_14', 'Label_15', 'Label_16', 'Label_17', 'Label_18',
               'Label_19', 'Label_20', 'Label_21', 'Label_22', KEY_IMAGE], TYPE_TEXTBOX, self.get_I_sec_properties)
        change_tab.append(t4)

        t5 = (KEY_DISP_COLSEC, ['Label_HS_1', 'Label_HS_2', 'Label_HS_3'],
              ['Label_HS_11', 'Label_HS_12', 'Label_HS_13', 'Label_HS_14', 'Label_HS_15', 'Label_HS_16', 'Label_HS_17', 'Label_HS_18',
               'Label_HS_19', 'Label_HS_20', 'Label_HS_21', 'Label_HS_22', KEY_IMAGE], TYPE_TEXTBOX, self.get_SHS_RHS_properties)
        change_tab.append(t5)

        t6 = (KEY_DISP_COLSEC, ['Label_CHS_1', 'Label_CHS_2', 'Label_CHS_3'],
              ['Label_CHS_11', 'Label_CHS_12', 'Label_CHS_13', 'Label_HS_14', 'Label_HS_15', 'Label_HS_16', 'Label_21', 'Label_22',
               KEY_IMAGE], TYPE_TEXTBOX, self.get_CHS_properties)
        change_tab.append(t6)

        t6 = (KEY_DISP_COLSEC, [KEY_SECSIZE], [KEY_SOURCE], TYPE_TEXTBOX, self.change_source)
        change_tab.append(t6)


        return change_tab

    def edit_tabs(self):
        """ This function is required if the tab name changes based on connectivity or profile or any other key.
                Not required for this module but empty list should be passed"""
        return []

    def input_dictionary_design_pref(self):
        """

        :return: This function is used to choose values of design preferences to be saved to design dictionary.

         It returns list of tuple which contains, tab name, input widget type of keys, keys whose values to be saved,

         [(Tab Name, input widget type of keys, [List of keys to be saved])]

         """
        design_input = []

        t1 = (KEY_DISP_COLSEC, TYPE_COMBOBOX, [KEY_SEC_MATERIAL])#Need to check
        design_input.append(t1)

        t1 = (KEY_DISP_COLSEC, TYPE_TEXTBOX, [KEY_SEC_FU, KEY_SEC_FY])
        design_input.append(t1)

        t2 = ("Optimization", TYPE_TEXTBOX, [ KEY_EFFECTIVE_AREA_PARA]) #, KEY_STEEL_COST
        design_input.append(t2)

        t2 = ("Optimization", TYPE_COMBOBOX, [KEY_ALLOW_CLASS, KEY_LOAD]) #, KEY_STEEL_COST
        design_input.append(t2)

        t6 = ("Design", TYPE_COMBOBOX, [KEY_DP_DESIGN_METHOD])
        design_input.append(t6)

        return design_input

    def input_dictionary_without_design_pref(self):

        design_input = []

        t1 = (KEY_MATERIAL, [KEY_SEC_MATERIAL], 'Input Dock')
        design_input.append(t1)

        t2 = (None, [KEY_ALLOW_CLASS, KEY_EFFECTIVE_AREA_PARA, KEY_LOAD, KEY_DP_DESIGN_METHOD], '') 
        design_input.append(t2)

        return design_input

    def refresh_input_dock(self):
    
        add_buttons = []

        t2 = (KEY_DISP_COLSEC, KEY_SECSIZE, TYPE_COMBOBOX, KEY_SECSIZE, None, None, "Columns")
        add_buttons.append(t2)

        return add_buttons

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
            KEY_LOAD : 'Normal',
            KEY_DP_DESIGN_METHOD: "Limit State Design",
        }[key]

        return val

    ####################################
    # Design Preference Functions End
    ####################################

    # Setting up logger and Input and Output Docks
    ####################################
    def module_name(self):
        return KEY_DISP_FLEXURE

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

        t1 = (KEY_SECSIZE, self.fn_profile_section)
        c_lst.append(t1)

        return c_lst

    def input_values(self):
        '''
        TODO : Make seperate sub-functions to add??
            At support & At Top restraints should be inactive
            Depending on Support Conditions : if cantilever  then active and Torsional &
            Warping Restraint be inactive.
 
        '''

        self.module = KEY_DISP_FLEXURE
        options_list = []

        t1 = (None, DISP_TITLE_CM, TYPE_TITLE, None, True, 'No Validator')
        options_list.append(t1)

        t1 = (KEY_MODULE, KEY_DISP_FLEXURE, TYPE_MODULE, None, True, "No Validator")
        options_list.append(t1)

        t2 = (KEY_SEC_PROFILE, KEY_DISP_SEC_PROFILE, TYPE_COMBOBOX, VALUES_SEC_PROFILE, True, 'No Validator') #'Beam and Column'
        options_list.append(t2)

        t4 = (KEY_SECSIZE, KEY_DISP_SECSIZE, TYPE_COMBOBOX_CUSTOMIZED, ['All','Customized'], True, 'No Validator')
        options_list.append(t4)

        t4 = (KEY_MATERIAL, KEY_DISP_MATERIAL, TYPE_COMBOBOX, VALUES_MATERIAL, True, 'No Validator')
        options_list.append(t4)

        t1 = (None, KEY_SECTION_DATA, TYPE_TITLE, None, True, 'No Validator')
        options_list.append(t1)

        t2 = (
            KEY_DESIGN_TYPE_FLEXURE,
            KEY_BEAM_SUPP_TYPE,
            TYPE_COMBOBOX,
            VALUES_SUPP_TYPE,
            True,
            "No Validator",
        )
        options_list.append(t2)

        #
        t3 = (KEY_BENDING, KEY_DISP_BENDING, TYPE_COMBOBOX, VALUES_BENDING_TYPE, False, 'No Validator')
        options_list.append(t3)
        #
        #
        t4 = (KEY_SUPPORT, KEY_DISP_SUPPORT, TYPE_COMBOBOX,KEY_DISP_SUPPORT_LIST, True, 'No Validator')
        options_list.append(t4)

        t5 = (KEY_LENGTH, KEY_DISP_LENGTH_BEAM, TYPE_TEXTBOX, None, True, 'Int Validator')
        options_list.append(t5)
        
        t10 = (KEY_TORSIONAL_RES, DISP_TORSIONAL_RES, TYPE_COMBOBOX, Torsion_Restraint_list, True, 'No Validator')
        options_list.append(t10)
        
        t11 = (KEY_WARPING_RES, DISP_WARPING_RES, TYPE_COMBOBOX, Warping_Restraint_list, True, 'No Validator')
        options_list.append(t11)

        t11 = (KEY_SUPPORT_TYPE, DISP_SUPPORT_RES, TYPE_COMBOBOX, Supprt_Restraint_list, True, 'No Validator')
        options_list.append(t11)

        t11 = (KEY_SUPPORT_TYPE2, DISP_TOP_RES, TYPE_COMBOBOX, Top_Restraint_list, False, 'No Validator')
        options_list.append(t11)

        t10 = (KEY_END1, KEY_DISP_END1, TYPE_COMBOBOX, VALUES_END1, True, 'No Validator')
        options_list.append(t10)

        t11 = (KEY_END2, KEY_DISP_END2, TYPE_COMBOBOX, VALUES_END2, True, 'No Validator')
        options_list.append(t11)

        t12 = (KEY_IMAGE, None, TYPE_IMAGE_COMPRESSION, "./ResourceFiles/images/6.RRRR.PNG", True, 'No Validator')
        options_list.append(t12)

        t7 = (None, DISP_TITLE_FSL, TYPE_TITLE, None, True, 'No Validator')
        options_list.append(t7)

        t8 = (KEY_SHEAR, KEY_DISP_SHEAR, TYPE_TEXTBOX, None, True, 'No Validator')
        options_list.append(t8)

        t8 = (KEY_MOMENT, KEY_DISP_MOMENT, TYPE_TEXTBOX, None, True, 'No Validator')
        options_list.append(t8)

        return options_list

    def fn_profile_section(self):

        profile = self[0]
        if profile == 'Beams': #Beam and Column
            return connectdb("Beams", call_type="popup")
            profile2 = connectdb("Columns", call_type="popup")
        # return list(set(profile1 + profile2))
            

    def fn_end1_end2(self):

        end1 = self[0]
        if end1 == 'Fixed':
            return VALUES_END2
        elif end1 == 'Free':
            return ['Fixed']
        elif end1 == 'Hinged':
            return ['Fixed', 'Hinged', 'Roller']
        elif end1 == 'Roller':
            return ['Fixed', 'Hinged']

    def fn_end1_image(self):

        if self == 'Fixed':
            return "./ResourceFiles/images/6.RRRR.PNG"
        elif self == 'Free':
            return "./ResourceFiles/images/1.RRFF.PNG"
        elif self == 'Hinged':
            return "./ResourceFiles/images/5.RRRF.PNG"
        elif self == 'Roller':
            return "./ResourceFiles/images/4.RRFR.PNG"

    def fn_end2_image(self):

        end1 = self[0]
        end2 = self[1]

        if end1 == 'Fixed':
            if end2 == 'Fixed':
                return "./ResourceFiles/images/6.RRRR.PNG"
            elif end2 == 'Free':
                return "./ResourceFiles/images/1.RRFF_rotated.PNG"
            elif end2 == 'Hinged':
                return "./ResourceFiles/images/5.RRRF_rotated.PNG"
            elif end2 == 'Roller':
                return "./ResourceFiles/images/4.RRFR_rotated.PNG"
        elif end1 == 'Free':
            return "./ResourceFiles/images/1.RRFF.PNG"
        elif end1 == 'Hinged':
            if end2 == 'Fixed':
                return "./ResourceFiles/images/5.RRRF.PNG"
            elif end2 == 'Hinged':
                return "./ResourceFiles/images/3.RFRF.PNG"
            elif end2 == 'Roller':
                return "./ResourceFiles/images/2.FRFR_rotated.PNG"
        elif end1 == 'Roller':
            if end2 == 'Fixed':
                return "./ResourceFiles/images/4.RRFR.PNG"
            elif end2 == 'Hinged':
                return "./ResourceFiles/images/2.FRFR.PNG"

    def input_value_changed(self):

        lst = []

        t1 = ([KEY_SEC_PROFILE], KEY_SECSIZE, TYPE_COMBOBOX_CUSTOMIZED, self.fn_profile_section)
        lst.append(t1)


        t3 = ([KEY_MATERIAL], KEY_MATERIAL, TYPE_CUSTOM_MATERIAL, self.new_material)
        lst.append(t3)

        t18 = ([KEY_BENDING],
               'After checking Non-dimensional slenderness ratio for given section, some sections maybe be ignored by Osdag.[Ref IS 8.2.2] ', TYPE_WARNING, self.major_bending_warning)
        lst.append(t18)

        return lst
    
    def major_bending_warning(self):

        if self[0] in ['Major']:
            return True
        else:
            return False

    def output_values(self, flag):

        out_list = []

        t1 = (None, DISP_TITLE_STRUT_SECTION, TYPE_TITLE, None, True)
        out_list.append(t1)

        t1 = (KEY_TITLE_OPTIMUM_DESIGNATION, KEY_DISP_TITLE_OPTIMUM_DESIGNATION, TYPE_TEXTBOX, self.result_designation if flag else '', True)
        out_list.append(t1)

        t1 = (KEY_OPTIMUM_UR_COMPRESSION, KEY_DISP_OPTIMUM_UR_COMPRESSION, TYPE_TEXTBOX, self.result_UR if flag else '', True)
        out_list.append(t1)

        t1 = (KEY_OPTIMUM_SC, KEY_DISP_OPTIMUM_SC, TYPE_TEXTBOX, self.result_section_class if flag else '', True)
        out_list.append(t1)

        t2 = (KEY_EFF_SEC_AREA_ZZ, KEY_DISP_EFF_SEC_AREA_ZZ, TYPE_TEXTBOX, round(self.result_effective_area, 2) if flag else '', True)
        out_list.append(t2)

        t1 = (None, DISP_TITLE_ZZ, TYPE_TITLE, None, True)
        out_list.append(t1)

        t2 = (KEY_EFF_LEN_ZZ, KEY_DISP_EFF_LEN_ZZ, TYPE_TEXTBOX, round(self.result_eff_len_zz * 1e-3, 2) if flag else '', True)
        out_list.append(t2)

        t2 = (KEY_EULER_BUCKLING_STRESS_ZZ, KEY_DISP_EULER_BUCKLING_STRESS_ZZ, TYPE_TEXTBOX, round(self.result_ebs_zz, 2) if flag else '', True)
        out_list.append(t2)

        t2 = (KEY_BUCKLING_CURVE_ZZ, KEY_DISP_BUCKLING_CURVE_ZZ, TYPE_TEXTBOX, self.result_bc_zz if flag else '', True)
        out_list.append(t2)

        t2 = (KEY_IMPERFECTION_FACTOR_ZZ, KEY_DISP_IMPERFECTION_FACTOR_ZZ, TYPE_TEXTBOX, round(self.result_IF_zz, 2) if flag else '', True)
        out_list.append(t2)

        t2 = (KEY_SR_FACTOR_ZZ, KEY_DISP_SR_FACTOR_ZZ, TYPE_TEXTBOX, round(self.result_srf_zz, 2) if flag else '', True)
        out_list.append(t2)

        t2 = (KEY_NON_DIM_ESR_ZZ, KEY_DISP_NON_DIM_ESR_ZZ, TYPE_TEXTBOX, round(self.result_nd_esr_zz, 2) if flag else '', True)
        out_list.append(t2)

        t2 = (KEY_COMP_STRESS_ZZ, KEY_DISP_COMP_STRESS_ZZ, TYPE_TEXTBOX, round(self.result_fcd_zz, 2) if flag else '', True)
        out_list.append(t2)

        t10 = (None, DISP_TITLE_YY, TYPE_TITLE, None, True)
        out_list.append(t10)

        t2 = (KEY_EFF_LEN_YY, KEY_DISP_EFF_LEN_YY, TYPE_TEXTBOX, round(self.result_eff_len_yy * 1e-3, 2) if flag else '', True)
        out_list.append(t2)

        t2 = (KEY_EULER_BUCKLING_STRESS_YY, KEY_DISP_EULER_BUCKLING_STRESS_YY, TYPE_TEXTBOX, round(self.result_ebs_yy, 2) if flag else '', True)
        out_list.append(t2)

        t2 = (KEY_BUCKLING_CURVE_YY, KEY_DISP_BUCKLING_CURVE_YY, TYPE_TEXTBOX, self.result_bc_yy if flag else '', True)
        out_list.append(t2)

        t2 = (KEY_IMPERFECTION_FACTOR_YY, KEY_DISP_IMPERFECTION_FACTOR_YY, TYPE_TEXTBOX, round(self.result_IF_yy, 2) if flag else '', True)
        out_list.append(t2)

        t2 = (KEY_SR_FACTOR_YY, KEY_DISP_SR_FACTOR_YY, TYPE_TEXTBOX, round(self.result_srf_yy, 2) if flag else '', True)
        out_list.append(t2)

        t2 = (KEY_NON_DIM_ESR_YY, KEY_DISP_NON_DIM_ESR_YY, TYPE_TEXTBOX, round(self.result_nd_esr_yy, 2) if flag else '', True)
        out_list.append(t2)

        # t2 = (KEY_EFF_SEC_AREA_YY, KEY_DISP_EFF_SEC_AREA_YY, TYPE_TEXTBOX, round(self.effective_area, 2) if flag else '', True)
        # out_list.append(t2)

        t2 = (KEY_COMP_STRESS_YY, KEY_DISP_COMP_STRESS_YY, TYPE_TEXTBOX, round(self.result_fcd_yy, 2) if flag else '', True)
        out_list.append(t2)

        t1 = (None, KEY_DESIGN_COMPRESSION, TYPE_TITLE, None, True)
        out_list.append(t1)

        t1 = (KEY_DESIGN_STRENGTH_COMPRESSION, KEY_DISP_DESIGN_STRENGTH_COMPRESSION, TYPE_TEXTBOX, round(self.result_capacity * 1e-3, 2) if flag else
        '', True)
        out_list.append(t1)

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
            if option[2] == TYPE_TEXTBOX or option[0] == KEY_LENGTH or option[0] == KEY_SHEAR or option[0] == KEY_MOMENT:
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
                    if float(design_dictionary[option[0]]) <= 0.0:
                        print("Input value(s) cannot be equal or less than zero.")
                        error = "Input value(s) cannot be equal or less than zero."
                        all_errors.append(error)
                    else:
                        flag2 = True
                elif option[0] == KEY_MOMENT:
                    if float(design_dictionary[option[0]]) <= 0.0:
                        print("Input value(s) cannot be equal or less than zero.")
                        error = "Input value(s) cannot be equal or less than zero."
                        all_errors.append(error)
                    else:
                        flag3 = True
            # elif option[2] == TYPE_COMBOBOX and option[0] not in [KEY_SEC_PROFILE, KEY_END1, KEY_END2, KEY_DESIGN_TYPE_FLEXURE, KEY_BENDING, KEY_SUPPORT]:
            #     val = option[3]
            #     if design_dictionary[option[0]] == val[0]:
            #         missing_fields_list.append(option[1])
                   

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

    def get_3d_components(self):

        components = []

        # t3 = ('Column', self.call_3DColumn)
        # components.append(t3)

        return components

    # warn if a beam of older version of IS 808 is selected
    def warn_text(self):
        """ give logger warning when a beam from the older version of IS 808 is selected """
        global logger
        red_list = red_list_function()

        if (self.sec_profile == VALUES_SEC_PROFILE[0]) or (self.sec_profile == VALUES_SEC_PROFILE[1]):  # Beams or Columns
            for section in self.sec_list:
                if section in red_list:
                    logger.warning(" : You are using a section ({}) (in red color) that is not available in latest version of IS 808".format(section))

    # Setting inputs from the input dock GUI
    def set_input_values(self, design_dictionary):
        super(Flexure, self).set_input_values(self, design_dictionary)

        # section properties
        self.module = design_dictionary[KEY_MODULE]
        self.mainmodule = 'Member'
        self.sec_profile = design_dictionary[KEY_SEC_PROFILE]
        self.sec_list = design_dictionary[KEY_SECSIZE]
        print(f"\n Inside set_input_values{self.sec_profile}")
        print(f"\n sec_profile{self.sec_list}")
        self.main_material = design_dictionary[KEY_MATERIAL]
        self.material = design_dictionary[KEY_SEC_MATERIAL]

        # design type
        self.design_type = design_dictionary[KEY_DESIGN_TYPE_FLEXURE]  # or KEY_DISP_DESIGN_TYPE2_FLEXURE
        if self.design_type == 'Laterally Supported':
            pass
        elif self.design_type == KEY_DISP_DESIGN_TYPE2_FLEXURE:
            self.bending_type = str(design_dictionary[KEY_BENDING]) if design_dictionary[KEY_BENDING] != 'Disabled' else 'NA'
            if self.bending_type == KEY_DISP_BENDING2:
                self.design_type = KEY_DISP_DESIGN_TYPE_FLEXURE
            elif self.bending_type == KEY_DISP_BENDING1:
                self.lambda_lt = self.lambda_lt_check_member_type
                if self.lambda_lt < 0.4:
                    self.design_type == KEY_DISP_DESIGN_TYPE_FLEXURE

        # section user data        
        self.length = float(design_dictionary[KEY_LENGTH])


        # end condition
        self.support = design_dictionary[KEY_SUPPORT]
        if self.support == 'Laterally Supported':
            pass


        # factored loads
        self.load = Load(
            shear_force=design_dictionary[KEY_SHEAR],
            axial_force="",
            moment=design_dictionary[KEY_MOMENT],
            unit_kNm=True,
        )

        # design preferences
        # self.allowable_utilization_ratio = float(design_dictionary[KEY_ALLOW_UR])
        self.effective_area_factor = float(design_dictionary[KEY_EFFECTIVE_AREA_PARA])
        self.allowable_utilization_ratio = 1.0
        self.optimization_parameter = "Utilization Ratio"
        self.allow_class = design_dictionary[KEY_ALLOW_CLASS]  # if 'Semi-Compact' is available
        self.steel_cost_per_kg = 50
        # self.in_plane = float(design_dictionary[KEY_Buckling_In_plane])
        # self.out_plane = float(design_dictionary[KEY_Buckling_Out_plane])
        self.allowed_sections = []
        if self.allow_class == "Yes":
            self.allowed_sections == "Semi-Compact"

        print(f"self.allowed_sections {self.allowed_sections}")
        print("==================")
        # print(f"self.load_type {self.load_type}")

        print(f"self.module{self.module}")
        print(f"self.sec_list {self.sec_list}")
        print(f"self.material {self.material}")
        print(f"self.length {self.length}")
        print(f"self.load {self.load}")
        print("==================")

        # safety factors
        self.gamma_m0 = IS800_2007.cl_5_4_1_Table_5["gamma_m0"]["yielding"]
        self.gamma_m1 = IS800_2007.cl_5_4_1_Table_5["gamma_m1"]["ultimate_stress"]
        self.material_property = Material(material_grade=self.material, thickness=0)
        print(f"self.material_property {self.material_property}]")
        print( "self.material_property",self.material_property.fy)
        # initialize the design status
        self.design_status_list = []
        self.design_status = False
        self.sec_prop_initial_dict = {}

        # self.K = self.in_plane * self.out_plane
        # print(
        #     "K = {}.The input values are set. Performing preliminary member check(s).".format(
        #         self.K
        #     )
        # )

        self.design(self, design_dictionary)
        self.results(self, design_dictionary)

    
    # Simulation starts here
    def design(self, design_dictionary, flag=0):
        # flag = self.section_classification(self)
        print(f"\n Inside design")

        """Perform design of struct"""
        # checking DP inputs
        '''
        TODO optimimation_tab_check changes to include self.material_property = Material(material_grade=self.material, thickness=0) 
        for each section'''
        self.optimization_tab_check(self)
        print( "self.material_property",self.material_property.fy)
        self.input_modifier(self)
        print( "self.material_property",self.material_property.fy)
        if len(self.input_modified) != 0:
            self.design_beam(self, design_dictionary)

    def optimization_tab_check(self):
        print(f"\n Inside optimization_tab_check")
        if (self.effective_area_factor <= 0.10) or (self.effective_area_factor > 1.0):
            logger.warning(
                "The defined value of Effective Area Factor in the design preferences tab is out of the suggested range."
            )
            logger.info("Provide an appropriate input and re-design.")
            logger.info("Assuming a default value of 1.0.")
            self.effective_area_factor = 1.0
            self.design_status = False
            self.design_status_list.append(self.design_status)

        elif (self.steel_cost_per_kg < 0.10) or (self.effective_area_factor > 1.0):
            # No suggested range in Description
            logger.warning(
                "The defined value of the cost of steel (in INR) in the design preferences tab is out of the suggested range."
            )
            logger.info("Provide an appropriate input and re-design.")
            logger.info("Assuming a default rate of 50 (INR/kg).")
            self.steel_cost_per_kg = 50
            self.design_status = False
            self.design_status_list.append(self.design_status)
        else:
            if (
                self.effective_area_factor >= self.material_property.fy * self.gamma_m0 / (self.material_property.fu * 0.9 * self.gamma_m1)
            ):
                pass
            else:
                self.effective_area_factor = (
                    self.material_property.fy
                    * self.gamma_m0
                    / (self.material_property.fu * 0.9 * self.gamma_m1)
                )
                logger.info(
                    f"The effect of holes in the tension flange is considered on the design bending strength. The ratio of net to gross area of the flange in tension is considered {self.effective_area_factor}"
                )

            logger.info("Provided appropriate design preference, now checking input.")
    
    def input_modifier(self):
        """Classify the sections based on Table 2 of IS 800:2007"""
        print(f"Inside input_modifier")
        local_flag = True
        self.input_modified = []
        self.input_section_list = []
        # self.input_section_classification = {}

        for section in self.sec_list:
            section = section.strip("'")
            self.section_property = self.section_conect_database(self, section)
            print( "self.material_property",self.material_property.fy)
            if self.allow_class:
                Zp_req = (
                    self.load.moment
                    * self.gamma_m0
                    / (
                        self.material_property.fy
                        * self.section_property.elast_sec_mod_z
                        / self.section_property.plast_sec_mod_z
                    )
                )
                print('Inside input_modifier',self.allow_class, self.load.moment, self.gamma_m0, self.material_property.fy
                        * self.section_property.elast_sec_mod_z
                        / self.section_property.plast_sec_mod_z)
            else:
                Zp_req = self.load.moment * self.gamma_m0 / self.material_property.fy
                print('Inside input_modifier',self.allow_class,self.load.moment, self.gamma_m0, self.material_property.fy)
            if self.section_property.plast_sec_mod_z >= Zp_req:
                self.input_modified.append(section)
                logger.info(
                    f"Required Zp_req={Zp_req} and Zp of section={self.section_property.plast_sec_mod_z}.{self.section_property.designation} section satisfy Min Zp_req value")
            else:
                logger.info(
                    f"Required Zp_req={Zp_req} and Zp of section={self.section_property.plast_sec_mod_z}.{self.section_property.designation} section dosen't satisfy Min Zp_req value")
        print("self.input_modified", self.input_modified)

    def section_conect_database(self, section):
        print(f"section_conect_database{section}")
        print(section)
        # print(self.sec_profile)
        if (
            self.sec_profile == VALUES_SECTYPE[1]
            or self.sec_profile == VALUES_SECTYPE[2]
            or self.sec_profile == "I-section"
        ):  # I-section
            self.section_property = ISection(
                designation=section, material_grade=self.material
            )
            self.material_property.connect_to_database_to_get_fy_fu(
                self.material, max(self.section_property.flange_thickness, self.section_property.web_thickness)
            )
            self.epsilon = math.sqrt(250 / self.material_property.fy)
        return self.section_property

    def design_beam(self, design_dictionary):
        # 1- Based on optimum UR
        self.optimum_section_ur_results = {}
        self.optimum_section_ur = []

        # 2 - Based on optimum cost
        self.optimum_section_cost_results = {}
        self.optimum_section_cost = []

        # 1 - section classification
        flag = self.section_classification(self)

        if flag:
            for section in self.input_section_list:
                # initialize lists for updating the results dictionary
                self.section_property = self.section_conect_database(self, section)

                # Step 1.1 - computing the effective sectional area
                self.effective_area = self.section_property.area
                self.common_checks_1(self, section, step=2)
                
                # 2 - Effective length
                self.effective_length = self.effective_length_beam(self, design_dictionary, self.length)  # mm
                print(f"self.effective_length {self.effective_length} \n self.input_section_classification{self.input_section_classification} ")

                list_result = []
                list_result.append(section)
                self.section_class = self.input_section_classification[section][0]

                # 3 - web buckling under shear
                web_buckling = IS800_2007.cl_8_2_1_web_buckling(
                    d=self.section_property.depth,
                    tw=self.section_property.web_thickness,
                    e=self.epsilon,
                )

                if web_buckling:
                    web_buckling_message = 'Thin web'
                    logger.warning("Thin web [Reference: Cl 8.2.1.1, IS 800:2007]")
                    # self.V_d = pass
                else:
                    self.V_d = IS800_2007.cl_8_4_design_shear_strength(
                        self.section_property.depth
                        * self.section_property.web_thickness,
                        self.material_property.fy, self.gamma_m0
                    )

                    self.high_shear_check = IS800_2007.cl_8_2_1_2_high_shear_check(
                        self.load.shear_force, self.V_d
                    )
                    # 4 -  design bending strength
                    self.bending_strength_section = self.bending_strength(self)

                    print(f"Common result {list_result, self.section_class, web_buckling, self.V_d, self.high_shear_check, self.bending_strength_section}")

                    #5 - Web Buckling check(when high shear) -If user wants then only
                    # if web_buckling:
                    #     b1 = input('Enter bearing')
                    #     self.web_buckling_strength = self.section_property.web_thickness * (b1 + 1.25 * self.section_property.depth)
                
                
                list_result.extend([self.section_class, self.effective_area, self.effective_length])

                # Step 2 - computing the design compressive stress
                self.common_checks_1(self, section, step=3)
                list_result.extend(
                    [
                        self.buckling_class,
                        self.imperfection_factor,
                        self.effective_length,
                    ]
                )

                if "Concentric Load" == "Concentric Load":
                    print(f"step == 4" f"list_result {list_result}")
                    self.lambda_vv = "NA"
                    self.lambda_psi = "NA"
                    # step == 4
                    self.common_checks_1(
                        self, section, step=4, list_result=["Concentric"]
                    )
                # else:
                #     # self.min_radius_gyration = min(self.section_property.rad_of_gy_y, self.section_property.rad_of_gy_z)
                #     returned_list = IS800_2007.cl_7_5_1_2_equivalent_slenderness_ratio_of_truss_compression_members_loaded_one_leg(
                #         self.length,
                #         self.min_radius_gyration,
                #         self.section_property.leg_a_length,
                #         self.section_property.leg_b_length,
                #         self.section_property.thickness,
                #         self.material_property.fy,
                #         2,
                #         self.fixity,
                #     )

                #     self.equivalent_slenderness = returned_list[0]
                #     self.lambda_vv = round(returned_list[1], 2)
                #     self.lambda_psi = round(returned_list[2], 2)
                #     self.k1 = returned_list[3]
                #     self.k2 = returned_list[4]
                #     self.k3 = returned_list[5]
                #     print(
                #         f"self.equivalent_slenderness {self.equivalent_slenderness} "
                #         f" \n self.slenderness {self.slenderness} "
                #         f" \n self.lambda_vv {self.lambda_vv} "
                #         f" \n self.lambda_psi {self.lambda_psi} "
                #         f" \n self.k1 {self.k1} "
                #         f" \n self.k2 {self.k2} "
                #         f" \n self.k3 {self.k3} "
                #     )
                #     self.common_checks_1(
                #         self,
                #         section,
                #         step=4,
                #         list_result=["Leg", self.equivalent_slenderness],
                #     )

                # 2.7 - Capacity of the section
                self.section_capacity = (
                    self.design_compressive_stress * self.effective_area
                )  # N

                # 2.8 - UR
                self.ur = round(self.load.axial_force / self.section_capacity, 3)
                self.optimum_section_ur.append(self.ur)

                # 2.9 - Cost of the section in INR
                self.cost = (
                    (
                        self.section_property.unit_mass
                        * self.section_property.area
                        * 1e-4
                    )
                    * self.length
                    * self.steel_cost_per_kg
                )
                self.optimum_section_cost.append(self.cost)

                list_result.extend(
                    [
                        self.slenderness,
                        self.euler_buckling_stress,
                        self.lambda_vv,
                        self.lambda_psi,
                        self.nondimensional_effective_slenderness_ratio,
                        self.phi,
                        self.stress_reduction_factor,
                        self.design_compressive_stress_fr,
                        self.design_compressive_stress_max,
                        self.design_compressive_stress,
                        self.section_capacity,
                        self.ur,
                        self.cost,
                    ]
                )

                # Step 3 - Storing the optimum results to a list in a descending order

                list_1 = [
                    "Designation",
                    "Section class",
                    "Effective area",
                    "Buckling_class",
                    "IF",
                    "Effective_length",
                    "Effective_SR",
                    "EBS",
                    "lambda_vv",
                    "lambda_psi",
                    "ND_ESR",
                    "phi",
                    "SRF",
                    "FCD_formula",
                    "FCD_max",
                    "FCD",
                    "Capacity",
                    "UR",
                    "Cost",
                ]

                self.common_checks_1(self, section, 5, list_result, list_1)

    def common_checks_1(self, section, step=1, list_result=[], list_1=[]):
        if step == 1:
            print(f"Working correct here")
        elif step == 2:
            # reduction of the area based on the connection requirements (input from design preferences)
            if self.effective_area_factor < 1.0:
                self.effective_area = round(
                    self.effective_area * self.effective_area_factor, 2
                )

                logger.warning(
                    "Reducing the effective sectional area as per the definition in the Design Preferences tab."
                )
                logger.info(
                    "The actual effective area is {} mm2 and the reduced effective area is {} mm2 [Reference: Cl. 7.3.2, IS 800:2007]".format(
                        round((self.effective_area / self.effective_area_factor), 2),
                        self.effective_area,
                    )
                )
            else:
                if self.section_class != "Slender":
                    logger.info(
                        "The effective sectional area is taken as 100% of the cross-sectional area [Reference: Cl. 7.3.2, IS 800:2007]."
                    )
        elif step == 3:
            # 2.1 - Buckling curve classification and Imperfection factor
            if self.section_property.type == 'Rolled':
                        self.buckling_class = IS800_2007.cl_7_1_2_2_buckling_class_of_crosssections(self.section_property.flange_width,self.section_property.depth,self.section_property.flange_thickness,cross_section='Rolled I-sections',section_type='Hot rolled')['z-z']
                                            
            else:
                self.buckling_class = IS800_2007.cl_7_1_2_2_buckling_class_of_crosssections(self.section_property.flange_width,
                                                                                            self.section_property.depth,
                                                                                            self.section_property.flange_thickness,
                                                                                            cross_section='Welded I-section',
                                                                                            section_type='Hot rolled')['z-z']
            self.imperfection_factor = IS800_2007.cl_7_1_2_1_imperfection_factor(
                buckling_class=self.buckling_class
            )

        elif step == 4:
            print(
                f"\n data sent "
                f" self.material_property.fy {self.material_property.fy}"
                f"self.gamma_m0 {self.gamma_m0}"
                f"self.slenderness {self.slenderness}"
                f" self.imperfection_factor {self.imperfection_factor}"
                f"self.section_property.modulus_of_elasticity {self.section_property.modulus_of_elasticity}"
            )

            list_cl_7_1_2_1_design_compressisive_stress = (
                IS800_2007.cl_7_1_2_1_design_compressisive_stress(
                    self.material_property.fy,
                    self.gamma_m0,
                    self.slenderness,
                    self.imperfection_factor,
                    self.section_property.modulus_of_elasticity,
                    check_type=list_result,
                )
            )
            for x in list_cl_7_1_2_1_design_compressisive_stress:
                print(f"x {x} ")
            self.euler_buckling_stress = list_cl_7_1_2_1_design_compressisive_stress[0]
            self.nondimensional_effective_slenderness_ratio = (
                list_cl_7_1_2_1_design_compressisive_stress[1]
            )
            self.phi = list_cl_7_1_2_1_design_compressisive_stress[2]
            self.stress_reduction_factor = list_cl_7_1_2_1_design_compressisive_stress[
                3
            ]
            self.design_compressive_stress_fr = (
                list_cl_7_1_2_1_design_compressisive_stress[4]
            )
            self.design_compressive_stress = (
                list_cl_7_1_2_1_design_compressisive_stress[5]
            )
            self.design_compressive_stress_max = (
                list_cl_7_1_2_1_design_compressisive_stress[6]
            )
        elif step == 5:
            # 1- Based on optimum UR
            self.optimum_section_ur_results[self.ur] = {}
            list_2 = list_result.copy()
            for j in list_1:
                # k = 0
                for k in list_2:
                    self.optimum_section_ur_results[self.ur][j] = k
                    # k += 1
                    list_2.pop(0)
                    break

            # 2- Based on optimum cost
            self.optimum_section_cost_results[self.cost] = {}

            list_2 = list_result.copy()  # Why?
            for j in list_1:
                for k in list_2:
                    self.optimum_section_cost_results[self.cost][j] = k
                    list_2.pop(0)
                    break
            print(
                f"\n self.optimum_section_cost_results {self.optimum_section_cost_results}"
                f"\n self.optimum_section_ur_results {self.optimum_section_ur_results}"
            )
        elif step == 6:
            self.single_result[self.sec_profile] = {}
            list_2 = list_result.copy()
            for j in list_1:
                # k = 0
                for k in list_2:
                    self.single_result[self.sec_profile][j] = k
                    # k += 1
                    list_2.pop(0)
                    break
            print(f"\n self.single_result {self.single_result}")    

    def bending_strength(self):
        # 4 - design bending strength -preliminary
        M_d = IS800_2007.cl_8_2_1_2_design_bending_strength(
            self.section_class,
            self.section_property.plast_sec_mod_z,
            self.section_property.elast_sec_mod_z,
            self.material_property.fy,
            self.gamma_m0,
            self.support,
        )
        if self.design_type == KEY_DISP_DESIGN_TYPE_FLEXURE:
            if self.high_shear_check:
                if self.section_class == "Plastic" or self.section_class == "Compact":
                    self.bending_strength_section = self.bending_strength_reduction(M_d)
                else:
                    self.bending_strength_section = (
                        self.section_property.elast_sec_mod_z
                        * self.material_property.fy
                        * self.gamma_m0
                    )
            else:
                self.bending_strength_section = M_d
        else:
            It = (
                2
                * self.section_property.flange_width
                * self.section_property.flange_thickness**3
            ) / 3 + (
                (self.section_property.depth - self.section_property.flange_thickness)
                * self.section_property.web_thickness**3
            ) / 3
            hf = self.section_property.depth - self.section_property.flange_thickness
            Iw = 0.5**2 * self.section_property.mom_inertia_y * hf**2
            M_cr = IS800_2007.cl_8_2_2_Unsupported_beam_bending_non_slenderness(
                self.material_property.modulus_of_elasticity,
                0.3,
                self.section_property.mom_inertia_y,
                It,
                Iw,
                self.effective_length,
            )
            if self.section_class == "Plastic" or self.section_class == "Compact":
                beta_b = 1.0
            else:
                beta_b = (
                    self.section_property.elast_sec_mod_z
                    / self.section_property.plast_sec_mod_z
                )
            if self.section_property.type == "Rolled":
                alpha_lt = 0.21
            else:
                alpha_lt = 0.49
            lambda_lt = IS800_2007.cl_8_2_2_Unsupported_beam_bending_non_slenderness(
                beta_b,
                self.section_property.plast_sec_mod_z,
                self.section_property.elast_sec_mod_z,
                self.material_property.fy,
                M_cr,
            )
            phi_lt = IS800_2007.cl_8_2_2_Unsupported_beam_bending_phi_lt(
                alpha_lt, lambda_lt
            )
            X_lt = IS800_2007.cl_8_2_2_Unsupported_beam_bending_stress_reduction_factor(
                phi_lt, lambda_lt
            )
            fcd = IS800_2007.cl_8_2_2_Unsupported_beam_bending_compressive_stress(
                X_lt, self.material_property.fy, self.gamma_m0
            )
            self.bending_strength_section = (
                IS800_2007.cl_8_2_2_Unsupported_beam_bending_strength(
                    self.section_property.plast_sec_mod_z,
                    self.section_property.elast_sec_mod_z,
                    fcd=fcd,
                    section_class=self.section_class,
                )
            )
            if self.high_shear_check:
                if self.section_class == "Plastic" or self.section_class == "Compact":
                    self.bending_strength_section = self.bending_strength_reduction(
                        self.bending_strength_section,
                    )
                else:
                    self.bending_strength_section = (
                        self.section_property.elast_sec_mod_z
                        * self.material_property.fy
                        * self.gamma_m0
                    )

    def bending_strength_reduction(self, Md):
        Zfd = (
            self.section_property.plast_sec_mod_z
            - (self.section_property.depth**2 * self.section_property.web_thickness)
            / 4
        )
        Mfd = Zfd * self.material_property.fy / self.gamma_m0
        beta = ((2 * self.load.shear_force / self.V_d) - 1) ** 2
        Mdv = Md - beta(Md - Mfd)
        if (
            Mdv
            <= 1.2
            * self.section_property.plast_sec_mod_z
            * self.material_property.fy
            / self.gamma_m0
        ):
            return Mdv
        else:
            return (
                1.2
                * self.section_property.plast_sec_mod_z
                * self.material_property.fy
                / self.gamma_m0
            )

    
    def section_classification(self, trial_section=""):
        """Classify the sections based on Table 2 of IS 800:2007"""
        print(f"Inside section_classification")
        local_flag = True
        self.input_section_list = []
        self.input_section_classification = {}

        for trial_section in self.input_modified:
            self.section_property = self.section_conect_database(self, trial_section)
            print(f"Type of section{self.section_property.designation}")
            if self.sec_profile != "":  
                if self.section_property.type == "Rolled":
                    web_class = IS800_2007.Table2_iii(
                        self.section_property.depth,
                        self.section_property.web_thickness,
                        self.material_property.fy,
                    )
                    flange_class = IS800_2007.Table2_i(
                        self.section_property.flange_width / 2,
                        self.section_property.web_thickness,
                        self.material_property.fy,
                    )[0]
                    print(f"\n \n \n flange_class {flange_class} \n web_class{web_class} \n \n")

                else:
                    """Need to check below formula"""
                    flange_class = IS800_2007.Table2_i(
                        (
                            (self.section_property.flange_width / 2)
                            - (self.section_property.web_thickness / 2)
                        ),
                        self.section_property.flange_thickness,
                        self.section_property.fy,
                        self.section_property.type,
                    )[0]

                    web_class = IS800_2007.Table2_iii(
                        (
                            self.section_property.depth
                            - (2 * self.section_property.flange_thickness)
                        ),
                        self.section_property.web_thickness,
                        self.material_property.fy,
                        classification_type="Axial compression",
                    )

            if flange_class == "Slender" or web_class == "Slender":
                self.section_class = "Slender"
            else:
                if flange_class == "Plastic" and web_class == "Plastic":
                    self.section_class = "Plastic"
                elif flange_class == "Plastic" and web_class == "Compact":
                    self.section_class = "Compact"
                elif flange_class == "Plastic" and web_class == "Semi-Compact":
                    self.section_class = "Semi-Compact"
                elif flange_class == "Compact" and web_class == "Plastic":
                    self.section_class = "Compact"
                elif flange_class == "Compact" and web_class == "Compact":
                    self.section_class = "Compact"
                elif flange_class == "Compact" and web_class == "Semi-Compact":
                    self.section_class = "Semi-Compact"
                elif flange_class == "Semi-Compact" and web_class == "Plastic":
                    self.section_class = "Semi-Compact"
                elif flange_class == "Semi-Compact" and web_class == "Compact":
                    self.section_class = "Semi-Compact"
                elif flange_class == "Semi-Compact" and web_class == "Semi-Compact":
                    self.section_class = "Semi-Compact"

            logger.info(
                "The section is {}. The trial section ({}) has flange {} and web_class is {}.  [Reference: Cl 3.7, IS 800:2007].".format(
                    self.section_class,
                    trial_section,
                    flange_class,
                    web_class
                )
            )

            if self.allow_class:
                if (
                    self.section_class == "Semi-Compact"
                    or self.section_class == "Compact"
                    or self.section_class == "Plastic"
                ):
                    self.input_section_list.append(trial_section)
                    self.input_section_classification.update({trial_section: [self.section_class, flange_class, web_class]})
                elif self.section_class == "Slender":
                    logger.warning(f"The section.{trial_section} is Slender. Ignoring")
            else:
                if self.section_class == "Compact" or self.section_class == "Plastic":
                    self.input_section_list.append(trial_section)
                    self.input_section_classification.update({trial_section: [self.section_class, flange_class, web_class]})
                elif self.section_class == "Slender":
                    logger.warning(f"The section.{trial_section} is Slender. Ignoring")
                    self.design_status = False
                    self.design_status_list.append(self.design_status)
                elif self.section_class == "Semi-Compact":
                    logger.warning(
                        f"The section.{trial_section} is Semi-Compact. Ignoring"
                    )
                    self.design_status = False
                    self.design_status_list.append(self.design_status)

        if len(self.input_section_list) == 0:
            local_flag = False
        else:
            local_flag = True
        return local_flag
    
    def effective_length_beam(self, design_dictionary, length):
        if self.support == KEY_DISP_SUPPORT1:
            self.Torsional_res = design_dictionary[KEY_TORSIONAL_RES]
            self.Warping = design_dictionary[KEY_WARPING_RES]
            self.Loading = design_dictionary[KEY_LOAD]  #'Normal'or 'Destabilizing'
            self.length = IS800_2007.cl_8_3_1_EffLen_Simply_Supported(
                Torsional=self.Torsional_res,
                Warping=self.Warping,
                length=self.length,
                depth=self.section_property.depth,
                load=self.Loading,
            )
        elif self.support == KEY_DISP_SUPPORT2:
            self.Support = design_dictionary[KEY_SUPPORT_TYPE]
            self.Top = design_dictionary[KEY_SUPPORT_TYPE2]
            self.Loading = design_dictionary[KEY_LOAD]  # 'Normal'or 'Destabilizing'
            self.length = IS800_2007.cl_8_3_3_EffLen_Cantilever(
                Support=self.Support,
                Top=self.Top,
                length=self.length,
                load=self.Loading,
            )
        return length


    def lambda_lt_check_member_type(self, Mcr=0, fcrb=0, Zp=0, f_y=0, Ze=0, beta_b=0):
        lambda_lt_1 = math.sqrt(beta_b * Zp * f_y / Mcr)
        lambda_lt_2 = math.sqrt(f_y / fcrb)
        lambda_lt_check = math.sqrt(1.2 * Ze * f_y / Mcr)
        if lambda_lt_1 == lambda_lt_2:
            if lambda_lt_1 <= lambda_lt_check:
                return lambda_lt_1
        logger.warning(" Issues with the non-dimensional slenderness ratio Lambda_lt")


  
    def design_column(self):
        """ Perform design of column """
        # checking DP inputs
        if (self.allowable_utilization_ratio <= 0.10) or (self.allowable_utilization_ratio > 1.0):
            logger.warning("The defined value of Utilization Ratio in the design preferences tab is out of the suggested range.")
            logger.info("Provide an appropriate input and re-design.")
            logger.info("Assuming a default value of 1.0.")
            self.allowable_utilization_ratio = 1.0
            self.design_status = False
            self.design_status_list.append(self.design_status)

        if (self.effective_area_factor <= 0.10) or (self.effective_area_factor > 1.0):
            logger.warning("The defined value of Effective Area Factor in the design preferences tab is out of the suggested range.")
            logger.info("Provide an appropriate input and re-design.")
            logger.info("Assuming a default value of 1.0.")
            self.effective_area_factor = 1.0
            self.design_status = False
            self.design_status_list.append(self.design_status)

        if (self.steel_cost_per_kg == 0.10) or (self.effective_area_factor > 1.0):
            logger.warning("The defined value of the cost of steel (in INR) in the design preferences tab is out of the suggested range.")
            logger.info("Provide an appropriate input and re-design.")
            logger.info("Assuming a default rate of 50 (INR/kg).")
            self.steel_cost_per_kg = 50
            self.design_status = False
            self.design_status_list.append(self.design_status)

        if len(self.input_section_list) > 0:

            # initializing lists to store the optimum results based on optimum UR and cost

            # 1- Based on optimum UR
            self.optimum_section_ur_results = {}
            self.optimum_section_ur = []

            # 2 - Based on optimum cost
            self.optimum_section_cost_results = {}
            self.optimum_section_cost = []

            i = 1
            for section in self.input_section_list:  # iterating the design over each section to find the most optimum section

                # fetching the section properties of the selected section
                if self.sec_profile == VALUES_SEC_PROFILE[0]:  # Beams
                    self.section_property = Beam(designation=section, material_grade=self.material)
                elif self.sec_profile == VALUES_SEC_PROFILE[1]:  # Columns
                    self.section_property = Column(designation=section, material_grade=self.material)
                elif self.sec_profile == VALUES_SEC_PROFILE[2]:  # RHS
                    self.section_property = RHS(designation=section, material_grade=self.material)
                elif self.sec_profile == VALUES_SEC_PROFILE[3]:  # SHS
                    self.section_property = SHS(designation=section, material_grade=self.material)
                elif self.sec_profile == VALUES_SEC_PROFILE[4]:  # CHS
                    self.section_property = CHS(designation=section, material_grade=self.material)
                else:   #Why?
                    self.section_property = Column(designation=section, material_grade=self.material)

                self.material_property.connect_to_database_to_get_fy_fu(self.material, max(self.section_property.flange_thickness,
                                                                                           self.section_property.web_thickness))

                self.epsilon = math.sqrt(250 / self.material_property.fy)

                # initialize lists for updating the results dictionary
                list_zz = []
                list_yy = []

                list_zz.append(section)
                list_yy.append(section)

                # Step 1 - computing the effective sectional area
                self.section_class = self.input_section_classification[section]

                if self.section_class == 'Slender':
                    logger.warning("The trial section ({}) is Slender. Computing the Effective Sectional Area as per Sec. 9.7.2, "
                                   "Fig. 2 (B & C) of The National Building Code of India (NBC), 2016.".format(section))

                    if (self.sec_profile == VALUES_SEC_PROFILE[0]) or (self.sec_profile == VALUES_SEC_PROFILE[1]):  # Beams or Columns
                        self.effective_area = (2 * ((31.4 * self.epsilon * self.section_property.flange_thickness) *
                                                    self.section_property.flange_thickness)) + \
                                              (2 * ((21 * self.epsilon * self.section_property.web_thickness) * self.section_property.web_thickness))
                    elif (self.sec_profile == VALUES_SEC_PROFILE[2]) or (self.sec_profile == VALUES_SEC_PROFILE[3]):
                        self.effective_area = (2 * 21 * self.epsilon * self.section_property.flange_thickness) * 2
                else:
                    self.effective_area = self.section_property.area  # mm2
                    # print(f"self.effective_area{self.effective_area}")

                # reduction of the area based on the connection requirements (input from design preferences)
                if self.effective_area_factor < 1.0:
                    self.effective_area = round(self.effective_area * self.effective_area_factor, 2)

                    logger.warning("Reducing the effective sectional area as per the definition in the Design Preferences tab.")
                    logger.info("The actual effective area is {} mm2 and the reduced effective area is {} mm2 [Reference: Cl. 7.3.2, IS 800:2007]".
                                format(round((self.effective_area / self.effective_area_factor), 2), self.effective_area))
                else:
                    if self.section_class != 'Slender':
                        logger.info("The effective sectional area is taken as 100% of the cross-sectional area [Reference: Cl. 7.3.2, IS 800:2007].")

                list_zz.append(self.section_class)
                list_yy.append(self.section_class)

                list_zz.append(self.effective_area)
                list_yy.append(self.effective_area)

                # Step 2 - computing the design compressive stress

                # 2.1 - Buckling curve classification and Imperfection factor
                if (self.sec_profile == VALUES_SEC_PROFILE[0]) or (self.sec_profile == VALUES_SEC_PROFILE[1]):  # Beams or Columns

                    if self.section_property.type == 'Rolled':
                        self.buckling_class_zz = IS800_2007.cl_7_1_2_2_buckling_class_of_crosssections(self.section_property.flange_width,
                                                                                                       self.section_property.depth,
                                                                                                       self.section_property.flange_thickness,
                                                                                                       cross_section='Rolled I-sections',
                                                                                                       section_type='Hot rolled')['z-z']
                        self.buckling_class_yy = IS800_2007.cl_7_1_2_2_buckling_class_of_crosssections(self.section_property.flange_width,
                                                                                                       self.section_property.depth,
                                                                                                       self.section_property.flange_thickness,
                                                                                                       cross_section='Rolled I-sections',
                                                                                                       section_type='Hot rolled')['y-y']
                    else:
                        self.buckling_class_zz = IS800_2007.cl_7_1_2_2_buckling_class_of_crosssections(self.section_property.flange_width,
                                                                                                       self.section_property.depth,
                                                                                                       self.section_property.flange_thickness,
                                                                                                       cross_section='Welded I-section',
                                                                                                       section_type='Hot rolled')['z-z']
                        self.buckling_class_yy = IS800_2007.cl_7_1_2_2_buckling_class_of_crosssections(self.section_property.flange_width,
                                                                                                       self.section_property.depth,
                                                                                                       self.section_property.flange_thickness,
                                                                                                       cross_section='Welded I-section',
                                                                                                       section_type='Hot rolled')['y-y']
                else:
                    self.buckling_class_zz = 'a'
                    self.buckling_class_yy = 'a'

                self.imperfection_factor_zz = IS800_2007.cl_7_1_2_1_imperfection_factor(buckling_class=self.buckling_class_zz)
                self.imperfection_factor_yy = IS800_2007.cl_7_1_2_1_imperfection_factor(buckling_class=self.buckling_class_yy)

                list_zz.append(self.buckling_class_zz)
                list_yy.append(self.buckling_class_yy)

                list_zz.append(self.imperfection_factor_zz)
                list_yy.append(self.imperfection_factor_yy)

                # 2.2 - Effective length
                self.effective_length_zz = IS800_2007.cl_7_2_2_effective_length_of_prismatic_compression_members(self.length_zz ,
                                                                                                                 end_1=self.end_1,
                                                                                                                 end_2=self.end_2)  # mm
                self.effective_length_yy = IS800_2007.cl_7_2_2_effective_length_of_prismatic_compression_members(self.length_yy ,
                                                                                                                 end_1=self.end_1,
                                                                                                                 end_2=self.end_2)  # mm

                list_zz.append(self.effective_length_zz)
                list_yy.append(self.effective_length_yy)

                # 2.3 - Effective slenderness ratio
                self.effective_sr_zz = self.effective_length_zz / self.section_property.rad_of_gy_z
                self.effective_sr_yy = self.effective_length_yy / self.section_property.rad_of_gy_y

                list_zz.append(self.effective_sr_zz)
                list_yy.append(self.effective_sr_yy)

                # 2.4 - Euler buckling stress
                self.euler_bs_zz = (math.pi ** 2 * self.section_property.modulus_of_elasticity) / self.effective_sr_zz ** 2
                self.euler_bs_yy = (math.pi ** 2 * self.section_property.modulus_of_elasticity) / self.effective_sr_yy ** 2

                list_zz.append(self.euler_bs_zz)
                list_yy.append(self.euler_bs_yy)

                # 2.5 - Non-dimensional effective slenderness ratio
                self.non_dim_eff_sr_zz = math.sqrt(self.material_property.fy / self.euler_bs_zz)
                self.non_dim_eff_sr_yy = math.sqrt(self.material_property.fy / self.euler_bs_yy)
                # print(f"self.non_dim_eff_sr_zz{self.non_dim_eff_sr_yy},self.phi_yy{self.non_dim_eff_sr_yy}/n")

                list_zz.append(self.non_dim_eff_sr_zz)
                list_yy.append(self.non_dim_eff_sr_yy)

                # 2.5 - phi
                self.phi_zz = 0.5 * (1 + (self.imperfection_factor_zz * (self.non_dim_eff_sr_zz - 0.2)) + self.non_dim_eff_sr_zz ** 2)
                self.phi_yy = 0.5 * (1 + (self.imperfection_factor_yy * (self.non_dim_eff_sr_yy - 0.2)) + self.non_dim_eff_sr_yy ** 2)
                # print(f"self.phi_zz{self.phi_zz},self.phi_yy{self.phi_yy}, self.imperfection_factor_zz{self.imperfection_factor_zz}")

                list_zz.append(self.phi_zz)
                list_yy.append(self.phi_yy)

                # 2.6 - Design compressive stress
                self.stress_reduction_factor_zz = 1 / (self.phi_zz + (self.phi_zz ** 2 - self.non_dim_eff_sr_zz ** 2) ** 0.5)
                self.stress_reduction_factor_yy = 1 / (self.phi_yy + (self.phi_yy ** 2 - self.non_dim_eff_sr_yy ** 2) ** 0.5)

                list_zz.append(self.stress_reduction_factor_zz)
                list_yy.append(self.stress_reduction_factor_yy)

                self.f_cd_1_zz = (self.stress_reduction_factor_zz * self.material_property.fy) / self.gamma_m0
                self.f_cd_1_yy = (self.stress_reduction_factor_yy * self.material_property.fy) / self.gamma_m0
                self.f_cd_2 = self.material_property.fy / self.gamma_m0

                self.f_cd_zz = min(self.f_cd_1_zz, self.f_cd_2)
                self.f_cd_yy = min(self.f_cd_1_yy, self.f_cd_2)

                self.f_cd = min(self.f_cd_zz, self.f_cd_yy)

                list_zz.append(self.f_cd_1_zz)
                list_yy.append(self.f_cd_1_yy)

                list_zz.append(self.f_cd_2)
                list_yy.append(self.f_cd_2)

                list_zz.append(self.f_cd_zz)
                list_yy.append(self.f_cd_yy)

                list_zz.append(self.f_cd)
                list_yy.append(self.f_cd)

                # 2.7 - Capacity of the section
                self.section_capacity = self.f_cd * self.effective_area  # N

                list_zz.append(self.section_capacity)
                list_yy.append(self.section_capacity)

                # 2.8 - UR
                self.ur = round(self.load.axial_force / self.section_capacity, 3)

                list_zz.append(self.ur)
                list_yy.append(self.ur)
                self.optimum_section_ur.append(self.ur)

                # 2.9 - Cost of the section in INR
                self.cost = (self.section_property.unit_mass * self.section_property.area * 1e-4) * min(self.length_zz, self.length_yy) * \
                            self.steel_cost_per_kg

                list_zz.append(self.cost)
                list_yy.append(self.cost)
                self.optimum_section_cost.append(self.cost)
                # print(f"list_zz{list_zz},list_yy{list_yy} ")

                # Step 3 - Storing the optimum results to a list in a descending order

                list_1 = ['Designation', 'Section class', 'Effective area', 'Buckling_curve_zz', 'IF_zz', 'Effective_length_zz', 'Effective_SR_zz',
                          'EBS_zz', 'ND_ESR_zz', 'phi_zz', 'SRF_zz', 'FCD_1_zz', 'FCD_2', 'FCD_zz', 'FCD', 'Capacity', 'UR', 'Cost', 'Designation',
                          'Section class', 'Effective area', 'Buckling_curve_yy', 'IF_yy', 'Effective_length_yy', 'Effective_SR_yy', 'EBS_yy',
                          'ND_ESR_yy', 'phi_yy', 'SRF_yy', 'FCD_1_yy', 'FCD_2', 'FCD_yy', 'FCD', 'Capacity', 'UR', 'Cost']

                # 1- Based on optimum UR
                self.optimum_section_ur_results[self.ur] = {}

                list_2 = list_zz + list_yy
                for j in list_1:
                    # k = 0
                    for k in list_2:
                        self.optimum_section_ur_results[self.ur][j] = k
                        # k += 1
                        list_2.pop(0)
                        break

                # 2- Based on optimum cost
                self.optimum_section_cost_results[self.cost] = {}

                list_2 = list_zz + list_yy                                  #Why?
                for j in list_1:
                    for k in list_2:
                        self.optimum_section_cost_results[self.cost][j] = k
                        list_2.pop(0)
                        break
        else:
            logger.warning("The section(s) defined for performing the column design is/are not selected based on the selected Inputs and/or "
                           "Design Preferences")
            logger.error("Cannot compute!")
            logger.info("Change the inputs provided and re-design.")
            self.design_status = False
            self.design_status_list.append(self.design_status)
            # print(f"design_status_list{self.design_status_list}")

    def results(self, design_dictionary):
        """ """
        # sorting results from the dataset

        # results based on UR
        if self.optimization_parameter == 'Utilization Ratio':
            filter_UR = filter(lambda x: x <= min(self.allowable_utilization_ratio, 1.0), self.optimum_section_ur)
            self.optimum_section_ur = list(filter_UR)

            self.optimum_section_ur.sort()
            # print(f"self.optimum_section_ur{self.optimum_section_ur}")
            #print(f"self.result_UR{self.result_UR}")

            # selecting the section with most optimum UR
            if len(self.optimum_section_ur) == 0:  # no design was successful
                logger.warning("The sections selected by the solver from the defined list of sections did not satisfy the Utilization Ratio (UR) "
                               "criteria")
                logger.error("The solver did not find any adequate section from the defined list.")
                logger.info("Re-define the list of sections or check the Design Preferences option and re-design.")
                self.design_status = False
                self.design_status_list.append(self.design_status)

            else:
                self.result_UR = self.optimum_section_ur[-1]  # optimum section which passes the UR check
                print(f"self.result_UR{self.result_UR}")
                self.design_status = True

        else:  # results based on cost
            self.optimum_section_cost.sort()

            # selecting the section with most optimum cost
            self.result_cost = self.optimum_section_cost[0]

        # print results
        if len(self.optimum_section_ur) == 0:
            logger.warning(
                "The sections selected by the solver from the defined list of sections did not satisfy the Utilization Ratio (UR) "
                "criteria")
            logger.error("The solver did not find any adequate section from the defined list.")
            logger.info("Re-define the list of sections or check the Design Preferences option and re-design.")
            self.design_status = False
            self.design_status_list.append(self.design_status)
            pass
        else:
            if self.optimization_parameter == 'Utilization Ratio':
                self.result_designation = self.optimum_section_ur_results[self.result_UR]['Designation']
                self.result_section_class = self.optimum_section_ur_results[self.result_UR]['Section class']
                self.result_effective_area = self.optimum_section_ur_results[self.result_UR]['Effective area']

                self.result_bc_zz = self.optimum_section_ur_results[self.result_UR]['Buckling_curve_zz']
                self.result_bc_yy = self.optimum_section_ur_results[self.result_UR]['Buckling_curve_yy']

                self.result_IF_zz = self.optimum_section_ur_results[self.result_UR]['IF_zz']
                self.result_IF_yy = self.optimum_section_ur_results[self.result_UR]['IF_yy']

                self.result_eff_len_zz = self.optimum_section_ur_results[self.result_UR]['Effective_length_zz']
                self.result_eff_len_yy = self.optimum_section_ur_results[self.result_UR]['Effective_length_yy']

                self.result_eff_sr_zz = self.optimum_section_ur_results[self.result_UR]['Effective_SR_zz']
                self.result_eff_sr_yy = self.optimum_section_ur_results[self.result_UR]['Effective_SR_yy']

                self.result_ebs_zz = self.optimum_section_ur_results[self.result_UR]['EBS_zz']
                self.result_ebs_yy = self.optimum_section_ur_results[self.result_UR]['EBS_yy']

                self.result_nd_esr_zz = self.optimum_section_ur_results[self.result_UR]['ND_ESR_zz']
                self.result_nd_esr_yy = self.optimum_section_ur_results[self.result_UR]['ND_ESR_yy']

                self.result_phi_zz = self.optimum_section_ur_results[self.result_UR]['phi_zz']
                self.result_phi_yy = self.optimum_section_ur_results[self.result_UR]['phi_yy']

                self.result_srf_zz = self.optimum_section_ur_results[self.result_UR]['SRF_zz']
                self.result_srf_yy = self.optimum_section_ur_results[self.result_UR]['SRF_yy']

                self.result_fcd_1_zz = self.optimum_section_ur_results[self.result_UR]['FCD_1_zz']
                self.result_fcd_1_yy = self.optimum_section_ur_results[self.result_UR]['FCD_1_yy']

                self.result_fcd_2 = self.optimum_section_ur_results[self.result_UR]['FCD_2']

                self.result_fcd_zz = self.optimum_section_ur_results[self.result_UR]['FCD_zz']
                self.result_fcd_yy = self.optimum_section_ur_results[self.result_UR]['FCD_yy']

                self.result_fcd = self.optimum_section_ur_results[self.result_UR]['FCD']
                self.result_capacity = self.optimum_section_ur_results[self.result_UR]['Capacity']
                self.result_cost = self.optimum_section_ur_results[self.result_UR]['Cost']
            else:
                self.result_UR = self.optimum_section_cost_results[self.result_cost]['UR']

                # checking if the selected section based on cost satisfies the UR
                if self.result_UR > min(self.allowable_utilization_ratio, 1.0):

                    trial_cost = []
                    for cost in self.optimum_section_cost:
                        self.result_UR = self.optimum_section_cost_results[cost]['UR']
                        if self.result_UR <= min(self.allowable_utilization_ratio, 1.0):
                            trial_cost.append(cost)

                    trial_cost.sort()

                    if len(trial_cost) == 0:  # no design was successful
                        logger.warning("The sections selected by the solver from the defined list of sections did not satisfy the Utilization Ratio (UR) "
                                       "criteria")
                        logger.error("The solver did not find any adequate section from the defined list.")
                        logger.info("Re-define the list of sections or check the Design Preferences option and re-design.")
                        self.design_status = False
                        self.design_status_list.append(self.design_status)
                        print(f"design_status_list{self.design_status} \n")
                    else:
                        self.result_cost = trial_cost[0]  # optimum section based on cost which passes the UR check
                        self.design_status = True

                # results
                self.result_designation = self.optimum_section_cost_results[self.result_cost]['Designation']
                self.result_section_class = self.optimum_section_cost_results[self.result_cost]['Section class']
                self.result_effective_area = self.optimum_section_cost_results[self.result_cost]['Effective area']

                self.result_bc_zz = self.optimum_section_cost_results[self.result_cost]['Buckling_curve_zz']
                self.result_bc_yy = self.optimum_section_cost_results[self.result_cost]['Buckling_curve_yy']

                self.result_IF_zz = self.optimum_section_cost_results[self.result_cost]['IF_zz']
                self.result_IF_yy = self.optimum_section_cost_results[self.result_cost]['IF_yy']

                self.result_eff_len_zz = self.optimum_section_cost_results[self.result_cost]['Effective_length_zz']
                self.result_eff_len_yy = self.optimum_section_cost_results[self.result_cost]['Effective_length_yy']

                self.result_eff_sr_zz = self.optimum_section_cost_results[self.result_cost]['Effective_SR_zz']
                self.result_eff_sr_yy = self.optimum_section_cost_results[self.result_cost]['Effective_SR_yy']

                self.result_ebs_zz = self.optimum_section_cost_results[self.result_cost]['EBS_zz']
                self.result_ebs_yy = self.optimum_section_cost_results[self.result_cost]['EBS_yy']

                self.result_nd_esr_zz = self.optimum_section_cost_results[self.result_cost]['ND_ESR_zz']
                self.result_nd_esr_yy = self.optimum_section_cost_results[self.result_cost]['ND_ESR_yy']

                self.result_phi_zz = self.optimum_section_cost_results[self.result_cost]['phi_zz']
                self.result_phi_yy = self.optimum_section_cost_results[self.result_cost]['phi_yy']

                self.result_srf_zz = self.optimum_section_cost_results[self.result_cost]['SRF_zz']
                self.result_srf_yy = self.optimum_section_cost_results[self.result_cost]['SRF_yy']

                self.result_fcd_1_zz = self.optimum_section_cost_results[self.result_cost]['FCD_1_zz']
                self.result_fcd_1_yy = self.optimum_section_cost_results[self.result_cost]['FCD_1_yy']

                self.result_fcd_2 = self.optimum_section_cost_results[self.result_cost]['FCD_2']

                self.result_fcd_zz = self.optimum_section_cost_results[self.result_cost]['FCD_zz']
                self.result_fcd_yy = self.optimum_section_cost_results[self.result_cost]['FCD_yy']

                self.result_fcd = self.optimum_section_cost_results[self.result_cost]['FCD']
                self.result_capacity = self.optimum_section_cost_results[self.result_cost]['Capacity']

                print(f"design_status_list2{self.design_status}")

        # end of the design simulation
        # overall design status
        for status in self.design_status_list:
            if status is False:
                self.design_status = False
                break
            else:
                self.design_status = True

        if self.design_status:
            logger.info(": ========== Design Status ============")
            logger.info(": Overall Column design is SAFE")
            logger.info(": ========== End Of Design ============")
        else:
            logger.info(": ========== Design Status ============")
            logger.info(": Overall Column design is UNSAFE")
            logger.info(": ========== End Of Design ============")

    ### start writing save_design from here!
    def save_design(self, popup_summary):

        if self.connectivity == 'Hollow/Tubular Column Base':
            if self.dp_column_designation[1:4] == 'SHS':
                select_section_img = 'SHS'
            elif self.dp_column_designation[1:4] == 'RHS':
                select_section_img = 'RHS'
            else:
                select_section_img = 'CHS'
        else:
            if self.column_properties.flange_slope != 90:
                select_section_img = "Slope_Beam"
            else:
                select_section_img = "Parallel_Beam"

            # column section properties
        if self.connectivity == 'Hollow/Tubular Column Base':
            if self.dp_column_designation[1:4] == 'SHS':
                section_type = 'Square Hollow Section (SHS)'
            elif self.dp_column_designation[1:4] == 'RHS':
                section_type = 'Rectangular Hollow Section (RHS)'
            else:
                section_type = 'Circular Hollow Section (CHS)'
        else:
            section_type = 'I Section'


        if self.section_property=='Columns' or self.section_property=='Beams':
            self.report_column = {KEY_DISP_SEC_PROFILE: "ISection",
                                  KEY_DISP_COLSEC_REPORT: self.section_property.designation,
                                  KEY_DISP_MATERIAL: self.section_property.material,
 #                                 KEY_DISP_APPLIED_AXIAL_FORCE: self.section_property.,
                                  KEY_REPORT_MASS: self.section_property.mass,
                                  KEY_REPORT_AREA: round(self.section_property.area * 1e-2, 2),
                                  KEY_REPORT_DEPTH: self.section_property.depth,
                                  KEY_REPORT_WIDTH: self.section_property.flange_width,
                                  KEY_REPORT_WEB_THK: self.section_property.web_thickness,
                                  KEY_REPORT_FLANGE_THK: self.section_property.flange_thickness,
                                  KEY_DISP_FLANGE_S_REPORT: self.section_property.flange_slope,
                                  KEY_REPORT_R1: self.section_property.root_radius,
                                  KEY_REPORT_R2: self.section_property.toe_radius,
                                  KEY_REPORT_IZ: round(self.section_property.mom_inertia_z * 1e-4, 2),
                                  KEY_REPORT_IY: round(self.section_property.mom_inertia_y * 1e-4, 2),
                                  KEY_REPORT_RZ: round(self.section_property.rad_of_gy_z * 1e-1, 2),
                                  KEY_REPORT_RY: round(self.section_property.rad_of_gy_y * 1e-1, 2),
                                  KEY_REPORT_ZEZ: round(self.section_property.elast_sec_mod_z * 1e-3, 2),
                                  KEY_REPORT_ZEY: round(self.section_property.elast_sec_mod_y * 1e-3, 2),
                                  KEY_REPORT_ZPZ: round(self.section_property.plast_sec_mod_z * 1e-3, 2),
                                  KEY_REPORT_ZPY: round(self.section_property.plast_sec_mod_y * 1e-3, 2)}
        else:
            self.report_column = {KEY_DISP_COLSEC_REPORT: self.section_property.designation,
                                  KEY_DISP_MATERIAL: self.section_property.material,
                                  #                                 KEY_DISP_APPLIED_AXIAL_FORCE: self.section_property.,
                                  KEY_REPORT_MASS: self.section_property.mass,
                                  KEY_REPORT_AREA: round(self.section_property.area * 1e-2, 2),
                                  KEY_REPORT_DEPTH: self.section_property.depth,
                                  KEY_REPORT_WIDTH: self.section_property.flange_width,
                                  KEY_REPORT_WEB_THK: self.section_property.web_thickness,
                                  KEY_REPORT_FLANGE_THK: self.section_property.flange_thickness,
                                  KEY_DISP_FLANGE_S_REPORT: self.section_property.flange_slope}


        self.report_input = \
            {KEY_MAIN_MODULE: self.mainmodule,
             KEY_MODULE: self.module, #"Axial load on column "
             KEY_DISP_SECTION_PROFILE: self.sec_profile,
             KEY_MATERIAL: self.material,
             KEY_DISP_ACTUAL_LEN_ZZ: self.length_zz,
             KEY_DISP_ACTUAL_LEN_YY: self.length_yy,
             KEY_DISP_END1: self.end_1,
             KEY_DISP_END2: self.end_2,
             KEY_DISP_AXIAL: self.load,
             KEY_DISP_SEC_PROFILE: self.sec_profile,
             KEY_DISP_SECSIZE: self.result_section_class,
             KEY_DISP_ULTIMATE_STRENGTH_REPORT: self.euler_bs_yy,
             KEY_DISP_YIELD_STRENGTH_REPORT: self.result_bc_yy,


             "Column Section - Mechanical Properties": "TITLE",
             "Section Details": self.report_column,
             }

        self.report_check = []

        self.h = (self.beam_D - (2 * self.beam_tf))

        #1.1 Input sections display
        t1 = ('SubSection', 'List of Input Sections',self.input_section_list),
        self.report_check.append(t1)

        # 2.2 CHECK: Buckling Class - Compatibility Check
        t1 = ('SubSection', 'Buckling Class - Compatibility Check', '|p{4cm}|p{3.5cm}|p{6.5cm}|p{2cm}|')
        self.report_check.append(t1)

        t1 = ("h/bf , tf ", comp_column_class_section_check_required(self.bucklingclass, self.h, self.bf),
              comp_column_class_section_check_provided(self.bucklingclass, self.h, self.bf, self.tf, self.var_h_bf),
              'Compatible')  # if self.bc_compatibility_status is True else 'Not compatible')
        self.report_check.append(t1)

        # 2.3 CHECK: Cross-section classification
        t1 = ('SubSection', 'Cross-section classification', '|p{4.5cm}|p{3cm}|p{6.5cm}|p{1.5cm}|')
        self.report_check.append(t1)

        t1 = ("b/tf and d/tw ", cross_section_classification_required(self.section),
              cross_section_classification_provided(self.tf, self.b1, self.epsilon, self.section, self.b1_tf,
                                                    self.d1_tw, self.ep1, self.ep2, self.ep3, self.ep4),
              'b = bf / 2,d = h – 2 ( T + R1),έ = (250 / Fy )^0.5,Compatible')  # if self.bc_compatibility_status is True else 'Not compatible')
        self.report_check.append(t1)

        # 2.4 CHECK : Member Check
        t1 = ("Slenderness", cl_7_2_2_slenderness_required(self.KL, self.ry, self.lamba),
              cl_7_2_2_slenderness_provided(self.KL, self.ry, self.lamba), 'PASS')
        self.report_check.append(t1)

        t1 = (
        "Design Compressive stress (fcd)", cl_7_1_2_1_fcd_check_required(self.gamma_mo, self.f_y, self.f_y_gamma_mo),
        cl_7_1_2_1_fcd_check_provided(self.facd), 'PASS')
        self.report_check.append(t1)

        t1 = ("Design Compressive strength (Pd)", cl_7_1_2_design_comp_strength_required(self.axial),
              cl_7_1_2_design_comp_strength_provided(self.Aeff, self.facd, self.A_eff_facd), "PASS")
        self.report_check.append(t1)

        t1 = ('', '', '', '')
        self.report_check.append(t1)
        print(sys.path[0])
        rel_path = str(sys.path[0])
        rel_path = rel_path.replace("\\", "/")
        fname_no_ext = popup_summary['filename']
        CreateLatex.save_latex(CreateLatex(), self.report_input, self.report_check, popup_summary, fname_no_ext,
                              rel_path, module=self.module)



