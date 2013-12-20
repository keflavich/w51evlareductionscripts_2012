from bandpass import bandpass
from rmtables import rmtables
from importvla import importvla
from importuvfits import importuvfits
from listobs import listobs
from applycal import applycal
from setjy import setjy
from gaincal import gaincal
from fluxscale import fluxscale
from accum import accum
from plotxy import plotxy
from plotcal import plotcal
from clean import clean
from split import split
from clearcal import clearcal
from imstat import imstat
from imregrid import imregrid
from exportfits import exportfits
from plotants import plotants
from plotms import plotms
import casac
import shutil
from taskinit import *
F=False
T=True

def split_and_cal(rootvis, rootprefix, spwn, fluxcal, phasecal, target,
        anttable=[], fieldpre=[], fresh_clean=False):
    print "Beginning calibration and mapping of spw ", spwn
    prefix = rootprefix+"_spw"+spwn

    # hopefully this decreases read/write times...
    vis = outvis = prefix+".ms"
    split(vis=rootvis, outputvis=outvis, spw=spwn, datacolumn='all')
    listobs(outvis)

    plotants(vis=vis,figfile=prefix+'plotants_'+vis+".png")
    #plotms(vis=vis, xaxis='', yaxis='', averagedata=False, transform=False, extendflag=False,
    #        plotfile='FirstPlot_AmpVsTime.png',selectdata=True,field='')
    plotms(vis=vis, spw='0', averagedata=True, avgchannel='64', avgtime='5', xaxis='uvdist', yaxis='amp', field=phasecal, plotfile=prefix+"phasecal_%s_AmpVsUVdist_spw%s.png" % (phasecal,spwn),overwrite=True)
    plotms(vis=vis, spw='0', averagedata=True, avgchannel='64', avgtime='5', xaxis='uvdist', yaxis='amp', field=fluxcal, plotfile=prefix+"fluxcal_%s_AmpVsUVdist_spw%s.png" % (fluxcal,spwn),overwrite=True)
    plotms(vis=vis, spw='0', averagedata=True, avgchannel='64', avgtime='5', xaxis='uvdist', yaxis='amp', field=target, plotfile=prefix+"target_%s_AmpVsUVdist_spw%s.png" % (target,spwn),overwrite=True)
    plotms(vis=vis, field='',correlation='RR,LL',timerange='',antenna='ea01',spw='0',
            xaxis='time',yaxis='antenna2',coloraxis='field',plotfile=prefix+'antenna2vsantenna1vstime_spw%s.png' % spwn,overwrite=True)

    #gencal(vis=vis,caltable=prefix+".antpos",caltype="antpos")

    # this apparently doubles the data size... clearcal(vis=vis,field='',spw='')
    #setjy(vis=vis, listmodels=T)
    gaincal(vis=vis, caltable=prefix+'.G0all', 
            field='0,1', refant='ea21', spw='0:32~96',
            gaintype='G',calmode='p', solint='int', 
            minsnr=5, gaintable=anttable)

    #didn't work
    plotcal(caltable=prefix+'.G0all',xaxis='time',yaxis='phase',
            spw='0',
            poln='R',plotrange=[-1,-1,-180,180],
            figfile=prefix+'.G0all.png')

    gaincal(vis=vis, caltable=prefix+'.G0', 
            field=fluxcal, refant='ea21', spw='0:20~100', calmode='p', solint='int', 
            minsnr=5, gaintable=anttable)

    plotcal(caltable=prefix+'.G0',xaxis='time',yaxis='phase',
            spw='0',
            poln='R',plotrange=[-1,-1,-180,180],
            figfile=prefix+'.G0.png')


    gaincal(vis=vis,caltable=prefix+'.K0', 
            field=fluxcal,refant='ea21',spw='0:5~123',gaintype='K', 
            solint='inf',combine='scan',minsnr=5,
            gaintable=anttable+[
                       prefix+'.G0'])

    plotcal(caltable=prefix+'.K0',xaxis='antenna',yaxis='delay',
            spw='0',
            figfile=prefix+'.K0_delayvsant_spw'+spwn+'.png')

    bandpass(vis=vis,caltable=prefix+'.B0',
             field=fluxcal,spw='0',refant='ea21',solnorm=True,combine='scan', 
             solint='inf',bandtype='B',
             gaintable=anttable+[
                        prefix+'.G0',
                        prefix+'.K0'])

    # In CASA
    plotcal(caltable= prefix+'.B0',poln='R', 
            spw='0',
            xaxis='chan',yaxis='amp',field=fluxcal,subplot=221, 
            figfile=prefix+'plotcal_fluxcal-B0-R-amp_spw'+spwn+'.png')
    #
    plotcal(caltable= prefix+'.B0',poln='L', 
            spw='0',
            xaxis='chan',yaxis='amp',field=fluxcal,subplot=221, 
            figfile=prefix+'plotcal_fluxcal-B0-L-amp_spw'+spwn+'.png')
    #
    plotcal(caltable= prefix+'.B0',poln='R', 
            spw='0',
            xaxis='chan',yaxis='phase',field=fluxcal,subplot=221, 
            plotrange=[-1,-1,-180,180],
            figfile=prefix+'plotcal_fluxcal-B0-R-phase_spw'+spwn+'.png')
    #
    plotcal(caltable= prefix+'.B0',poln='L', 
            spw='0',
            xaxis='chan',yaxis='phase',field=fluxcal,subplot=221, 
            plotrange=[-1,-1,-180,180],
            figfile=prefix+'plotcal_fluxcal-B0-L-phase_spw'+spwn+'.png')
             

    gaincal(vis=vis,caltable=prefix+'.G1',
            field=fluxcal,spw='0:5~123',
            solint='inf',refant='ea21',gaintype='G',calmode='ap',solnorm=F,
            gaintable=anttable+[
                       prefix+'.K0',
                       prefix+'.B0'])
            
    gaincal(vis=vis,caltable=prefix+'.G1',
            field=phasecal,
            spw='0:5~123',solint='inf',refant='ea21',gaintype='G',calmode='ap',
            gaintable=anttable+[
                       prefix+'.K0',
                       prefix+'.B0'],
            append=True)

    plotcal(caltable=prefix+'.G1',xaxis='time',yaxis='phase',
            spw='0',
            poln='R',plotrange=[-1,-1,-180,180],figfile=prefix+'plotcal_fluxcal-G1-phase-R_spw'+spwn+'.png')
    plotcal(caltable=prefix+'.G1',xaxis='time',yaxis='phase',
            spw='0',
            poln='L',plotrange=[-1,-1,-180,180],figfile=prefix+'plotcal_fluxcal-G1-phase-L_spw'+spwn+'.png')
    plotcal(caltable=prefix+'.G1',xaxis='time',yaxis='amp',
            spw='0',
            poln='R',figfile=prefix+'plotcal_fluxcal-G1-amp-R_spw'+spwn+'.png')
    plotcal(caltable=prefix+'.G1',xaxis='time',yaxis='amp',
            spw='0',
            poln='L',figfile=prefix+'plotcal_fluxcal-G1-amp-L_spw'+spwn+'.png')


    myscale = fluxscale(vis=vis,
                        caltable=prefix+'.G1', 
                        fluxtable=prefix+'.fluxscale1', 
                        reference=[fluxcal],
                        transfer=[phasecal])


    applycal(vis=vis,
             field=fluxcal,
             spw='0',
             gaintable=anttable+[ 
                        prefix+'.fluxscale1',
                        prefix+'.K0',
                        prefix+'.B0',
                        ],
             gainfield=fieldpre+[fluxcal,'',''], 
             interp=fieldpre+['nearest','',''],
             calwt=F)
     
    applycal(vis=vis,
             field=phasecal,
             spw='0',
             gaintable=anttable+[ 
                        prefix+'.fluxscale1',
                        prefix+'.K0',
                        prefix+'.B0',
                        ],
             gainfield=fieldpre+[phasecal,'',''], 
             interp=fieldpre+['nearest','',''],
             calwt=F)

    applycal(vis=vis,
             field=target,
             spw='0',
             gaintable=anttable+[ 
                        prefix+'.fluxscale1',
                        prefix+'.K0',
                        prefix+'.B0',
                        ],
             gainfield=fieldpre+[phasecal,'',''], 
             interp=fieldpre+['linear','',''],
             calwt=F)

    plotms(vis=prefix+'.ms',field=fluxcal,correlation='',
            spw='0',
           antenna='',avgtime='60s',
           xaxis='channel',yaxis='amp',ydatacolumn='corrected',
           plotfile=prefix+'_fluxcal-corrected-amp_spw'+spwn+'.png',overwrite=True)
    #
    plotms(vis=prefix+'.ms',field=fluxcal,correlation='',
            spw='0',
           antenna='',avgtime='60s',
           xaxis='channel',yaxis='phase',ydatacolumn='corrected',
           plotrange=[-1,-1,-180,180],coloraxis='corr',
           plotfile=prefix+'_fluxcal-corrected-phase_spw'+spwn+'.png',overwrite=True)
    #
    plotms(vis=prefix+'.ms',field=phasecal,correlation='RR,LL',
            spw='0',
           timerange='',antenna='',avgtime='60s',
           xaxis='channel',yaxis='amp',ydatacolumn='corrected',
           plotfile=prefix+'_phasecal-corrected-amp_spw'+spwn+'.png',overwrite=True)
    #
    plotms(vis=prefix+'.ms',field=phasecal,correlation='RR,LL',
            spw='0',
           timerange='',antenna='',avgtime='60s',
           xaxis='channel',yaxis='phase',ydatacolumn='corrected',
           plotrange=[-1,-1,-180,180],coloraxis='corr',
           plotfile=prefix+'_phasecal-corrected-phase_spw'+spwn+'.png',overwrite=True)

    plotms(vis=prefix+'.ms',field=phasecal,correlation='RR,LL',
            spw='0',
           timerange='',antenna='',avgtime='60s',
           xaxis='phase',xdatacolumn='corrected',yaxis='amp',ydatacolumn='corrected',
           plotrange=[-180,180,0,3],coloraxis='corr',
           plotfile=prefix+'_phasecal-corrected-ampvsphase_spw'+spwn+'.png',overwrite=True)

    plotms(vis=vis,xaxis='uvwave',yaxis='amp',
            spw='0',
           field=fluxcal,avgtime='30s',correlation='RR',
           plotfile=prefix+'_fluxcal-mosaic0-uvwave_spw'+spwn+'.png',overwrite=True)

    plotms(vis=vis,xaxis='uvwave',yaxis='amp',
            spw='0',
           field=target,avgtime='30s',correlation='RR',
           plotfile=prefix+'_target-mosaic0-uvwave_spw'+spwn+'.png',overwrite=True)

    for antenna in xrange(28):
        plotms(vis=vis, xaxis='time', yaxis='amp', spw='0',
                field='', avgchannel='64', coloraxis='corr',
                avgtime='5s',
                antenna='%i' % antenna,
                plotfile=prefix+"_antenna%02i_ampVStime.png" % antenna,
                overwrite=True)

    imagename = prefix+"_mfs"

    if fresh_clean:
        shutil.rmtree(imagename+".model")
        shutil.rmtree(imagename+".image")
        shutil.rmtree(imagename+".psf")
        shutil.rmtree(imagename+".flux")
        shutil.rmtree(imagename+".residual")

    clean(vis=outvis,
          imagename=imagename,
          field=target,spw='',
          mode='mfs', # use channel to get cubes
          nterms=1, # no linear polynomial
          niter=5000,
          gain=0.1, threshold='1.0mJy',
          psfmode='clark',
          multiscale=[0], 
          interactive=False,
          imsize=[2560,2560], 
          cell=['0.1arcsec','0.1arcsec'],
          stokes='I',
          weighting='uniform',
          allowchunk=True,
          usescratch=True)
    exportfits(imagename=imagename+".image", fitsimage=imagename+".fits", overwrite=True)
    print "Finished spw ",spwn

