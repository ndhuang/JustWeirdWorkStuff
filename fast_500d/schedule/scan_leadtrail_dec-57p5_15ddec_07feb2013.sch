(Source src, Count nmaps, Integer iElStart, Integer iElStop, Boolean doFastPoint)

#=======================================================================
# Schedule to do a lead/trail scan of a 60 x 15 degree (on the sky)
# field at dec = [-50, -65].
#
#                            ___                 ___
#                 __________|___|_______________|_  |
#                |   _______|___|______________ |_|_|
#                |  |            |             |  |
#                |  |            |             |  |
#                |  |            |             |  |
#                |  |            |             |  |
#                |  |            |             |  |
#                |  |            |             |  |
#                |  |            |             |  |
#  ---------     |  |            x             |  |
#      |         |  |            |             |  |
#      |         |  |            |             |  |
#                |  |            |             |  |
# elOff -        |  |            |             |  |
# dEl_dither*iEl |  |            |             |  |
#      |         |  |            |             |  |
#      |        _|_ |____________| ___ ________|  |
#  ____|____   | |_|______________|___|___________|
#              |___|              |___|
#
#                |            -->|<--- azOff
#                |               |    (trail)
#                |               |
#                |<--- azOff --->|
#                |    (lead)     |
#
#
#
# Each scan takes large steps DEl in elevation, so we dither the
# starting elevation offsets by dEl_dither = DEl/nel_dither, so that 
# after nel_dither scans, we have complete coverage of the field with
# effective el step of dEl_dither.
#
# Indices for the elevation dither start at 0 (ie, this offset places
# the top edge of the array at the bottom edge of the target field).
#
# Each lead/trail pair takes approximately 4 hours, so we do one pair
# between calibrations.  iElStart and iElStop refer to the starting 
# and stoping index. A call to this schedule like:
#
#      scan_leadtrail_dec-57p5_15ddec_07feb2013.sch(ra0hdec-57.5, 2, 12, 15, false)
#
# would therefore do 2 complete repetitions of:
#
#                iEl = 12
#                iEl = 13
#                iEl = 14
#                iEl = 15
#
# The number of possible dither steps in this scan file is :
# 
#    nEl_dither = 18
#
# Thus on can call this schedule for iElStart and iElStop between 0 and 17
# 
#=======================================================================

#------------------------------------------------------------
# import the file we always need
#------------------------------------------------------------

import ~sptdaq/gcproot/control/sch/schedlib.sch

#=======================================================================
# Define an observation
#=======================================================================

group LeadTrailObs {
  Scan scanName,             # The name of the stepped az scan
  Integer nreps,             # The number of times to execute it
  PointingOffset azScanOff,  # The fixed az offset for each scan
  PointingOffset elScanOff,  # The fixed el offset for each scan
  PointingOffset dEl_dither, # The el subsampling interval
  Time dtTrail               # The time it takes the sky to rotate
}                            #  by the separation of the lead/trail fields

LeadTrailObs fastScan = {daz-33p43-1p09ds-2dss-9p2ams, 106, -32.1485, -8.15, 0.00854298, 01:59:40.3413}

#=======================================================================
# Turn housekeeping on briefly, then turn off
#=======================================================================

command hkOnOff() {

  log "Turning on housekeeping for 1 minute"
  recordHousekeepingData true
  until $acquired(script)
  until $elapsed > 1m
  recordHousekeepingData false
  until $acquired(script)
  log "Turned housekeeping off"
}

#=======================================================================
# Slew to the next requested position, and wait until the specified
# start time to scan
#=======================================================================

command offsetAndScan(Time ts, Time dtOff, Features feat, LeadTrailObs obs) {

  #------------------------------------------------------------
  # Slew to an RA, offset by the specified interval 
  # (timeOffset), from the nominal pointing position, and wait 
  # until the telescope has acquired the new position
  #------------------------------------------------------------

  radec_offset dt=$dtOff
  until $acquired(source)

  zeroScanOffsets  
  until $acquired(source)

  #------------------------------------------------------------
  # Now set the feature bit, but wait until the specified start 
  # time to start the scan
  #------------------------------------------------------------

  mark add, $feat
  until $acquired(mark)

  until $after($ts, utc)
  scan/add  $obs.scanName, nreps=$obs.nreps
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
#  Command to do a single lead/trail map of the target field
#=======================================================================

command scan_field_el62p5_2013(Source target, LeadTrailObs obs, Integer iEl) {

  # Log the dither step of this observation
  String log_msg = "Start scan_field_el62p5_2013 for dither step " + $intToString($iEl)
  log $log_msg

  acquire_source($target)

  offset/add az=-70
  until $acquired(source)
  offset/add az=70
  until $acquired(source)

  #------------------------------------------------------------
  # Offset to the edge of the scan area for the current (iEl)
  # elevation sub-sampling
  #------------------------------------------------------------

  PointingOffset elOff = $obs.elScanOff
  PointingOffset dEl_dither   = $obs.dEl_dither * $iEl

  elOff = $elOff + $dEl_dither

  offset az=$obs.azScanOff, el=$elOff
  
  #------------------------------------------------------------
  # Initialize the lead field scan to start 10 seconds from 
  # now.  Although we do not need to slew for the lead field, 
  # this is just to guarantee that we have time to get on-source 
  # with no offsets before the specified start time.
  #------------------------------------------------------------

  Time ts = $time(utc) + 00:00:30
  offsetAndScan $ts, 00:00:00, f0, $obs
 
  #------------------------------------------------------------
  # Now increment the start time by dt to get on the trail field.  
  # This will be the start time for the trail field scan.  
  # Note that I set an 
  # additional feature bit (not to my knowledge used for any 
  # other purpose) for the 'trail' field, for convenience of
  # subsequent analysis.
  #------------------------------------------------------------

  ts = $ts + $obs.dtTrail
  offsetAndScan $ts, $obs.dtTrail, f0+f10, $obs

  # Log the dither step of this observation
  log_msg = "Finish scan_field_el62p5_2013 for dither step " + $intToString($iEl)
  log $log_msg

  halt
}

#=======================================================================
# Cleanup
#=======================================================================

command clean_up_schedule() {
  halt
  track current
  terminate("finished scan_leadtrail_dec-57p5_15ddec_07feb2013.sch")
#  calibrator_OFF
  offset az=0, el=0
  mark remove, f0+f10
  until $acquired(mark)
  until $acquired(source)
  halt
}

#=======================================================================
# Start of the schedule file
#=======================================================================

#------------------------------------------------------------
# Always do at beginning of observation
#------------------------------------------------------------

init_obs("starting scan_leadtrail_dec-57p5_15ddec_07feb2013.sch")

calibrator_ensure_filament_chopper_on
calibrator_6Hz
#set_up_radio_warm_2011_el55p0
set_up_radio_cold_2013_el55p0

#------------------------------------------------------------
# Cycle is: observe calibrators, then one iteration of
# lead/trail, since this takes about 2*120 minutes, for a total
# of 4h 20m for two iterations
#------------------------------------------------------------

if ($doFastPoint) {
 fast_point RCW38, -1:15:00, az-2p2d-0p4ds-1dss
 fast_point Mat5a, -1.845, az-3p1d-0p55ds-1dss
}

#------------------------------------------------------------
# Iterate over the number of maps requested
#------------------------------------------------------------

do Count rep_index=1,$nmaps,1 {

  do Integer iEl=$iElStart,$iElStop,1 {

    hkOnOff
    scan_field_el62p5_2013 $src, $fastScan, $iEl
    hkOnOff

    very_fast_point rcw38, -1:15:00, az-2p2d-0p4ds-1dss
    very_fast_point Mat5a, -1.845, az-3p1d-0p55ds-1dss

  }

}

cleanup {
  clean_up_schedule
}

