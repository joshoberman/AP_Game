import matplotlib.pyplot as plt
import ast
from numpy import absolute, mean
from os import listdir
def get_level(level):
    player_trajectories = []
    Level = listdir()

Level1 = listdir("Subject 3/Level 1")
Level1=["Subject 3/Level 1/{0}".format(i) for i in Level1]
player_trajectories = []
for f in Level1:
    trajectory=open(f, 'r')
    for line in trajectory:
        player_trajectories.append(line)

print player_trajectories
to_plot1 = [line for line in player_trajectories]
to_plot1 = [ast.literal_eval(item) for item in to_plot1]
x_val1 = [x[1] for x in to_plot1]
y_val1 = [x[0] for x in to_plot1]
enemy_sightings = open("sight_times.txt", "r")
to_plot2 = [line for line in enemy_sightings]
to_plot2 = [ast.literal_eval(item) for item in to_plot2]
#print to_plot2
x_val2 = [x[1] for x in to_plot2]
y_val2 = [x[0] for x in to_plot2]
plt.plot(x_val1,y_val1,'.r')
plt.plot(x_val2,y_val2, 'ob')
plt.gca().invert_yaxis()
plt.show()
def mad(data, point):
    mad=mean(absolute(data-point))
    return mad
    
def divide():
    for x in x_val1:
        if x-(x-1)>.5:
            return new_list
        else:
            new_list=[]
            new_list.append(x)