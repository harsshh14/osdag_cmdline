# output = [(None, 'Bolt', 'Title', None, True), ('Bolt.Diameter', 'Diameter (mm)', 'TextBox', 30, True), ('Bolt.Grade_Provided', 'Property Class', 'TextBox', 8.8, True), ('Bolt.Shear', 'Shear
#  Capacity (kN)', 'TextBox', 78.23, True), ('Bolt.Bearing', 'Bearing Capacity (kN)', 'TextBox', '', True), ('Bolt.Capacity', 'Capacity (kN)', 'TextBox', 78.23, True), ('Bolt.Force (k
# N)', 'Bolt Force (kN)', 'TextBox', 76.87, True), ('Bolt.Line', 'Bolt Columns (nos)', 'TextBox', 2, True), ('Bolt.OneLine', 'Bolt Rows (nos)', 'TextBox', 3, True), ('spacing', 'Spaci
# ng', 'Output_dock_Button', ['Spacing Details', <bound method FinPlateConnection.spacing of <CommandlineOsdag.FinPlate.FinPlate object at 0x0000017B90B2A748>>], True), (None, 'Plate'
# , 'Title', None, True), ('Plate.Thickness', 'Thickness (mm)', 'TextBox', 10, True), ('Plate.Height', 'Height (mm)', 'TextBox', 270.0, True), ('Plate.Length', 'Length (mm)', 'TextBox
# ', 205.0, True), ('button1', 'Capacity', 'Output_dock_Button', ['Capacity Details', <bound method FinPlateConnection.capacities of <CommandlineOsdag.FinPlate.FinPlate object at 0x00
# 00017B90B2A748>>], True), (None, 'Section Details', 'Title', None, True), ('button2', 'Capacity', 'Output_dock_Button', ['Capacity Details', <bound method FinPlateConnection.capacit
# ies of <CommandlineOsdag.FinPlate.FinPlate object at 0x0000017B90B2A748>>], True), (None, 'Weld', 'Title', None, True), ('Weld.Size', 'Size (mm)', 'TextBox', 8, True), ('Weld.Streng
# th', 'Strength (N/mm2)', 'TextBox', 1060.48, True), ('Weld.Stress', 'Stress (N/mm)', 'TextBox', 1059.22, True)]

import pandas as pd
import os
#convert output to excel file
def create_excel_file(output, filename):
    columns_schema = ['Name', 'Title', 'Type', 'Value', 'Enabled']
    columns = []
    for tup in output:
        if tup[0] is None:
            #make it level 0
            columns.append(tup[1])
        else:
            columns.append(tup[0])
    df = pd.DataFrame(output)
    df.to_excel(filename, index=False)
    print("Excel file created successfully")
    return filename

