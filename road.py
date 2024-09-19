import random as rand
from faker import Faker #need to pip install faker, used to make random street names

fake = Faker()
epsilon = 0.0000000001  #used to prevent dividing by zero
biggerepsilon = 0.001   #used to avoid new roads seeing an intersection with the road it's branching from

class Road():

    def __init__(self,x0,y0,x1,y1):
        self.x0 = x0                        #x0,y0 is start position of the road, x1,y1 is end position
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.m = (y1-y0)/(x1-x0+epsilon)    #slope of linear equation describing this line, +epsilon is to prevent dividing by zero without significantly affecting the result
        self.b = y0 - self.m*x0             #y-intercept of linear equation
        self.width = 0
        self.length = ((x1-x0)**2 + (y1-y0)**2)**0.5

        self.name = f"{fake.street_name().split(" ")[0]} St" #faker street names have a ton of random suffixes, but it feels more consistent to just call everything Something St
        self.color = "gray1"
        self.tag = ""

        self.buildings = []                 #list of Building objects which lie along this road
    
    def __str__(self):
        return f"{self.name}"

    def PrintEndpoints(self):
        print(f"({self.x0:.2f},{self.y0:.2f}) to ({self.x1:.2f},{self.y1:.2f})")

    def Draw(self, canvas):
        canvas.create_line(self.x0,self.y0,self.x1,self.y1, width=self.width, fill=self.color, activefill="lawn green", tag=self.tag)

    
    def NewRandomBranch(self, otherroads, RoadType):    #makes a new road branching off of this road, perpendicularly, making either a three-way or four-way intersection
        randomt = rand.uniform(.1,.9)   #pick a random point along the line, except near the edges because that doesn't look good
        x0,y0 = CalculatePosFromT(self, randomt)
        newm = -1/self.m        #new road is perpendicular to this road
        newb = y0 - newm*x0     #new road passes through this road at (x0,y0)
        foundintersections = FindIntersections(newm, newb, otherroads)  #other roads that this new road would intersect with
        closestintersections = FindClosestIntersections(foundintersections,x0,y0)

        #new road has an equal chance to make a three-way intersection turning right, turning left, or to make a four-way intersection
        choice = rand.uniform(0,1)
        if choice < 1/3:    #three-way, turns one way
            xi = closestintersections[0][1]
            yi = closestintersections[0][2]
            newroad = RoadType(x0,y0,xi,yi)
            newroad.tag = f"r{len(otherroads)}"
            otherroads.append(newroad)

            return
        if choice < 2/3:    #three-way, turns the other way
            xi = closestintersections[1][1]
            yi = closestintersections[1][2]
            newroad = RoadType(x0,y0,xi,yi)
            newroad.tag = f"r{len(otherroads)}"
            otherroads.append(newroad)

            return
        else:               #four-way
            xi1 = closestintersections[0][1]
            yi1 = closestintersections[0][2]
            xi2 = closestintersections[1][1]
            yi2 = closestintersections[1][2]
            newroad = RoadType(xi1,yi1,xi2,yi2)
            newroad.tag = f"r{len(otherroads)}"
            otherroads.append(newroad)

            return




class Boundary(Road):   #the "walls" of the town marking the edge of the town region, inherits from Road so that they play nicely with intersection code

    def __init__(self,x0,y0,x1,y1,tag):
        super().__init__(x0,y0,x1,y1)
        self.name = "Boundary"
        self.color = "gray1"
        self.width = 25
        self.tag = tag

    def Draw(self, canvas):
        return canvas.create_line(self.x0,self.y0,self.x1,self.y1, width=self.width, fill=self.color, tag=self.tag)

class MajorRoad(Road):  #the big roads that are created first and everything branches off from, always ends at the boundaries

    def __init__(self,x0,y0,x1,y1):
        super().__init__(x0,y0,x1,y1)
        self.color = "gray12"
        self.width = 19
    
    def ExtendToBoundaries(self, otherroads):   #take the randomized starting road segments and make them continue all the way to the edge, then recalculate x0,y0
        foundintersections = FindIntersections(self.m, self.b, otherroads)
        
        boundaryintersections = [i for i in foundintersections if isinstance(i[0], Boundary)]
        self.x0 = boundaryintersections[0][1]   #boundary is rectangular so there will only be two boundary intersection points (ignoring the super tiny chance of a perfectly diagonal line through the corners)
        self.y0 = boundaryintersections[0][2]
        self.x1 = boundaryintersections[1][1]
        self.y1 = boundaryintersections[1][2]
        self.length = ((self.x1-self.x0)**2 + (self.y1-self.y0)**2)**0.5



class MinorRoad(Road):  #smaller roads which immediately branch off from major roads

    def __init__(self,x0,y0,x1,y1):
        super().__init__(x0,y0,x1,y1)
        self.color = "gray20"
        self.width = 13

class TinyRoad(Road):   #even smaller roads which branch off from minor roads

    def __init__(self,x0,y0,x1,y1):
        super().__init__(x0,y0,x1,y1)
        self.color = "gray30"
        self.width = 9



def CalculateLerpT(road,xi):    #solve x0+(x1-x0)*t = xi to find linear interpolation t, between the endpoints of the given road
    return (xi-road.x0)/(road.x1-road.x0+epsilon)

def CalculatePosFromT(road,t):
    xi = road.x0+(road.x1-road.x0)*t
    yi = road.y0+(road.y1-road.y0)*t
    return (xi,yi)

def FindIntersections(m0,b0,otherroads):     #solves system of linear equations to find intersection points for the given slope & y-intercept with every other road's slope & y-intercept
    intersections = []      #list of intersection points: road object, position, t value on other road

    for otherroad in otherroads:
        m1 = otherroad.m
        b1 = otherroad.b

        xi = (b1-b0)/(m0-m1+epsilon)  #solve m0*x+b0 = m1*x+b1 to find intersection point (xi,yi)
        yi = m0*xi + b0
        t = CalculateLerpT(otherroad,xi)

        
        if (t>=0 and t<=1):   #if t is not in the range 0-1, then the intersection point isn't on the line segment of the road so it's not actually a valid intersection point
            #print(f"{m0:.2f} and {b0:.2f}: {otherroad}, ({xi:.2f},{yi:.2f}), t={t:.2f}")
            intersections.append((otherroad,xi,yi,t))

    return intersections

def FindClosestIntersections(intersections,xi,yi):    #takes the output of FindIntersections as input, returns the closest intersections
    left = [i for i in intersections if i[1]<xi and abs(i[1]-xi)>biggerepsilon]     #all intersections with xi < x0, making sure to avoid xi=x0 
    right = [i for i in intersections if i[1]>xi and abs(i[1]-xi)>biggerepsilon]    #all intersections with xi > x0, making sure to avoid xi=x0
    closestleft = sorted(left, key=lambda i: (i[1]-xi)**2+(i[2]-yi)**2)[0]          #closest intersection with xi < x0
    closestright = sorted(right, key=lambda i: (i[1]-xi)**2+(i[2]-yi)**2)[0]        #closest intersection with xi > x0
    return (closestleft,closestright)


def NewRandomMajorRoad(otherroads,townwidth,townheight):
    newroad = MajorRoad(rand.uniform(.2,.8)*townwidth,rand.uniform(.2,.8)*townheight,rand.uniform(.2,.8)*townwidth,rand.uniform(.2,.8)*townheight)
    newroad.ExtendToBoundaries(otherroads)
    newroad.tag = f"r{len(otherroads)}"
    otherroads.append(newroad)

def DrawAllRoads(roads, canvas):
    for r in roads[::-1]:   #looped in reverse so that the larger roads are drawn on top of the smaller ones
        r.Draw(canvas)