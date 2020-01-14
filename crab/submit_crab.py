from PhysicsTools.NanoAODTools.postprocessing.samples.samples import *
import os

def cfg_writer(label, dataset, outdir):
    f = open("crab_cfg.py", "w")
    f.write("from WMCore.Configuration import Configuration\n")
    f.write("from CRABClient.UserUtilities import config, getUsernameFromSiteDB\n")
    f.write("\nconfig = Configuration()\n")
    f.write("config.section_('General')\n")
    f.write("config.General.requestName = '"+label+"'\n")
    f.write("config.General.transferLogs=True\n")
    f.write("config.section_('JobType')\n")
    f.write("config.JobType.pluginName = 'Analysis'\n")
    f.write("config.JobType.psetName = 'PSet.py'\n")
    f.write("config.JobType.scriptExe = 'crab_script.sh'\n")
    f.write("config.JobType.inputFiles = ['crab_script_prova.py','../scripts/haddnano.py']\n") #hadd nano will not be needed once nano tools are in cmssw
    f.write("config.JobType.sendPythonFolder = True\n")
    f.write("config.section_('Data')\n")
    f.write("config.Data.inputDataset = '"+dataset+"'\n")
    #f.write("config.Data.inputDBS = 'phys03'")
    f.write("config.Data.inputDBS = 'global'\n")
    f.write("config.Data.splitting = 'FileBased'\n")
    #config.Data.runRange = ''
    #config.Data.lumiMask  = ''
    #f.write("config.Data.splitting = 'EventAwareLumiBased'")
    f.write("config.Data.unitsPerJob = 10\n")
    #f.write("config.Data.totalUnits = 10\n")
    f.write("config.Data.outLFNDirBase = '/store/user/%s/%s' % (getUsernameFromSiteDB(), '" +outdir+"')\n")
    f.write("config.Data.publication = False\n")
    f.write("config.Data.outputDatasetTag = '"+label+"'\n")
    f.write("config.section_('Site')\n")
    f.write("config.Site.storageSite = 'T2_IT_Pisa'\n")
    #f.write("config.Site.storageSite = "T2_CH_CERN"
    #f.write("config.section_("User")
    #f.write("config.User.voGroup = 'dcms'
    f.close()

def crab_script_writer(files, outpath, isMC, year, modules):
    f = open("crab_script_prova.py", "w")
    f.write("#!/usr/bin/env python\n")
    f.write("import os\n")
    f.write("from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *\n")
    f.write("from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *\n")
    f.write("from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis\n")
    f.write("from PhysicsTools.NanoAODTools.postprocessing.examples.MySelectorModule import *\n")
    f.write("from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *\n")
    f.write("from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *\n")

    f.write("metCorrector = createJMECorrector(isMC="+isMC+", dataYear="+year+", jesUncert='All', redojec=True)\n")
    f.write("fatJetCorrector = createJMECorrector(isMC="+isMC+", dataYear="+year+", jesUncert='All', redojec=True, jetType = 'AK8PFchs')\n")

    f.write("passMETFilter = 'Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter'\n")
    #f.write("infile = "+str(files)+"\n")
    f.write("outpath = '"+ outpath+"'\n")
    path = os.path.dirname(os.path.abspath(__file__))
    f.write("branc_sel = '"+path+"/../python/postprocessing/examples/keep_and_drop.txt'\n")
    #Deafult PostProcessor(outputDir,inputFiles,cut=None,branchsel=None,modules=[],compression='LZMA:9',friend=False,postfix=None, jsonInput=None,noOut=False,justcount=False,provenance=False,haddFileName=None,fwkJobReport=False,histFileName=None,histDirName=None, outputbranchsel=None,maxEntries=None,firstEntry=0, prefetch=False,longTermCache=False)\n")
    f.write("p=PostProcessor(outpath, inputFiles(), passMETFilter, modules=["+modules+"], provenance=True, fwkJobReport=True, jsonInput=runsAndLumis(), outputbranchsel=branc_sel)\n")
    f.write("p.run()\n")
    f.write("print 'DONE'\n")
    f.close()

sample = TT_Mtt700to1000_2016
#Writing the configuration file
print "Producing crab configuration file"
cfg_writer(sample.label, sample.dataset, "OutDir")

#Writing the script file 
if '2016' in sample.label:
    year = '2016'
if '2017' in sample.label:
    year = '2017'
if '2018' in sample.label:
    year = '2018'
if ('SingleMuon' in sample.label) or ('SingleElectron' in sample.label):
    isMC = 'False'
else:
    isMC = 'True'
modules = "MySelectorModule(), PrefireCorr(), metCorrector(), fatJetCorrector()" # Put here all the modules you want to be runned by crab

print "Producing crab script"
crab_script_writer(sample.files,'/eos/user/a/adeiorio/Wprime/nosynch/', isMC, year, modules)

#Launching crab
print "Submitting crab jobs..."
os.system("crab submit -c crab_cfg.py")