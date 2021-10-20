from LDMX.Framework import ldmxcfg
process=ldmxcfg.Process("test")
process.maxEvents=1
process.outputFiles=['debug.root']

from LDMX.Hcal import hgcrocFormat
from LDMX.Hcal import DetectorMap

hcal_det_map = DetectorMap.HcalDetectorMap('${LDMX_BASE}/hcal/data/testbeam_connections.csv')
hcal_decoder=hgcrocFormat.HcalRawDecoder('HcalDigis',
                                         input_file='sample_run206.raw',
                                         translate_eid=True) # this means use
                                                             # the
                                                             # HcalDetectorMap

process.sequence=[hcal_decoder]
