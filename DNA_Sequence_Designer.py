# Import relevant python packages. Written and tested in python 3.7
# tkinter for gui creation
# itertools for sequence combinatorics
# clipboard for copy and paste functionality
# os for file path functionality
import tkinter as tk
from tkinter import simpledialog
import itertools
import clipboard
import os

#All gui aspects are include as field in the Application class. tk.Frame is a dsuperclass that includes the functionality for the application
class Application(tk.Frame):
    # A constructor for creating the application gui.
    def __init__(self, master=None):    
        tk.Frame.__init__(self, master)   
        self.grid()                       
        self.createWidgets()
   
    #Initialization of some relevant fields outside of the constructor
    bases =["A","G","C","T"]
    availableSequences = []
    slidingWindow = -1
    extendingStrand = ""
    designedSequence = ""

    #The function that creates each widget on the application screen
    def createWidgets(self):
        self.columnconfigure(0, minsize = "1c")
        self.columnconfigure(1, minsize = "1c")
        self.columnconfigure(2, minsize = "1c")
        self.columnconfigure(3, minsize = "1c")
        self.columnconfigure(4, minsize = "1c")

        #Creates an array that is the length of the number of existing strands in the system (provided by the user)
        #Each entry in the array is then assigned as a reference to a entry box widget which are arranged on the screen
        self.strandsArray = [None] * numberOfStrands
        for i in range(numberOfStrands):
            self.strandsArray[i] = tk.Entry(self)
            self.strandsArray[i].grid(row = i + 1, column = 1, sticky = tk.E)

        #Create and grids an entry box for inputting the number of nucleotides required for sequence symmetry
        self.nucleotides = tk.Entry(self)
        self.nucleotides.grid(row = 0, column = 1, sticky = tk.E)

        #Creates a button for starting the sequence generation algortithm after all relevant information has been included
        self.compute = tk.Button(self, text = "begin", command = self.compute)
        self.compute.grid(row = 1, column = 2, sticky = tk.W)


        #Creates an integer control variable for the "extend existing strand" checkbutton. This variable corresponds to the state of the button
        self.checked = tk.IntVar()
        #Creates a button mapped to the "checked" control variable and the "extendingClicked" event handler
        self.startFromStrand = tk.Checkbutton(self, text = "Extend Existing Strand?", variable = self.checked)
        self.startFromStrand.grid(row = 0, column = 3, sticky = tk.E)
        self.startFromStrand.bind('<Button-1>',self.extendingClicked)

        #Creates four buttons for appending "A", "T", "C", or "G" to the built sequence. The buttons are disabled until compute is clicked
        self.A = tk.Button(self, text = "A", command = self.aClicked, state = "disabled", width = 10)
        self.T = tk.Button(self, text = "T", command = self.tClicked, state = "disabled", width = 10)
        self.C = tk.Button(self, text = "C", command = self.cClicked, state = "disabled", width = 10)
        self.G = tk.Button(self, text = "G", command = self.gClicked, state = "disabled", width = 10)
        self.A.grid(row = numberOfStrands + 3, column = 1)
        self.T.grid(row = numberOfStrands + 3, column = 2)
        self.C.grid(row = numberOfStrands + 3, column = 3)
        self.G.grid(row = numberOfStrands + 3, column = 4)

        #Creates an text field (not editable by the user) that displays the last 20 bases of the designed strand
        self.strandOut = tk.Label(self)
        self.strandOut.grid(column = 0, row = numberOfStrands + 1, sticky = tk.W)

        #Creates a text label for the "Bases for symmetry" text field
        self.labelSymmetry = tk.Label(self, text = "Bases for symmetry")
        self.labelSymmetry.grid(row = 0, column = 0, sticky = tk.N + tk.E)

        #Creates labels for each of the entry boxes for existing DNA sequences
        self.labelSequenceArray = [None]*(numberOfStrands)
        for i in range(numberOfStrands):
            self.labelSequenceArray[i] = tk.Label(self, text = "Enter Sequence" + " " + str(i+1) + "")
            self.labelSequenceArray[i].grid(row = i+1, column = 0, sticky = tk.N + tk.E)

        #Creates a label field that displays the length of the current strand being extended
        self.labelLength = tk.Label(self, text = "Length: 0 nt")
        self.labelLength.grid(row= numberOfStrands + 2, column = 1)

        #Creates a button to copy the generated sequence to the clipboard
        self.copyToClipboard = tk.Button(self, text = "Copy sequence to clipboard", command = self.ctc)
        self.copyToClipboard.grid(column = 0, row = numberOfStrands + 3)
        
        #Creates a button to save the generated sequence as a text file
        self.saveAsTxt = tk.Button(self, text = "Save strand as .txt", command = self.toText)
        self.saveAsTxt.grid(row = numberOfStrands + 4, column = 0)

        #Creates a menu button to let the user chose which existing strand to extend
        #This menu is disabled until "extend existing strand?" is checked
        self.mb = tk.Menubutton(self, text='Which Strand?',
                             relief="raised", 
                             state="disabled")
        self.mb.grid()
        
        #Creates the framework for menu options assosiated with the above menu button
        self.mb.menu = tk.Menu(self.mb, tearoff=0)
        self.mb['menu'] = self.mb.menu
    
    #When the "copy to clipboard" button is clicked, the generated sequence is copied to the systems clipboard
    def ctc(self):
        clipboard.copy(self.designedSequence)
    
    #Produces a dialogue box to ask for the text file name, then saves the generated sequence as a text file
    def toText(self):
        name = simpledialog.askstring(title = "fileName", prompt = "File name: ")
        if name is not None:
            name = name + '.txt'
            text_file = open(name, "w")
            n = text_file.write(self.designedSequence)
            text_file.close()

    #When the "A" button is clicked, adds "A" to the generated sequence. Unavailable if "A" will break sequence symmetry rules
    def aClicked(self):
        self.designedSequence += "A"
        self.availableSequences.remove(self.designedSequence[len(self.designedSequence) - (self.slidingWindow):len(self.designedSequence)])
        self.buildSequence()
     
    #When the "T" button is clicked, adds "T" to the generated sequence. Unavailable if "T" will break sequence symmetry rules    
    def tClicked(self):
        self.designedSequence += "T"
        self.availableSequences.remove(self.designedSequence[len(self.designedSequence) - (self.slidingWindow):len(self.designedSequence)])
        self.buildSequence()

    #When the "C" button is clicked, adds "C" to the generated sequence. Unavailable if "C" will break sequence symmetry rules
    def cClicked(self):
        self.designedSequence += "C"
        self.availableSequences.remove(self.designedSequence[len(self.designedSequence) - (self.slidingWindow):len(self.designedSequence)])
        self.buildSequence()
    
    #When the "G" button is clicked, adds "G" to the generated sequence. Unavailable if "G" will break sequence symmetry rules
    def gClicked(self):
        self.designedSequence += "G"
        self.availableSequences.remove(self.designedSequence[len(self.designedSequence) - (self.slidingWindow):len(self.designedSequence)])
        self.buildSequence()  



    def setExtendingStrand(self, n):
        self.extendingStrand = self.strandsArray[n].get().upper()

    #Enables and displays the popup menu to chose the strand to extend when the "extending strand" option is checked
    firstClick = True
    def extendingClicked(self, event):
        if self.checked.get() == 0:
            self.mb["state"] = "normal"
            if self.firstClick:
                for i in range(numberOfStrands):
                    self.mb.menu.add_radiobutton(label = "Strand" + str(i+1))
        else:
            self.mb["state"] = "disabled"
        self.firstClick = False


    #Determines if all of the characters in a string are uppercase and that the streng is greater than or equal to the sliding window length
    def isValidSequence(self, string):
        isValid = True
        for char in string:
            if char.upper() != "A" and char.upper() != "T" and char.upper() != "C" and char.upper() != "G": 
                   isValid = False
        if len(string) < self.slidingWindow:
            isValid = False
        return isValid

    #Converts a list into an unordered set. Note this does not modify the input list, it produces an output that must be assigned to a variable
    def removeDuplicates(self, list):
        returnList = []
        [returnList.append(x) for x in list if x not in returnList]
        return returnList

    #Converts a string into all posible substring of the length specified by "sliding window" and returns them as a list
    def chunkByWindow(self, string):
        returnList = []
        for i in range(len(string) - (self.slidingWindow - 1)):
            stringToAppend = ""
            for j in range(self.slidingWindow):
                stringToAppend += string[i+j]
            returnList.append(stringToAppend)
        return(returnList)

    #Converts a list of strings or characters into a single string
    def listToString(self, list):
        returnString = ""
        for string in list:
            returnString += string
        return returnString

    #Flattens a list of lists into a 1D list
    def flattenListOfLists(self, listOfLists):
        returnList = [i for list in listOfLists for i in list]
        return returnList

    #Returns an version of the list "available" that removes any elements from "available" that were contained in "taken"
    def removeMatches(self, available, taken):
        returnList = []
        [returnList.append(x) for x in available if x not in taken]
        return returnList


    #Analyses the existing sequence that has been built and decides which of the four nucleotides can be added without breaking symmetry rules
    #The output of this function is enabling a supset of the A,T,C,G buttons. Each button can then be used to add a letter and call buildSequence
    def buildSequence(self):
        #Displays up to 20 bases of the currently designed sequence
        if len(self.designedSequence) >= 20:
            self.strandOut["text"] = "..." + self.designedSequence[len(self.designedSequence) - 20:len(self.designedSequence)]
        else:
            self.strandOut["text"] = self.designedSequence
        self.labelLength["text"] = "Length: " + str(len(self.designedSequence)) + " nt"

        #Sets each nucleotide button back to disabled to aid the logic in the next branch
        self.A["state"] = "disabled"
        self.T["state"] = "disabled"
        self.C["state"] = "disabled"
        self.G["state"] = "disabled"

        #Determines if the user inputted sequence or existing sequence is long enough for sequence symmetry minimization
        if len(self.designedSequence) < self.slidingWindow:
            raise Exception("The starting sequence is not long enough to use sequence symmetry minimization with the specified symmetry cutoff")
        #If the sequence is long enough, it checks to see which bases can be added without reusing any substrings and enables the appropriate buttons
        else:
            nextArray = []
            #determines if any of the next possible substrings have been used, and otherwise enabled the respective buttons
            base = self.designedSequence[len(self.designedSequence) - (self.slidingWindow - 1):len(self.designedSequence)]
            possible = [base + "A", base + "T", base + "C", base + "G"]
            [nextArray.append(x[-1]) for x in possible if x in self.availableSequences]
            if "A" in nextArray:
                self.A["state"] = "normal"
            if "T" in nextArray:
                self.T["state"] = "normal"
            if "C" in nextArray:
                self.C["state"] = "normal"
            if "G" in nextArray:
                self.G["state"] = "normal"

    #Carries out the sequence symmetry minimization combinatorial logic based on the user specified initial conditions
    def compute(self):
        #Intialized the designed sequence to the empty string
        self.designedSequence = ""
        #If the "Extend existing strand" option is selected, it find the correct strrand and adds it to the start of the designed sequece
        if self.checked.get() == 1:
            self.designedSequence += self.extendingStrand
            self.strandOut["text"] = self.designedSequence
        else:
            self.designedSequence = simpledialog.askstring(title = "Starting Sequence", prompt = "Enter a starting sequence longer than or equal to the specified bases for symmetry: ").upper()
            self.strandOut["text"] = self.designedSequence
        #Checks to make sure the entry for "nucleotides for symmetry is valid
        #If so, all of the possible combinations of the specified substring length are computed and storeds in a list
        #If not, no computation is carried out
        if self.nucleotides.get().isdigit():
            self.slidingWindow = int(self.nucleotides.get())
            combinations= itertools.product(self.bases,repeat=self.slidingWindow)
            self.availableSequences = list(combinations)
            self.availableSequences = [self.listToString(list) for list in self.availableSequences]
        else:
            return
        #Intiilized a list of used sequences to an empty list
        usedSequences = []
        #Verify that each imout  strand only contains valid characters, and if so add it to the used Sequences list
        for strand in self.strandsArray:
            if not(self.isValidSequence(strand.get())) or not (strand.get()):
                return
            else:
                usedSequences.append(strand.get().upper())
        #determines all of the unique substrings of the imported sequences and removes any of these used sequences from the available sequence list
        usedSequences = [chunk for seq in usedSequences for chunk in self.chunkByWindow(seq)]
        usedSequences = self.removeDuplicates(usedSequences)
        self.availableSequences = self.removeMatches(self.availableSequences, usedSequences)
        #calls the buildSequence function which handles all sequence building after the intial computation
        self.buildSequence()

            
        


#Before opening, asks the user how many DNA strands they will be importing
numberOfStrands = int(input("Number of existing strands: "))

#Creats and labels the application
app = Application()                       
app.master.title('DNA Sequence Generator')    
app.mainloop()           
