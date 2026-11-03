# OpenSees native FVD/BRB recorder check, illustrative kN-m-s profiles
set basedir [lindex $argv 0]
if {$basedir eq ""} {set basedir native_device_results}
file mkdir $basedir
set dt 0.002
set nsteps 1000
foreach name {FVD BRB} {
  wipe
  set dir [file join $basedir $name]
  file mkdir $dir
  model BasicBuilder -ndm 3 -ndf 6
  node 1 0.0 0.0 0.0
  node 2 1.0 0.0 0.0
  fix 1 1 1 1 1 1 1
  fix 2 0 1 1 1 1 1
  mass 2 1.0 0.0 0.0 0.0 0.0 0.0
  if {$name eq "FVD"} {
    uniaxialMaterial ViscousDamper 10 2000.0 20.0 0.3
    element twoNodeLink 20 1 2 -mat 10 -dir 1
    set amp 10.0
    recorder Element -file [file join $dir basicForce.out] -time -ele 20 basicForce
    recorder Element -file [file join $dir basicDisplacement.out] -time -ele 20 basicDisplacement
  } else {
    uniaxialMaterial Steel02 10 350000.0 200000000.0 0.01 20.0 0.925 0.15
    element corotTruss 20 1 2 0.001 10
    set amp 400.0
    recorder Element -file [file join $dir axialForce.out] -time -ele 20 axialForce
    recorder Element -file [file join $dir deformations.out] -time -ele 20 deformations
  }
  recorder Node -file [file join $dir u.out] -time -node 2 -dof 1 disp
  recorder Node -file [file join $dir v.out] -time -node 2 -dof 1 vel
  timeSeries Trig 100 0.0 2.0 1.0 -factor $amp
  pattern Plain 100 100 {
    load 2 1.0 0.0 0.0 0.0 0.0 0.0
  }
  constraints Plain
  numberer RCM
  system BandGeneral
  test NormDispIncr 1e-8 50 0
  algorithm Newton
  integrator Newmark 0.5 0.25
  analysis Transient
  set rc 0
  for {set i 0} {$i < $nsteps} {incr i} {
    set rc [analyze 1 $dt]
    if {$rc != 0} {break}
  }
  set f [open [file join $dir status.txt] w]
  puts $f "case=$name"
  puts $f "steps=[expr {$i+1}]"
  puts $f "time=[getTime]"
  puts $f "return_code=$rc"
  close $f
  if {$rc != 0} {puts "FAIL $name";exit 2}
  puts "COMPLETED_UNCALIBRATED $name"
}
wipe
