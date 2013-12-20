"""
drwxr-xr-x  2 ginsbura calculon  2 Dec  5 18:27 12B-365.sb12057814.eb12929296.56216.09073398148/
drwxr-xr-x 20 ginsbura calculon 37 Dec  5 18:29 12B-365.sb12057814.eb12929296.56216.09073398148.ms/
drwxr-xr-x  4 ginsbura calculon  5 Dec  5 18:27 12B-365.sb12057814.eb12929296.56216.09073398148.ms.flagversions/
drwxr-xr-x  3 ginsbura calculon 34 Dec  5 17:18 12B-365.sb12058790.eb14029898.56255.03972864583/
drwxr-xr-x 20 ginsbura calculon 54 Dec  5 17:18 12B-365.sb12058790.eb14029898.56255.03972864583.ms/
drwxr-xr-x  4 ginsbura calculon  5 Dec  5 17:01 12B-365.sb12058790.eb14029898.56255.03972864583.ms.flagversions/
drwxr-xr-x  2 ginsbura calculon  2 Dec  5 17:01 12B-365.sb12079719.eb13845934.56243.986530752314/
drwxr-xr-x 20 ginsbura calculon 34 Dec  5 17:18 12B-365.sb12079719.eb13845934.56243.986530752314.ms/
drwxr-xr-x  4 ginsbura calculon  5 Dec  5 17:18 12B-365.sb12079719.eb13845934.56243.986530752314.ms.flagversions/

"""
rootvis = vis = 'w51_Nov24_2012.ms'
rootprefix = prefix = vis.replace(".ms","")
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

import cal_script
for spwn in [ '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '0', '1', '2','3','4','5',  ]:
    cal_script.split_and_cal(rootvis, rootprefix, spwn, fluxcal, phasecal, target, anttable=anttable, fieldpre=fieldpre)
