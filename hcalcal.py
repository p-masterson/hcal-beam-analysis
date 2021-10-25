import sys
import ROOT
from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText, TStyle, TTree, TH1F, TH1D, TH2D, TLegend, TGraph, TGraphErrors
from ROOT import gROOT, gStyle, gSystem, gPad
from TranslateHcalID import HcalDigiID, bar_to_pos, HcalID

gSystem.Load("libFramework.so")

inputFile=TFile(sys.argv[1], "read")
tree=inputFile.Get("LDMX_Events")

f = ROOT.TFile('h_adc.root','recreate')

h = {}
id = []

pedestals = ROOT.TH1F('pedestals', 'pedestals', 384, 0, 384)
p = {}

section = 0
layers = [i for i in range(1,20)]

DigiIDs=[]

for e in tree :

    for d in e.EIDHcalDigis_unpack :

        if d.id() not in h :

           h[d.id()] = ROOT.TH1F(f'adc_eid_{d.id()}', f'ADC EID {d.id()}',1024,0,1024)
           id.append(d.id())
           print(d.id())

        h[d.id()].Fill(d.soi().adc_t())

for i in range(len(id)):
    pedestals.SetBinContent(i+1, h[id[i]].GetMean())
    p[id[i]] = h[id[i]].GetMean() #Need to fit mean

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

with open('HcalReconConditions.csv', 'w') as file:
    file.write("# HcalDigiID Format: (section: layer: bar: end)\n")
    file.write("HcalDigiID, DetID, ADC_PEDESTAL, ADC_GAIN, TOT_PEDESTAL, TOT_GAIN\n")
    i = 0
    for DigiID in DigiIDs:
        HcalDigi =HcalDigiID().from_ID(DigiID)
        # Can't have commas, would break the parser
        digiStr=str(HcalDigi).replace(',',':')
        #eid = eid_map[HcalDigi] Einar is making this map
        pedest = p[eid] #Maybe fit function later
        file.write("{}, {}, {}, 1.2, 1, 2.5\n".format(digiStr, DigiID, pedest))
        i = i + 1

f.Write()
f.Close()
