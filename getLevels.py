

import pandas as pd
import math
import json
import jsonpickle

class Coordinate:
	def __init__(self,x,y):
		self.x = x
		self.y = y

steelBeamRxnPerFloorType_dict = {}
class RAM_Analytical_Model:
		def __init__(self, layoutTypes = [], levelCount=0, origin_RAM = Coordinate(0,0), stories = [], beams = []):
			self.LayoutTypes = layoutTypes
			self.LevelCount = levelCount
			self.Origin_RAM = origin_RAM
			self.Stories = stories
			self.Beams = beams

ramAnalyticalModel = RAM_Analytical_Model()

class Beam:
	def __init__(self, layoutType, size, start_Coordinate, end_coordinate,  startTotalRxnPositive, endTotalRxnPositive):
		self.LayoutType = layoutType
		self.Size = size
		self.Start_Coordinate = start_Coordinate
		self.End_Coordinate = end_coordinate
		self.StartTotalRxnPositive = startTotalRxnPositive
		self.EndTotalRxnPositive = endTotalRxnPositive
		self.Cantilevered = False




class Story:
	def __init__(self, level, storyLabel, layoutType, height, elevation):
		self.Level = level
		self.StoryLabel = storyLabel
		self.LayoutType = layoutType
		self.Height = height
		self.Elevation = elevation

df = pd.read_excel("data echo.xlsx", header = None)
df.index+=1

def getFirstColumn_df(df):
	return df.iloc[:,0]

firstColumn = getFirstColumn_df(df)


def GetFloorLayoutTypes():
	layoutTypesHeader = None
	tablesSelectedHeader = None
	for x in firstColumn:
	    if x == "Layout Types:":
	        layoutTypesHeader = firstColumn[firstColumn =="Layout Types:"].index[0]
	    if x == "Tables Selected:":
	        tablesSelectedHeader = firstColumn[firstColumn =="Tables Selected:"].index[0]

	ramAnalyticalModel.LayoutTypes = firstColumn[layoutTypesHeader:tablesSelectedHeader-1].tolist()

GetFloorLayoutTypes()

def DetermineNumLevels():
	storyDataHeader = firstColumn[firstColumn =="Story Data:"].index[0]
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
		ramAnalyticalModel.Stories.append(story)

def CreateStoryDataFrane():
	storyDataHeader = firstColumn[firstColumn =="Story Data:"].index[0]
	storyData_df=df.iloc[storyDataHeader+1:storyDataHeader+ramAnalyticalModel.LevelCount+1,0:5]
	storyData_df_sorted = storyData_df.sort_values(0,ascending = True)
	storyData_df_sorted.columns = ['Level', 'NaN', 'Story Label', 'Layout Type', 'Height']
	storyData_df_sorted = storyData_df_sorted.drop('NaN', 1)
	storyData_df_sorted['Elevation']=storyData_df_sorted['Height'].cumsum()
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

ramAnalyticalModel.Origin_RAM.x = yGrid_df_sorted.iloc[0,1]
ramAnalyticalModel.Origin_RAM.y = xGrid_df_sorted.iloc[0,1]

# GET STEEL BEAM REACTION DATA
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


for df in steelBeamRxnPerFloorType_df_list:
	df['Size'] = df['Size'].str.strip()


def checkCountFloorToDFMapping():
	steelBeamRxnPerFloorType_df_count = len(steelBeamRxnPerFloorType_df_list)
	floorTypes_count = len(floorTypes)
	return steelBeamRxnPerFloorType_df_count == floorTypes_count

def createSteelBeamRxnPerFloorTypeMapping():
	if(checkCountFloorToDFMapping()):
		for i in range(0, len(steelBeamRxnPerFloorType_df_list)):
			steelBeamRxnPerFloorType_dict[floorTypes[i]] = steelBeamRxnPerFloorType_df_list[i]
	else:
		raise ValueError('Count mismatch between number of floor types classified and the coresponding number of data frames generated')

createSteelBeamRxnPerFloorTypeMapping()


# Provide Beam Reaction Data
# TODO: Handle case only start is provided.
def ProvideBeamRxnData():
	numBeams = 0
	for key, value in steelBeamRxnPerFloorType_dict.items():
		#print(value)
		numFloorTypesWithBeamRxnData = len(steelBeamRxnPerFloorType_dict.items())
		#print(numFloorTypesWithBeamRxnData)
		dataFrameIndex =0
		i =0
		while (dataFrameIndex < len(value)-1):
			size = value.iloc[dataFrameIndex]['Size']
			nextSize = value.iloc[dataFrameIndex+1]['Size']
			#print("next size is " + str(nextSize))
			if isinstance( nextSize, str ) and isinstance( size, str ):
				beam = Beam(key, value.iloc[dataFrameIndex]['Size'], Coordinate(value.iloc[dataFrameIndex]['X'], value.iloc[dataFrameIndex]['Y']),
					'NA', value.iloc[dataFrameIndex]['+Total'], 'NA')
				beam.Cantilevered = True
				ramAnalyticalModel.Beams.append(beam)
				dataFrameIndex=dataFrameIndex+1
				numBeams+=1
				#print(beam.LayoutType, beam.Size, beam.Start_Coordinate.x, beam.Start_Coordinate.y, beam.End_Coordinate, beam.StartTotalRxnPositive, beam.EndTotalRxnPositive)					
			else:
				if isinstance( size, str ):
					beam = Beam(key,value.iloc[dataFrameIndex]['Size'], Coordinate(value.iloc[dataFrameIndex]['X'], value.iloc[dataFrameIndex]['Y']),
						Coordinate(value.iloc[(dataFrameIndex+1)]['X'], value.iloc[(dataFrameIndex+1)]['Y']), value.iloc[dataFrameIndex]['+Total'], value.iloc[(dataFrameIndex+1)]['+Total'])
					ramAnalyticalModel.Beams.append(beam)
					#print(beam.LayoutType, beam.Size, beam.Start_Coordinate.x, beam.Start_Coordinate.y, beam.End_Coordinate.x, beam.End_Coordinate.y, beam.StartTotalRxnPositive, beam.EndTotalRxnPositive)
					numBeams+=1
				dataFrameIndex=dataFrameIndex+1

	print(len(ramAnalyticalModel.Beams))
	print(numBeams)
	tempInt = 0
	print(ramAnalyticalModel.Beams[tempInt].LayoutType, ramAnalyticalModel.Beams[tempInt].Size,
		ramAnalyticalModel.Beams[tempInt].Start_Coordinate.x, ramAnalyticalModel.Beams[tempInt].Start_Coordinate.y,
		ramAnalyticalModel.Beams[tempInt].End_Coordinate.x, ramAnalyticalModel.Beams[tempInt].End_Coordinate.y,
		ramAnalyticalModel.Beams[tempInt].StartTotalRxnPositive, ramAnalyticalModel.Beams[tempInt].EndTotalRxnPositive)
	#if math.isnan(ramAnalyticalModel.Beams[tempInt].Size):
		#boolean = True
		#print(boolean)
	#print(steelBeamRxnPerFloorType_dict.values())

ProvideBeamRxnData()

#print(steelBeamRxnPerFloorType_df_list[0])

with open('RAM_Analytical_Model.txt', 'w') as outfile:
	ramAnalyticalModelString = jsonpickle.encode(ramAnalyticalModel.Beams[7])
	#ramAnalyticalModelString = steelBeamRxnPerFloorType_df_list[0].to_json(orient='split')
	outfile.write(ramAnalyticalModelString)
    #json.dump(ramAnalyticalModel.LayoutTypes, outfile)