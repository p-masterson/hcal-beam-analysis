
import ROOT
from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText, TStyle, TTree, TH1D, TH2D, TLegend, TGraph, TGraphErrors
from ROOT import gROOT, gStyle, gSystem, gPad
gSystem.Load("libFramework.so")
from TranslateHcalID import HcalDigiID, bar_to_pos

inputFile=TFile("sim.root", "READ")  # debug.root
eventTree=inputFile.Get("LDMX_Events")



for event in eventTree:
    digis = event.HcalDigis_test
    print(digis.getNumSamplesPerDigi())
