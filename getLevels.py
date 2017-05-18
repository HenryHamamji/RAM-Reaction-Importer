

import pandas as pd
df = pd.read_excel("data echo.xlsx", header = None)
df.index+=1

firstColumn = df.iloc[:,0]


levelsHeader = None
tablesSelectedHeader = None
for x in firstColumn:
    if x == "Layout Types:":
        #print(list(firstColumn).index("Layout Types:"))
        levelsHeader = firstColumn[firstColumn =="Layout Types:"].index[0]
    if x == "Tables Selected:":
        tablesSelectedHeader = firstColumn[firstColumn =="Tables Selected:"].index[0]



levels = firstColumn[levelsHeader+1:tablesSelectedHeader]

storyDataHeader = firstColumn[firstColumn =="Story Data:"].index[0]


levelsToHeightDictStart = storyDataHeader

levelCount =0
while True:
	level = df.loc[storyDataHeader+2+levelCount,0]
	if isinstance( level, int ):
		levelCount+=1
	else:
		break

storyData_df=df.iloc[storyDataHeader+1:storyDataHeader+levelCount+1,0:5]

storyData_df_sorted = storyData_df.sort_values(0,ascending = True)

storyData_df_sorted[5]=storyData_df_sorted[4].cumsum()

print(storyData_df_sorted)

xGrid_df_Header = firstColumn[firstColumn ==" X Grids"].index[0]
#print(xGrid_df_Header)

xGridCount =0
while True:
	gridCoordinate = df.loc[xGrid_df_Header+2+xGridCount,2]
	if not isinstance( gridCoordinate, str ):
		xGridCount+=1
	else:
		break


xGrid_df = df.iloc[xGrid_df_Header+1:xGrid_df_Header+xGridCount+1,1:3]
print(xGrid_df)