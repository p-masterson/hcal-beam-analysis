import sys
tmpargv = sys.argv
sys.argv = []
import getopt
import ROOT
from ROOT import gROOT, TFile, TTree, TChain, gDirectory, TLine, gStyle, TCanvas, TLegend, TH1F, TH2F
sys.argv = tmpargv

#List arguments
def print_usage():
    print("\nUsage: {0} <output file base name> <input Data text file>".format(sys.argv[0]))
    print('\t-h: this help message')
    print

options, remainder = getopt.gnu_getopt(sys.argv[1:], 'h')

# Parse the command line arguments
for opt, arg in options:
		if opt=='-h':
			print_usage()
			sys.exit(0)

def openPDF(outfile, c):
	c.Print(outfile+".pdf[")

def closePDF(outfile, c):
	c.Print(outfile+".pdf]")

gStyle.SetOptStat(0)
c = TCanvas("c","c",800,600)

outfile = remainder[0]
infile = remainder[1]

nChan = 192
calib_index = 20
pedestals = TH2F("pedestals", "pedestals", nChan, 0, nChan, 100, 0, 150)

word = []
word_val = []
with open(infile, mode='r') as file:
    for line in file:
        hex_string = "0x"+line.rstrip()
        val = int(hex_string, 16)
        word.append(line.rstrip())
        word_val.append(val)

channels = []
chan = 0
for i in range(len(word)):
    if(word[i] == "ffffffff"):
        for j in range(i+2, i+35):
            if(j == i + calib_index):
                continue
            adc = word_val[j]
            if(chan >= 96 and chan <= 127): #Suspect this link is factor 2 too high
                adc = adc / 2
            pedestals.Fill(chan, adc)
            chan = chan + 1
            if(chan >= nChan):
                chan = 0

openPDF(outfile, c)

pedestals.Draw("COLZ")
pedestals.SetTitle("")
pedestals.GetXaxis().SetTitle("Channel")
pedestals.GetYaxis().SetTitle("ADC Counts")
c.Print(outfile+".pdf")

closePDF(outfile, c)
