(Source target, Count nmaps, Integer iEl_Start, Integer iEl_Stop, Boolean doFastPoint)

#SSCH_SUM
# One of many general schedules to scan over source or field
#ESCH_SUM

#=======================================================================
#SSCH_DOC
# Schedule to do a simple scan of a 4h x 15 degree field at dec = [-50,- 65]
#
#                                                              ___  
#                               ______________________________|_  |
#                              |   __________________________ |_|_|
#                              |  |                           |  |
#                              |  |                           |  |
#                              |  |                           |  |
#                              |  |                           |  |
#                              |  |                           |  |
#                              |  |                           |  |
#                              |  |                           |  | 
#          ---------           |  |             x             |  |
#              |               |  |                           |  |
#              |               |  |                           |  |
#              |               |  |                           |  |
#                              |  |                           |  |
# elOff-dEl_dither*iEl_dither  |  |                           |  |
#                              |  |                           |  |
#              |               |  |                           |  |
#              |              _|_ |___________ ___ ___________|  |
#          ____|____         | |_|____________|_|_|______________|
#                            |___|            |___|                       
#
#                              |                |
#                              |<--- azOff ---->|
#                              |                |
#               
# 
# Each scan takes large steps DEl in elevation, so we dither the
# starting elevation offsets by dEl_dither = DEl / nEl_dither.  Choose
# nEl_dither so that your effective El sampling is half the size of one pixel
# on the sky, or .5 arcmin:
# 
#     nEl_dither = (elevation step) / .5 arcmin
# 
# Thus in this file, DEl = 8.97 arcmin, so nEl_dither = 18.  The size of
# each dither step is then given by
# 
#     dEl_dither = (elevationstep)/nEl_dither
# 
# At the beginning of each map, the telescope's elevation is offset (in
# positive elevation) by iEl_dither*dEl_dither, where iEl_dither is
# calculated as:
# 
#     iEl_dither = (iEl_Start + map_index) mod(nEl_dither)
# 
# iEl_Start is an input into the schedule file call and can be any
# number between 0 and nEl_dither-1, where nEl_dither is defined inside
# the schedule file.  map_index starts at 1 and is increased by 1 each
# time the full field is scanned.
#
# A example call to this schedule will look like:
#
#    scan_dec-57p5_15ddec_withCal_25May2014.sch(ra0hdec-57.5, 1, 0, 1, true)
#
#ESCH_DOC
#=======================================================================

#-----------------------------------------------------------------------
# import the file we always need
#-----------------------------------------------------------------------

import ~sptdaq/gcproot/control/sch/schedlib.sch

#=======================================================================
# Define an observation
#=======================================================================

group FieldObservation {
  Scan scanName,             # The name of the stepped az scan
  Integer nreps,             # The number of times to execute it
  PointingOffset az_offset,  # The fixed az offset for each scan,
                             #   given in diff_scan_maker output
  PointingOffset el_offset,  # The fixed el offset for each scan
  PointingOffset dEl_dither, # The size of El dither steps in deg
  Integer nEl_dither         # The number of El dither steps
}

FieldObservation fastScan = {daz_63p1-2p0ds-2p0dss-9p0ams, 109, -34.203134, -8.15, 0.00833333, 19}

#=======================================================================
# Slew to the next requested position and scan.
#=======================================================================

command offsetAndScan(Time ts, Features feat, FieldObservation obs) {

  #------------------------------------------------------------
  # Set the feature bit, but wait until the specified start 
  # time to start the scan
  #------------------------------------------------------------

  mark add, $feat
  until $acquired(mark)

  until $after($ts, utc)
  scan/add $obs.scanName, nreps=$obs.nreps
  until $acquired(scan)

  mark remove, $feat
  until $acquired(mark)

  #------------------------------------------------------------
  # And clear the RA and scan offsets before exiting
  #------------------------------------------------------------

  radec_offset ra=0
  until $acquired(source)

  zeroScanOffsets  
  until $acquired(source)
}

#=======================================================================
#  Command to do a single map of the target fieild
#=======================================================================

command scan_field_el57p5_2014(Source target, FieldObservation obs, Integer iEl_dither) {

  #-----------------------------------------------------------------------
  # Make sure that the telescope will not run into one of its az limits
  # in the middle of this schedule
  #-----------------------------------------------------------------------

  PointingOffset testAZ = 100.7 # max_az from scan + 2 hrs ob time * 15 deg/hr

  acquire_source($target)
  offset/add az=$obs.az_offset
  until $acquired(source)
  offset/add az=$testAZ
  until $acquired(source)
  offset az=0
  until $acquired(source)

  #-----------------------------------------------------------------------
  # Offset to the edge of the scan area for the current iEl_dither.
  #-----------------------------------------------------------------------

  PointingOffset elOff = $obs.dEl_dither * $iEl_dither
  elOff = $obs.el_offset + $elOff

  offset az=$obs.az_offset, el=$elOff
  until $acquired(source)

  log "In command scan_field_el57p5_2014 iEl_dither=", $iEl_dither 

  #------------------------------------------------------------
  # Initialize the field scan to start 10 seconds from now.
  # This is just to guarantee that we have time to get on-source 
  # with no offsets before the specified start time
  # and to let the telescope vibrations settle.
  #------------------------------------------------------------

  recordHkInTurnaround true  #turn on housekeeping in turnarounds

  Time ts = $time(utc) + 00:00:10
  offsetAndScan $ts, f0, $obs

  recordHkInTurnaround false
  halt
}

#=======================================================================
# Cleanup
#=======================================================================

command clean_up_schedule() {
  halt
  track current
  terminate("finished scan.sch")
  #calibrator_OFF
  offset az=0, el=0
  mark remove, f0
  until $acquired(mark)
  until $acquired(source)
  halt
}

#=======================================================================
# Start of the schedule file
#=======================================================================

#-----------------------------------------------------------------------
# always do at beginning of observation
#-----------------------------------------------------------------------

init_obs("starting scan.sch")

calibrator_ensure_filament_chopper_on
calibrator_6Hz
# set_up_radio_warm_2013_el55p0
set_up_radio_cold_2013_el55p0
housekeeping_on_off(15s)

#------------------------------------------------------------
# Cycle is: observe the calibrators, then one iteration of the scan,
#   followed by calibrator.
#------------------------------------------------------------

if ($doFastPoint) {
 fast_point RCW38, -1:15:00, az-2p2d-0p4ds-1dss
 fast_point Mat5a, -1.845, az-3p1d-0p55ds-1dss
}

#------------------------------------------------------------
# Iterate over the number of maps requested
#------------------------------------------------------------

do Count map_index=1,$nmaps,1 {
  do Integer iEl_dither=$iEl_Start,$iEl_Stop,1 {
    #----------------------------------------------------------
    # calculate the dither offset
    #----------------------------------------------------------

    if ($iEl_dither >= $fastScan.nEl_dither) {
      iEl_dither = $iEl_dither - $fastScan.nEl_dither
    }

    #----------------------------------------------------------
    # Run one full map of the observation field
    #----------------------------------------------------------
    
    do_cal_bot_mid_top $target, -$fastScan.el_offset, 1m
    scan_field_el57p5_2014 $target, $fastScan, $iEl_dither
    exec "/home/sptdaq/gcproot/control/scr/schedule_client.py C_T python /home/sptdaq/pywtl/sptpol/amydump.py"
    very_fast_point rcw38, -1:15:00, az-2p2d-0p4ds-1dss
    very_fast_point Mat5a, -1.845, az-3p1d-0p55ds-1dss
  }
  do_cal_bot_mid_top $target, -$fastScan.el_offset, 1m
}

cleanup {
  clean_up_schedule
}

