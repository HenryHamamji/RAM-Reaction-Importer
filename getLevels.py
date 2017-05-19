

import pandas as pd
import math

class Coordinate:
	def __init__(self,x,y):
		self.x = x
		self.y = y

class RAM_Analytical_Model:
	steelBeamRxnPerFloorType_dict = {}
	LayoutTypes = []
	LevelCount = 0
	origin_RAM = Coordinate(0,0)
	Stories = []

ramAnalyticalModel = RAM_Analytical_Model()


class Story:
	def __init__(self, level, storyLabel, layoutType, height, elevation):
		self.Level = level
		self.StoryLabel = storyLabel
		self.LayoutType = layoutType
		self.Height = height
		self.Elevation = elevation

#print(s1.Level, s1.StoryLabel, s1.LayoutType, s1.Height, s1.Elevation)
df = pd.read_excel("data echo.xlsx", header = None)
df.index+=1

firstColumn = df.iloc[:,0]


layoutTypesHeader = None
tablesSelectedHeader = None
for x in firstColumn:
    if x == "Layout Types:":
        layoutTypesHeader = firstColumn[firstColumn =="Layout Types:"].index[0]
    if x == "Tables Selected:":
        tablesSelectedHeader = firstColumn[firstColumn =="Tables Selected:"].index[0]

ramAnalyticalModel.LayoutTypes = firstColumn[layoutTypesHeader:tablesSelectedHeader-1]




storyDataHeader = firstColumn[firstColumn =="Story Data:"].index[0]
levelsToHeightDictStart = storyDataHeader

def DetermineNumLevels():
	while True:
		level = df.loc[storyDataHeader+2+ramAnalyticalModel.LevelCount,0]
		if isinstance( level, int ):
			ramAnalyticalModel.LevelCount+=1
		else:
			break

DetermineNumLevels()

def ProvideStoryData(df):
	for i in range(0, len(df)):
		story = Story(df.iloc[i]['Level'], df.iloc[i]['Story Label'], df.iloc[i]['Layout Type'], df.iloc[i]['Height'], df.iloc[i]['Elevation'])
		RAM_Analytical_Model.Stories.append(story)

def CreateStoryDataFrane():
	storyData_df=df.iloc[storyDataHeader+1:storyDataHeader+ramAnalyticalModel.LevelCount+1,0:5]
	storyData_df_sorted = storyData_df.sort_values(0,ascending = True)
	storyData_df_sorted.columns = ['Level', 'NaN', 'Story Label', 'Layout Type', 'Height']
	storyData_df_sorted = storyData_df_sorted.drop('NaN', 1)
	storyData_df_sorted['Elevation']=storyData_df_sorted['Height'].cumsum()
	#print(storyData_df_sorted)
	ProvideStoryData(storyData_df_sorted)

CreateStoryDataFrane()




#print(ramAnalyticalModel.Stories[1].Level, ramAnalyticalModel.Stories[1].StoryLabel, ramAnalyticalModel.Stories[1].LayoutType, ramAnalyticalModel.Stories[1].Height, ramAnalyticalModel.Stories[1].Elevation)
#TODO: create mapping from level/ label / elevation to layout type.


# GET RAM GRID INFO
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
floorTypes = []
for index, val in firstColumnSteelBeamRxns.iteritems():
	if isinstance( val, str ):
		if "Floor Type:" in val:
			floorTypes.append(val)
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

ramAnalyticalModel.origin_RAM.x = yGrid_df_sorted.iloc[0,1]
ramAnalyticalModel.origin_RAM.y = xGrid_df_sorted.iloc[0,1]
#print(ramAnalyticalModel.origin_RAM.x, ramAnalyticalModel.origin_RAM.y)

for df in steelBeamRxnPerFloorType_df_list:
	df['Size'] = df['Size'].str.strip()


def checkCountFloorToDFMapping():
	steelBeamRxnPerFloorType_df_count = len(steelBeamRxnPerFloorType_df_list)
	floorTypes_count = len(floorTypes)
	return steelBeamRxnPerFloorType_df_count == floorTypes_count

def createSteelBeamRxnPerFloorTypeMapping():
	if(checkCountFloorToDFMapping()):
		for i in range(0, len(steelBeamRxnPerFloorType_df_list)):
			ramAnalyticalModel.steelBeamRxnPerFloorType_dict[floorTypes[i]] = steelBeamRxnPerFloorType_df_list[i]
	else:
		raise ValueError('Count mismatch between number of floor types classified and the coresponding number of data frames generated')

createSteelBeamRxnPerFloorTypeMapping()
#print(ramAnalyticalModel.steelBeamRxnPerFloorType_dict)