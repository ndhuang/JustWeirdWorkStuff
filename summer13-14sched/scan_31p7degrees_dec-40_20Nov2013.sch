(Source target, Count nmaps, Integer iEl_Start, Boolean doFastPoint)

#SSCH_SUM
# One of many general schedules to scan over source or field
#ESCH_SUM

#=======================================================================
#SSCH_DOC
# Schedule to do a simple scan of a 2h x 10 degree field centered at dec=-35
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
#              |              _|_ |_____________ ___ _________|  |
#          ____|____         | |_|______________|_|_|____________|
#                            |___|              |___|                       
#
#                              |                |
#                              |<--- azOff ---->|
#                              |    (lead)      |
#               
# 
# Each scan takes large steps DEl in elevation, so we dither the
# starting elevation offsets by dEl_dither = DEl / nEl_dither.  Choose
# nEl_dither so that your effective El sampling is half the size of one pixel
# on the sky, or .5 arcmin:
# 
#     nEl_dither = (elevation step) / .5 arcmin
# 
# Thus in this file, DEl = 10 arcmin, so nEl_dither = 20.  The size of
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
#    scan_31p7degrees_dec-40_20Nov2013.sch([source], 2, 0, true)
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

FieldObservation fastScan = {daz_31p7-0p60ds-2p0dss-10p0ams.scan, 68, -16.021003, 5.65, 0.00833333, 20}

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

command scan_field_el50_2013(Source target, FieldObservation obs, Integer iEl_dither) {

  #-----------------------------------------------------------------------
  # Make sure that the telescope will not run into one of its az limits
  # in the middle of this schedule
  #-----------------------------------------------------------------------

  PointingOffset testAZ = 16.036199 + 60.

  acquire_source($target)
  offset/add az=-$testAZ
  until $acquired(source)
  offset/add az=$testAZ
  until $acquired(source)

  #-----------------------------------------------------------------------
  # Offset to the edge of the scan area for the current iEl_dither.
  #-----------------------------------------------------------------------

  PointingOffset elOff = $obs.dEl_dither * $iEl_dither
  elOff = $obs.el_offset + $elOff

  offset az=$obs.az_offset, el=$elOff
  #offset/add el = $dEl_dither * $iEl_dither

  log "In command scan_field_el50_2013 iEl_dither=", $iEl_dither 

  #------------------------------------------------------------
  # Initialize the lead field scan to start 10 seconds now.
  # This is just to guarantee that we have time to get on-source 
  # with no offsets before the specified start time.
  #------------------------------------------------------------

  Time ts = $time(utc) + 00:00:10
  offsetAndScan $ts, f0, $obs

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
set_up_radio_warm_2013_el55p0

#------------------------------------------------------------
# Cycle is: observe the calibrators, then one iteration of the scan,
#   followed by calibrator.
#------------------------------------------------------------

if ($doFastPoint) {
 fast_point RCW38, -1.006, az-1p7d-0p4ds-1dss
 fast_point Mat5a, -1.496, az-2p4d-0p55ds-1dss
}

#------------------------------------------------------------
# Initialize the dither counter
#------------------------------------------------------------

Integer iEl_dither = $iEl_Start

#------------------------------------------------------------
# Iterate over the number of maps requested
#------------------------------------------------------------

do Count map_index=1,$nmaps,1 {

  #----------------------------------------------------------
  # calculate the dither offset
  #----------------------------------------------------------

  if ($iEl_dither >= $fastScan.nEl_dither) {
    iEl_dither = $iEl_dither - $fastScan.nEl_dither
  }

  #----------------------------------------------------------
  # Run one full map of the observation field
  #----------------------------------------------------------

  scan_field_el50_2013 $target, $fastScan, $iEl_dither
  very_fast_point RCW38, -1.006, az-1p7d-0p4ds-1dss
  very_fast_point Mat5a, -1.496, az-2p4d-0p55ds-1dss

  #----------------------------------------------------------
  # Update the dither iterator
  #----------------------------------------------------------

  iEl_dither = $iEl_dither + 1
}

cleanup {
  clean_up_schedule
}

