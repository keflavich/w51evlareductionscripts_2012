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
vis = '12B-365.sb12057814.eb12929296.56216.09073398148.ms'
vis_sband = '12B-365.sb12057814.eb12929296.56216.09073398148.ms'
vis = '12B-365.sb12079719.eb13845934.56243.986530752314.ms'
vis = '12B-365.sb12058790.eb14029898.56255.03972864583.ms'
vis = 'w51_Oct16_2012.ms'
prefix = vis.replace(".ms","")
fluxcal = '0137+331=3C48'
phasecal = 'J1922+1530'
target = 'W51'

if False:
    listobs(vis)
    tflagdata(vis=vis, mode='manual', scan='1')
    tflagdata(vis=vis, mode='quack', quackinterval=10.0, quackmode='beg')
    tflagdata(vis=vis, mode='manual', field=phasecal, timerange='2:20:00~2:24:45')
    gencal(vis=vis,caltable=prefix+".antpos",caltype="antpos")
    setjy(vis=vis, field=fluxcal, modimage='3C48_C.im',
            standard='Perley-Butler 2010', usescratch=True, scalebychan=True,
            spw='')

for spwn in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '0']:
    prefix = vis.replace(".ms","")
    prefix = prefix+"_spw"+spwn

    # hopefully this decreases read/write times...
    outvis = prefix+".ms"
    split(vis=vis, outputvis=outvis, spw=spwn)
    vis = outvis

    plotants(vis=vis,figfile='plotants_'+vis+".png")
    #plotms(vis=vis, xaxis='', yaxis='', averagedata=False, transform=False, extendflag=False,
    #        plotfile='FirstPlot_AmpVsTime.png',selectdata=True,field='')
    plotms(vis=vis, spw='0', averagedata=True, avgchannel='64', avgtime='5', xaxis='uvdist', yaxis='amp', field=phasecal, plotfile="phasecal_%s_AmpVsUVdist_spw%s.png" % (phasecal,spwn),overwrite=True)
    plotms(vis=vis, spw='0', averagedata=True, avgchannel='64', avgtime='5', xaxis='uvdist', yaxis='amp', field=fluxcal, plotfile="fluxcal_%s_AmpVsUVdist_spw%s.png" % (fluxcal,spwn),overwrite=True)
    plotms(vis=vis, spw='0', averagedata=True, avgchannel='64', avgtime='5', xaxis='uvdist', yaxis='amp', field=target, plotfile="target_%s_AmpVsUVdist_spw%s.png" % (target,spwn),overwrite=True)
    plotms(vis=vis, field='',correlation='RR,LL',timerange='',antenna='ea01',spw='0',
            xaxis='time',yaxis='antenna2',coloraxis='field',plotfile='antenna2vsantenna1vstime_spw%s.png' % spwn,overwrite=True)

    gencal(vis=vis,caltable=prefix+".antpos",caltype="antpos")

    # this apparently doubles the data size... clearcal(vis=vis,field='',spw='')
    #setjy(vis=vis, listmodels=T)
    gaincal(vis=vis, caltable=prefix+'.G0all', 
            field='0,1', refant='ea21', spw='0:32~96',
            gaintype='G',calmode='p', solint='int', 
            minsnr=5, gaintable=[prefix+'.antpos'])

    #didn't work
    plotcal(caltable=prefix+'.G0all',xaxis='time',yaxis='phase',
            spw='0'
            poln='R',plotrange=[-1,-1,-180,180],
            figfile=prefix+'.G0all.png')

    gaincal(vis=vis, caltable=prefix+'.G0', 
            field=fluxcal, refant='ea21', spw='0:20~100', calmode='p', solint='int', 
            minsnr=5, gaintable=[prefix+'.antpos'])

    plotcal(caltable=prefix+'.G0',xaxis='time',yaxis='phase',
            spw='0'
            poln='R',plotrange=[-1,-1,-180,180],
            figfile=prefix+'.G0.png')


    gaincal(vis=vis,caltable=prefix+'.K0', 
            field=fluxcal,refant='ea21',spw='0:5~123',gaintype='K', 
            solint='inf',combine='scan',minsnr=5,
            gaintable=[prefix+'.antpos',
                       prefix+'.G0'])

    plotcal(caltable=prefix+'.K0',xaxis='antenna',yaxis='delay',
            spw='0'
            figfile=prefix+'.K0_delayvsant_spw'+spwn+'.png')

    bandpass(vis=vis,caltable=prefix+'.B0',
             field=fluxcal,spw='0',refant='ea21',solnorm=True,combine='scan', 
             solint='inf',bandtype='B',
             gaintable=[prefix+'.antpos',
                        prefix+'.G0',
                        prefix+'.K0'])

    # In CASA
    plotcal(caltable= prefix+'.B0',poln='R', 
            spw='0'
            xaxis='chan',yaxis='amp',field=fluxcal,subplot=221, 
            figfile='plotcal_fluxcal-B0-R-amp_spw'+spwn+'.png')
    #
    plotcal(caltable= prefix+'.B0',poln='L', 
            spw='0'
            xaxis='chan',yaxis='amp',field=fluxcal,subplot=221, 
            figfile='plotcal_fluxcal-B0-L-amp_spw'+spwn+'.png')
    #
    plotcal(caltable= prefix+'.B0',poln='R', 
            spw='0'
            xaxis='chan',yaxis='phase',field=fluxcal,subplot=221, 
            plotrange=[-1,-1,-180,180],
            figfile='plotcal_fluxcal-B0-R-phase_spw'+spwn+'.png')
    #
    plotcal(caltable= prefix+'.B0',poln='L', 
            spw='0'
            xaxis='chan',yaxis='phase',field=fluxcal,subplot=221, 
            plotrange=[-1,-1,-180,180],
            figfile='plotcal_fluxcal-B0-L-phase_spw'+spwn+'.png')
             

    gaincal(vis=vis,caltable=prefix+'.G1',
            field=fluxcal,spw='0:5~123',
            solint='inf',refant='ea21',gaintype='G',calmode='ap',solnorm=F,
            gaintable=[prefix+'.antpos',
                       prefix+'.K0',
                       prefix+'.B0'])
            
    gaincal(vis=vis,caltable=prefix+'.G1',
            field=phasecal,
            spw='0:5~123',solint='inf',refant='ea21',gaintype='G',calmode='ap',
            gaintable=[prefix+'.antpos',
                       prefix+'.K0',
                       prefix+'.B0'],
            append=True)

    plotcal(caltable=prefix+'.G1',xaxis='time',yaxis='phase',
            spw='0'
            poln='R',plotrange=[-1,-1,-180,180],figfile='plotcal_fluxcal-G1-phase-R_spw'+spwn+'.png')
    plotcal(caltable=prefix+'.G1',xaxis='time',yaxis='phase',
            spw='0'
            poln='L',plotrange=[-1,-1,-180,180],figfile='plotcal_fluxcal-G1-phase-L_spw'+spwn+'.png')
    plotcal(caltable=prefix+'.G1',xaxis='time',yaxis='amp',
            spw='0'
            poln='R',figfile='plotcal_fluxcal-G1-amp-R_spw'+spwn+'.png')
    plotcal(caltable=prefix+'.G1',xaxis='time',yaxis='amp',
            spw='0'
            poln='L',figfile='plotcal_fluxcal-G1-amp-L_spw'+spwn+'.png')


    myscale = fluxscale(vis=vis,
                        caltable=prefix+'.G1', 
                        fluxtable=prefix+'.fluxscale1', 
                        reference=[fluxcal],
                        transfer=[phasecal])


    applycal(vis=vis,
             field=fluxcal,
             spw='0'
             gaintable=[prefix+'.antpos', 
                        prefix+'.fluxscale1',
                        prefix+'.K0',
                        prefix+'.B0',
                        ],
             gainfield=['',fluxcal,'',''], 
             interp=['','nearest','',''],
             calwt=F)
     
    applycal(vis=vis,
             field=phasecal,
             spw='0'
             gaintable=[prefix+'.antpos', 
                        prefix+'.fluxscale1',
                        prefix+'.K0',
                        prefix+'.B0',
                        ],
             gainfield=['',phasecal,'',''], 
             interp=['','nearest','',''],
             calwt=F)

    applycal(vis=vis,
             field=target,
             spw='0'
             gaintable=[prefix+'.antpos', 
                        prefix+'.fluxscale1',
                        prefix+'.K0',
                        prefix+'.B0',
                        ],
             gainfield=['',phasecal,'',''], 
             interp=['','linear','',''],
             calwt=F)

    plotms(vis=prefix+'.ms',field=fluxcal,correlation='',
            spw='0'
           antenna='',avgtime='60s',
           xaxis='channel',yaxis='amp',ydatacolumn='corrected',
           plotfile='plotms_fluxcal-corrected-amp_spw'+spwn+'.png',overwrite=True)
    #
    plotms(vis=prefix+'.ms',field=fluxcal,correlation='',
            spw='0'
           antenna='',avgtime='60s',
           xaxis='channel',yaxis='phase',ydatacolumn='corrected',
           plotrange=[-1,-1,-180,180],coloraxis='corr',
           plotfile='plotms_fluxcal-corrected-phase_spw'+spwn+'.png',overwrite=True)
    #
    plotms(vis=prefix+'.ms',field=phasecal,correlation='RR,LL',
            spw='0'
           timerange='',antenna='',avgtime='60s',
           xaxis='channel',yaxis='amp',ydatacolumn='corrected',
           plotfile='plotms_phasecal-corrected-amp_spw'+spwn+'.png',overwrite=True)
    #
    plotms(vis=prefix+'.ms',field=phasecal,correlation='RR,LL',
            spw='0'
           timerange='',antenna='',avgtime='60s',
           xaxis='channel',yaxis='phase',ydatacolumn='corrected',
           plotrange=[-1,-1,-180,180],coloraxis='corr',
           plotfile='plotms_phasecal-corrected-phase_spw'+spwn+'.png',overwrite=True)

    plotms(vis=prefix+'.ms',field=phasecal,correlation='RR,LL',
            spw='0'
           timerange='',antenna='',avgtime='60s',
           xaxis='phase',xdatacolumn='corrected',yaxis='amp',ydatacolumn='corrected',
           plotrange=[-180,180,0,3],coloraxis='corr',
           plotfile='plotms_phasecal-corrected-ampvsphase_spw'+spwn+'.png',overwrite=True)

    plotms(vis=vis,xaxis='uvwave',yaxis='amp',
            spw='0'
           field=fluxcal,avgtime='30s',correlation='RR',
           plotfile='plotms_fluxcal-mosaic0-uvwave_spw'+spwn+'.png',overwrite=True)




    imagename = prefix+"_spw"+spwn
    clean(vis=outvis,
          imagename=imagename,
          field=target,spw='',
          mode='channel',
          niter=25000,
          gain=0.1, threshold='1.0mJy',
          psfmode='clark',
          multiscale=[0], 
          interactive=False,
          imsize=[2560,2560], cell=['0.1arcsec','0.1arcsec'],
          stokes='I',
          weighting='briggs',robust=0.5,
          allowchunk=True,
          usescratch=True)
    exportfits(imagename=imagename, fitsimage=imagename.replace(".image",".fits"))

