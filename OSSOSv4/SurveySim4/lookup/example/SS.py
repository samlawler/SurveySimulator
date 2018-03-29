import ephem
from astropy.io import ascii
import math
import numpy
from pylab import *
from matplotlib.patches import Rectangle
from matplotlib.projections import register_projection


import numpy as np
from  matplotlib.projections.geo import MollweideAxes

def OGLE_footprint():
   vertix = [[270,-23],[271,-23],[271,-24],[270,-24],[270,-23]]

   footprint = []
   for vert in vertix:
      ra=math.radians(vert[0])
      dec = math.radians(vert[1])
      ra  =  ra > math.pi and ra - 2*math.pi or ra
      footprint.append([ra,dec])

   footprint = numpy.array(footprint)
   FOV = Polygon(footprint, alpha=1, facecolor='g')
   return FOV


def build_footprint():
   vertix = [[40,0],[50,-20],[60,-20],[75,-60],[45,-60],[30,-50],[20,-55],[15,-45],[0,-50],[0,-20],[40,0]]

   footprint = []
   for vert in vertix:
      ra=math.radians(vert[0])
      dec = math.radians(vert[1])
      ra  =  ra > math.pi and ra - 2*math.pi or ra
      footprint.append([ra,dec])

   footprint = numpy.array(footprint)
   FOV = Polygon(footprint, alpha=0.2, facecolor='k')
   return FOV

class myMollweideAxes(MollweideAxes):
   """my custom projection for doing astro All Sky Plots"""
   name = 'bollweide'

   class HoursFormatter(Formatter):
     """
     This is a custom formatter that converts the native unit of
     radians into (truncated) degrees and adds a degree symbol.
     """
     def __init__(self, round_to=1.0):
         self._round_to = round_to

     def __call__(self, x, pos=None):
         #degrees = (field_offset-(np.degrees(x)))*24/360.
         degrees = np.degrees(x)*24/360
         if ( degrees > 24 ) :
             degrees=degrees-24
         if ( degrees < 0 ) :
             degrees=degrees+24
         # degrees = round(degrees / self._round_to) * self._round_to
         # \u00b0 : degree symbol
         return u"%dh" % (degrees)

   def set_longitude_grid(self,degrees):
         #degrees = field_offset - degrees
         super(myMollweideAxes,self).set_longitude_grid(degrees)
         self.xaxis.set_major_formatter(self.HoursFormatter(degrees))

register_projection(myMollweideAxes)


fig=figure()
ax=fig.add_subplot(111,projection="bollweide")
#ax.set_longitude_grid(45)
ax.set_latitude_grid(30)
dimen=math.radians(1.0)

#    a      e       i      node     peri      M       H
kbos = ascii.read('CFEPS_MODEL.txt')
dt = ephem.date(2453157.50000-2415020.5 )
eb = ephem.EllipticalBody()
ra = []
dec = []
dra = []
ddec = []
ddra = []
dddec = []
FOV = build_footprint()
for kbo in kbos:
   eb._a = kbo['a']
   eb._e = kbo['e']
   eb._inc = kbo['i']
   eb._Om = kbo['node']
   eb._om = kbo['peri']
   eb._M = kbo['M']
   eb._H = kbo['H']
   eb._epoch_M = dt
   eb._epoch = dt
   eb.compute(dt)
   this_ra = float(eb.ra)
   this_dec = float(eb.dec)
   galactic = ephem.Galactic(eb)
   (glon, glat) = galactic.get()
   ecliptic = ephem.Ecliptic(eb)
   (elon, elat) = ecliptic.get()
   if this_ra < math.radians(270) and this_ra > math.radians(269) and this_dec < math.radians(-23) and this_dec > math.radians(-25):
      print math.degrees(eb.ra), math.degrees(eb.dec), eb.mag, "OGLE"
   if glat < math.radians(-30) and elat < math.radians(-20) and ( (float(eb.ra) < math.radians(60) and float(eb.dec) < math.radians(-20)) or float(eb.ra) < math.radians(45)) and eb.mag < 26.5:
      print math.degrees(eb.ra), math.degrees(eb.dec), eb.mag, "MLS", FOV.contains_point((this_ra, this_dec))
      ddra.append(this_ra)
      dddec.append(this_dec)
   this_ra  =  this_ra > math.pi and this_ra - 2*math.pi or this_ra
   ra.append(this_ra)
   dec.append(this_dec)

ax.plot(ra,dec,',', alpha=0.15)
#ax.plot(dra, ddec, '.', alpha=0.2)
#ax.plot(ddra, dddec, 'r.', alpha=0.2)

ax.add_artist(FOV)
ax.add_artist(OGLE_footprint())
savefig('sky.png')
