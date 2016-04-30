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
import pdb

# import sqlite3 as lite
# import sys
# import dateutil.parser
# import time
# import pytz
# import json

from .models import Major, Class
#from .forms import UploadFIleForm
# from .placewithfunction import parse_uploaded_file
# from .forms import MajorForm

# def upload_file(request):
#     if request.method == 'POST':
#         form = UploadFIleForm(request.POST, request.FILES)
#         if form.is_valid():
#             #parse_uploaded_file(request.FILES['file'])
#             # go back to index page
#             # return HttpResponseRedirect('/')
#     else:
#         form = UploadFIleForm
#     #go back to index page

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

        print(classForChosenMajorOne.schoolCode)


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

def creditsInSem(semClasses):
    numCredits = 0;
    for c in semClasses:
        numCredits += c.creditNum
    return numCredits


def getFullSemester(majorOne, majorTwo=[]):

    fourYearSchedule = []
    creditLimit = 18

    # if majorTwo is not None:
    listOfAllClassIDs = list(set().union(majorOne, majorTwo))
    listOfAllClasses = []

    for classIDs in listOfAllClassIDs:
        listOfAllClasses.append(Class.objects.get(pk = int(classIDs)))


    currentSemesterClasses = []
    currentCredit = 0

    #listOfAllClasses.sort(key=lambda x: x.courseCode, reverse=False)

    classesTaken = []
    coursesPerSem = creditLimit/3;
    counter = 0;

    while counter < len(listOfAllClasses):
        c = listOfAllClasses[counter];
        if c.listOfPrereqs:
            if c.listOfPrereqs != "0":
                for p in c.listOfPrereqs.split(', '):
                        prereqDone = True
                        prereqClass = Class.objects.get(pk = int(p))
                        if prereqClass not in classesTaken:
                            prereqDone = False
                if prereqDone:
                    classesTaken.append(c)
                    counter += 1
                else:
                    if prereqClass not in listOfAllClasses:
                        listOfAllClasses.append(prereqClass)
                    listOfAllClasses.append(listOfAllClasses.pop(counter))
            else:
                classesTaken.append(c)
                counter += 1
        else:
            classesTaken.append(c)
            counter += 1

    listOfAllClasses = classesTaken


    for i in range(0,7):
        fourYearSchedule.append([])

    semesterCounter = 0;
    for classObject in listOfAllClasses:
        #pdb.set_trace()
        if (creditsInSem(fourYearSchedule[semesterCounter]) + classObject.creditNum > 18):
            semesterCounter += 1;
            # ("incrementing %i", semesterCounter)
        addedCredit = classObject.creditNum
        latestSemester = semesterCounter;
        addSemester = 0;
        sameSemester = False;
        if classObject.listOfPrereqs and classObject.listOfPrereqs != "0":
            for p in classObject.listOfPrereqs.split(', '):
                prereqClass = Class.objects.get(pk = int(p))
                for i in range(len(fourYearSchedule)):
                    if prereqClass in fourYearSchedule[i] and i >= latestSemester:
                            latestSemester = i
                            sameSemester = True
            if sameSemester:
                addSemester = latestSemester + 1
            else:
                addSemester = latestSemester
        else:
            addSemester = semesterCounter
        if((classObject.semOffered == 0 and addSemester % 2 != 0) or (classObject.semOffered == 1 and addSemester % 2 == 0) ):
            if(creditsInSem(fourYearSchedule[addSemester-1]) + classObject.creditNum > 18):
                addSemester += 1;
            else:
                addSemester -= 1;
        #else if(classObject.semOffered == 1 and addSemester % 2 == 0):

        fourYearSchedule[addSemester].append(classObject)
        currentCredit += addedCredit


                

    return fourYearSchedule


def convertToHTML(fourYearSchedule):
    stringOfHTML = ""
    for classes in range(1,8):
        stringOfHTML += "<tr>"
        for semester in fourYearSchedule:
            if classes > len(semester):
                stringOfHTML += "<td bgcolor=\"#00FF00\">FREE TIME</td>"
            else:
                stringForClass = "<td>" + semester[classes-1].className + "</td>"
                stringOfHTML += stringForClass
        stringOfHTML += "</tr>"
    return stringOfHTML