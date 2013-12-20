"""
Oct 29 12B-365.sb11988384.eb13796420.56229.0065880787.ms/
Nov 17 12B-365.sb11988384.eb13946573.56248.74433101852.ms/
Oct 16 12B-365.sb12057814.eb12929296.56216.09073398148.ms/
Nov 24 12B-365.sb12058790.eb14029898.56255.03972864583.ms/
Nov 12 12B-365.sb12079719.eb13845934.56243.986530752314.ms/
Dec 09
"""
import os
vis = '12B-365.sb12057814.eb12929296.56216.09073398148.ms' # Oct 16
rootvis = 'w51_Oct16_2012.ms'
rootprefix = prefix = rootvis.replace(".ms","")
fluxcal = '0137+331=3C48'
phasecal = 'J1922+1530'
target = 'W51'

if False:
    listobs(vis)
    tflagdata(vis=vis, mode='manual', scan='1')
    tflagdata(vis=vis, mode='quack', quackinterval=10.0, quackmode='beg')
    #tflagdata(vis=vis, mode='manual', field=phasecal, timerange='2:20:00~2:24:45')
    gencal(vis=vis,caltable=prefix+".antpos",caltype="antpos")
    setjy(vis=vis, field=fluxcal, modimage='3C48_C.im',
            standard='Perley-Butler 2010', usescratch=True, scalebychan=True,
            spw='')
if os.path.exists(prefix+'.antpos'):
    anttable = [prefix+'.antpos']
    fieldpre = ['']
else:
    anttable= []
    fieldpre = []

# for interactive stuff
prefix = rootprefix+"_spw0"
vis = outvis = prefix+".ms"

import cal_script
for spwn in [   '8', '9', '10', '11', '12', '13', '14', '15', '0', '1', '2','3','4','5', '6', '7',]:
    cal_script.split_and_cal(rootvis, rootprefix, spwn, fluxcal, phasecal, target, anttable=anttable, fieldpre=fieldpre)
