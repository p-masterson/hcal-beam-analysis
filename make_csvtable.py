
# This generates a CSV file with all the raw DetectorID's and the
# ADC_PEDESTAL/ADC_GAIN/TOT_PEDESTAL/TOT_GAIN values that were hardcoded in
# ldmx_hcal_hardcoded_conditions


from TranslateHcalID import HcalDigiID, bar_to_pos, HcalID

section = 0
layers = [i for i in range(1,20)]

DigiIDs=[]

for layer in layers:
    if layer < 10:
        max_bar=8
    else:
        max_bar=12
    for bar in range(0,max_bar):
        DigiID_pos = HcalDigiID().from_vars(section, layer, bar, 0)
        DigiID_neg = HcalDigiID().from_vars(section, layer, bar, 1)
        DigiIDs.append(DigiID_pos.ID)
        DigiIDs.append(DigiID_neg.ID)

with open('DumbReconConditions.csv', 'w') as file:
    file.write("# HcalDigiID Format: (section: layer: bar: end)\n")
    file.write("HcalDigiID, DetID, ADC_PEDESTAL, ADC_GAIN, TOT_PEDESTAL, TOT_GAIN\n")
    for DigiID in DigiIDs:
        HcalDigi =HcalDigiID().from_ID(DigiID)
        # Can't have commas, would break the parser
        digiStr=str(HcalDigi).replace(',',':')
        file.write("{}, {}, 1, 1.2, 1, 2.5\n".format(digiStr, DigiID))


