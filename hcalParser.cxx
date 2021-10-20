//parser for LDMX Hcal raw files
//
//compile with 
//g++ `root-config --cflags --glibs` hcalParser.cxx -o hcalParser


#include <iostream>
#include <fstream>
#include <bitset>
#include <map>
#include <TFile.h> 
#include <TH1.h> 
#include <TH2.h> 

typedef std::map<int,TH1I*> adcHistMap;

void readFile(const std::string &inFileName, adcHistMap &hMap, TH2I *hFull)
{
  std::ifstream f;
  f.open(inFileName.c_str(), std::ios::in | std::ios::binary);

  int n=0;
  int i=-5;
  int line;
  std::bitset<40> readoutMap;
  while(true)
  {
    ++i;
    f.read((char*)&line, sizeof(line));
    if(f.gcount()<4) break;

    if(i<0)
    {
      //TODO: this is only a guess, but is it correct?
      if(line==0x11111111) i=-8;
    }

    if(i==0) 
    {
      //this line also encodes the link number, which is not used at the moment 
      std::bitset<32> readoutMapTmp(line);
      for(int j=0; j<8; ++j) readoutMap[j+32]=readoutMapTmp[j];
    }
    if(i==1) 
    {
      std::bitset<32> readoutMapTmp(line);
      for(int j=0; j<32; ++j) readoutMap[j]=readoutMapTmp[j];
    }

    if(i==2)
    {
      //values at i==2 not used currently
      for(int j=1; j<39; ++j)   //actually 40 according to the document, but this doesn't agree with the file
      {
        if(readoutMap[j]==1)
        {
          ++i;
          f.read((char*)&line, sizeof(line));
          if(j==19 || j==20 || j==39) continue;
          if(f.gcount()<4) break;
          int adc=line & 0x3ff;

          int channel=(j-1)+36*n;
          if(j>20) channel=(j-3)+36*n;
          adcHistMap::iterator h=hMap.find(channel);
          if(h==hMap.end())
          {
            hMap[channel]=new TH1I(Form("Pedestal%i",channel),Form("Pedestal%i;ADC;",channel),200,0,200);
            h=hMap.find(channel);
          }
          h->second->Fill(adc);
          hFull->Fill(channel,adc);
        }
      }
      i=-1;
      readoutMap.reset();
      ++n;
      if(n==6) {n=0; i=-10;}   //FIXME the max number of links (n=6) is currently hard coded
      if(f.gcount()<4) break;
    }
  }

  f.close();
}

int main(int argc, char *argv[])
{
  if(argc!=3)
  {
    std::cout<<"Usage "<<std::endl;
    std::cout<<argv[0]<<" infile.raw outfile.root"<<std::endl;
    return -1;
  }
  std::string inFileName=argv[1];
  std::string outFileName=argv[2];

  TFile *file = new TFile(outFileName.c_str(),"recreate");
  adcHistMap adcHists;
  TH2I *adcHistFull = new TH2I("Pedestals","Pedestals;channel;ADC",220,0,220,200,0,200);

  readFile(inFileName, adcHists, adcHistFull);

  adcHistFull->Write();
  for(adcHistMap::iterator h=adcHists.begin(); h!=adcHists.end(); ++h) h->second->Write();

  file->Close();

  return 0;
}
