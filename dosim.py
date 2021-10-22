from LDMX.Framework import ldmxcfg
process=ldmxcfg.Process("test")
process.maxEvents = 10
process.outputFiles=['sim.root']

from LDMX.SimCore import generators
gun=generators.gun('particle_gun')
gun.particle='pi-'
gun.direction=[0.,0.,1.]
gun.position=[0.,0.,-1.]
gun.energy=2.0

from LDMX.SimCore import simulator
simulation=simulator.simulator('test')
simulation.runNumber=1
simulation.generators=[gun]

# Note: Name is hard coded in ldmx-sw
simulation.setDetector('ldmx-hcal-prototype-v1.0')

from LDMX.Conditions.SimpleCSVTableProvider import SimpleCSVIntegerTableProvider, SimpleCSVDoubleTableProvider

HcalReconConditionsDummy=SimpleCSVDoubleTableProvider('HcalReconConditions',
                                                     ["ADC_PEDESTAL",
                                                      "ADC_GAIN",
                                                      "TOT_PEDESTAL",
                                                      "TOT_GAIN"])
HcalReconConditionsDummy.validForever('./DumbReconConditions.csv')

# This is what the hardcoded version looked like
# HcalReconConditionsHardcode=SimpleCSVDoubleTableProvider("HcalReconConditions",["ADC_PEDESTAL","ADC_GAIN","TOT_PEDESTAL","TOT_GAIN"])

# HcalReconConditionsHardcode.validForAllRows([
#     1. , #ADC_PEDESTAL - should match HgcrocEmulator
#     1.2, #ADC_GAIN - 4 ADCS per PE - maxADCRange/readoutPadCapacitance/1024
#     1 , #TOT_PEDESTAL - dummy value since TOT is not implemented
#     2.5, #TOT_GAIN - dummy value - conversion to estimated charge deposited in TOT mode
#     ])

# Only needed for sim
HcalHgcrocConditionsHardcode=SimpleCSVDoubleTableProvider("HcalHgcrocConditions", [
            "PEDESTAL",
            "MEAS_TIME",
            "PAD_CAPACITANCE",
            "TOT_MAX",
            "DRAIN_RATE",
            "GAIN",
            "READOUT_THRESHOLD",
            "TOA_THRESHOLD",
            "TOT_THRESHOLD"
        ])

HcalHgcrocConditionsHardcode.validForAllRows([
    1. , #PEDESTAL
    12.5, #MEAS_TIME - ns - clock_cycle/2 - defines the point in the BX where an in-time (time=0 in times vector) hit would arrive
    20., #PAD_CAPACITANCE - pF
    200., #TOT_MAX - ns - maximum time chip would be in TOT mode
    10240. / 200., #DRAIN_RATE - fC/ns - dummy value for now
    1.2, #GAIN - large ADC gain for now - conversion from ADC to mV
    1. + 4., #READOUT_THRESHOLD - 4 ADC counts above pedestal
    1.*1.2 + 1*5, #TOA_THRESHOLD - mV - 1 PE above pedestal ( 1 PE  - 5 mV conversion)
    10000., #TOT_THRESHOLD - mV - very large for now
    ])
from LDMX.Hcal import digi
import LDMX.Hcal.HcalGeometry
# from LDMX.Hcal import hcal_hardcoded_conditions

hcal_digis=digi.HcalDigiProducer()
hcal_recs=digi.HcalRecProducer()


process.sequence=[simulation, hcal_digis, hcal_recs]
