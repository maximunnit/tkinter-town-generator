import random as rand
from numpy import linspace

from road import *

class Building():

    def __init__(self,x0,y0,x1,y1,width):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.length = self.length = ((x1-x0)**2 + (y1-y0)**2)**0.5
        self.width = width

        self.name = "1 Nothing St"
        self.color = "gray1"
        self.tag = ""
    
    def Draw(self, canvas): #buildings will just be rectangular boxes, so we can draw that with a line
        canvas.create_line(self.x0,self.y0,self.x1,self.y1, width=self.width, fill=self.color, activefill="lawn green", tag=self.tag)

class House(Building):

    def __init__(self,x0,y0,x1,y1,width):
        super().__init__(x0,y0,x1,y1,width)
        self.color = "tomato4"

class Store(Building):

    def __init__(self,x0,y0,x1,y1,width):
        super().__init__(x0,y0,x1,y1,width)
        self.color = "RoyalBlue1"

class Restaurant(Building):

    def __init__(self,x0,y0,x1,y1,width):
        super().__init__(x0,y0,x1,y1,width)
        self.color = "goldenrod"

class ServiceBuilding(Building):

    def __init__(self,x0,y0,x1,y1,width):
        super().__init__(x0,y0,x1,y1,width)
        self.color = "gray80"


def IsValidBuildingSpot(x0,y0,x1,y1,width,length,canvas):  #checks whether this potential building spot would overlap with anything already on the canvas
    #we want to avoid putting any buildings in a spot what would overlap a road or another building
    #instead of writing some super convoluted math to solve for valid spots from the roads' equations and width, the building's size, etc
    #we can just check to see whether the canvas already has something drawn there
    #tkinter's find_overlapping function only works for rectangular regions (including single 1x1 points), which makes this a little tricky, but it's cleaner than any other way I can think of

    N = 5  #checks an NxN grid of points across the region the building would be for any overlaps, higher is more likely to catch overlaps but 5 is plenty

    ox = x0 + width/(2*length) * (y0-y1)    #origin for the grid, located at the bottom left corner of the building
    oy = y0 + width/(2*length) * (x1-x0)
    ux = -width/((N-1)*length) * (y0-y1)    #horizontal unit vector for the grid
    uy = -width/((N-1)*length) * (x1-x0)
    vx = 1/(N-1) * (x1-x0)                  #vertical unit vector for the grid
    vy = 1/(N-1) * (y1-y0)

    for i in range(N):
        for j in range(N):
            check = canvas.find_overlapping(ox+ux*i+vx*j, oy+uy*i+vy*j, ox+ux*i+vx*j, oy+uy*i+vy*j)
            #canvas.create_oval(ox+ux*i+vx*j-1, oy+uy*i+vy*j-1, ox+ux*i+vx*j+1, oy+uy*i+vy*j+1, fill="blue") #for debug
            if len(check)>0:
                return False    #if any point overlaps anything, this isn't a valid spot to put the building
    return True

def PickRandomBuildingType():
    choice = rand.uniform(0,1)
    if choice < 0.8:        #80% chance
        return House
    if choice < 0.9:        #10% chance
        return Store
    if choice < 0.95:       #5% chance
        return Restaurant
    else:                   #5% chance
        return ServiceBuilding

def LineRoadWithBuildings(road, canvas):
    
    leftx = (road.width+5)/(2*road.length) * (road.y0 - road.y1)    #vector to the left side of the road from the middle, (width+5) instead of just (width) so that it's a little beyond the edge of the road
    lefty = (road.width+5)/(2*road.length) * (road.x1 - road.x0)

    rightx = -leftx     #vector to the right side of the road from the middle
    righty = -lefty

    numberofleftbuildings = 0
    for t in linspace(0,1,51): #travel along the left side of the road with steps of 0.02 in the t coordinate
        randomwidth = rand.randint(15,25)
        randomlength = rand.randint(15,25)
        x0,y0 = CalculatePosFromT(road, t)                  #x0,y0,x1,y1 are the endpoints of the line depicting the building
        x0 += leftx                                         #start point is on the side of the road
        y0 += lefty
        x1 = x0 + 2*randomlength/(road.width+5) * leftx     #end point is further away outwards from the road
        y1 = y0 + 2*randomlength/(road.width+5) * lefty

        if IsValidBuildingSpot(x0,y0,x1,y1,randomwidth,randomlength,canvas):
            BuildingType = PickRandomBuildingType()
            newbuilding = BuildingType(x0,y0,x1,y1,randomwidth)
            newbuilding.name = f"{numberofleftbuildings*2 + 1} {road.name}" #odd numbered on left side, starting from 1
            newbuilding.tag = f"{road.tag} b{numberofleftbuildings}"
            newbuilding.Draw(canvas)
            road.buildings.append(newbuilding)
            numberofleftbuildings += 1

    numberofrightbuildings = 0
    for t in linspace(0,1,51): #then travel along the right side
        randomwidth = rand.randint(15,25)
        randomlength = rand.randint(15,25)
        x0,y0 = CalculatePosFromT(road, t)
        x0 += rightx
        y0 += righty
        x1 = x0 + 2*randomlength/(road.width+5) * rightx
        y1 = y0 + 2*randomlength/(road.width+5) * righty

        if IsValidBuildingSpot(x0,y0,x1,y1,randomwidth,randomlength,canvas):
            BuildingType = PickRandomBuildingType()
            newbuilding = BuildingType(x0,y0,x1,y1,randomwidth)
            newbuilding.name = f"{numberofrightbuildings*2 + 2} {road.name}" #even numbered on right side, starting from 2
            newbuilding.tag = f"{road.tag} b{numberofleftbuildings+numberofrightbuildings}"
            newbuilding.Draw(canvas)
            road.buildings.append(newbuilding)
            numberofrightbuildings += 1

def LineAllRoadsWithBuildings(roads, canvas):
    for r in roads:
        if not isinstance(r, Boundary):         #don't put buildings on the boundary walls
            LineRoadWithBuildings(r, canvas)