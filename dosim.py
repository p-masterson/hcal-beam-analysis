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


from LDMX.Hcal import digi
import LDMX.Hcal.HcalGeometry
from LDMX.Hcal import hcal_hardcoded_conditions

hcal_digis=digi.HcalDigiProducer()
hcal_recs=digi.HcalRecProducer()


process.sequence=[simulation, hcal_digis, hcal_recs]
