from CommandlineOsdag.FinPlate import FinPlate
from CommandlineOsdag.EndPlate import EndPlate
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
        self.select_module()
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
        available_module_in_cmd = {'Fin Plate': FinPlate, 'End Plate': EndPlate}
        print(Fore.GREEN+ 'Available Modules are: ')
        i=1
        for key in available_module_in_cmd:
            print(Fore.GREEN+ '',str(i)+'.',key)
            i+=1
        print(Fore.GREEN+ 'Select Module: ')
        module_no = input()
        if module_no=='1':
            module_name = 'Fin Plate'
            FinPlate()
        elif module_no=='2':
            module_name = 'End Plate'
            EndPlate()
        else:
            print(Fore.RED+ 'Invalid Module')
            return self.select_module()

Osdag.__init__(self=Osdag())