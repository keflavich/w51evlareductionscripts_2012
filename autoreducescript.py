import sys
import os
# continuum_script available at http://code.google.com/p/casaradio/source/browse/trunk/casavla/continuum_script.py
sys.path.append('/Users/adam/work/CASA/')
import continuum_script
from taskinit import *
import numpy as np

redo_pipeline = False
reconcat = False
doclean = False
stepclean = False
manual = True

if redo_pipeline:
    continuum_script.reduce_continuum('msAW158', archivedata=('AW158_A860427.xp2',), srcname='W51DE', cleanup=True)
    continuum_script.reduce_continuum('msAM449', archivedata=('AM449_A940115.xp7',), srcname='W51', cleanup=True)
    continuum_script.reduce_continuum('msAD128',archivedata=('AD128_A840206.xp1','AD128_A840206.xp2'), srcname='W51',
            cleanup=True)
    continuum_script.reduce_continuum('msAD129',
            archivedata=('AD129_A840503.xp3','AD129_B850517.xp1','AD129_B850517.xp2'),cleanup=True, srcname='W51')
    continuum_script.reduce_continuum('msAD175', archivedata=('AD175_A851206.xp1',), srcname='W51', cleanup=True)
    continuum_script.reduce_continuum('msAH361', archivedata=('AH361_A890730.xp3',), srcname='1921+142', cleanup=True)
    continuum_script.reduce_continuum('msAM0434', archivedata=('AM0434_A940819.xp8','AM0434_A940819.xp9'), srcname='W51', cleanup=True)
    continuum_script.reduce_continuum('msAP246',
            archivedata=('AP246_A921122.xp3','AP246_A921122.xp4','AP246_A921122.xp5','AP246_A921123.xp6'), srcname='W51', cleanup=True)

if reconcat:
    os.system('rm -r W51_merge.ms')
    msfiles = ['msAD129.W51.split.ms', 'msAH361.1921+142.split.ms',
            'msAP246.W51.split.ms',        #'msAM0434.W51.split.ms',
            #'msAW158.W51DE.split.ms', #this one kinda sucks
            'msAD128.W51.split.ms', #'msAD175.W51.split.ms',
            'msAM449.W51.split.ms']

    # a useful reference: http://www.aoc.nrao.edu/~smyers/casa/scripts/scaleweights.py
    for msfn in msfiles:
        tb.open(msfn,nomodify=False)
        ms.open(msfn,nomodify=False)
        wtbackupfile = msfn.replace('.ms','.weight.npy')
        if os.path.exists(wtbackupfile):
            weight = np.fromfile(wtbackupfile)
            if len(weight.shape) == 1:
                weight.shape = [1,weight.shape[0]]
        else: #if not os.path.exists(msfn.replace('.ms','.weight.txt')):
            weight = tb.getcol('WEIGHT')
            np.save(wtbackupfile, weight)
        weight[np.isnan(weight)+np.isinf(weight)] = 0
        scales = np.median(weight,axis=1).reshape([weight.shape[0],1])
        scales[scales == 0] = np.mean(weight[scales==0,:])
        scales[scales == 0] = 1.0
        print "Rescaling weights to  ",scales
        if np.isnan(scales).sum() > 0:
            raise ValueError("NAN!")
        weight /= scales
        print "Total weight: ",weight.sum()
        if np.all(weight==0):
            weight[:] = 1.0
        tb.putcol('WEIGHT',weight)
        ms.putdata({'WEIGHT':weight})
        ms.close()
        tb.close()

    concat(vis=msfiles, concatvis='W51_merge.ms')

if stepclean:
    beamsize = {
        'msAD128.W51.split.ms': (6.944444444444E-04,3.472222222222E-04),
        'msAD129.W51.split.ms': (7.371956772274E-04,6.580011049906E-04),
        'msAD175.W51.split.ms': (4.108799828423E-03,3.682451513078E-03),
        'msAM0434.W51.split.ms':(6.944444444444E-04,3.472222222222E-04),
        'msAM449.W51.split.ms': (1.220734914144E-02,7.413729561700E-03),
        'msAP246.W51.split.ms': (6.944444444444E-04,3.472222222222E-04),
        }

    beams = np.array([(n,np.sqrt(b[0]**2+b[1]**2)) for n,b in beamsize.items()])
    beamsorted = beams[np.argsort(beams[:,1])[::-1],:]
    modelimage = ""
    for order,msfn in enumerate(beamsorted[:,0]):
        msfn = str(msfn)
        cleanfn = msfn.replace(".split.ms",".clean")
        os.system('rm -rf %s*' % cleanfn)
        clean(vis=msfn,  imagename=cleanfn,  mode='mfs',  stokes='I',
            field='',  spw='',  psfmode='clark', imagermode='',
            imsize=[1024,1024],  cell=['0.2arcsec'], gain=0.1,
            niter=10000, weighting='briggs',  robust=0.5, threshold="5mJy",
            mask='', interactive =False,  calready=True,  npercycle=100,
            modelimage=modelimage)
        modelimage = cleanfn+".image"
        imregrid(cleanfn+".image",'J2000',cleanfn+".regrid.image")
        exportfits(imagename=cleanfn+".regrid.image", fitsimage="%02i%s.fits" % (order+1,cleanfn), overwrite=True)
    
if manual:
    os.system('rm -rf msAD1289_175.W51.ms')
    print "Flagging"
    # this is useful for flagging based on other stuff: http://www.aoc.nrao.edu/~smyers/casa/scripts/flagaverage.py
    flagdata('msAD128.W51.split.ms',selectdata=True,mode='manualflag',antenna='VA22,VA27,VA11',timerange='1984/02/06/21:30:00~21:35:00')
    flagdata('msAD128.W51.split.ms',selectdata=True,mode='manualflag',spw=['0,1','1','1'],timerange=['1984/02/06/20:20:30~20:23:20','1985/05/17/14:20:40.0~14:20:50.0','1985/05/17/14:21:25.0'])
    flagdata('msAD129.W51.split.ms',selectdata=True,mode='manualflag',spw=['0,1','1','1'],timerange=['1984/02/06/20:20:30~20:23:20','1985/05/17/14:20:40.0~14:20:50.0','1985/05/17/14:21:25.0'])
    #flagdata('msAM449.W51.split.ms',selectdata=True,mode='manualflag',clipexpr='ABS RR',clipminmax=[0,50])
    #flagdata('msAD175.W51.split.ms',selectdata=True,mode='manualflag',correlation='RL LR')
    print "Concatenating"
    concat(vis=['msAD128.W51.split.ms','msAD129.W51.split.ms','msAD175.w51.split.ms'],concatvis='msAD1289_175.W51.ms')
    flagdata('msAD1289_175.W51.ms',selectdata=True,mode='manualflag',spw=['0,1','1','1'],timerange=['1984/02/06/20:20:30~20:23:20','1985/05/17/14:20:40.0~14:20:50.0','1985/05/17/14:21:25.0'])
    #flagdata('msAD1289_175.W51.ms',selectdata=True,mode='manualflag',correlation='RL LR')
    flagdata('msAD1289_175.W51.ms',selectdata=True,mode='manualflag',antenna='VA22,VA27,VA11',timerange='1984/02/06/21:30:00~21:35:00')
    os.system('rm -rf msAD1289_175.W51.clean*')
    print "Cleaning"
    clean(vis='msAD1289_175.W51.ms',  imagename='msAD1289_175.W51.clean',  mode='mfs',  stokes='I',
        field='',  spw='',  psfmode='clark', imagermode='',multiscale = [0,5,15,50],
        imsize=[1024,1024],  cell=['0.2arcsec'], gain=0.1,
        niter=10000, weighting='briggs',  robust=0.5, threshold="1mJy",
        mask='', interactive =False,  calready=True,  npercycle=100)
    imregrid("msAD1289_175.W51.clean.image",'J2000',"msAD1289_175.W51.clean.regrid.image")
    exportfits(imagename='msAD1289_175.W51.clean.regrid.image',fitsimage='msAD1289_175.W51.clean.fits',overwrite=True)
    print "Self Cal"
    continuum_script.selfcal('msAD1289_175.W51', mode='mfs',  
        psfmode='clark', imagermode='',multiscale = [0,5,15,50],
        imsize=[1024,1024],  cell=['0.2arcsec'], gain=0.1,
        niter=10000, weighting='briggs',  robust=0.5, threshold="1mJy",
        mask='', interactive =False,  calready=True,  npercycle=100, selfcaliter=4)

    os.system('rm -rf msAD1289.W51.ms')
    print "Flagging"
    flagdata('msAD128.W51.split.ms',selectdata=True,mode='manualflag',antenna='VA22,VA27,VA11',timerange='1984/02/06/21:30:00~21:35:00')
    flagdata('msAD128.W51.split.ms',selectdata=True,mode='manualflag',spw=['0,1','1','1'],timerange=['1984/02/06/20:20:30~20:23:20','1985/05/17/14:20:40.0~14:20:50.0','1985/05/17/14:21:25.0'])
    flagdata('msAD129.W51.split.ms',selectdata=True,mode='manualflag',spw=['0,1','1','1'],timerange=['1984/02/06/20:20:30~20:23:20','1985/05/17/14:20:40.0~14:20:50.0','1985/05/17/14:21:25.0'])
    #flagdata('msAM449.W51.split.ms',selectdata=True,mode='manualflag',clipexpr='ABS RR',clipminmax=[0,50])
    #flagdata('msAD175.W51.split.ms',selectdata=True,mode='manualflag',correlation='RL LR')
    print "Concatenating"
    concat(vis=['msAD128.W51.split.ms','msAD129.W51.split.ms'],concatvis='msAD1289.W51.ms')
    flagdata('msAD1289.W51.ms',selectdata=True,mode='manualflag',spw=['0,1','1','1'],timerange=['1984/02/06/20:20:30~20:23:20','1985/05/17/14:20:40.0~14:20:50.0','1985/05/17/14:21:25.0'])
    #flagdata('msAD1289.W51.ms',selectdata=True,mode='manualflag',correlation='RL LR')
    flagdata('msAD1289.W51.ms',selectdata=True,mode='manualflag',antenna='VA22,VA27,VA11',timerange='1984/02/06/21:30:00~21:35:00')
    os.system('rm -rf msAD1289.W51.clean*')
    print "Cleaning"
    clean(vis='msAD1289.W51.ms',  imagename='msAD1289.W51.clean',  mode='mfs',  stokes='I',
        field='',  spw='',  psfmode='clark', imagermode='',multiscale = [0,5,15,50],
        imsize=[1024,1024],  cell=['0.2arcsec'], gain=0.1,
        niter=10000, weighting='briggs',  robust=0.5, threshold="1mJy",
        mask='', interactive =False,  calready=True,  npercycle=100)
    imregrid("msAD1289.W51.clean.image",'J2000',"msAD1289.W51.clean.regrid.image")
    exportfits(imagename='msAD1289.W51.clean.regrid.image',fitsimage='msAD1289.W51.clean.fits',overwrite=True)
    print "Self Cal"
    continuum_script.selfcal('msAD1289.W51', mode='mfs',  
        psfmode='clark', imagermode='',multiscale = [0,5,15,50],
        imsize=[1024,1024],  cell=['0.2arcsec'], gain=0.1,
        niter=10000, weighting='briggs',  robust=0.5, threshold="1mJy",
        mask='', interactive =False,  calready=True,  npercycle=100, selfcaliter=4)


if doclean:

    os.system('rm -rf W51_merged.clean.*')
    clean(vis='W51_merge.ms',  imagename='W51_merged.clean',  mode='mfs',  stokes='I',
        field='',  spw='',  psfmode='clark', imagermode='',
        imsize=[1024,1024],  cell=['0.2arcsec','0.2arcsec'], gain=0.1,  niter=10000,
        weighting='briggs',  robust=0.5, threshold="50mJy",
        mask='',  interactive =False,  calready=True,  npercycle=100, )
    exportfits(imagename="W51_merged.clean.image", fitsimage="W51_merged.clean.fits", overwrite=True)

    os.system('rm -rf W51_merged.uniform.*')
    clean(vis='W51_merge.ms',  imagename='W51_merged.uniform',  mode='mfs',  stokes='I',
        field='',  spw='',  psfmode='clark', imagermode='',
        imsize=[1024,1024],  cell=['0.2arcsec','0.2arcsec'], gain=0.1,  niter=100000,
        weighting='uniform',  robust=-2, threshold="0.025Jy",
        mask='',  interactive =False,  calready=True,  npercycle=100, )
    exportfits(imagename="W51_merged.uniform.image", fitsimage="W51_merged.uniform.fits", overwrite=True)

    os.system('rm -rf W51_merged.robustm1.*')
    clean(vis='W51_merge.ms',  imagename='W51_merged.robustm1',  mode='mfs',  stokes='I',
        field='',  spw='',  psfmode='clark', imagermode='',
        imsize=[1024,1024],  cell=['0.2arcsec','0.2arcsec'], gain=0.1,  niter=10000,
        weighting='briggs',  robust=-1, threshold="0.025Jy",
        mask='',  interactive =False,  calready=True,  npercycle=100, )
    exportfits(imagename="W51_merged.robustm1.image", fitsimage="W51_merged.robustm1.fits", overwrite=True)

    os.system('rm -rf W51_merged.robust0.*')
    clean(vis='W51_merge.ms',  imagename='W51_merged.robust0',  mode='mfs',  stokes='I',
        field='',  spw='',  psfmode='clark', imagermode='',
        imsize=[1024,1024],  cell=['0.2arcsec','0.2arcsec'], gain=0.1,  niter=10000,
        weighting='briggs',  robust=0, threshold="0.025Jy",
        mask='',  interactive =False,  calready=True,  npercycle=100, )
    exportfits(imagename="W51_merged.robust0.image", fitsimage="W51_merged.robust0.fits", overwrite=True)

    os.system('rm -rf W51_merged.natural.*')
    clean(vis='W51_merge.ms',  imagename='W51_merged.natural',  mode='mfs',  stokes='I',
        field='',  spw='',  psfmode='clark', imagermode='',
        imsize=[1024,1024],  cell=['0.2arcsec','0.2arcsec'], gain=0.1,  niter=10000,
        weighting='natural',  robust=2, threshold="0.025Jy",
        mask='',  interactive =False,  calready=True,  npercycle=100, )
    exportfits(imagename="W51_merged.natural.image", fitsimage="W51_merged.natural.fits", overwrite=True)

    os.system('rm -rf W51_merged.hogbom.*')
    clean(vis='W51_merge.ms',  imagename='W51_merged.hogbom',  mode='mfs',  stokes='I',
        field='',  spw='',  psfmode='hogbom', imagermode='',
        imsize=[1024,1024],  cell=['0.2arcsec','0.2arcsec'], gain=0.1,  niter=10000,
        weighting='briggs',  robust=0, threshold="0.025Jy",
        mask='',  interactive =False,  calready=True,  npercycle=100, )
    exportfits(imagename="W51_merged.hogbom.image", fitsimage="W51_merged.hogbom.fits", overwrite=True)

    os.system('rm -rf W51_merged.multiscale.*')
    clean(vis='W51_merge.ms',  imagename='W51_merged.multiscale',  mode='mfs',  stokes='I',
        field='',  spw='',  psfmode='hogbom', imagermode='', multiscale = [0,5,15,50],
        imsize=[1024,1024],  cell=['0.2arcsec','0.2arcsec'], gain=0.1,  niter=10000,
        weighting='briggs',  robust=0, threshold="0.025Jy",
        mask='',  interactive =False,  calready=True,  npercycle=100, )
    exportfits(imagename="W51_merged.multiscale.image", fitsimage="W51_merged.multiscale.fits", overwrite=True)

    os.system('rm -rf W51_merged.csclean.*')
    clean(vis='W51_merge.ms',  imagename='W51_merged.csclean',  mode='mfs',  stokes='I',
        field='',  spw='',  psfmode='clark', imagermode='csclean',
        imsize=[1024,1024],  cell=['0.2arcsec','0.2arcsec'], gain=0.1,  niter=10000,
        weighting='briggs',  robust=0, threshold="0.025Jy",
        mask='',  interactive =False,  calready=True,  npercycle=100, )
    exportfits(imagename="W51_merged.csclean.image", fitsimage="W51_merged.csclean.fits", overwrite=True)
