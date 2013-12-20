vis = 'w51_Oct16_2012.ms'
rootvis = vis = 'w51_Nov24_2012.ms'
rootprefix = prefix = vis.replace(".ms","")
fluxcal = '0137+331=3C48'
phasecal = 'J1922+1530'
target = 'W51'

for spwn in [ '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '0', '1', '2','3','4','5',  ]:
    print "Beginning calibration and mapping of spw ", spwn
    prefix = rootvis.replace(".ms","")
    prefix = prefix+"_spw"+spwn

    # hopefully this decreases read/write times...
    outvis = prefix+".ms"

    imagename = prefix+"_channel"
    clean(vis=outvis,
          imagename=imagename,
          field=target,spw='',
          mode='channel', # use channel to get cubes
          niter=5000,
          gain=0.1, threshold='1.0mJy',
          psfmode='clark',
          multiscale=[0], 
          interactive=False,
          imsize=[2560,2560], cell=['0.1arcsec','0.1arcsec'],
          stokes='I',
          weighting='briggs',robust=0.5,
          allowchunk=True,
          usescratch=True)
    exportfits(imagename=imagename+".image", fitsimage=imagename+".fits")
    print "Finished spw ",spwn


