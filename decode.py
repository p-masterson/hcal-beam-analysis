from LDMX.Framework import ldmxcfg
process=ldmxcfg.Process("test")
process.maxEvents=1
process.outputFiles=['debug.root']

from LDMX.Hcal import hgcrocFormat
from LDMX.Hcal import DetectorMap

from TranslateHcalID import HcalDigiID, bar_to_pos, HcalID

from LDMX.Conditions.SimpleCSVTableProvider import SimpleCSVDoubleTableProvider

HcalReconConditionsDummy=SimpleCSVDoubleTableProvider('HcalReconConditions',
                                                     ["ADC_PEDESTAL",
                                                      "ADC_GAIN",
                                                      "TOT_PEDESTAL",
                                                      "TOT_GAIN"])
HcalReconConditionsDummy.validForever('./DumbReconConditions.csv')

from LDMX.Hcal import HcalGeometry
from LDMX.Packing import rawio

reader=rawio.SingleSubsystemUnpacker(raw_file='run208.raw', output_name='HcalRaw',
                                     num_words_per_event=1026, bytes_per_word=4,
                                     detector_name='ldmx-hcal-prototype-v1.0')
det_map=DetectorMap.HcalDetectorMap('${LDMX_BASE}/ldmx-sw/Hcal/data/testbeam_connections.csv')
# Note: I'm calling the output HcalDigis instead of EIDHcalDigis because we are
# making the translation from electronics IDs to DigiIDs


hcal_decoder=hgcrocFormat.HcalRawDecoder(output_name='HcalDigis',
                                         input_name='HcalRaw',
                                         input_file='run208.raw',
                                         translate_eid=True) # this means use
                                                             # the
                                                             # HcalDetectorMap


from LDMX.Hcal import digi
hcal_recs=digi.HcalRecProducer()
hcal_recs.digiCollName='HcalDigis'
process.sequence=[reader,hcal_decoder,hcal_recs]
