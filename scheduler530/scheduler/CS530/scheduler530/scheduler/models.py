from __future__ import unicode_literals

from django.db import models


# for anything that stores a list of ints, we should consider using this custom model field: http://stackoverflow.com/questions/24749762/i-have-a-list-of-long-integers-that-i-assign-to-a-django-model-charfield-the-li

# any updates need to be remigrated into the db
# list of updates

# Table for every school that lists requirements to get a degree with that school
class School(models.Model):
    schoolCode = models.CharField(primary_key=True, max_length=1)
    schoolName = models.CharField(max_length=60)
    listOfClasses = models.TextField(max_length=None, null=True)
    creditsToGraduate = models.SmallIntegerField(default=120)

    attributes = models.TextField(max_length=None, null=True, blank=True)
    description = models. TextField(max_length=None, null=True, blank=True)
    
    def __unicode__(self):
        sID = str(self.schoolCode)
        return sID

# Table for every major showing requirements to get that major
class Major(models.Model):
    majorID = models.AutoField(primary_key=True)
    majorName = models.CharField(max_length=60)
    schoolCode = models.ForeignKey(School, on_delete=models.CASCADE)

    listOfClasses = models.TextField(max_length = None, null=False) #JSON-serialized (text version)

    attributes = models.TextField(max_length=None, null=True)
    description = models. TextField(max_length=None, null=True)

    def __unicode__(self):
        mID = str(self.majorName)
        return mID

# Table for every class listing requirements to take that class
class Class(models.Model):

    # admin info
    classID = models.AutoField(primary_key=True)
    className = models.CharField(max_length=60)
    schoolCode = models.ForeignKey(School, on_delete=models.CASCADE)
    deptID = models.CharField(null = False, max_length=4)
    courseCode = models.CharField(max_length = 5)

    # scheduler info
    creditNum = models.SmallIntegerField(null = False, default = 3)
    semOffered = models.SmallIntegerField(null = False, default = 2) # 2 if offered both semesters, 1 if offered in spring only, 0 if offered in Fall only
    listOfPrereqs = models.TextField(max_length = None, null=True, blank=True) #JSON-serialized (text version)
    numPrereqs = models.SmallIntegerField(null = True, blank=True)
    classStanding = models.SmallIntegerField(null = False, default = 0)

    attributes = models.TextField(max_length=None, null=True)
    description = models. TextField(max_length=None, null=True)

    def __unicode__(self):
        cID = str(self.className)
        return cID


# c = Class(className = "Computer Science", schoolCode = "E", deptID = 81, courseCode = "131", creditNum = 3, semOffered = 2,listOfPrereqs = "", numPrereqs = 0)

