from clean import clean
from exportfits import exportfits
rootvis = vis = 'w51_Nov24_2012.ms'
rootprefix = prefix = vis.replace(".ms","")
fluxcal = '0137+331=3C48'
phasecal = 'J1922+1530'
target = 'W51'


for spwn in [ '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '0', '1', '2','3','4','5',  ]:
    print "Beginning calibration and mapping of spw ", spwn
    prefix = rootvis.replace(".ms","")
    prefix = prefix+"_spw"+spwn
    vis=prefix+".ms"
    
    imagename = prefix+"_mfs_uni"
    clean(vis=vis,
          imagename=imagename,
          field=target,spw='',
          mode='mfs', # use channel to get cubes
          niter=5000,
          gain=0.1, threshold='1.0mJy',
          psfmode='clark',
          multiscale=[0], 
          interactive=False,
          imsize=[2560,2560], cell=['0.1arcsec','0.1arcsec'],
          stokes='I',
          weighting='uniform',
          allowchunk=True,
          mask=[[1041,1271,1100,1394],[1500,1750,1600,1800],[1014,1150,1525,1701]],
          usescratch=True)
    exportfits(imagename=imagename+".image", fitsimage=imagename+".fits")

    # imagename = prefix+"_mfs_uni"
    # clean(vis=vis,
    #       imagename=imagename,
    #       field=target,spw='',
    #       mode='mfs', # use channel to get cubes
    #       nterms=2,
    #       niter=5000,
    #       gain=0.1, threshold='1.0mJy',
    #       psfmode='clark',
    #       multiscale=[0], 
    #       interactive=False,
    #       imsize=[2560,2560], cell=['0.1arcsec','0.1arcsec'],
    #       stokes='I',
    #       mask=[[1041,1271,1100,1394],[1612,1692,1670,1760]],
    #       weighting='uniform',
    #       allowchunk=True,
    #       usescratch=True)
    # exportfits(imagename=imagename+".image.tt0", fitsimage=imagename+".tt0.fits")
    # exportfits(imagename=imagename+".image.tt1", fitsimage=imagename+".tt1.fits")

    print "Finished spw ",spwn

