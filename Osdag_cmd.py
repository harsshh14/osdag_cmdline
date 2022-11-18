from CommandlineOsdag.FinPlate import FinPlate
from CommandlineOsdag.EndPlate import EndPlate

from CommandlineOsdag.ColumnCoverPlate import BeamCoverPlateBolted
from CommandlineOsdag.excel_based import Workbook
from design_type.compression_member.compression import Compression
from design_type.connection.column_cover_plate import ColumnCoverPlate
from design_type.connection.column_end_plate import ColumnEndPlate
from design_type.connection.fin_plate_connection import FinPlateConnection
from design_type.connection.cleat_angle_connection import CleatAngleConnection
from design_type.connection.seated_angle_connection import SeatedAngleConnection
from design_type.connection.end_plate_connection import EndPlateConnection
from design_type.connection.base_plate_connection import BasePlateConnection
from design_type.connection.beam_cover_plate import BeamCoverPlate
from design_type.connection.beam_cover_plate_weld import BeamCoverPlateWeld
from design_type.connection.column_cover_plate_weld import ColumnCoverPlateWeld
from design_type.tension_member.tension_bolted import Tension_bolted
from design_type.tension_member.tension_welded import Tension_welded

import prettytable
import colorama
from colorama import Fore

colorama.init(autoreset=True)

class Osdag():
    def __init__(self):
        print(Fore.CYAN+"1. Enter Inputs")
        print(Fore.CYAN+"2. Read from CSV/Excel")
        if(int(input())==1):
            self.select_module()
        else:
            print("Enter Path : ")
            path = input()
            Workbook(path)
    def select_module(self):
        all_modules = {'Base Plate': BasePlateConnection, 'Beam Coverplate  Weld Connection': BeamCoverPlateWeld,
                       'Beam Coverplate Connection': BeamCoverPlate,
                       'Cleat Angle': CleatAngleConnection, 'Column Coverplate Weld Connection': ColumnCoverPlateWeld,
                       'Column Coverplate Connection': ColumnCoverPlate,
                       'Column Endplate Connection': ColumnEndPlate, 'End Plate': EndPlateConnection,
                       'Fin Plate': FinPlateConnection, 'Seated Angle': SeatedAngleConnection,
                       'Tension Members Bolted Design': Tension_bolted, 'Tension Members Welded Design': Tension_welded,
                       'Compression Member': Compression,
                       }

        available_module = {'Beam Coverplate  Weld Connection': BeamCoverPlateWeld,
                            'Beam Coverplate Connection': BeamCoverPlate,
                            'Cleat Angle': CleatAngleConnection,
                            'Column Coverplate Weld Connection': ColumnCoverPlateWeld,
                            'Column Coverplate Connection': ColumnCoverPlate,
                            'Column Endplate Connection': ColumnEndPlate, 'End Plate': EndPlateConnection,
                            'Fin Plate': FinPlateConnection, 'Seated Angle': SeatedAngleConnection,
                            'Tension Members Bolted Design': Tension_bolted,
                            'Tension Members Welded Design': Tension_welded, 'Compression Member': Compression,
                            }
        available_module_in_cmd = {'Fin Plate': FinPlate, 'End Plate': EndPlate,'Beam Cover Plate (Bolted)': BeamCoverPlateBolted}
        print(Fore.GREEN+ 'Available Modules are: ')
        i=1
        for key in available_module_in_cmd:
            print(Fore.GREEN+ '',str(i)+'.',key)
            i+=1
        print(Fore.GREEN+ 'Select Module: ')
        module_no = input()
        if module_no=='1':
            module_name = 'Fin Plate'
            FinPlate(1)
        elif module_no=='2':
            module_name = 'End Plate'
            EndPlate()
        elif module_no=='3':
            BeamCoverPlateBolted(1)
        else:
            print(Fore.RED+ 'Invalid Module')
            return self.select_module()

Osdag.__init__(self=Osdag())