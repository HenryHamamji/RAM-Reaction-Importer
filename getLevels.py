

import pandas as pd
import math

class Coordinate:
	def __init__(self,x,y):
		self.x = x
		self.y = y


df = pd.read_excel("data echo.xlsx", header = None)
df.index+=1

firstColumn = df.iloc[:,0]


levelsHeader = None
tablesSelectedHeader = None
for x in firstColumn:
    if x == "Layout Types:":
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

#print(storyData_df_sorted)

xGrid_df_Header = firstColumn[firstColumn ==" X Grids"].index[0]

xGridCount =0
while True:
	xGridCoordinate = df.loc[xGrid_df_Header+2+xGridCount,2]
	if not isinstance( xGridCoordinate, str ):
		xGridCount+=1
	else:
		break


xGrid_df = df.iloc[xGrid_df_Header+1:xGrid_df_Header+xGridCount+1,1:3]
xGrid_df_sorted = xGrid_df.sort_values(1,ascending = True)

#print(xGrid_df_sorted)

yGrid_df_Header = firstColumn[firstColumn ==" Y Grids"].index[0]
yGridCount =0
while True:
	yGridCoordinate = df.loc[yGrid_df_Header+2+yGridCount,2]
	if math.isnan(yGridCoordinate):
		break
	else:
		yGridCount+=1

yGrid_df = df.iloc[yGrid_df_Header+1:yGrid_df_Header+yGridCount+1,1:3]


yGrid_df_sorted = yGrid_df.sort_values(1,ascending = True)
#print(yGrid_df_sorted)



steelBeamRxn_df = pd.read_excel("reactions.xlsx", header = None)
steelBeamRxn_df.index+=1

firstColumnSteelBeamRxns = steelBeamRxn_df.iloc[:,0]

floorTypeIndexes = []
for index, val in firstColumnSteelBeamRxns.iteritems():
	if isinstance( val, str ):
		if "Floor Type:" in val:
			floorTypeIndexes.append(index)


steelBeamRxnPerFloorType_df_startIndexes = []
for index in floorTypeIndexes:
	index+=2
	steelBeamRxnPerFloorType_df_startIndexes.append(index)

steelBeamRxnPerFloorType_df_endIndexes = steelBeamRxnPerFloorType_df_startIndexes[1:]
steelBeamRxnPerFloorType_df_endIndexes[:] = [x-3 for x in steelBeamRxnPerFloorType_df_endIndexes]

rowCount = steelBeamRxn_df.shape[0]
steelBeamRxnPerFloorType_df_endIndexes.append(rowCount+1)

steelBeamRxnPerFloorType_df_list = []
for i in range(len(steelBeamRxnPerFloorType_df_startIndexes)):
	steelBeamRxnPerFloorType_df=steelBeamRxn_df.iloc[steelBeamRxnPerFloorType_df_startIndexes[i]:steelBeamRxnPerFloorType_df_endIndexes[i],2:10]
	steelBeamRxnPerFloorType_df.columns = ['Size', 'X', 'Y', 'DL', '+LL', "-LL", '+Total', '-Total']
	steelBeamRxnPerFloorType_df_list.append(steelBeamRxnPerFloorType_df)

origin_RAM = Coordinate(yGrid_df_sorted.iloc[0,1],xGrid_df_sorted.iloc[0,1])
#print(origin_RAM.x, origin_RAM.y)

for df in steelBeamRxnPerFloorType_df_list:
	df['Size'] = df['Size'].str.strip()

#print(steelBeamRxnPerFloorType_df_list[2])