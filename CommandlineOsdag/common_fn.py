import pandas as pd

def getModule(series):
    return series['Module'][0]
def read_series(series):
    diction = {}
    if getModule(series)=='FinPlate':
        diction['Module']='Fin Plate Connection'
#  create design dictionary
def getConnectivty(series: pd.Series):
    return series['Connectivity'][0]

def getEndPlateType(series: pd.Series):
    return series['EndPlateType'][0]

def getConnectionLocation(series: pd.Series):
    return series['Connection Location'][0]

def getMaterial(series: pd.Series):
    return series['Material'][0]

def getDesignation(series):
    return series['Member']['Designation'][0]

def getSupportingSectionDesignation(series):
    return series['Member']['Column Section / Primary Beam']['Designation']

def getSupportingSectionMaterial(series):
    return series['Member']['Column Section / Primary Beam']['Material'][0]

def getSupportedSectionDesignation(series):
    return series['Member']['Beam Section / Secondary Beam']['Designation']

def getSupportedSectionMaterial(series):
    return series['Member']['Beam Section / Secondary Beam']['Material'][0]

def getLength(series):
    return series['Member']['Length'][0]

def getProfile(series):
    return series['Member']['Profile'][0]

def getLength_zz(series):
    return series['Member']['Length_zz'][0]

def getLength_yy(series):
    return series['Member']['Length_yy'][0]

def getShear(series):
    return str(series['Load']['Shear (kN)'][0])

def getAxial(series):
    return str(series['Load']['Axial (kN)'][0])

def getMoment(series):
    return str(series['Load']['Moment (kN-m)'][0])

def getBoltDiameter(series):

    return str(series['Bolt']['Available Diameters (mm)'][0]).split(',')

def getBoltType(series):
    return series['Bolt']['Type'][0]

def getGrade(series):
    print(series['Bolt']['Grade'][0])
    return str(series['Bolt']['Grade'][0]).split(',')

def getBolt_Hole_Type(series):
    return series['Bolt']['Bolt_Hole_Type'][0]

def getSlip_Factor(series):
    return series['Bolt']['Slip_Factor'][0]

def isPreTensed(series):
    return series['Bolt']['Is pre-tensioned'][0]

def getConnectorMaterial(series):
    return series['Connector']['Material'][0]

def getConnectorPlate(series):
    return str(series['Connector']['Plate'][0]).split(',')

def getConnectorFlangePrefernce(series):
    print(series['Connector']['Flange_Splice']['Preferences'])
    return series['Connector']['Flange_Splice']['Preferences']
def getConnectorFlangeThickness(series):
    return str(series['Connector']['Flange_Splice']['Thickness_List']).split(',')
def getConnectorWeb(series):
    return str(series['Connector']['Web_Splice'][0]).split(',')

def getConnectorTopAngle(series):
    return series['Connector']['Top_Angle'][0]

def getWeldType(series):
    return series['Weld']['Type'][0]

def getWeldFab(series):
    return series['Weld']['Fab'][0]

def getWeldMaterial_gradeOverwrite(series):
    return series['Weld']['Material_Grade_Overwrite'][0]

def getDetailingCorrosive_Influences(series):
    return series['Detailing']['Corrosive_Influences'][0]

def getDetailingEdge_Type(series):
    return series['Detailing']['Edge_Type'][0]

def getDetailingGap(series):
    return series['Detailing']['Gap'][0]

def getDesignMethod(series):
    return series['Design']['Design_Method'][0]

def supportConditionsEnd1ZZ(series):
    return series['Support conditions']['End 1-ZZ'][0]

def supportConditionsEnd2ZZ(series):
    return series['Support conditions']['End 2-ZZ'][0]

def supportConditionsEnd1YY(series):
    return series['Support conditions']['End 1-YY'][0]

def supportConditionsEndYY(series):
    return series['Support conditions']['End 2-YY'][0]
