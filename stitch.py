# Python script for stitch task
# Original author: Miriam Krauss
# Written 2012-03-01 (CASA v.3.3.0 r16856)

from taskinit import *
import numpy as np

def stitch(vis = None,
           baseband1 = None,
           baseband2 = None,
           startchan = None,
           numchan = None,
           dosplit = None,
           outputvis = None,
           datacolumn = None,
           field = None,
           correlation = None,
           keepflags = None):

    casalog.origin('stitch')
    
    #### Construct channel ranges:

    # Last channel for first baseband
    chanBB1_end = startchan + numchan - 1

    # Determine channels to use from second baseband

    myTT = tbtool.create()
    myTT.open(vis + '/SPECTRAL_WINDOW')
    chanFreqs = myTT.getcol('CHAN_FREQ')
    numChans = myTT.getcol('NUM_CHAN')
    refFreq = myTT.getcol('REF_FREQUENCY')
    chanWidth = myTT.getcol('CHAN_WIDTH')
    myTT.close()

    totChans = np.unique(numChans[range(baseband1[0],baseband1[1] + 1) +
                                  range(baseband2[0],baseband2[1] + 1)])

    channelWidth = np.unique(chanWidth[range(baseband1[0],baseband1[1] + 1) +
                                       range(baseband2[0],baseband2[1] + 1)])

    if (len(totChans) > 1):
        casalog.post('Spectral windows in provided basebands have differing numbers of channels', priority='ERROR')
        return
    
    if (len(channelWidth) > 1):
        casalog.post('Spectral windows in provided basebands have differing channel widths', priority='ERROR')
        return
    
    numBB2_chan = totChans[0] - numchan

    # Determine first channel for second baseband
    freq1_end = chanFreqs[chanBB1_end, baseband1[0]]
                     
    freq2_startInd = np.where((chanFreqs[:,baseband2[0]] >=
                               (freq1_end + channelWidth[0] / 2.))
                              & (chanFreqs[:,baseband2[0]]
                                 <= (freq1_end + 3. * channelWidth[0] / 2.)))

    if (len(freq2_startInd) > 1):
        casalog.post('Degenerate start channel for second baseband', priority='ERROR')
        return
    
    #    chanBB2_start = chanBB1_end - bboffset + 1
    chanBB2_start = freq2_startInd[0][0]

    # Last channel for second baseband
    chanBB2_end = chanBB2_start + numBB2_chan - 1

    # Construct strings for channel ranges
    chanBB1_str = str(startchan) + '~' + str(chanBB1_end)
    chanBB2_str = str(chanBB2_start) + '~' + str(chanBB2_end)
    
    # Want to use all lower channels in first baseband, and all higher
    # channels in last:
    first_spw_chan = '0~' + str(chanBB1_end)
    last_spw_chan = str(chanBB2_start) + '~' + str(totChans[0] - 1)
    
    #### Construct complete string:

    spwStr = str(baseband1[0]) + ':' + first_spw_chan + ',' + \
             str(baseband1[0] + 1) + '~' + str(baseband1[1]) + ':' + \
             chanBB1_str + ',' + str(baseband2[0]) + '~' + \
             str(baseband2[1] - 1) + ':' + chanBB2_str + ',' + \
             str(baseband2[1]) + ':' + last_spw_chan

    casalog.post('Spectral window / channel string to construct new MS:')
    casalog.post('   ' + spwStr)
    
    #### Run split, if requested:

    if (dosplit):

        if keepflags:
            taqlstr = ''
        else:
            taqlstr = 'NOT (FLAG_ROW OR ALL(FLAG))'

        myMS = mstool.create()
        myMS.open(vis)
        
        try: 
            myMS.split(outputms=outputvis, whichcol=datacolumn,
                       spw=spwStr, taql=taqlstr,
                       correlation=correlation)

        except Exception, instance:
            casalog.post( '*** Error ***' + str(instance), 'SEVERE' )
            return {}

        myMS.close()

    else:
        return spwStr


