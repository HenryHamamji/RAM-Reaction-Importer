

import pandas as pd
import math
import json

class Coordinate:
	def __init__(self,x,y):
		self.x = x
		self.y = y

steelBeamRxnPerFloorType_dict = {}
class RAM_Analytical_Model:
		def __init__(self, layoutTypes = [], levelCount=0, origin_RAM = Coordinate(0,0), stories = [], beams = [], xGrids = [], yGrids = []):
			self.LayoutTypes = layoutTypes
			self.LevelCount = levelCount
			self.Origin_RAM = origin_RAM
			self.Stories = stories
			self.Beams = beams
			self.XGrids = xGrids
			self.YGrids = yGrids

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


class Grid:
	def __init__(self, name, location):
		self.Name = name
		self.Location = location


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
	print(storyData_df_sorted)

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
#print(yGrid_df_sorted)
ramAnalyticalModel.Origin_RAM.x = yGrid_df_sorted.iloc[0,1]
ramAnalyticalModel.Origin_RAM.y = xGrid_df_sorted.iloc[0,1]


def ProvideGridData(xGrid_df, yGrid_df):
	for i in range(0, xGrid_df.shape[0]):
		grid = Grid(xGrid_df.iloc[i,0], xGrid_df.iloc[i,1])
		ramAnalyticalModel.XGrids.append(grid)
	for j in range(0, yGrid_df.shape[0]):
		grid = Grid(yGrid_df.iloc[j,0], yGrid_df.iloc[j,1])
		ramAnalyticalModel.YGrids.append(grid)

	myfile = open('xGridData.txt', 'w')
	for i in range(0, len(ramAnalyticalModel.XGrids)):
		myfile.write(str(ramAnalyticalModel.XGrids[i].Name) + "," + str(ramAnalyticalModel.XGrids[i].Location))
		if(i!= len(ramAnalyticalModel.XGrids)-1):
			myfile.write(";")
	myfile.close()
	myfile2 = open('yGridData.txt', 'w')
	for j in range(0, len(ramAnalyticalModel.YGrids)):
		myfile2.write(str(ramAnalyticalModel.YGrids[j].Name) + "," + str(ramAnalyticalModel.YGrids[j].Location))
		if(j!= len(ramAnalyticalModel.YGrids)-1):
			myfile2.write(";")
	myfile2.close()
	#print("Grid Name: " + str(ramAnalyticalModel.YGrids[0].Name), "Grid Location: " + str(ramAnalyticalModel.YGrids[0].Location))

ProvideGridData(xGrid_df_sorted, yGrid_df_sorted)

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
def ProvideBeamRxnData():
	numBeams = 0
	numCantiLeveredBeams = 0
	for key, value in steelBeamRxnPerFloorType_dict.items():
		numFloorTypesWithBeamRxnData = len(steelBeamRxnPerFloorType_dict.items())
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
				numCantiLeveredBeams+=1
				#print(beam.LayoutType, beam.Size, beam.Start_Coordinate.x, beam.Start_Coordinate.y, beam.End_Coordinate, beam.StartTotalRxnPositive, beam.EndTotalRxnPositive)					
			else:
				if isinstance( size, str ):
					beam = Beam(key,value.iloc[dataFrameIndex]['Size'], Coordinate(value.iloc[dataFrameIndex]['X'], value.iloc[dataFrameIndex]['Y']),
						Coordinate(value.iloc[(dataFrameIndex+1)]['X'], value.iloc[(dataFrameIndex+1)]['Y']), value.iloc[dataFrameIndex]['+Total'], value.iloc[(dataFrameIndex+1)]['+Total'])
					ramAnalyticalModel.Beams.append(beam)
					#print(beam.LayoutType, beam.Size, beam.Start_Coordinate.x, beam.Start_Coordinate.y, beam.End_Coordinate.x, beam.End_Coordinate.y, beam.StartTotalRxnPositive, beam.EndTotalRxnPositive)
					numBeams+=1
				dataFrameIndex=dataFrameIndex+1

	print("numBeams: " + str(numBeams))
	print("numCantileveredBeams: " + str(numCantiLeveredBeams))

	tempInt = 0
	#print(ramAnalyticalModel.Beams[tempInt].LayoutType, ramAnalyticalModel.Beams[tempInt].Size,
		#ramAnalyticalModel.Beams[tempInt].Start_Coordinate.x, ramAnalyticalModel.Beams[tempInt].Start_Coordinate.y,
		#ramAnalyticalModel.Beams[tempInt].End_Coordinate.x, ramAnalyticalModel.Beams[tempInt].End_Coordinate.y,
		#ramAnalyticalModel.Beams[tempInt].StartTotalRxnPositive, ramAnalyticalModel.Beams[tempInt].EndTotalRxnPositive)

	myfile = open('beamData.txt', 'w')
	beamCount = 0
	cantiLeveredBeamCount = 0;
	for beam in ramAnalyticalModel.Beams:
		if(beam.Cantilevered == False):
			beamInfo = beam.LayoutType + ',' + beam.Size + ',' + str(beam.Start_Coordinate.x) + ',' + str(beam.Start_Coordinate.y) + ',' + str(beam.End_Coordinate.x) + ',' + str(beam.End_Coordinate.y)+ ',' + str(beam.StartTotalRxnPositive) + ',' + str(beam.EndTotalRxnPositive) + ';'
			myfile.write(beamInfo)
			beamCount+=1
		else:
			beamInfo = beam.LayoutType + ',' + beam.Size + ',' + str(beam.Start_Coordinate.x) + ',' + str(beam.Start_Coordinate.y) + ',' + beam.End_Coordinate + ',' + beam.End_Coordinate + ',' + str(beam.StartTotalRxnPositive) + ',' + str(beam.EndTotalRxnPositive) + ';'
			myfile.write(beamInfo)
			beamCount+=1
			cantiLeveredBeamCount+=1
	myfile.close()
	print("beamCount: " + str(beamCount))
	print("cantiLeveredBeamCount: " + str(cantiLeveredBeamCount))


def WriteRAMModelDataToTXTFile():
		myfile = open('RAMModelData.txt', 'w')
		myfile.write("LevelCount:" + str(ramAnalyticalModel.LevelCount) + ";")
		myfile.write("RAMOriginX:" + str(ramAnalyticalModel.Origin_RAM.x)+";")
		myfile.write("RAMOriginY:" + str(ramAnalyticalModel.Origin_RAM.y))
		myfile.close()
		myfile2 = open('RAMStoryData.txt', 'w')
		for i in range(0, len(ramAnalyticalModel.Stories)):
			myfile2.write(str(ramAnalyticalModel.Stories[i].Level)+"," + str(ramAnalyticalModel.Stories[i].StoryLabel) + "," + str(ramAnalyticalModel.Stories[i].LayoutType) + "," + str(ramAnalyticalModel.Stories[i].Height) + "," + str(ramAnalyticalModel.Stories[i].Elevation))
			if(i != len(ramAnalyticalModel.Stories)-1):
				myfile2.write(";")
		myfile2.close()


WriteRAMModelDataToTXTFile()
ProvideBeamRxnData()