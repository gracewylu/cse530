from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.core import serializers
from django.views import generic
from django.utils import timezone
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render

# Things to change
# 1. Make global for flattened oldClassesBySemester
# 2. Maybe make new function to get classes

from .models import School, Major, Class


def index(request):

    # showing the majors in order on dropdown and loading page
    majors = Major.objects.order_by('-majorName')
    template = loader.get_template('scheduler/index.html')
    classes = Class.objects.order_by('-className')
    context = {
        'majors': majors,
        'classes': classes,
    }

    # Getting selection of majors
    # 2 majors populated = 2, 1 major populated = 1, none = 0

    chosenMajorOne = request.POST.get('majorChoice1')
    chosenMajorTwo = request.POST.get('majorChoice2')
    prevSchool = request.POST.get('school1')
    prevClass1 = request.POST.get('class1')
    prevClass2 = request.POST.get('class2')
    prevClass3 = request.POST.get('class3')
    prevClass4 = request.POST.get('class4')
    #currently prevClass is the classID, but you can change it in the index.html in the value= part
    print(prevClass1)
    print(prevClass2)
    print(prevClass3)
    print(prevClass4)

    oldSchedule = [] # will be populated once transcript parser is up
    
    try:
        for index1 in range(0,8):
            currentOldSemester = []

            for index2 in range(1,8):
                classIndex = index1*7+index2
                oldClassID = request.POST.get('class' + str(classIndex))
                if oldClassID == 'Class Name': print("NOT ALLOWED")
                else:
                    currentOldSemester.append(Class.objects.get(classID = oldClassID))

            if len(currentOldSemester) == 0: continue
            else:
                oldSchedule.append(currentOldSemester)

        print(oldSchedule)
    except Class.DoesNotExist:
        return HttpResponse(template.render(context, request))

    # Feeds majors and schools into function, populates page
    try:
        majorOneObj = Major.objects.get(majorName = chosenMajorOne)
        majorTwoObj = Major.objects.get(majorName = chosenMajorTwo)
        schoolObj = School.objects.get(schoolCode = majorOneObj.schoolCode)

        print("Old sched 1")
        print(oldSchedule)

        context = {
            'majors': majors,
            'classes': classes,
            'schedule' : convertToHTML(getFourYearSchedule(oldSchedule,schoolObj, majorOneObj, majorTwoObj)),
        }

    except Major.DoesNotExist:
        try:
            majorOneObj = Major.objects.get(majorName = chosenMajorOne)
            schoolObj = School.objects.get(schoolCode = majorOneObj.schoolCode)

            print("Old sched 2")
            print(oldSchedule)

            context = {
                'majors': majors,
                'classes': classes,
                'schedule' : convertToHTML(getFourYearSchedule(oldSchedule,schoolObj, majorOneObj)),
            }

        except Major.DoesNotExist:
            try:
                majorOneObj = Major.objects.get(majorName = chosenMajorTwo)

                schoolObj = School.objects.get(schoolCode = majorOneObj.schoolCode)

                print("Old sched 3")
                print(oldSchedule)

                context = {
                    'majors': majors,
                    'classes': classes,
                    'schedule' : convertToHTML(getFourYearSchedule(oldSchedule,schoolObj, majorOneObj)),
                }

            except Major.DoesNotExist:
                return HttpResponse(template.render(context, request))


    # if scenario > 0:
    #     listOfClassesOfChosenMajorOne = classForChosenMajorOne.listOfClasses
    #     listOfClassesOfChosenMajorOneStripped = [x.strip() for x in listOfClassesOfChosenMajorOne.split(',')]
    #     if scenario > 1:
    #         listOfClassesOfChosenMajorTwo = classForChosenMajorTwo.listOfClasses
    #         listOfClassesOfChosenMajorTwoStripped = [x.strip() for x in listOfClassesOfChosenMajorTwo.split(',')]
    #         context = {
    #             'majors': majors,
    #             'schedule' : convertToHTML(getFullSemester(listOfClassesOfChosenMajorOneStripped, listOfClassesOfChosenMajorTwoStripped)),
    #         }
    #     else:
    #         context = {
    #             'majors': majors,
    #             'schedule' : convertToHTML(getFullSemester(listOfClassesOfChosenMajorOneStripped)),
    #         }
    # else:
    #     pass


    return HttpResponse(template.render(context, request))



def getFourYearSchedule(oldSchedule, school, majorOne, majorTwo=None):

    # create fourYearSchedule object
    fys = fourYearSchedule()

    # feed in old schedule as list of lists
    fys.oldClassesBySemester = oldSchedule

    # drawing hard coded classes per major/school out
    listAllClassID = []
    listSch = [x.strip() for x in school.listOfClasses.split(',')]
    listMaj1 = [x.strip() for x in majorOne.listOfClasses.split(',')]

    if majorTwo is not None:
        listMaj2 = [x.strip() for x in majorTwo.listOfClasses.split(',')]
        listAllClassID = list(set().union(listMaj1, listMaj2, listSch)) # might fuck up

    else:
        listAllClassID = list(set().union(listMaj1, listSch)) # might fuck up



    # remove duplicates from based on old Schedule
    fys.eliminateTaken(listAllClassID)

    # make a new list of class objects
    listAllClassObj = []
    for classIDs in listAllClassID:
        listAllClassObj.append(Class.objects.get(pk = int(classIDs)))

    listAllClassObjForPrereqCheck = list(listAllClassObj)

    #removes classes already taken from list of classes that need to be taken so that the classes
    #are not considered when checking for prereqs but still included in the list of prereqs
    listAllClassObj = list(set(listAllClassObj) - set(fys.flatten(fys.oldClassesBySemester)))

    # carry out prereq check
    while len(listAllClassObj) != 0:

        listOfClassesToBeRemoved = []
        # listOfClassesToBeRevisited = []

        for classes in listAllClassObj:
            # print(" ")
            # print("This is current class")
            # print(classes)


            if classes.numPrereqs == 0:
                fys.addClass(classes)

                # print("This is listAllClassObj: ")
                # print(listAllClassObj)
                # listAllClassObj.pop(listAllClassObj.index(classes))
                listOfClassesToBeRemoved.append(classes)
                # print("This is listAllClassObj: ")
                # print(listAllClassObj)

            else:
                # parses list of prereq
                listOfPrereqs = [x.strip() for x in classes.listOfPrereqs.split(',')]
                # print("This is current class: ")
                # print(classes)
                # print("This is list of prereqs: ")
                # print(listOfPrereqs)
                listOfPrereqsClass = []

                for classIDs in listOfPrereqs:
                    # print("This is current classID: " + classIDs)
                    listOfPrereqsClass.append(Class.objects.get(pk = int(classIDs))) # may change?

                # if all prereqs are fulfilled, allPrereqsFulfilled stays set at True; otherwise it gets changed to False, break
                allPrereqsFulfilled = True
                for prereq in listOfPrereqsClass:
                    if not fys.searchClass(prereq):
                        if prereq not in listAllClassObjForPrereqCheck: # might break
                            listAllClassObj.append(prereq)
                            listAllClassObjForPrereqCheck.append(prereq)
                        allPrereqsFulfilled = False
                        break

                if allPrereqsFulfilled:
                    if fys.addClass(classes):
                        # listAllClassObj.pop(listAllClassObj.index(classes))
                        #print("This is current class") MEGAN 
                        #print(classes)
                        #print('\n')
                        #print("This is currently what's in listAllClassObj")
                        #print(listAllClassObj)
                        #print('\n')
                        listOfClassesToBeRemoved.append(classes)

                    # else:
                        # listAllClassObj.append(listAllClassObj.pop(listAllClassObj.index(classes)))
                # else:
                    # listAllClassObj.append(listAllClassObj.pop(listAllClassObj.index(classes)))

        for classes in listOfClassesToBeRemoved:
            listAllClassObj.remove(classes)

        del listOfClassesToBeRemoved[:]

        # for classes in listOfClassesToBeRevisited:
        #     listAllClassObj.append()

        fys.switchSem()


    return fys


class fourYearSchedule:

    def __init__(self):
        self.oldClassesBySemester = []
        # self.classesTaken = []
        self.currentSemester = []
        self.newClassesBySemester = []
        self.creditLimit = 18

    # switches to next semester artificially
    def switchSem(self):
        print "SWITCHING SEMESTERS"
        self.newClassesBySemester.append(list(self.currentSemester)) # pointer issue may arise
        del self.currentSemester[:]
        # print("This is current semester")
        # print(self.currentSemester)

    # flatten flattens a list of lists (typically used to denote semesters)
    def flatten(self, listOfListToBeFlattened):

        returnSet = set()
        for semester in listOfListToBeFlattened:
            for classes in semester:
                returnSet.add(classes)

        return returnSet

    # isFall returns True if fall, False if spring
    def isFall(self):
        return (len(self.newClassesBySemester) + len(self.oldClassesBySemester)) % 2 == 0 # kinda confusing, lookout for this

    # eliminateTaken eliminates classes already taken from list of classes needed
    # only called at start after user submits major combinations
    # requires preprocessing of oldClassesBySemester followed by a removal of intersection
    def eliminateTaken(self, classesNeeded):

        oldClasses = self.flatten(self.oldClassesBySemester)

        intersection = set(oldClasses).intersection(set(classesNeeded))
        return list(set(classesNeeded).difference(intersection))

    # addClass checks if there's space in the current semester, and then checks if the class can be taken in that semester
    # It returns True if class can be added, and False otherwise
    def addClass(self, newClass):

        # print("addClass called on: " + newClass.className)

        currentSemesterCredit = 0
        for classes in self.currentSemester:
            currentSemesterCredit += classes.creditNum

        if currentSemesterCredit + newClass.creditNum > self.creditLimit:
            # print("This is current semester before appending: ")
            # print(self.currentSemester)

            self.newClassesBySemester.append(list(self.currentSemester)) # pointer issue may arise
            del self.currentSemester[:]

            # print("This is current semester after deleting: ")
            # print(self.currentSemester)

        if (newClass.semOffered == 2) or (self.isFall() and newClass.semOffered == 0) or (not(self.isFall())and newClass.semOffered == 1):
            self.currentSemester.append(newClass)
            # print("This is current semester after appending: ")
            # print(self.currentSemester)

            return True

        else:
            return False


    # searchClass called whenever we need to check for a class as prereq in oldClassesBySemester and newClassesBySemester
    def searchClass(self, classToTake):

        classesToCheck = self.flatten(self.oldClassesBySemester).union(self.flatten(self.newClassesBySemester))
        return (classToTake in classesToCheck) # might give some bugs


# def parseTranscript():
#
#     return oldClassesBySemester


# fys = new fourYearSchedule()
# fys.oldClassesBySemester = parseTranscript()
# < draw



#HELPER METHODS USED IN VIEWS

# Pseudo code:
# 1. get both majors
# 2. for each major, get classes
# 3. run a union of both classes
# 4. populate majors onto schedule, assuming cap of 18 credits per semester
# 5. add additional features if necessary

# def getFullSemester(majorOne, majorTwo=None):
#
#     fourYearSchedule = []
#     creditLimit = 18
#
#     if majorTwo is not None:
#         listOfAllClassIDs = list(set().union(majorOne, majorTwo))
#         listOfAllClasses = []
#
#         for classIDs in listOfAllClassIDs:
#             listOfAllClasses.append(Class.objects.get(pk = int(classIDs)))
#
#         listOfAllClasses.sort(key = lambda classes: classes.numPrereqs)
#
#         populate(listOfAllClasses,fourYearSchedule,creditLimit)
#
#
#     return fourYearSchedule


# def populate(allClasses, fourYearSchedule, creditLimit):
#
#
#     currentSemesterClasses = []
#     currentCredit = 0
#
#     while len(allClasses) > 3:
#         print(len(allClasses))
#         for classObject in allClasses:
#             if allPrereqFulfilled(fourYearSchedule, classObject) is True:
#                 addedCredit = classObject.creditNum
#                 if currentCredit + addedCredit < creditLimit:
#                     currentSemesterClasses.append(classObject)
#                     allClasses.remove(classObject)
#                     currentCredit += addedCredit
#                     print("added")
#
#                 else:
#                     fourYearSchedule.append(currentSemesterClasses)
#                     currentSemesterClasses = []
#                     currentSemesterClasses.append(classObject)
#                     allClasses.remove(classObject)
#                     currentCredit = addedCredit
#                     print("added")
#             else:
#                 # allClasses.append(allClasses.pop(0))
#                 pass
#
#         fourYearSchedule.append(currentSemesterClasses)
#         currentSemesterClasses = []
#
#     emptySemesters = 8 - len(fourYearSchedule)
#     for index in range(emptySemesters):
#         fourYearSchedule.append([])


# def allPrereqFulfilled(fourYearSchedule, classObject):
#
#     if classObject.numPrereqs == 0: return True
#
#     numPrereqsFulfilled = 0
#     listOfPrereqs = [x.strip() for x in classObject.listOfPrereqs.split(',')]
#
#     for prereq in listOfPrereqs:
#
#         canITakeIt = False
#         for semester in fourYearSchedule:
#             for classes in semester:
#                 if int(classes.classID) == int(prereq):
#                     canITakeIt = True
#         if canITakeIt is True:
#             numPrereqsFulfilled += 1
#
#     if numPrereqsFulfilled == len(listOfPrereqs): return True
#     else: return False


def convertToHTML(fys):

    oldFourYearSchedule = fys.oldClassesBySemester
    newfourYearSchedule = fys.newClassesBySemester # have to add oldSemesters
    # print("This is the FYS")
    # print(fourYearSchedule)

    stringOfHTML = """<thead>
                    <tr>
                        <th>Freshman Fall</th>
                        <th>Freshman Spring</th>
                        <th>Sophomore Fall</th>
                        <th>Sophomore Spring</th>
                        <th>Junior Fall</th>
                        <th>Junior Spring</th>
                        <th>Senior Fall</th>
                        <th>Senior Spring</th>
                    </tr>
                </thead>"""
    for classes in range(1,6):
        stringOfHTML += "<tr>"
        semestersLeft = 8 - len(oldFourYearSchedule) - len(newfourYearSchedule)
        for semester in oldFourYearSchedule:
            if classes > len(semester):
                stringOfHTML += "<td >--</td>"
            else:
                stringForClass = "<td >" + semester[classes-1].className + "</td>"
                stringOfHTML += stringForClass
        for semester in newfourYearSchedule:
            if classes > len(semester):
                stringOfHTML += "<td>Electives</td>"
            else:
                stringForClass = "<td>" + semester[classes-1].className + "</td>"
                stringOfHTML += stringForClass
        if (semestersLeft > 0):
            for semester in range (0,semestersLeft):
                stringOfHTML += "<td >Electives</td>"
        stringOfHTML += "</tr>"

    return stringOfHTML