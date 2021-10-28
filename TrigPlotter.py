#!/usr/bin/python
# -*- coding: utf-8 -*-
#this is a simplified and enhanced trigger+hcal plotting program derived from Peter's from-scratch frankenpaste prototype plotter
# Plots include:
# TS:
# - TDC
# - ADC
# - Charge
# - ADC vs TDC
# - etc.
# HCal:
# - ADC value vs hcal channel
# - Number of hcal hits over threshold per channel

#naming standard: thisThing

# ***Example usage:***
# ldmx python TrigPlotter.py -i inputFile -p v12
# Note:  inputFile should not include the suffix .root.

# NOTE:  The DumbReconConditions.csv file containing pedestal values is only a template!  This file will need to be replaced 
#        eventually, and the relevant HistogramFiller code checked.


#this program takes many things that end with ".root" and outputs simulation and reconstruction plots into the folder "plots"
#the process name in the config file should be "process", but can be specified in command line arguments 
#now available on github
import inspect
from numpy import *
import ROOT as r
import pdb
import copy
from array import array
from ROOT import gSystem
from optparse import OptionParser
from TranslateHcalID import HcalDigiID, bar_to_pos
import csv

gSystem.Load("libFramework.so") #this library is vital for it to run. It might be old though?
# rootColors=[1,2,4,28,7] #a presumably color-blind friendly color palette
# rootColors=[28,2,4] #a three-compare color-blind friendly color palette
rootColors=[4,2] #a -v+ comparison
# rootColors=[1,2,3,4,5,6,7,8,9] #Colorblind unfriendly for comparing many things
rootMarkers=[4,26,32] #this is getting out of hand
r.gROOT.SetBatch(1); #makes root not try to display plots in a new window

#we dint wantrecs, we want digis
#for adcs, there are 5 times on the x axis
#adcs analog to digital converter

def ADCtoQ(ADC):
  if ADC <= 0: return -16;
  if ADC >= 255: return 350000;
  nbins_= [0, 16, 36, 57, 64];
  sense_ = [3.1,   6.2,   12.4,  24.8, 24.8, 49.6, 99.2, 198.4, 198.4, 396.8, 793.6, 1587, 1587, 3174, 6349, 12700];
  edges_ = [-16,   34,    158,    419,    517,   915,
                      1910,  3990,  4780,   7960,   15900, 32600,
                      38900, 64300, 128000, 261000, 350000];
  gain_ = 1                    
  rr = ADC / 64;  # range
  v1 = ADC % 64;  # temp. var
  ss = 0;         # sub range

  for i in range (1,4):# to get the subrange
    if v1 > nbins_[i]: ss += 1;
  
  cc = 64 * rr + nbins_[ss];
  temp = edges_[4 * rr + ss] + (v1 - nbins_[ss]) * sense_[4 * rr + ss] +  sense_[4 * rr + ss] / 2;
  return temp / gain_;

def unabbreviate(str):
    if str == "digiRecT": return "TDC"
    elif str == "digiRecA": return "ADC"
    elif str == "digiRecJ": return "Charge"
    elif str == "digiRecA(T)": return "ADC (y) vs TDC (x)"
    elif str == "digiRecA(ts)": return "ADC (y) vs time sample (x)"
    elif str == "digiRecT(ts)": return "TDC (y) vs time sample (x)"
    elif str == "digiH_adc": return "ADC (y) vs bar+(end*13) (x)"
    elif str == "digiH_thresh": return "Hits over threshold"
    else: return str

def histogramFiller(hist, plotVar, allData,  channel=0, collection="trigScintQIEDigisUp_",process= "process", hcalThresholds = None):

    if plotVar == 'digiRecT':
        for entry in allData: 
            for ih,h in enumerate(getattr(entry, collection+process)):
                if h.getChanID()== channel:
                    for time in range(0,5):
                        hist.Fill(h.getTDC()[time])     
        
    elif plotVar == 'digiRecA':
        for entry in allData: 
            for ih,h in enumerate(getattr(entry, collection+process)):
                if h.getChanID()== channel:
                    for time in range(0,5):
                        hist.Fill(h.getADC()[time]) 

    elif plotVar == 'digiRecA(T)':
        for entry in allData: 
            for ih,h in enumerate(getattr(entry, collection+process)):
                if h.getChanID()== channel:
                    for time in range(0,5):
                        hist.Fill(h.getTDC()[time],h.getADC()[time]) 

    elif plotVar == 'digiRecT(ts)':
        for entry in allData: 
            for ih,h in enumerate(getattr(entry, collection+process)):
                if h.getChanID()== channel:
                    for time in range(0,5):
                        if h.getTDC()[time]<51: hist.Fill(time,h.getTDC()[time])
                        
                        
    elif plotVar == 'digiRecA(ts)':
        for entry in allData: 
            for ih,h in enumerate(getattr(entry, collection+process)):
                if h.getChanID()== channel:
                    for time in range(0,5):
                        hist.Fill(time,h.getADC()[time])
                        
    elif plotVar == 'digiRecJ':
        for entry in allData: 
            for ih,h in enumerate(getattr(entry, collection+process)):
                if h.getChanID()== channel:
                    integral = 0
                    for time in range(0,5):
                        integral+= ADCtoQ(h.getADC()[time])
                    hist.Fill(integral) 

    elif plotVar == 'digiH_adc':
        for entry in allData:
            digis = getattr(entry, collection+process)
            for i in range(digis.getNumDigis()):
                d = digis.getDigi(i)
                chID = d.id()
                digiID = HcalDigiID().from_ID(chID)
                if digiID.layer() == channel:
                    hist.Fill(digiID.bar() + 0.5*digiID.end(), d.soi().adc_t())

    elif plotVar == 'digiH_thresh':
        for entry in allData:
            digis = getattr(entry, collection+process)
            for i in range(digis.getNumDigis()):
                d = digis.getDigi(i)
                chID = d.id()
                digiID = HcalDigiID().from_ID(chID)
                #print("chiD:", chID)
                #print(hcalThresholds.keys())
                if d.soi().adc_t() >  hcalThresholds[chID][0] + 1.0*hcalThresholds[chID][1] \
                  and digiID.layer() == channel:
                    hist.Fill(digiID.bar() + 0.5*digiID.end())

    return hist                



def main(options):       
    #In each line, just specify in the form (('digiRecT','fileName'),),   

    fileName = options.input_file
    plotGroupsT = [
        (('digiRecT',fileName),),
        (('digiRecA',fileName),),
        (('digiRecJ',fileName),),
        (('digiRecA(T)',fileName),),
        (('digiRecT(ts)',fileName),),
        (('digiRecA(ts)',fileName),),
        ]
    plotGroupsH = [
        # New hcal plots
        (('digiH_adc', fileName),),
        (('digiH_thresh', fileName),),
        ]         


    plotDictT = {
        'trigRecT' :{'xaxis' : 'Time [ns]', 'yaxis' : 'Counts', 'binning' : {'nBins':20, 'min':0, 'max':10}, 'dimension' : 1}, #machine has a resolution of 0.5 ns apparently
        'trigRecE' :{'xaxis' : 'Energy [MeV]', 'yaxis' : 'Counts', 'binning' : {'nBins':40, 'min':0, 'max':2}, 'dimension' : 1}, #I have no idea what the machine resolution is
        'digiRecT' :{'xaxis' : 'TDC value', 'yaxis' : 'Counts', 'binning' : {'nBins':64, 'min':0, 'max':64}, 'dimension' : 1}, #
        'digiRecA' :{'xaxis' : 'ADC value', 'yaxis' : 'Counts', 'binning' : {'nBins':256, 'min':0, 'max':256}, 'dimension' : 1}, #
        'digiRecJ' :{'xaxis' : 'Charge [fC?]', 'yaxis' : 'Counts', 'binning' : {'nBins':100, 'min':0, 'max':60000}, 'dimension' : 1}, #
        'digiRecA(T)' :{'xaxis' : 'TDC', 'yaxis' : 'ADC', 'dimension' : 2,
                        'binningX' : {'nBins':100, 'min':0, 'max':100},  
                        'binningY' : {'nBins':200, 'min':0, 'max':200}}, 
        'digiRecT(ts)' :{'xaxis' : 'time sample', 'yaxis' : 'TDC', 'dimension' : 2,
                        'binningX' : {'nBins':5, 'min':0, 'max':5},  
                        'binningY' : {'nBins':64, 'min':0, 'max':64}},           
        'digiRecA(ts)' :{'xaxis' : 'time sample', 'yaxis' : 'ADC', 'dimension' : 2,
                        'binningX' : {'nBins':5, 'min':0, 'max':5},  
                        'binningY' : {'nBins':200, 'min':0, 'max':200}},                              
    }

    plotDictH = {
        # For Hcal:
        'digiH_adc'    :{'xaxis' : 'Bar number', 'yaxis' : 'ADC', 'dimension' : 2,
                        'binningX' : {'nBins':24, 'min':0, 'max':12},
                        'binningY' : {'nBins':100, 'min':0, 'max':100}},
        'digiH_thresh' :{'xaxis' : 'Bar number', 'yaxis' : 'Hits over threshold', 'dimension' : 1,
                        'binning' : {'nBins':24, 'min':0, 'max':12}},
    }    

    # Read in csv file of thresholds for hcal over-threshold plots
    thresholds = {}
    with open("DumbReconConditions.csv") as csvfile:
        freader = csv.reader(csvfile, delimiter=',')
        rownum = 0
        for row in freader:
            #print(row)
            if rownum < 2:
                rownum += 1
                continue
            # (adc_pedestal, adc_gain) 
            #print("ADDING")
            thresholds[long(row[1])] = (float(row[2]), float(row[3]))


    for section in ['HCal']:
        if section == 'TS':
            channelRange = (1, 13)  # Main reason we need to do this:  TS and HCal use different channel/section divisions
            plotGroups = plotGroupsT
            plotDict = plotDictT
            collection = options.tcollection
            process = options.process
            channel_or_layer = 'channel'
        elif section == 'HCal':
            channelRange = (1, 20)  # For each section
            plotGroups = plotGroupsH
            plotDict = plotDictH
            collection = options.hcollection
            process = options.process
            channel_or_layer = 'layer'
        print("plotgroups is ", plotGroups)
    
        for channel in range(channelRange[0], channelRange[1]):  #(1,13):
            for plotNumber in range(len(plotGroups)):
                canvas = r.TCanvas( 'c1', 'Histogram Drawing Options',1000,1000 )
                pad = r.TPad( 'pad', 'The pad with the histogram', 0,0,1,1 )
                pad.Draw()
                pad.cd()
                pad.SetGridx()
                pad.SetGridy()
                # pad.SetLogy()  
                pad.GetFrame().SetFillColor( 18 )
                
                r.gStyle.SetOptStat("n");
                
    
                pad.SetRightMargin(0.1);
                # pad.SetLeftMargin(0);
                # pad.SetTopMargin(0);
                
                lines=[]
                # legend = r.TLegend(0.7,0.95,1,1);
                # legend.SetTextSize(0.03)
                
                # inFile = r.TFile(fileName+".root","READ")  
                # allData = inFile.Get("LDMX_Events")
                
                for j in plotGroups[plotNumber]: #creates a plot for each variable you are going to plot
                    plotVar = var  = j[0]
                    fileName = j[1]           
    
                    #tried to make this more efficient by only running it once, but such methods are doomed to fail            
                    inFile = r.TFile(fileName+".root","READ")  
                    allData = inFile.Get("LDMX_Events")
                    # allData.Print("toponly")  #this command is godlike for learning things          
                    
                    
                    if plotDict[j[0]]['dimension'] == 1:
                        histName = unabbreviate(plotVar)+" channel "+str(channel)       
                        histTitle = ""       
                        binning = plotDict[j[0]]['binning']                
                        hist = r.TH1F(histName,histTitle,binning['nBins'],binning['min'],binning['max']) #name, title, nbins, start, finish          
    
                        
                    elif plotDict[j[0]]['dimension'] == 2:
                        if section == "TS":
                            histName = "Channel "+str(channel)                     
                        elif section == "HCal":
                            histName = "Bar "+str(channel)
                        histTitle = ""                     
                        binningX = plotDict[j[0]]['binningX']
                        binningY = plotDict[j[0]]['binningY']                               
                        # hist = r.TH2F(plotVar,histTitle,binningX['nBins'],binningX['min'],binningX['max'] #name, title, nbins, start, finish
                        # ,binningY['nBins'],binningY['min'],binningY['max']) #nbins, start, finish                    
    
                        hist = r.TProfile(histName,histTitle,binningX['nBins'],binningX['min'],binningX['max'] #name, title, nbins, start, finish
                                          ,binningY['min'],binningY['max']) #nbins, start, finish          
    
                        hist.GetXaxis().SetNdivisions(binningX['nBins'])                                      
                        pad.SetRightMargin(0.12);
                        pad.SetLeftMargin(0.14);
    
    
                    hist.SetYTitle(plotDict[plotVar]['yaxis'])
                    hist.SetXTitle(plotDict[plotVar]['xaxis'])
                    
                    # hist.SetFillStyle(0);
                    hist.SetMarkerStyle(8) 
                    hist.SetMarkerColor(4)
                    # hist.SetMarkerSize(3)
                    hist.SetLineColor(rootColors[len(lines)])

                    if section == "HCal":
                        for l in range(0, 26, 2):
                            hist.GetXaxis().ChangeLabel(l, -1,-1,-1,-1,-1, " ")
                            
                    # process = fileName        
                    #process = "process"       
                    hist = histogramFiller(hist, plotVar, allData, channel, collection=collection, process=process, hcalThresholds=thresholds) 

    
                    
                    # depositionAnalyser(plotVar, allData, fileName)
    
                    if plotDict[j[0]]['dimension'] == 1:
                        hist.SetMinimum(0.5)
                        pad.SetLogy()
                        
                        # try: 
                            # hist.Scale(1./hist.Integral()) #normalises
                            # hist.SetYTitle("Normalised entries")
                            # hist.SetMaximum(1)                    
                        # except: print("didnt normalise")
                    
                    
                    lines.append(copy.deepcopy(hist))          
    
                    # hist.SetOption("")
                    
                    if plotDict[j[0]]['dimension'] == 1:
                        # lines[-1].Draw("HIST SAME")
                        lines[-1].Draw("SAME E")
                    if plotDict[j[0]]['dimension'] == 2:
                        lines[-1].Draw("COLZ")    
    
                    
                    # legend.AddEntry(lines[-1],j[0]+" "+j[1],"f");
    
    
                
                # if plotDict[j[0]]['dimension'] == 1: legend.Draw();
    
               
                label = r.TLatex()
                label.SetTextFont(42)
                label.SetTextSize(0.03)
                label.SetNDC()
                # label.DrawLatex(0,  0.97, "Default: 0.5 GeV e-")
    
                canvas.SaveAs("plots/{}-{}-{}.png".format(plotVar, channel_or_layer, channel))
                # canvas.SaveAs("plots/Digi.png")
    
                canvas.Close() #memory leak killer

if __name__=="__main__":
    parser = OptionParser()	
    parser.add_option('-i','--input', dest='input_file', default = "sim.root", help="The input file to generate plots from")
    parser.add_option('-c','--collection', dest='tcollection', default = "trigScintQIEDigisUp_" ,help='The name of the collection under which the hcal digis are stored')
    parser.add_option('-p','--process', dest='process', default = "process" ,help='The name of the process under which the trigger digis are stored')
    parser.add_option('-o','--hcollection', dest='hcollection', default="HcalDigis_", help='The name of the collection under which the hcal digis are stored')
    options = parser.parse_args()[0]
    main(options)


