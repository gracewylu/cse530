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

# import sqlite3 as lite
# import sys
# import dateutil.parser
# import time
# import pytz
# import json

from .models import Major, Class


def index(request):
    majors = Major.objects.order_by('-majorName')
    template = loader.get_template('scheduler/index.html')
    context = {
        'majors': majors,
    }

    # 2 majors populated = 2, 1 major populated = 1, none = 0
    scenario = 0

    chosenMajorOne = request.POST.get('majorChoice1')
    chosenMajorTwo = request.POST.get('majorChoice2')

    try:
        classForChosenMajorOne = Major.objects.get(majorName = chosenMajorOne)
        classForChosenMajorTwo = Major.objects.get(majorName = chosenMajorTwo)
        scenario = 2

    except Major.DoesNotExist:
        try:
            classForChosenMajorOne = Major.objects.get(majorName = chosenMajorOne)
            scenario = 1

        except Major.DoesNotExist:
            try:
                classForChosenMajorOne = Major.objects.get(majorName = chosenMajorTwo)
                scenario = 1

            except Major.DoesNotExist:
                scenario = 0
                return HttpResponse(template.render(context, request))

    if scenario > 0:
        listOfClassesOfChosenMajorOne = classForChosenMajorOne.listOfClasses
        listOfClassesOfChosenMajorOneStripped = [x.strip() for x in listOfClassesOfChosenMajorOne.split(',')]
        if scenario > 1:
            listOfClassesOfChosenMajorTwo = classForChosenMajorTwo.listOfClasses
            listOfClassesOfChosenMajorTwoStripped = [x.strip() for x in listOfClassesOfChosenMajorTwo.split(',')]
            context = {
                'majors': majors,
                'schedule' : convertToHTML(getFullSemester(listOfClassesOfChosenMajorOneStripped, listOfClassesOfChosenMajorTwoStripped)),
            }
        else:
            context = {
                'majors': majors,
                'schedule' : convertToHTML(getFullSemester(listOfClassesOfChosenMajorOneStripped)),
            }
    else:
        pass


    return HttpResponse(template.render(context, request))



#HELPER METHODS USED IN VIEWS

# Pseudo code:
# 1. get both majors
# 2. for each major, get classes
# 3. run a union of both classes
# 4. populate majors onto schedule, assuming cap of 18 credits per semester
# 5. add additional features if necessary

def getFullSemester(majorOne, majorTwo=None):

    fourYearSchedule = []
    creditLimit = 18

    if majorTwo is not None:
        listOfAllClassIDs = list(set().union(majorOne, majorTwo))
        listOfAllClasses = []

        for classIDs in listOfAllClassIDs:
            listOfAllClasses.append(Class.objects.get(pk = int(classIDs)))

        listOfAllClasses.sort(key = lambda classes: classes.numPrereqs)

        populate(listOfAllClasses,fourYearSchedule,creditLimit)


    return fourYearSchedule


def populate(allClasses, fourYearSchedule, creditLimit):

    
    currentSemesterClasses = []
    currentCredit = 0

    while len(allClasses) > 3:
        print(len(allClasses))
        for classObject in allClasses:
            if allPrereqFulfilled(fourYearSchedule, classObject) is True:
                addedCredit = classObject.creditNum
                if currentCredit + addedCredit < creditLimit:
                    currentSemesterClasses.append(classObject)
                    allClasses.remove(classObject)
                    currentCredit += addedCredit
                    print("added")

                else:
                    fourYearSchedule.append(currentSemesterClasses)
                    currentSemesterClasses = []
                    currentSemesterClasses.append(classObject)
                    allClasses.remove(classObject)
                    currentCredit = addedCredit
                    print("added")
            else:
                # allClasses.append(allClasses.pop(0))
                pass

        fourYearSchedule.append(currentSemesterClasses)
        currentSemesterClasses = []

    emptySemesters = 8 - len(fourYearSchedule)
    for index in range(emptySemesters):
        fourYearSchedule.append([])


def allPrereqFulfilled(fourYearSchedule, classObject):

    if classObject.numPrereqs == 0: return True

    numPrereqsFulfilled = 0
    listOfPrereqs = [x.strip() for x in classObject.listOfPrereqs.split(',')]

    for prereq in listOfPrereqs:

        canITakeIt = False
        for semester in fourYearSchedule:
            for classes in semester:
                if int(classes.classID) == int(prereq):
                    canITakeIt = True
        if canITakeIt is True:
            numPrereqsFulfilled += 1

    if numPrereqsFulfilled == len(listOfPrereqs): return True
    else: return False


def convertToHTML(fourYearSchedule):
    stringOfHTML = ""
    for classes in range(1,8):
        stringOfHTML += "<tr>"
        for semester in fourYearSchedule:
            if classes > len(semester):
                stringOfHTML += "<td bgcolor=\"#00FF00\">Elective</td>"
            else:
                stringForClass = "<td>" + semester[classes-1].className + "</td>"
                stringOfHTML += stringForClass
        stringOfHTML += "</tr>"
    return stringOfHTML