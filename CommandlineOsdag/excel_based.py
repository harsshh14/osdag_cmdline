import pandas as pd
def workbook():
    df = pd.read_excel("inputStructure.xlsx")
    df = pd.DataFrame(df)
    print(df.head())
    print(df["Connectivity"][2])
workbook()