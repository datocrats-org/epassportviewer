# Copyright 2012 Antonin Beaujeant
#
# This file is part of epassportviewer.
#
# epassportviewer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# epassportviewer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with epassportviewer.
# If not, see <http://www.gnu.org/licenses/>.

from time import time
from Tkinter import *
import tkMessageBox
import Image, ImageTk
import os
import re
import pickle
from tkFileDialog import askdirectory, askopenfilename

from pypassport.attacks import macTraceability, bruteForce, aaTraceability, signEverything, errorFingerprinting
from pypassport import reader
from pypassport.iso7816 import Iso7816
from pypassport.doc9303.mrz import MRZ
from epassportviewer.util.image import ImageFactory
from epassportviewer.dialog import InfoBoxWindows
from epassportviewer.const import *


###################
#     ATTACKS     #
###################

class AttacksFrame(Frame):

    def __init__(self, master, mrz=None):
        Frame.__init__(self, master)
        
        im = Image.open(ImageFactory().create(ImageFactory().HELP))
        image = ImageTk.PhotoImage(im)
        
        self.mrz = mrz
        bgcolor = "#D1D1D1"

        # MENU
        menuFrame = Frame(self, borderwidth=1, relief=GROOVE)
        menuFrame.pack(fill=BOTH, expand=1)
        
        self.macTraceabilityButton = Button(menuFrame, text="MAC Traceability", bg=bgcolor, width=15, command=self.switchMac)
        self.macTraceabilityButton.pack(side=LEFT, padx=5, pady=5)
        
        self.bruteForceButton = Button(menuFrame, text="Brute Force", bg=bgcolor, width=15, command=self.switchBrute)
        self.bruteForceButton.pack(side=LEFT, padx=5, pady=5)
        
        self.activeAuthenticationButton = Button(menuFrame, text="Active Authentication", bg=bgcolor, width=15, command=self.switchAA)
        self.activeAuthenticationButton.pack(side=LEFT, padx=5, pady=5)
        
        self.errorFingerprintingButton = Button(menuFrame, text="Error Fingerprinting", bg=bgcolor, width=15, command=self.switchError)
        self.errorFingerprintingButton.pack(side=LEFT, padx=5, pady=5) 
        
        
        ######################
        ## MAC TRACEABILITY ##

        self.macTraceabilityFrame = Frame(self, borderwidth=1, relief=GROOVE, bg=bgcolor)

        # REACH MAX
        reachMaxFrame = Frame(self.macTraceabilityFrame, bg=bgcolor)
        reachMaxFrame.pack(fill=BOTH, expand=1)
        
        self.frenchVar = IntVar()
        reachMaxCheck = Checkbutton(reachMaxFrame, text="Reach max", variable=self.frenchVar, bg=bgcolor)
        reachMaxCheck.pack(side=LEFT, padx=5, pady=5)
        
        helpReachMax = Button(reachMaxFrame, image=image, command=self.helpReachMaxDialog)
        helpReachMax.image = image
        helpReachMax.pack(side=RIGHT, padx=5, pady=5)
        
        # IS VULNERABLE?
        vulnFrame = Frame(self.macTraceabilityFrame, bg=bgcolor)
        vulnFrame.pack(fill=BOTH, expand=1)
        
        vulnerableButton = Button(vulnFrame, text="Is vulnerable?", width=13, command=self.isVulnerable)
        vulnerableButton.pack(side=LEFT, padx=5, pady=5)
        
        coLabel = Label(vulnFrame, text="Cut-off:", justify=LEFT, bg=bgcolor)
        coLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.coForm = Entry(vulnFrame, width=3)
        self.coForm.pack(side=LEFT, padx=5, pady=5)
        
        helpVuln = Button(vulnFrame, image=image, command=self.helpVulnDialog)
        helpVuln.image = image
        helpVuln.pack(side=RIGHT, padx=5, pady=5)
        
        # SAVE PAIR
        saveFrame = Frame(self.macTraceabilityFrame, bg=bgcolor)
        saveFrame.pack(fill=BOTH, expand=1)
        
        saveButton = Button(saveFrame, text="Save pair...", width=13, command=self.save)
        saveButton.pack(side=LEFT, padx=5, pady=5)
        
        helpSave = Button(saveFrame, image=image, command=self.helpSaveDialog)
        helpSave.image = image
        helpSave.pack(side=RIGHT, padx=5, pady=5)
        
        # CHECK FROM FILE
        checkFrame = Frame(self.macTraceabilityFrame, bg=bgcolor)
        checkFrame.pack(fill=BOTH, expand=1)
        
        checkButton = Button(checkFrame, text="Check from file...", width=13, command=self.checkFromFile)
        checkButton.pack(side=LEFT, padx=5, pady=5)
        
        coFileLabel = Label(checkFrame, text="Cut-off:", justify=LEFT, bg=bgcolor)
        coFileLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.coFileForm = Entry(checkFrame, width=3)
        self.coFileForm.pack(side=LEFT, padx=5, pady=5)
        
        helpCheck = Button(checkFrame, image=image, command=self.helpCheckDialog)
        helpCheck.image = image
        helpCheck.pack(side=RIGHT, padx=5, pady=5)
        
        # TEST
        testFrame = Frame(self.macTraceabilityFrame, bg=bgcolor)
        testFrame.pack(fill=BOTH, expand=1)
        
        testButton = Button(testFrame, text="Perfom test", width=13, command=self.test)
        testButton.pack(side=LEFT, padx=5, pady=5)
        
        untilLabel = Label(testFrame, text="Until:", justify=LEFT, bg=bgcolor)
        untilLabel.pack(side=LEFT, padx=5, pady=5)

        self.untilForm = Entry(testFrame, width=2)
        self.untilForm.pack(side=LEFT, padx=15, pady=5)
        
        delayLabel = Label(testFrame, text="Accuracy:", justify=LEFT, bg=bgcolor)
        delayLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.perDelayForm = Entry(testFrame, width=2)
        self.perDelayForm.pack(side=LEFT, padx=5, pady=5)
        
        helpTest = Button(testFrame, image=image, command=self.helpTestDialog)
        helpTest.image = image
        helpTest.pack(side=RIGHT, padx=5, pady=5)
        
        # RESET BAC
        rstFrame = Frame(self.macTraceabilityFrame, bg=bgcolor)
        rstFrame.pack(fill=BOTH, expand=1)
        
        rstButton = Button(rstFrame, text="Reset BAC", width=13, command=self.reset)
        rstButton.pack(side=LEFT, padx=5, pady=5)
        
        helpRst = Button(rstFrame, image=image, command=self.helpRstDialog)
        helpRst.image = image
        helpRst.pack(side=RIGHT, padx=5, pady=5)
        
        # DEMO
        demoFrame = Frame(self.macTraceabilityFrame, bg=bgcolor)
        demoFrame.pack(fill=BOTH, expand=1)
        
        demoButton = Button(demoFrame, text="Demo", width=13, command=self.demo)
        demoButton.pack(side=LEFT, padx=5, pady=5)
        
        helpDemo = Button(demoFrame, image=image, command=self.helpDemoDialog)
        helpDemo.image = image
        helpDemo.pack(side=RIGHT, padx=5, pady=5)
        
        # LOG
        self.logMACFrame = ScrollFrame(self.macTraceabilityFrame)
        self.logMACFrame.pack(fill=BOTH, expand=1)
        
        # VERBOSE
        verboseMACFrame = Frame(self.macTraceabilityFrame, bg=bgcolor)
        verboseMACFrame.pack(fill=BOTH, expand=1)

        self.verboseMACVar = IntVar()
        verboseMACCheck = Checkbutton(verboseMACFrame, text="Verbose", variable=self.verboseMACVar, bg=bgcolor)
        verboseMACCheck.pack(side=LEFT, padx=5, pady=5)
        
        # DESCRIPTION
        macDescription = "\
DESCRIPTION:\n\
\n\
During the BAC process, the IFD send a encrypted message that contains a random number \n\
formely send by the ICC. The Message is concatenated with its MAC. Upon reception, the ICC \n\
first check the MAC it is the proper one for the ciphertext. If it does not, the ICC sent \n\
and error, else it decrypt the message and check if the random number is the same than the \n\
one it sent previously. If it does not, it send en error.\n\
The attack concist of capturing a correct pair ciphertext||MAC from a legitimate (using the \n\
correct MRZ) communication between an IFD and ICC. The decryption and nonce verification \n\
lasting couple of milisecond, the difference of reponse time between a wrong MAC and a wrong \n\
nonce is big enough to be measured and deduce if the MAC is correct (meaning the passport is \n\
the same than the one that was in the communication that produce the pair).\n\
An attack must send a random pair and store the reponse time (RT1), then send the pair \n\
captured previously and store the response time (RT2). If RT1 > RT2 and RT1 - RT2 > cut off \n\
(usually 1.7ms), this means the MAC of the pair captured is correct."
        
        self.writeToLogMAC(macDescription)

        
        
        
        #################
        ## BRUTE FORCE ##

        self.bruteForceFrame = Frame(self, borderwidth=1, relief=GROOVE, bg=bgcolor)
        
        self.response = self.initInfoLabel = None
        
        
        # DOCUMENT NUMBER
        docFrame = Frame(self.bruteForceFrame, bg=bgcolor)
        docFrame.pack(fill=BOTH, expand=1)
        
        docLabel = Label(docFrame, text="DOCUMENT NUMBER", width=16, justify=LEFT)
        docLabel.pack(side=LEFT, padx=5, pady=5)
        
        minDocLabel = Label(docFrame, text="Min:", justify=LEFT, bg=bgcolor)
        minDocLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.minDocForm = Entry(docFrame, width=10)
        self.minDocForm.pack(side=LEFT, pady=5)

        maxDocLabel = Label(docFrame, text="Max:", justify=LEFT, bg=bgcolor)
        maxDocLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.maxDocForm = Entry(docFrame, width=10)
        self.maxDocForm.pack(side=LEFT, pady=5)
        
        helpDoc = Button(docFrame, image=image, command=self.helpDocDialog)
        helpDoc.image = image
        helpDoc.pack(side=RIGHT, padx=5, pady=5)
        
        # DATE OF BIRTH
        dobFrame = Frame(self.bruteForceFrame, bg=bgcolor)
        dobFrame.pack(fill=BOTH, expand=1)
        
        dobLabel = Label(dobFrame, text="DATE OF BIRTH", width=16, justify=LEFT)
        dobLabel.pack(side=LEFT, padx=5, pady=5)
        
        minDOBLabel = Label(dobFrame, text="Min:", justify=LEFT, bg=bgcolor)
        minDOBLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.minDOBForm = Entry(dobFrame, width=7)
        self.minDOBForm.pack(side=LEFT, pady=5)
        self.minDOBForm.insert(0, "YYMMDD")
        
        maxDOBLabel = Label(dobFrame, text="Max:", justify=LEFT, bg=bgcolor)
        maxDOBLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.maxDOBForm = Entry(dobFrame, width=7)
        self.maxDOBForm.pack(side=LEFT, pady=5)
        self.maxDOBForm.insert(0, "YYMMDD")
        
        helpDOB = Button(dobFrame, image=image, command=self.helpDOBDialog)
        helpDOB.image = image
        helpDOB.pack(side=RIGHT, padx=5, pady=5)
        
        # DATE OF EXPIRY
        doiFrame = Frame(self.bruteForceFrame, bg=bgcolor)
        doiFrame.pack(fill=BOTH, expand=1)
        
        doeLabel = Label(doiFrame, text="DATE OF EXPIRY", width=16, justify=LEFT)
        doeLabel.pack(side=LEFT, padx=5, pady=5)
        
        minDOELabel = Label(doiFrame, text="Min:", justify=LEFT, bg=bgcolor)
        minDOELabel.pack(side=LEFT, padx=5, pady=5)
        
        self.minDOEForm = Entry(doiFrame, width=7)
        self.minDOEForm.pack(side=LEFT, pady=5)
        self.minDOEForm.insert(0, "YYMMDD")
        
        maxDOELabel = Label(doiFrame, text="Max:", justify=LEFT, bg=bgcolor)
        maxDOELabel.pack(side=LEFT, padx=5, pady=5)
        
        self.maxDOEForm = Entry(doiFrame, width=7)
        self.maxDOEForm.pack(side=LEFT, pady=5)
        self.maxDOEForm.insert(0, "YYMMDD")
        
        helpDOE = Button(doiFrame, image=image, command=self.helpDOEDialog)
        helpDOE.image = image
        helpDOE.pack(side=RIGHT, padx=5, pady=5)
        
        # CHECK
        checkDataFrame = Frame(self.bruteForceFrame, bg=bgcolor)
        checkDataFrame.pack(fill=BOTH, expand=1)
        
        checkDataButton = Button(checkDataFrame, text="Check", width=13, command=self.checkData)
        checkDataButton.pack(side=LEFT, padx=5, pady=5)
        
        helpCheckData = Button(checkDataFrame, image=image, command=self.helpCheckDialog)
        helpCheckData.image = image
        helpCheckData.pack(side=RIGHT, padx=5, pady=5)
        
        # GET STATS
        statsFrame = Frame(self.bruteForceFrame, bg=bgcolor)
        statsFrame.pack(fill=BOTH, expand=1)
        
        statsButton = Button(statsFrame, text="Get stats", width=13, command=self.getStats)
        statsButton.pack(side=LEFT, padx=5, pady=5)
        
        helpStats = Button(statsFrame, image=image, command=self.helpStatsDialog)
        helpStats.image = image
        helpStats.pack(side=RIGHT, padx=5, pady=5)
        
        # GENERATE NONCE/MAC
        initFrame = Frame(self.bruteForceFrame, bg=bgcolor)
        initFrame.pack(fill=BOTH, expand=1)
        
        initButton = Button(initFrame, text="Generate ANS/MAC", width=13, command=self.generate)
        initButton.pack(side=LEFT, padx=5, pady=5)

        helpInit = Button(initFrame, image=image, command=self.helpInitDialog)
        helpInit.image = image
        helpInit.pack(side=RIGHT, padx=5, pady=5)
        
        # LIVE EXPLOIT
        liveFrame = Frame(self.bruteForceFrame, bg=bgcolor)
        liveFrame.pack(fill=BOTH, expand=1)
        
        liveButton = Button(liveFrame, text="Live brute force", width=13, command=self.live)
        liveButton.pack(side=LEFT, padx=5, pady=5)
        
        self.rstBruteVar = IntVar()
        rstBruteCheck = Checkbutton(liveFrame, text="Reset", variable=self.rstBruteVar, bg=bgcolor)
        rstBruteCheck.pack(side=LEFT, padx=5, pady=5)
        
        helpLive = Button(liveFrame, image=image, command=self.helpLiveDialog)
        helpLive.image = image
        helpLive.pack(side=RIGHT, padx=5, pady=5)
        
        # OFFLINE EXPLOIT
        offlineFrame = Frame(self.bruteForceFrame, bg=bgcolor)
        offlineFrame.pack(fill=BOTH, expand=1)
        
        offlineButton = Button(offlineFrame, text="Offline brute force", width=13, command=self.offline)
        offlineButton.pack(side=LEFT, padx=5, pady=5)
        
        helpOffline = Button(offlineFrame, image=image, command=self.helpOfflineDialog)
        helpOffline.image = image
        helpOffline.pack(side=RIGHT, padx=5, pady=5)
        
        # LOG
        self.logBruteFrame = ScrollFrame(self.bruteForceFrame)
        self.logBruteFrame.pack(fill=BOTH, expand=1)
        
        # VERBOSE
        verboseBruteFrame = Frame(self.bruteForceFrame, bg=bgcolor)
        verboseBruteFrame.pack(fill=BOTH, expand=1)

        self.verboseBruteVar = IntVar()
        verboseBruteCheck = Checkbutton(verboseBruteFrame, text="Verbose", variable=self.verboseBruteVar, bg=bgcolor)
        verboseBruteCheck.pack(side=LEFT, padx=5, pady=5)
        
                # DESCRIPTION
        bfDescription = "\
DESCRIPTION:\n\
\n\
The derrivation of the keys used during the session keys establishment require one ID (8 \n\
characteres) and two dates (6 digits). The - low - entropy could be reduced if the attacker \n\
has personnal information about the bearer. Therefore a brute force on the MRZ might be \n\
possible.\n\
The attack concist of trying one by one each possibility of MRZ in the range set by the \n\
attacker. Whenever a BAC succeed, this means the MRZ tried is correct one."
        
        self.writeToLogBF(bfDescription)
        
        
        
        
        ###########################
        ## ACTIVE AUTHENTICATION ##

        self.activeAuthenticationFrame = Frame(self, borderwidth=1, relief=GROOVE, bg=bgcolor)

        
        # IS VULNERABLE?
        vulnAAFrame = Frame(self.activeAuthenticationFrame, bg=bgcolor)
        vulnAAFrame.pack(fill=BOTH, expand=1)
        
        vulnerableAAButton = Button(vulnAAFrame, text="Is vulnerable?", width=13, command=self.isVulnerableAA)
        vulnerableAAButton.pack(side=LEFT, padx=5, pady=5)
        
        helpVulnAA = Button(vulnAAFrame, image=image, command=self.helpVulnAADialog)
        helpVulnAA.image = image
        helpVulnAA.pack(side=RIGHT, padx=5, pady=5)
        
        # GET HIGHEST SIGNATURE
        getHighestFrame = Frame(self.activeAuthenticationFrame, bg=bgcolor)
        getHighestFrame.pack(fill=BOTH, expand=1)
        
        getHighestButton = Button(getHighestFrame, text="Get highest sign", width=13, command=self.getHighestSign)
        getHighestButton.pack(side=LEFT, padx=5, pady=5)
        
        maxHighestLabel = Label(getHighestFrame, text="Max:", justify=LEFT, bg=bgcolor)
        maxHighestLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.maxHighestForm = Entry(getHighestFrame, width=3)
        self.maxHighestForm.pack(side=LEFT, pady=5)
        
        helpGetHighest = Button(getHighestFrame, image=image, command=self.helpGetHighestDialog)
        helpGetHighest.image = image
        helpGetHighest.pack(side=RIGHT, padx=5, pady=5)
        
        # GET MODULO
        getModuloFrame = Frame(self.activeAuthenticationFrame, bg=bgcolor)
        getModuloFrame.pack(fill=BOTH, expand=1)
        
        getModuloButton = Button(getModuloFrame, text="Get modulo", width=13, command=self.getModulo)
        getModuloButton.pack(side=LEFT, padx=5, pady=5)
        
        helpGetModulo = Button(getModuloFrame, image=image, command=self.helpGetModuloDialog)
        helpGetModulo.image = image
        helpGetModulo.pack(side=RIGHT, padx=5, pady=5)
        
        # COMPARE
        compareFrame = Frame(self.activeAuthenticationFrame, bg=bgcolor)
        compareFrame.pack(fill=BOTH, expand=1)
        
        compareButton = Button(compareFrame, text="Compare", width=13, command=self.compare)
        compareButton.pack(side=LEFT, padx=5, pady=5)
        
        self.moduloCompareForm = Entry(compareFrame, width=8)
        self.moduloCompareForm.pack(side=LEFT, padx=5, pady=5)
        self.moduloCompareForm.insert(0, "Modulo")
        
        self.signCompareForm = Entry(compareFrame, width=8)
        self.signCompareForm.pack(side=LEFT, padx=5, pady=5)
        self.signCompareForm.insert(0, "Signature")
        
        accCompareLabel = Label(compareFrame, text="Accuracy:", justify=LEFT, bg=bgcolor)
        accCompareLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.accCompareForm = Entry(compareFrame, width=2)
        self.accCompareForm.pack(side=LEFT, pady=5)
        
        helpCompare = Button(compareFrame, image=image, command=self.helpCompareDialog)
        helpCompare.image = image
        helpCompare.pack(side=RIGHT, padx=5, pady=5)
        
        # MATCH?
        matchFrame = Frame(self.activeAuthenticationFrame, bg=bgcolor)
        matchFrame.pack(fill=BOTH, expand=1)
        
        matchButton = Button(matchFrame, text="Match?", width=13, command=self.mayBelongsTo)
        matchButton.pack(side=LEFT, padx=5, pady=5)
        
        self.moduloMatchForm = Entry(matchFrame, width=8)
        self.moduloMatchForm.pack(side=LEFT, padx=5, pady=5)
        self.moduloMatchForm.insert(0, "Modulo")
        
        self.signMatchForm = Entry(matchFrame, width=8)
        self.signMatchForm.pack(side=LEFT, padx=5, pady=5)
        self.signMatchForm.insert(0, "Signature")
        
        helpMatch = Button(matchFrame, image=image, command=self.helpMatchDialog)
        helpMatch.image = image
        helpMatch.pack(side=RIGHT, padx=5, pady=5)
        
        # SAVE
        saveSignFrame = Frame(self.activeAuthenticationFrame, bg=bgcolor)
        saveSignFrame.pack(fill=BOTH, expand=1)
        
        saveSignButton = Button(saveSignFrame, text="Save sign/mod...", width=13, command=self.saveSign)
        saveSignButton.pack(side=LEFT, padx=5, pady=5)
        
        self.typeSign = IntVar()
        self.typeSign.set(1)
        signatureRadioButton = Radiobutton(saveSignFrame, text="Signature", variable=self.typeSign, value=1, bg=bgcolor)
        signatureRadioButton.pack(side=LEFT, padx=5, pady=5)

        moduloRadioButton = Radiobutton(saveSignFrame, text="Modulo", variable=self.typeSign, value=2, bg=bgcolor)
        moduloRadioButton.pack(side=LEFT, padx=5, pady=5)
        
        helpSaveSign = Button(saveSignFrame, image=image, command=self.helpSaveSignDialog)
        helpSaveSign.image = image
        helpSaveSign.pack(side=RIGHT, padx=5, pady=5)
        
        # CHECK FROM FILE
        checkSignFrame = Frame(self.activeAuthenticationFrame, bg=bgcolor)
        checkSignFrame.pack(fill=BOTH, expand=1)
        
        checkSignButton = Button(checkSignFrame, text="Check from file...", width=13, command=self.checkSignFromFile)
        checkSignButton.pack(side=LEFT, padx=5, pady=5)
        
        self.moduloFileForm = Entry(checkSignFrame, width=8)
        self.moduloFileForm.pack(side=LEFT, padx=5, pady=5)
        self.moduloFileForm.insert(0, "Signature")
        
        coFileLabel = Label(checkSignFrame, text="Accuracy:", justify=LEFT, bg=bgcolor)
        coFileLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.accFileForm = Entry(checkSignFrame, width=3)
        self.accFileForm.pack(side=LEFT, padx=5, pady=5)
        
        helpCheckSign = Button(checkSignFrame, image=image, command=self.helpCheckSignDialog)
        helpCheckSign.image = image
        helpCheckSign.pack(side=RIGHT, padx=5, pady=5)
        
        # SIGN EVERYTHING
        signEverythingFrame = Frame(self.activeAuthenticationFrame, bg=bgcolor)
        signEverythingFrame.pack(fill=BOTH, expand=1)
        
        signEverythingButton = Button(signEverythingFrame, text="Sign...", width=13, command=self.signEverything)
        signEverythingButton.pack(side=LEFT, padx=5, pady=5)
        
        self.nonceToSignForm = Entry(signEverythingFrame, width=16)
        self.nonceToSignForm.pack(side=LEFT, pady=5)
        self.nonceToSignForm.insert(0, "Nonce to sign...")
        
        helpSignEverything = Button(signEverythingFrame, image=image, command=self.helpSignEverythingDialog)
        helpSignEverything.image = image
        helpSignEverything.pack(side=RIGHT, padx=5, pady=5)
        
        # LOG
        self.logAAFrame = ScrollFrame(self.activeAuthenticationFrame)
        self.logAAFrame.pack(fill=BOTH, expand=1)
        
        # VERBOSE
        verboseAAFrame = Frame(self.activeAuthenticationFrame, bg=bgcolor)
        verboseAAFrame.pack(fill=BOTH, expand=1)

        self.verboseAAVar = IntVar()
        verboseAACheck = Checkbutton(verboseAAFrame, text="Verbose", variable=self.verboseAAVar, bg=bgcolor)
        verboseAACheck.pack(side=LEFT, padx=5, pady=5)
        
        # DESCRIPTION
        aaDescription = "\
DESCRIPTION:\n\
\n\
In some case, it is possible to execute an active authentication before the BAC and \n\
thus geting a signature. In RSA algorythm, the signature can't be higher than the modulo.\n\
Therefore, after a couple of test, by keeping the highest signature, we know that we are \n\
more and more close  to the modulo. Since the modulo is unique it is possible to identify \n\
(with a little lack of accuracy) a passport. If the highest signature is higher than the \n\
modulo of a passport (avaible in DG15), we know for sure that the passport scanned is NOT \n\
the one to which belongs the modulo."
        
        self.writeToLogAA(aaDescription)
        
        
        
        
        ##########################
        ## ERROR FINGERPRINTING ##

        self.errorFingerprintingFrame = Frame(self, borderwidth=1, relief=GROOVE, bg=bgcolor)

        
        # APDU
        apduFrame = Frame(self.errorFingerprintingFrame, bg=bgcolor)
        apduFrame.pack(fill=BOTH, expand=1)
        

        customCLALabel = Label(apduFrame, text="CLA:", justify=LEFT, bg=bgcolor)
        customCLALabel.pack(side=LEFT, padx=5, pady=5)
        
        self.customCLAForm = Entry(apduFrame, width=2)
        self.customCLAForm.pack(side=LEFT, pady=5)
        self.customCLAForm.insert(0, "00")
        
        customINSLabel = Label(apduFrame, text="INS:", justify=LEFT, bg=bgcolor)
        customINSLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.customINSForm = Entry(apduFrame, width=2)
        self.customINSForm.pack(side=LEFT, pady=5)
        self.customINSForm.insert(0, "84")
        
        customP1Label = Label(apduFrame, text="P1:", justify=LEFT, bg=bgcolor)
        customP1Label.pack(side=LEFT, padx=5, pady=5)
        
        self.customP1Form = Entry(apduFrame, width=2)
        self.customP1Form.pack(side=LEFT, pady=5)
        self.customP1Form.insert(0, "00")
        
        customP2Label = Label(apduFrame, text="P2:", justify=LEFT, bg=bgcolor)
        customP2Label.pack(side=LEFT, padx=5, pady=5)
        
        self.customP2Form = Entry(apduFrame, width=2)
        self.customP2Form.pack(side=LEFT, pady=5)
        self.customP2Form.insert(0, "00")
        
        customLCLabel = Label(apduFrame, text="LC:", justify=LEFT, bg=bgcolor)
        customLCLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.customLCForm = Entry(apduFrame, width=3)
        self.customLCForm.pack(side=LEFT, pady=5)
        
        customDATALabel = Label(apduFrame, text="DATA:", justify=LEFT, bg=bgcolor)
        customDATALabel.pack(side=LEFT, padx=5, pady=5)
        
        self.customDATAForm = Entry(apduFrame, width=8)
        self.customDATAForm.pack(side=LEFT, pady=5)
        
        customLELabel = Label(apduFrame, text="LE:", justify=LEFT, bg=bgcolor)
        customLELabel.pack(side=LEFT, padx=5, pady=5)
        
        self.customLEForm = Entry(apduFrame, width=2)
        self.customLEForm.pack(side=LEFT, pady=5)
        self.customLEForm.insert(0, "08")
        
        # SEND CUSTOM APDU
        sendCustomFrame = Frame(self.errorFingerprintingFrame, bg=bgcolor)
        sendCustomFrame.pack(fill=BOTH, expand=1)
        
        sendCustomButton = Button(sendCustomFrame, text="Send custom APDU", width=13, command=self.sendCustom)
        sendCustomButton.pack(side=LEFT, padx=5, pady=5)
        
        helpSendCustom = Button(sendCustomFrame, image=image, command=self.helpSendCustomDialog)
        helpSendCustom.image = image
        helpSendCustom.pack(side=RIGHT, padx=5, pady=5)
        
        # ADD ERROR
        addErrorFrame = Frame(self.errorFingerprintingFrame, bg=bgcolor)
        addErrorFrame.pack(fill=BOTH, expand=1)
        
        addErrorButton = Button(addErrorFrame, text="Add error", width=13, command=self.addError)
        addErrorButton.pack(side=LEFT, padx=5, pady=5)
        
        countryLabel = Label(addErrorFrame, text="Country:", justify=LEFT, bg=bgcolor)
        countryLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.countryForm = Entry(addErrorFrame, width=3)
        self.countryForm.pack(side=LEFT, pady=5)
        
        yearLabel = Label(addErrorFrame, text="Year:", justify=LEFT, bg=bgcolor)
        yearLabel.pack(side=LEFT, padx=5, pady=5)
        
        self.yearForm = Entry(addErrorFrame, width=4)
        self.yearForm.pack(side=LEFT, pady=5)
        
        helpAddError = Button(addErrorFrame, image=image, command=self.helpAddErrorDialog)
        helpAddError.image = image
        helpAddError.pack(side=RIGHT, padx=5, pady=5)
        
        # IDENTIFY
        identifyFrame = Frame(self.errorFingerprintingFrame, bg=bgcolor)
        identifyFrame.pack(fill=BOTH, expand=1)
        
        identifyButton = Button(identifyFrame, text="Identify", width=13, command=self.identify)
        identifyButton.pack(side=LEFT, padx=5, pady=5)
        
        helpIdentify = Button(identifyFrame, image=image, command=self.helpIdentifyDialog)
        helpIdentify.image = image
        helpIdentify.pack(side=RIGHT, padx=5, pady=5)
        
        # LOG
        self.logErrorFrame = ScrollFrame(self.errorFingerprintingFrame)
        self.logErrorFrame.pack(fill=BOTH, expand=1)
        
        # VERBOSE
        verboseErrorFrame = Frame(self.errorFingerprintingFrame, bg=bgcolor)
        verboseErrorFrame.pack(fill=BOTH, expand=1)

        self.verboseErrorVar = IntVar()
        verboseErrorCheck = Checkbutton(verboseErrorFrame, text="Verbose", variable=self.verboseErrorVar, bg=bgcolor)
        verboseErrorCheck.pack(side=LEFT, padx=5, pady=5)
        
        # DESCRIPTION
        errDescription = "\
DESCRIPTION:\n\
\n\
ICAO did not defined the message to send regarding the error triggered. Therefore, each \n\
country decided which message to the send (among the SW1|SW2 list). Due to this non-\n\
standardisation, it is possible to identify a country issuer when triggering on purpose \n\
an error that the attacker knows the answer will be different regarding the country."
        
        self.writeToLogERR(errDescription)
        

        # PACK
        self.currentFrame = self.macTraceabilityFrame
        self.currentFrame.pack(fill=BOTH, expand=1)
        self.currentButton = self.macTraceabilityButton
        self.currentButton.config(relief=SUNKEN, bg="#D1D1D1")
        
        
        

        
        
        
        
    
    #########
    # METHODS
    #########
    
    def writeToLogMAC(self, msg, desc=None):
        if desc: self.logMACFrame.insert(END, "{0} > {1}\n".format(msg, desc))
        else: self.logMACFrame.insert(END, "{0}\n".format(msg))
    
    def writeToLogBF(self, msg, desc=None):
        if desc: self.logBruteFrame.insert(END, "{0} > {1}\n".format(msg, desc))
        else: self.logBruteFrame.insert(END, "{0}\n".format(msg))
    
    def writeToLogAA(self, msg, desc=None):
        if desc: self.logAAFrame.insert(END, "{0} > {1}\n".format(msg, desc), False)
        else: self.logAAFrame.insert(END, "{0}\n".format(msg), False)
    
    def writeToLogERR(self, msg, desc=None):
        if desc: self.logErrorFrame.insert(END, "{0} > {1}\n".format(msg, desc))
        else: self.logErrorFrame.insert(END, "{0}\n".format(msg))
    
    def switchMac(self):
        self.currentButton.config(relief=RAISED)
        self.currentButton = self.macTraceabilityButton
        self.currentButton.config(relief=SUNKEN)
        self.switch(self.macTraceabilityFrame)
        
    def switchBrute(self):
        self.currentButton.config(relief=RAISED)
        self.currentButton = self.bruteForceButton
        self.currentButton.config(relief=SUNKEN, bg="#D1D1D1")
        self.switch(self.bruteForceFrame)
    
    def switchAA(self):
        self.currentButton.config(relief=RAISED)
        self.currentButton = self.activeAuthenticationButton
        self.currentButton.config(relief=SUNKEN, bg="#D1D1D1")
        self.switch(self.activeAuthenticationFrame)
    
    def switchError(self):
        self.currentButton.config(relief=RAISED)
        self.currentButton = self.errorFingerprintingButton
        self.currentButton.config(relief=SUNKEN, bg="#D1D1D1")
        self.switch(self.errorFingerprintingFrame)
    
    def switch(self, frame):
        self.currentFrame.pack_forget()
        self.currentFrame = frame
        self.currentFrame.pack(fill=BOTH, expand=1)
    
    def getReader(self):
        return 1
         
    
    #########################
    # ACTION MAC TRACEABILITY
    #########################
    
    # IS VULNERABLE?
    def isVulnerable(self):
        try:

            if self.coForm.get(): co = self.coForm.get()
            else: co = 1.7

            r = reader.ReaderManager().waitForCard()
            attack = macTraceability.MacTraceability(Iso7816(r))
            if self.verboseMACVar.get():
                attack.register(self.writeToLogMAC)
            if attack.setMRZ(self.mrz.buildMRZ()):
                if self.frenchVar.get(): attack.reachMaxDelay()
                self.writeToLogMAC("Is vulnerable? : {0}".format(attack.isVulnerable(int(co))))
            else:
                tkMessageBox.showerror("Error: Wrong MRZ", "The check digits are not correct")

        except Exception, msg:
            tkMessageBox.showerror("Error: is vulnerable", str(msg))
    
    # SAVE
    def save(self):
        
        try:
            
            directory = askdirectory(title="Select directory", mustexist=1)
            if directory:
                directory = str(directory)
                if os.path.isdir(directory):

                    r = reader.ReaderManager().waitForCard()
                    attack = macTraceability.MacTraceability(Iso7816(r))
                    if self.verboseMACVar.get():
                        attack.register(self.writeToLogMAC)
                    if attack.setMRZ(self.mrz.buildMRZ()):
                        attack.savePair(directory)
                        tkMessageBox.showinfo("Save successful", "The pair has bee saved in:\n{0}".format(directory))
                    else:
                        tkMessageBox.showerror("Error: Wrong MRZ", "The check digits are not correct")
                else:
                    tkMessageBox.showerror("Error: save", "The path you selected is not a directory")
        except Exception, msg:
            tkMessageBox.showerror("Error: save", str(msg))
    
    # CHECK FROM FILE
    def checkFromFile(self):
        try:
            
            directory = askopenfilename(title="Select file")
            if directory:
                directory = str(directory)
                if os.path.isfile(directory):
                    if self.coForm.get(): co = self.coForm.get()
                    else: co = 1.7
                    r = reader.ReaderManager().waitForCard()
                    attack = macTraceability.MacTraceability(Iso7816(r))
                    if self.verboseMACVar.get():
                        attack.register(self.writeToLogMAC)
                    if self.frenchVar.get(): attack.reachMaxDelay()
                    self.writeToLogMAC("Does the pair belongs the the passport scanned: {0}".format(attack.checkFromFile(directory, co)))
                else:
                    tkMessageBox.showerror("Error: save", "The path you selected is not a file")
        except Exception, msg:
            tkMessageBox.showerror("Error: save", str(msg))
    
    # TEST
    def test(self):
        try:

            r = reader.ReaderManager().waitForCard()
            attack = macTraceability.MacTraceability(Iso7816(r))
            if self.verboseMACVar.get():
                attack.register(self.writeToLogMAC)
            if attack.setMRZ(self.mrz.buildMRZ()):
                if self.untilForm.get(): until = int(self.untilForm.get())
                else: until = 20
                if self.perDelayForm.get(): per_delay = int(self.perDelayForm.get())
                else: per_delay = 10
                
                j = 0
                while j<until:
                    self.writeToLogMAC("Delay increased between {0} and {1} error(s)".format(j, j+1))
                    self.writeToLogMAC("Average: {0}".format(attack.test(j, per_delay)))
                    j+=1
            else:
                tkMessageBox.showerror("Error: Wrong MRZ", "The check digits are not correct")

        except Exception, msg:
            tkMessageBox.showerror("Error: is vulnerable", str(msg))
        
    # BAC RESET
    def reset(self):
        try:
            r = reader.ReaderManager().waitForCard()
            attack = macTraceability.MacTraceability(Iso7816(r))
            if self.verboseMACVar.get():
                attack.register(self.writeToLogMAC)
            if attack.setMRZ(self.mrz.buildMRZ()):
                attack.rstBAC()
                self.writeToLogMAC("BAC reset")
            else:
                tkMessageBox.showerror("Error: Wrong MRZ", "The check digits are not correct")
        except Exception, msg:
            tkMessageBox.showerror("Error: is vulnerable", str(msg))
    
    # DEMO
    def demo(self):
        try:
            r = reader.ReaderManager().waitForCard()
            attack = macTraceability.MacTraceability(Iso7816(r))
            if self.verboseMACVar.get():
                attack.register(self.writeToLogMAC)
            if attack.setMRZ(self.mrz.buildMRZ()):
                tkMessageBox.showinfo("Passport scanned", "Press ok then remove your passport from the reader.\nWait 5s before testing if a passport match.")
                if attack.demo():
                    self.writeToLogMAC("This passport match the one scanned")
            else:
                tkMessageBox.showerror("Error: Wrong MRZ", "The check digits are not correct")
        except Exception, msg:
            tkMessageBox.showerror("Error: is vulnerable", str(msg))
    
    
    ####################
    # ACTION BRUTE FORCE
    ####################
    
    # Init Data
    def initData(self):
        try:
            r = reader.ReaderManager().waitForCard()
            bf = bruteForce.BruteForce(Iso7816(r))
            if self.verboseBruteVar.get():
                bf.register(self.writeToLogBF)

            if self.minDocForm.get() == '': minDoc = None
            else: minDoc = self.minDocForm.get()
            if self.maxDocForm.get() == '': maxDoc = None
            else: maxDoc = self.maxDocForm.get()
            
            if self.minDOBForm.get() == 'YYMMDD': minDOB = None
            else: minDOB = self.minDOBForm.get()
            if self.maxDOBForm.get() == 'YYMMDD': maxDOB = None
            else: maxDOB = self.maxDOBForm.get()

            if self.minDOEForm.get() == 'YYMMDD': minDOE = None
            else: minDOE = self.minDOEForm.get()
            if self.maxDOEForm.get() == 'YYMMDD': maxDOE = None
            else: maxDOE = self.maxDOEForm.get()
            
            bf.setID(minDoc, maxDoc)
            bf.setDOB(minDOB, maxDOB)
            bf.setExpDate(minDOE, maxDOE)
            
            return bf
            
        except Exception, msg:
            tkMessageBox.showerror("Error: Initialisation data", str(msg))
      
    # CHECK  
    def checkData(self):
        try:
            bf = self.initData()
            chk, err = bf.check()
            if chk:
                self.writeToLogBF("Format values are correct")
            else:
                self.writeToLogBF(err)

        except Exception, msg:
            tkMessageBox.showerror("Error: Initialisation data", str(msg))
        
    #GET STATS
    def getStats(self):
        try:
            bf = self.initData()
            chk, err = bf.check()
            if chk:
                (id_low, id_high, entropy_id) = bf.getIdStat()
                (dob_low, dob_high, entropy_dob) = bf.getDOBStat()
                (exp_low, exp_high, entropy_exp) = bf.getExpDateStat()
                self.writeToLogBF("Entropy: {0} possibilities.".format(entropy_id * entropy_dob * entropy_exp))
            else:
                self.writeToLogBF(err)

        except Exception, msg:
            tkMessageBox.showerror("Error: Initialisation data", str(msg))

    # GENERATE NONCE AND RESPONSE/MAC
    def generate(self):
        try:
            if self.mrz.buildMRZ():
                bf = self.initData()
                self.response = bf.initOffline(self.mrz.buildMRZ())
                self.writeToLogBF("Nonce and response/MAC from {0} loaded".format(self.mrz.buildMRZ()[0:9]))
            else:
                tkMessageBox.showerror("Error: MRZ", "You have to set the proper MRZ")
        except Exception, msg:
            tkMessageBox.showerror("Error: Initialisation data", str(msg))
    
    # LIVE BRUTE FORCE
    def live(self):
        try:
            bf = self.initData()
            chk, err = bf.check()
            if chk:
                found = bf.exploit(self.rstBruteVar.get())
                if found:
                    self.writeToLogBF("MRZ found: {0}".format(found))
                else:
                    self.writeToLogBF("MRZ not found")
            else:
                self.writeToLogBF(err)

        except Exception, msg:
            tkMessageBox.showerror("Error: Initialisation data", str(msg))
    
    # OFFLINE BRUTE FORCE
    def offline(self):
        try:
            bf = self.initData()
            chk, err = bf.check()
            if chk:
                found = bf.exploitOffline(self.response)
                if found:
                    self.writeToLogBF("MRZ found: {0}".format(found))
                else:
                    self.writeToLogBF("MRZ not found")
            else:
                self.writeToLogBF(err)

        except Exception, msg:
            tkMessageBox.showerror("Error: Initialisation data", str(msg))
    
    
    ##############################
    # ACTION ACTIVE AUTHENTICATION
    ##############################
    
    # IS VULNERABLE?
    def isVulnerableAA(self):
        try:
            r = reader.ReaderManager().waitForCard()
            attack = aaTraceability.AATraceability(Iso7816(r))
            if self.verboseAAVar.get():
                attack.register(self.writeToLogAA)
            self.writeToLogAA("Is vulnerable? : {0}".format(attack.isVulnerable()))
        except Exception, msg:
            tkMessageBox.showerror("Error: Is vulnerable", str(msg))
    
    # GET HIGHEST SIGNATURE
    def getHighestSign(self):
        try:
            if self.maxHighestForm.get() == '': max_loop = 100
            else: max_loop = int(self.maxHighestForm.get())

            r = reader.ReaderManager().waitForCard()
            attack = aaTraceability.AATraceability(Iso7816(r))
            if self.verboseAAVar.get():
                attack.register(self.writeToLogAA)
            start_time = time()
            self.writeToLogAA("Highest signature: {0}".format(attack.getHighestSign(max_loop)))
            self.writeToLogAA("Time: {0}".format(time()-start_time))
        except Exception, msg:
            tkMessageBox.showerror("Error: Get highest signature", str(msg))
        
    # GET MODULO
    def getModulo(self):
        try:
            if self.mrz.buildMRZ()!='':
                r = reader.ReaderManager().waitForCard()
                attack = aaTraceability.AATraceability(Iso7816(r))
                if self.verboseAAVar.get():
                    attack.register(self.writeToLogAA)
                self.writeToLogAA("Modulo: {0}".format(attack.getModulo(self.mrz.buildMRZ())))
            else:
                tkMessageBox.showerror("Error: Wrong MRZ", "You have to set the proper MRZ")
        except Exception, msg:
            tkMessageBox.showerror("Error: Get modulo", str(msg))
    
    # COMPARE
    def compare(self):
        try:
            if self.accCompareForm.get() == '': accuracy = 6
            else: accuracy = int(self.accCompareForm.get())

            r = reader.ReaderManager().waitForCard()
            attack = aaTraceability.AATraceability(Iso7816(r))
            if self.verboseAAVar.get():
                attack.register(self.writeToLogAA)
            self.writeToLogAA("Difference: {0}%".format(attack.compare(self.moduloCompareForm.get(), self.signCompareForm.get(), accuracy)))
            
        except Exception, msg:
            tkMessageBox.showerror("Error: Compare", str(msg))
    
    # MAY BELONGS TO
    def mayBelongsTo(self):
        try:
            r = reader.ReaderManager().waitForCard()
            attack = aaTraceability.AATraceability(Iso7816(r))
            if self.verboseAAVar.get():
                attack.register(self.writeToLogAA)
            self.writeToLogAA("May belongs to? : {0}".format(attack.mayBelongsTo(self.moduloMatchForm.get(), self.signMatchForm.get())))
            
        except Exception, msg:
            tkMessageBox.showerror("Error: May belongs to?", str(msg))
        
    # SAVE
    def saveSign(self):
        try:
            directory = askdirectory(title="Select directory", mustexist=1)
            if directory:
                directory = str(directory)
                if os.path.isdir(directory):
                    r = reader.ReaderManager().waitForCard()
                    attack = aaTraceability.AATraceability(Iso7816(r))
                    if self.verboseAAVar.get():
                        attack.register(self.writeToLogAA)
                    if self.typeSign.get()==1:
                        sign = attack.getHighestSign(100)
                        attack.save(sign, directory, "sign")
                        tkMessageBox.showinfo("Save successful", "The signature has bee saved in:\n{0}".format(directory))
                    
                    if self.typeSign.get()==2:
                        if self.mrz.buildMRZ()!='': 
                            modulo = attack.getModulo(self.mrz.buildMRZ())
                            attack.save(modulo, directory, "modulo")
                            tkMessageBox.showinfo("Save successful", "The modulo has bee saved in:\n{0}".format(directory))
                        else:
                            tkMessageBox.showerror("Error: Wrong MRZ", "You have to set the proper MRZ")
                else:
                    tkMessageBox.showerror("Error: save", "The path you selected is not a directory")
        except Exception, msg:
            tkMessageBox.showerror("Error: save", str(msg))

    # CHECK FROM FILE
    def checkSignFromFile(self):
        try:
            directory = askopenfilename(title="Select file")
            if directory:
                directory = str(directory)
                if os.path.isfile(directory):
                    if self.accFileForm.get()!='': accuracy = int(self.accFileForm.get())
                    else: accuracy = None
                    r = reader.ReaderManager().waitForCard()
                    attack = aaTraceability.AATraceability(Iso7816(r))
                    if self.verboseAAVar.get():
                        attack.register(self.writeToLogAA)
                    if accuracy:
                        self.writeToLogAA("Difference: {0}%".format(attack.checkFromFile(self.moduloFileForm.get(), directory, accuracy)))
                    else:
                        self.writeToLogAA("May belongs to? : {0}".format(attack.checkFromFile(self.moduloFileForm.get(), directory, accuracy)))
                else:
                    tkMessageBox.showerror("Error: save", "The path you selected is not a file")
        except Exception, msg:
            tkMessageBox.showerror("Error: Check from file", str(msg))
    
    # SIGN EVERYTHING
    def signEverything(self):
        try:
            pattern_id = '^[0-9A-F]{15,16}$'
            reg=re.compile(pattern_id)
            if not reg.match(self.nonceToSignForm.get()): 
                raise Exception("The message to sign must be 15 or 16 HEX [0-9A-F]")

            r = reader.ReaderManager().waitForCard()
            attack = signEverything.SignEverything(Iso7816(r))
            if self.verboseAAVar.get():
                attack.register(self.writeToLogAA)
            
            if self.mrz.buildMRZ()!='': mrz = self.mrz.buildMRZ()
            else: mrz = None
            
            (signature, validated) = attack.sign(self.nonceToSignForm.get(), mrz)
            self.writeToLogAA("{0} signed: {1}".format(self.nonceToSignForm.get(), signature))
            self.writeToLogAA("Validated?: {0}".format(validated))
            
            
        except Exception, msg:
            tkMessageBox.showerror("Error: Sign everything", str(msg))
        
    
    #############################
    # ACTION ERROR FINGERPRINTING
    #############################
    
    def sendCustom(self):
        try:
            r = reader.ReaderManager().waitForCard()
            attack = errorFingerprinting.ErrorFingerprinting(Iso7816(r))
            if self.verboseErrorVar.get():
                attack.register(self.writeToLogERR)

            (ans, message) = attack.sendCustom( self.customCLAForm.get(), \
                                                self.customINSForm.get(), \
                                                self.customP1Form.get(), \
                                                self.customP2Form.get(), \
                                                self.customLCForm.get(), \
                                                self.customDATAForm.get(), \
                                                self.customLEForm.get())
            
            self.writeToLogERR("Message: {0}".format(message))
            self.writeToLogERR("Success?: {0}".format(ans))
        except Exception, msg:
            tkMessageBox.showerror("Error: Sendcustom", str(msg))
    
    # ADD ERROR
    def addError(self):
        try:
            r = reader.ReaderManager().waitForCard()
            attack = errorFingerprinting.ErrorFingerprinting(Iso7816(r))
            if self.verboseErrorVar.get():
                attack.register(self.writeToLogERR)

            response = attack.sendCustom( self.customCLAForm.get(), \
                                                self.customINSForm.get(), \
                                                self.customP1Form.get(), \
                                                self.customP2Form.get(), \
                                                self.customLCForm.get(), \
                                                self.customDATAForm.get(), \
                                                self.customLEForm.get())
            (ans, message) = response
            if not ans:
                query = self.customCLAForm.get() +\
                        self.customINSForm.get() +\
                        self.customP1Form.get() +\
                        self.customP2Form.get() +\
                        self.customLCForm.get() +\
                        self.customDATAForm.get() +\
                        self.customLEForm.get()
                attack.addError(query, response, self.countryForm.get(), self.yearForm.get())
                self.writeToLogERR("Error added")
            else:
                tkMessageBox.showerror("Error: Add error", "The query triggered a correct answer")

                
        except Exception, msg:
            tkMessageBox.showerror("Error: Sign everything", str(msg))
        
    # IDENTIFY
    def identify(self):
        try:
            r = reader.ReaderManager().waitForCard()
            attack = errorFingerprinting.ErrorFingerprinting(Iso7816(r))
            if self.verboseErrorVar.get():
                attack.register(self.writeToLogERR)

            possibilities = attack.identify( self.customCLAForm.get(), \
                                                self.customINSForm.get(), \
                                                self.customP1Form.get(), \
                                                self.customP2Form.get(), \
                                                self.customLCForm.get(), \
                                                self.customDATAForm.get(), \
                                                self.customLEForm.get())
            
            for pos in possibilities:
                self.writeToLogERR(" - {0}".format(pos))
            self.writeToLogERR("Possibilities:")
        except Exception, msg:
            tkMessageBox.showerror("Error: Sign everything", str(msg))



    
    ################
    # HELP DIALOGS #
    ################
    
    # MAC TRACEABILITY
    ##################
    
    def helpVulnDialog(self):
        title = "is vulnerable?"
        text = "Check whether a passport is vulnerable:\n\
    - Initiate a legitimate BAC and store a pair of message/MAC\n\
    - Reset a BAC with a random number for mutual authentication and store the answer together with the response time\n\
    - Reset a BAC and use the pair of message/MAC from step 1 and store the answer together with the response time\n\
\n\
If answers are different, this means the the passport is vulnerable.\n\
If not, the response time is compared. If the gap is wide enough, the passport might be vulnerable.\n\
\n\
Note: The French passport (and maybe others) implemented a security against brute forcing:\n\
anytime the BAC fail, an incremented delay occur before responsding.\n\
That's the reson why we need to establish a proper BAC to reset the delay to 0\n\
Note 2: The default cut off set to 1.7ms is based on the paper from Tom Chotia and Vitaliy Smirnov:\n\
A traceability Attack Against e-Pasport.\n\
They figured out a 1.7 cut-off suit for every country they assessed without raising low rate of false-positive and false-negative\n\
\n\
@param CO: The cut off used to determine whether the response time is long enough to considerate the passport as vulnerable\n\
@type CO: an integer that represent the cut off in milliseconds\n\
\n\
@return: A boolean where True means that the passport seems to be vulnerable and False means doesn't"
        InfoBoxWindows(self, title, text)
    
    def helpSaveDialog(self):
        title = "save pair"
        text = "savePair stores a message with its valid MAC in a file.\n\
The pair can be used later, in a futur attack, to define if the passport is the one that creates the pair (See checkFromFile()).\n\
If the path doesn't exist, the folders and sub-folders will be create.\n\
If the file exist, a number will be add automatically.\n\
\n\
@param path: The path where the file has to be create. It can be relative or absolute.\n\
@type path: A string (e.g. '/home/doe/' or 'foo/bar')\n\
@param filename: The name of the file where the pair will be saved\n\
@type filename: A string (e.g. 'belgian-pair' or 'pair.data')\n\
\n\
@return: the path and the name of the file where the pair has been saved."
        InfoBoxWindows(self, title, text)
    
    def helpCheckDialog(self):
        title = "check from file"
        text = "checkFromFile read a file that contains a pair and check if the pair has been capture from the passport .\n\
\n\
@param path: The path of the file where the pair has been saved.\n\
@type path: A string (e.g. '/home/doe/pair' or 'foo/bar/pair.data')\n\
@param CO: The cut off used to determine whether the response time is long enough to considerate the passport as vulnerable\n\
@type CO: an integer that represent the cut off in milliseconds\n\
\n\
@return: A boolean where True means that the passport is the one who create the pair in the file."
        InfoBoxWindows(self, title, text)
    
    def helpTestDialog(self):
        title = "test"
        text = "test is a method developped for analysing the response time of password whenever a wrong command is sent\n\
French passport has an anti MRZ brute forcing. This method help to highlight the behaviour\n\
Note: It might take a while before getting the results\n\
\n\
@param until: Number of wrong message to send before comparing the time delay\n\
@type until: An integer\n\
@param per_delay: how result per delay you want to output\n\
@type per_delay: An integer"
        InfoBoxWindows(self, title, text)
    
    def helpMaxDialog(self):
        title = "reach max"
        text = "Send a 13 (or more) wrong pair in order to reach the longest delay\n\
Note: Useful only for passport with anti MRZ brute forcing security."
        InfoBoxWindows(self, title, text)
    
    def helpRstDialog(self):
        title = "reset BAC"
        text = "Establish a legitimate BAC with the passport then reset the connection."
        InfoBoxWindows(self, title, text)
    
    def helpDemoDialog(self):
        title = "demo"
        text = "Here is a little demo to show how accurate is the traceability attack.\n\
Please note that the French passport will most likely output a false positive because of the anti brute forcing delay.\n\
\n\
@param CO: The cut off used to determine whether the response time is long enough to considerate the passport as vulnerable\n\
@type CO: an integer that represent the cut off in milliseconds\n\
@param valisate: check 3 time before validate the passport as identified\n\
@type validate: An integer that represent the number of validation\n\
\n\
@return: A boolean True whenever the initial passport is on the reader"
        InfoBoxWindows(self, title, text)
        
    def helpReachMaxDialog(self):
        title = "configuration"
        text = "Reader #: (optional) The number of the reader.\n\
For instance, the Omnikey 5321 use the reader number 1 for the RFID communication\n\
\n\
Reach max: French passport implement an anti brute-force\n\
This means anytime a BAC fail, a delay increment before the passport responce.\n\
The MAC traceability is based on the reponse time. Therefore it is impotrant to\n\
reach the maximum delay. By selecting 'Reach max', the application will run\n\
14 wrong BAC.\n\
Note: If 'Reach max' is selected, you will reach a delay of about 15s per\n\
BAC query"
        InfoBoxWindows(self, title, text)
    
    
    # BRUTE FORCE
    #############
    
    def helpDocDialog(self):
        title = "Document Number"
        text = "The document number is print on the passport.\n\
It is composed of 8 to 9 chars. Each chars are either a digit (0-9) either a capital letter (A-Z)\n\
The document number is the 8 or 9 first chars of the MRZ. \n\
\n\
MIN:\n\
 * If min is empty, it is set to 00000000\n\
 * If min is set and the max is empty, the brute force will check for the min set only\n\
\n\
MAX:\n\
 * If min and max are empty, max is set to ZZZZZZZZZ\n\
 * If min and max are set, the brute force will check from min to max"
        InfoBoxWindows(self, title, text)

    def helpDOBDialog(self):
        title = "Date of birth"
        text = "Date of birth of the passport's holder is print on the passport.\n\
It is composed of 6 digits (on the passport): YY MM DD where YY is the two last digits of the year,\n\
MM is the month and DD is the day (e.g. May the 4th 2012 is written 12 05 04)\n\
The date of birth is the 14th-19th chars in the MRZ\n\
\n\
MIN:\n\
 * If min is left YYMMDD, it is set to the date of today - 100 years\n\
 * If min is set and the max is empty, the brute force will check for the date set only\n\
\n\
MAX:\n\
 * If min and max are empty, max is set to the date of today\n\
 * If min and max are set, the brute force will check from min to max"
        InfoBoxWindows(self, title, text)

    def helpDOEDialog(self):
        title = "Date of expiry"
        text = "Date of expiry of the passport is print on the passport.\n\
It is composed of 6 digits (on the passport): YY MM DD where YY is the two last digits of the year,\n\
MM is the month and DD is the day (e.g. May the 4th 2012 is written 12 05 04)\n\
The date of expiry is the 22th-27th chars in the MRZ\n\
\n\
MIN:\n\
 * If min is left YYMMDD, it is set to the date of today - 10 years\n\
 * If min is set and the max is empty, the brute force will check for the date set only\n\
\n\
MAX:\n\
 * If min and max are empty, max is set to the date of today\n\
 * If min and max are set, the brute force will check from min to max"
        InfoBoxWindows(self, title, text)

    def helpCheckDialog(self):
        title = "Check"
        text = "Set and check if all input (e.i. document #, DOB and DOE)\nare correct value."
        InfoBoxWindows(self, title, text)

    def helpStatsDialog(self):
        title = "Get stats"
        text = "Set the data and compute the maximum number of possiblities"
        InfoBoxWindows(self, title, text)

    def helpInitDialog(self):
        title = "Generate ANS/MAC"
        text = "Live brute forcing attakcs takes time because the attack is limited to\n\
the passport and its communication but it is possible for an attacker to perform an offline attack.\n\
During a VALID external authentication (BAC), the passport send a message together with its MAC.\n\
If an attacker capture the message (from a valid authentication), it is possible to perform an\n\
offline brute forcing attack by guessing the KSmac that will match the MAC.\n\
This function generate the message + MAC of a legitmate external authentication an attacker could\n\
capture."
        InfoBoxWindows(self, title, text)

    def helpLiveDialog(self):
        title = "Live brute force"
        text = "Live brute force uses the range set for the document #, the DOB and the DOE\n\
and attemp a BAC with every possibilities until the process succeed.\n\
Couple of passport (such as the belgian one) 'block' the passport after a wrong external\n\
external authentication (i.e. any external authentication even correct will raise an error).\n\
This means with those passports, a reset is needed after each attempt.\n\
\n\
With reset: 9.7 attempts/s (with omnikey 5321)\n\
Without reset: 44.6 attempts/s (with omnikey 5321)"
        InfoBoxWindows(self, title, text)

    def helpOfflineDialog(self):
        title = "Offline brute force"
        text = "Offline brute force uses the ANS/MAC generated in order to guess the KSmac\n\
that will match the MAC. Offline brute forcing attack is way more faster than the live attack.\n\
\n\
About 2404 attempts/s (with omnikey 5321)"
        InfoBoxWindows(self, title, text)
    
    
    # ACTIVE AUTHENTICATION
    #######################

    def helpVulnAADialog(self):
        title = "Is vulnerable?"
        text = "The active authentication vulnerabilities are exploitable only if AA can\n\
occurs before the BAC. This method perfom an internal authentication without performing\n\
a BAC. If the passport raised no error, it means the passport might be vulnerable."
        InfoBoxWindows(self, title, text)

    def helpGetHighestDialog(self):
        title = "Get highest signature"
        text = "The method ask 100 times (default) for the signature of a 8 byte number\n\
and it keeps the highest signature."
        InfoBoxWindows(self, title, text)

    def helpGetModuloDialog(self):
        title = "Get modulo"
        text = "Once authenticate (with a BAC), the method ask for the DG15 (public key).\n\
The modulo is extracted from the key."
        InfoBoxWindows(self, title, text)

    def helpCompareDialog(self):
        title = "Compare"
        text = "In an authentication with RSA algorythm the message is sign with the\n\
private key (private exposant, common modulo). The signature can't be higher than the\n\
modulo. The compare method takes two 'highest signature' or one 'highest signature' and a\n\
modulo compare the difference in pourcent. Low difference means a close/same modulo.\n\
\n\
Accuracy an integer that tells how many digit to compare (6 by default)"
        InfoBoxWindows(self, title, text)

    def helpMatchDialog(self): 
        title = "Match?"
        text = "In an authentication with RSA algorythm the message is sign with the\n\
private key (private exposant, common modulo). The signature can't be higher than the\n\
modulo. Therefore if the signature is higher than the modulo, the passport that generated\n\
the signature is DEFINITLY not the same than the one that generate the modulo.\n\
This method compare a signature and a modulo and check that if the signature MIGHT belong\n\
to the same passport that generated the modulo."
        InfoBoxWindows(self, title, text)

    def helpSaveSignDialog(self):
        title = "Save signature/modulo"
        text = "This methods help to save signatures and modulos for futur tests."
        InfoBoxWindows(self, title, text)

    def helpCheckSignDialog(self):
        title = "Check from file"
        text = "Compare a signature with a modulo or a signature store in a file with the\n\
method save.\n\
If accuracy is set, the method works like 'Compare' if accuracy is empty, it works like the\n\
method 'Match?'"
        InfoBoxWindows(self, title, text)

    def helpSignEverythingDialog(self):
        title = "Sign everything"
        text = "The method send a message to the passport and ask to sign it.\n\
Each passport tested so far require a 8 bytes to sign"
        InfoBoxWindows(self, title, text)
    
    
    # ERROR FINGERPRINTING
    ######################

    def helpSendCustomDialog(self):
        title = "Send custom APDU"
        text = "Send to the passport the APDU set in the form above and print the reponse."
        InfoBoxWindows(self, title, text)

    def helpAddErrorDialog(self):
        title = "Add error"
        text = "Errors are structured and store in a dictionnaire in order to identify a\n\
passport based on the errors it raises.\n\
To be the most accurate, the method expect a country (e.g. BEL, FRA, GER) and the date\n\
of issue. "
        InfoBoxWindows(self, title, text)

    def helpIdentifyDialog(self):
        title = "Identify"
        text = "Since the ICAO didn't standardize the error message regarding APDU, it\n\
possible to identify group of passport. Based on the dictionnaire created with the\n\
method 'Add error' and the response of the APDU set, this method will list all \n\
possibilities the passport MIGHT belong to."
        InfoBoxWindows(self, title, text)



class ScrollFrame(Frame):
    def __init__(self, master, height=16):
        Frame.__init__(self, master)
        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text = Text(self, yscrollcommand=scrollbar.set, height=height)
        self.text.pack(side=TOP, fill=BOTH, expand=True)
        scrollbar.config(command=self.text.yview) 
        
    def insert(self, loc, msg, dis=True):
        if dis:
            self.text.config(state=NORMAL)
        self.text.insert(loc, "{0}".format(msg))
        self.text.yview(END)
        if dis:
            self.text.config(state=DISABLED)
        
        