# **************************************************************************** #
# Skyler Malinowski [ som12 ]
# Andrew Dos Reis [ ad1005 ]
# Project 3
# CS 440
# **************************************************************************** #

import sys
import math
import time
import heapq
import operator

import numpy as np
import IO
import glob, os
from random import shuffle
import xlsxwriter

# class  ***********************************************************************
class cell:

	def __init__( self, row, col, parent=None ):
		self.parent = parent
		self.where = (row,col)
		self.f = 0.
		self.g = 0.
		self.h = 0.

	def __str__(self):
		return str(self.where)


class aStar:

	def __init__( self, world, weight=1, heuristic=0):
		self.heuristic = heuristic
		self.g = 0
		self.nodes_expanded = 0
		self.nodes_considered = 0
		self.world = world
		self.goal = None
		self.length = [len(world),len(world[0])]
		self.pathData = np.zeros(shape=(self.length[0],self.length[1],5))
		self.openList = []
		self.closedList = []
		self.found = False
		self.w = weight
		self.pathList = []
		while( len(self.openList) == 0 and self.goal == None ):
			for row in range(self.length[0]):
				for col in range(self.length[1]):
					if( world[row][col] == 's' ):
						self.openList.append(cell(row,col))
					elif(  world[row][col] == 'g' ):
						self.goal = (row,col)
		# calculate h
		self.openList[0].h = 0.25 * math.sqrt(math.pow(self.openList[0].where[0]-self.goal[0],2)
								 + math.pow(self.openList[0].where[1]-self.goal[1],2))
		# calculate f
		self.openList[0].f = self.openList[0].h

	def search( self ):

		def heapsort( cellList ):
			heap = []
			for cell in cellList:
				heap.append((cell.f,cell))
			heap.sort(key=operator.itemgetter(0))
			for i in range(len(heap)):
				heap[i] = heap[i][1]
			return heap

		def g( p, c ):
			# diagonal movement or not
			m = 2
			if( c.where[0]-p.where[0] == 0 and c.where[1]-p.where[1] != 0 or
			c.where[0]-p.where[0] != 0 and c.where[1]-p.where[1] == 0):
				m = 1
			else:
				m = math.sqrt(2)

			# movement cost given terrain
			if( self.world[p.where[0]][p.where[1]] == '2' ):
				if( self.world[c.where[0]][c.where[1]] in ['2','b'] ):
					c.g = p.g + ( m*2 )
				else:
					c.g = p.g + ( m*1.5 )

			elif( self.world[p.where[0]][p.where[1]] == 'a' ):
				if( self.world[c.where[0]][c.where[1]] == 'a' ):
					c.g = p.g + ( m*0.25 )
				elif( self.world[c.where[0]][c.where[1]] == 'b' ):
					c.g = p.g + ( m*0.375 )
				elif( self.world[c.where[0]][c.where[1]] == '2' ):
					c.g = p.g + ( m*1.5 )
				else:
					c.g = p.g + ( m*1 )

			elif( self.world[p.where[0]][p.where[1]] == 'b' ):
				if( self.world[c.where[0]][c.where[1]] == 'a' ):
					c.g = p.g + ( m*0.375 )
				elif( self.world[c.where[0]][c.where[1]] == 'b' ):
					c.g = p.g + ( m*0.5 )
				elif( self.world[c.where[0]][c.where[1]] == '2' ):
					c.g = p.g + ( m*1.5 )
				else:
					c.g = p.g + ( m*1 )

			else:
				if( self.world[c.where[0]][c.where[1]] in ['2','b'] ):
					c.g = p.g + ( m*1.5 )
				else:
					c.g = p.g + ( m*1 )

		def h( c, i=0 ):
			if( i == 1 ):  # Raw Manhattan Distance -- Inadmissable
				c.h = math.fabs(c.where[0]-self.goal[0]) + math.fabs(c.where[1]-self.goal[1])
			elif( i == 2 ):  # Raw Chebyshev Distance -- Inadmissable
				c.h = max(math.fabs(c.where[0]-self.goal[0]), math.fabs(c.where[1]-self.goal[1]))
			elif( i == 3 ):  # Custom Manhattan Distance -- Inadmissable
				c.h = 0.25 * math.fabs(c.where[0]-self.goal[0]) + math.fabs(c.where[1]-self.goal[1])
			elif( i == 4 ):  # Custom Chebyshev Distance -- Admissable
				c.h = 0.25 * max(math.fabs(c.where[0]-self.goal[0]), math.fabs(c.where[1]-self.goal[1]))
			else:  # Custom Euclidean Distance -- Admissable
				c.h = 0.25 * math.sqrt(math.pow(c.where[0]-self.goal[0],2)+math.pow(c.where[1]-self.goal[1],2))

		def tracePath( c ):
			if(self.w == 1):
				print("Shortest Movement Path Cost =",c.g)
				self.g = c.g
			if(self.w > 1):
				print("Shortest Movement Path Cost with weight {} =".format(self.w),c.g)
				self.g = c.g
			if(self.w == 0):
				print("Shortest Movement Path Cost for Uniform Cost Search =",c.g)
				self.g = c.g
			curr = c
			#print("Shortest Path Trace")
			while( curr.parent != None ):
				#print(curr.where,curr.f,curr.g,curr.h)
				self.pathData[curr.where[0]][curr.where[1]] = [curr.where[0],curr.where[1],curr.f,curr.g,curr.h]
				self.pathList.append(curr.where)
				curr = curr.parent
			#print(curr.where,curr.f,curr.g,curr.h)
			self.pathData[curr.where[0]][curr.where[1]] = [curr.where[0],curr.where[1],curr.f,curr.g,curr.h]
			self.pathList.append(curr.where)



		def successors( parent ):
			s = []

			# Top Left
			if(parent.where[0]+1 >= 0 and parent.where[0]+1 < self.length[0]
			and parent.where[1]-1 >= 0 and parent.where[1]-1 < self.length[1]
			and self.world[parent.where[0]+1][parent.where[1]-1] != '0'):
				s.append(cell(parent.where[0]+1,parent.where[1]-1,parent))
			# Top Center
			if(parent.where[0]+1 >= 0 and parent.where[0]+1 < self.length[0]
			and self.world[parent.where[0]+1][parent.where[1]] != '0'):
				s.append(cell(parent.where[0]+1,parent.where[1],parent))
			# Top Right
			if(parent.where[0]+1 >= 0 and parent.where[0]+1 < self.length[0]
			and parent.where[1]+1 >= 0 and parent.where[1]+1 < self.length[1]
			and self.world[parent.where[0]+1][parent.where[1]+1] != '0'):
				s.append(cell(parent.where[0]+1,parent.where[1]+1,parent))

			# Center Left
			if(parent.where[1]-1 >= 0 and parent.where[1]-1 < self.length[1]
			and self.world[parent.where[0]][parent.where[1]-1] != '0'):
				s.append(cell(parent.where[0],parent.where[1]-1,parent))
			# Center Right
			if(parent.where[1]+1 >= 0 and parent.where[1]+1 < self.length[1]
			and self.world[parent.where[0]][parent.where[1]+1] != '0'):
				s.append(cell(parent.where[0],parent.where[1]+1,parent))

			# Bottom Left
			if(parent.where[0]-1 >= 0 and parent.where[0]-1 < self.length[0]-1
			and parent.where[1]-1 >= 0 and parent.where[1]-1 < self.length[1]
			and self.world[parent.where[0]-1][parent.where[1]-1] != '0'):
				s.append(cell(parent.where[0]-1,parent.where[1]-1,parent))
			# Bottom Center
			if(parent.where[0]-1 >= 0 and parent.where[0]-1 < self.length[0]
			and self.world[parent.where[0]-1][parent.where[1]] != '0'):
				s.append(cell(parent.where[0]-1,parent.where[1],parent))
			# Bottom Right
			if(parent.where[0]-1 >= 0 and parent.where[0]-1 < self.length[0]
			and parent.where[1]+1 >= 0 and parent.where[1]+1 < self.length[1]
			and self.world[parent.where[0]-1][parent.where[1]+1] != '0'):
				s.append(cell(q.where[0]-1,parent.where[1]+1,parent))

			for child in s:
				# calculate g
				g(parent,child)
				# calculate h
				h(child,self.heuristic)
				# calculate f
				child.f = child.g + self.w*child.h

				# Goal Found
				if(self.world[child.where[0]][child.where[1]] == 'g'):
					print("Path Found")
					tracePath(child)
					self.found = True
					print("Nodes Expanded =",self.nodes_expanded)
					print("Nodes Considered =",self.nodes_considered)
					return

				# populate openList with new valid cells
				good = True
				for listCell in self.openList:
					if( child.where == listCell.where and child.f >= listCell.f ):
						good = False
				for listCell in self.closedList:
					if( child.where == listCell.where and child.f >= listCell.f ):
						good = False
				if( good == True ):
					self.openList.append(child)
					self.nodes_considered += 1

		# main()
		while( len(self.openList) != 0 ):
			# find smallest 'f' in openList
			self.openList = heapsort(self.openList)
			# pop the smallest 'f'
			q = self.openList.pop(0)
			self.pathData[q.where[0]][q.where[1]] = [q.where[0],q.where[1],q.f,q.g,q.h]
			# generate successors
			if( self.found == False ):
				successors(q)
			self.closedList.append(q)
			self.nodes_expanded += 1

		if( self.found == False ):
			print("Path Not Found")
		return self.pathData, self.pathList, self.nodes_expanded, self.nodes_considered, self.g, self.w


# main()  **********************************************************************
def main():

	workbook = xlsxwriter.Workbook('Output.xlsx')
	worksheet = workbook.add_worksheet()

	# world = [
	# 	['s','1','1','1','1','1'],
	# 	['0','1','0','0','0','1'],
	# 	['0','1','0','0','0','1'],
	# 	['1','1','0','1','1','1'],
	# 	['1','0','0','1','0','1'],
	# 	['1','1','1','1','0','1'],
	# 	['0','0','0','0','0','g']
	# ]


	tic = []
	toc = []
	results = []
	fileName = sys.argv[1]
	os.chdir("maps")
	row = 0
	count = 0
	filelist = glob.glob("*.txt")
	shuffle(filelist)
	for fileName in filelist:

		i = 0
		tic = []
		toc = []
		line = []
		line.append(fileName)
		print(fileName)

		world,length,kCells,Centers = IO.readFile(fileName)

		tic.append( time.clock() )
		pathData, pathList, opened, considered, pathcost, weight = aStar(world,0).search()  # Uniform Cost Search
		line.append(pathcost)
		line.append(opened)
		line.append(considered)
		#IO.display(fileName,world,pathData,pathList)
		toc.append( time.clock() )
		print( "Elapsed Time =", toc[i] - tic[i] )
		line.append(toc[i] - tic[i])

		heuristics = {0:"Custom Euclidean Distance -- Admissable",1:"Raw Manhattan Distance -- Inadmissable",2:"Raw Chebyshev Distance -- Inadmissable",3:"Custom Manhattan Distance -- Inadmissable",4:"Custom Chebyshev Distance -- Admissable"}
		for h in heuristics.keys():
			line.append(heuristics[h])
			print(heuristics[h])
			i += 1
			tic.append( time.clock() )
			pathData, pathList, opened, considered, pathcost, weight = aStar(world,1,h).search()  # aStar
			line.append(pathcost)
			line.append(opened)
			line.append(considered)
			#IO.display(fileName,world,pathData,pathList)
			toc.append( time.clock() )
			print( "Elapsed Time =", toc[i] - tic[i] )
			line.append(toc[i] - tic[i])

			for w in [1.5,2.0]:
				i += 1
				tic.append( time.clock() )
				pathData, pathList, opened, considered, pathcost, weight = aStar(world,w,h).search()  # aStar
				line.append(weight)
				line.append(pathcost)
				line.append(opened)
				line.append(considered)
				#IO.display(fileName,world,pathData,pathList)
				toc.append( time.clock() )
				print( "Elapsed Time =", toc[i] - tic[i] )
				line.append(toc[i] - tic[i])

		for col in range(len(line)):
			worksheet.write(row, col, line[col])
		row+= 1
		print(row)
	# Start from the first cell. Rows and columns are zero indexed.
	# Iterate over the data and write it out row by row.

	# Write a total using a formula.

	workbook.close()

# Self Run  ********************************************************************
if( __name__ == "__main__" ):
	main()
