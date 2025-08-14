import pandas as pd

read_file = pd.read_excel("cn-kor/evaluated_51-100.xlsx")
read_file.to_csv("cn-kor/evaluated_51-100.csv", index=None, header=True)
# df = pd.DataFrame(pd.read_csv("evaluated.csv"))

# print(df)