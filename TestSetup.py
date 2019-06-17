from DatabaseManagers import * 
from math import *
import numpy as np
import math
import matplotlib.pyplot as plt

#User, Game, Zone Data
db=MainDatabaseManager()
db.write('User', [[0,'Scrooge McDuck']], True)
db.write('Game', [[0,'Klondike Gold Rush']], True)
db.write('Zone', [[0,'Test Zone']], True)

#variables
N=10 #Noise
R=100 #Radius Of The Circle
P=0.99 #Probability Of Maintaining Kidnap
S=0 #Random Seed

#Position Data
x=np.reshape(np.arange(0,2*R+1), (-1,1))
r=np.random.rand(len(x),1)
r=(r-0.5)*N
y1=np.sqrt(2*R*x-x**2)+R+r
y2=-np.sqrt(2*R*x-x**2)+R+r
y=np.append(y1,np.flip(y2))
x=np.append(x,np.flip(x))
t=np.arange(len(x))
z=np.zeros(x.shape)
lines=np.array([z,z,z,z,t,x, y, z]).T
db.write('Position',lines, True)
d=np.sqrt((R-x)**2+(R-y)**2)

#Inner Data
inner=(d<R)*1
e=np.repeat("inner",len(d))
inner=np.array([z,z,z,z,z,t,e,inner]).T
inner=np.insert(inner, 0, [-1]*8, axis=0)
lines=np.array([inner[i+1] for i in range(len(inner)-1) if inner[i,7]!=inner[i+1,7]])

#Border Data
border=(d<R)*1
e=np.repeat("border",len(d))
border=np.array([z,z,z,z,z,t,e,border]).T
border=np.insert(border, 0, border[0], axis=0)
border=np.array([border[i] for i in range(len(border)-1) if int(border[i,7]!=border[i+1,7])])
border[:,7]=1
lines=np.append(lines,border,axis=0)

#Kidnap Data
e=np.repeat("kidnap",len(t))
np.random.seed(S)
kidnap=(np.random.rand(len(t))<P)*1
kidnap=np.array([z,z,z,z,z,t,e,kidnap]).T
kidnap=np.insert(kidnap, 0, [-1]*8, axis=0)
kidnap=np.array([kidnap[i+1] for i in range(len(kidnap)-1) if kidnap[i,7]!=kidnap[i+1,7]])
lines=np.append(lines, kidnap, axis=0)
db.write('DiscreteEvent',lines, True)

#Distance Data
e=np.repeat("distance",len(d))
lines=np.array([z,z,z,z,z,t,e,np.absolute(R-d)]).T
db.write('ContinuousEvent',lines, True)



