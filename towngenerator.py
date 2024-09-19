import random as rand 
import tkinter as tk

from road import *
from building import *

windowwidth = 960
windowheight = 601
townwidth = 800
townheight = 600

root = tk.Tk()
root.title("Town Generator")
root.geometry(f"{windowwidth}x{windowheight}")

namelabel = tk.Label(root, relief="raised")
namelabel.place(x=townwidth+50, y=50)
typelabel = tk.Label(root)
typelabel.place(x=townwidth+50, y=75)

def GenerateTown():
    canvas = tk.Canvas(root, bg="green", width=townwidth, height=townheight)
    canvas.place(anchor="nw")

    def MouseMotion(event):     #handle showing the name of roads and buildings on the side of the window
        canvasobject = canvas.find_withtag("current")
        tags = canvas.itemcget(canvasobject, "tags")
        if "current" in tags:
            roadindex = int(tags.split(" ")[0][1:])             #the first tag ([0]) on the canvas object will be something like "r4" or "r15", and we just want the number part ([1:])
            if "b" in tags:
                buildingindex = int(tags.split(" ")[1][1:])     #if there's a "b" anywhere in the tags then this is a building, the second tag ([1]) gives the building index
                namelabel.config(text=roads[roadindex].buildings[buildingindex].name)
                typelabel.config(text=type(roads[roadindex].buildings[buildingindex]).__name__)
            else:
                namelabel.config(text=roads[roadindex].name)    #if there's no "b", then this is just a road
                typelabel.config(text=type(roads[roadindex]).__name__)
        else:
            namelabel.config(text="                   ")        #if there's nothing currently being hovered over, make the info box empty
            typelabel.config(text="")
    canvas.bind("<Motion>", MouseMotion)

    roads = []  #list of all the roads that exist in this town, of every type, including the boundaries

    roads.append(Boundary(0,0,townwidth,0,"r0"))        #create the four boundaries manually
    roads.append(Boundary(townwidth,0,townwidth,townheight,"r1"))
    roads.append(Boundary(townwidth,townheight,0,townheight,"r2"))
    roads.append(Boundary(0,townheight,0,0,"r3"))

    numberofmajorroads = rand.randint(2,3)
    for r in range(numberofmajorroads):
        NewRandomMajorRoad(roads,townwidth,townheight)

    numberofminorroads = 0
    for r in range(4,4+numberofmajorroads):
        for _ in range(int(rand.uniform(0,roads[r].length/150))):   #scale the number of possible branching roads by how long the road being branched from is
            numberofminorroads += 1                                 #so that tiny roads don't get (as) cluttered
            roads[r].NewRandomBranch(roads, MinorRoad)

    for r in range(4+numberofmajorroads,4+numberofmajorroads+numberofminorroads):
        for _ in range(int(rand.uniform(0,roads[r].length/80))):
            roads[r].NewRandomBranch(roads, TinyRoad)

    DrawAllRoads(roads,canvas)
    LineAllRoadsWithBuildings(roads,canvas)

generatebutton = tk.Button(root, width=18, height=15, text="Generate New Town", command=GenerateTown)
generatebutton.place(x=windowwidth-150,y=windowheight-280)

GenerateTown()
root.mainloop()