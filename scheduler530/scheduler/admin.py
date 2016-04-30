from django.contrib import admin

from .models import Major, Class, School


# Things to work on:
# 1. Compressing the add forms so they look better
# 2. Appending the lists when seeing it in the admin site, so that they don't take up too much space'
# 3. sorting of results by ID (might have to sort within database)


class SchoolAdmin(admin.ModelAdmin):
    fieldsets = [
        ('School Data', {'fields' : ['schoolCode', 'schoolName']}),
        ('Scheduling Data', {'fields' : ['listOfClasses', 'attributes', 'description']})
    ]

    list_display = ('schoolCode', 'schoolName', 'listOfClasses', 'attributes', 'description')
    list_filter = ('schoolCode', 'schoolName', 'listOfClasses', 'attributes', 'description')
    search_fields = ('schoolCode', 'schoolName', 'listOfClasses', 'attributes', 'description')


class MajorAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Major Data', {'fields' : ['majorName', 'schoolCode']}),
        ('Scheduling Data', {'fields' : ['listOfClasses', 'attributes', 'description']})
    ]

    list_display = ('majorID', 'majorName', 'listOfClasses', 'attributes', 'description')
    list_filter = ('majorID', 'majorName', 'listOfClasses', 'attributes', 'description')
    search_fields = ('majorID', 'majorName', 'listOfClasses', 'attributes', 'description')


class ClassAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Class Data', {'fields' : ['className', 'schoolCode','deptID','courseCode']}),

        ('Scheduling Data', {'fields' : ['creditNum','listOfPrereqs','numPrereqs', 'classStanding','semOffered', 'attributes', 'description']})
    ]

    list_display = ('classID', 'className', 'schoolCode', 'deptID', 'courseCode', 'creditNum', 'listOfPrereqs', 'numPrereqs', 'classStanding', 'semOffered', 'attributes', 'description')
    list_filter = ('classID', 'className', 'schoolCode', 'deptID', 'courseCode', 'creditNum', 'listOfPrereqs', 'numPrereqs', 'classStanding', 'semOffered', 'attributes', 'description')
    search_fields = ('classID', 'className', 'schoolCode', 'deptID', 'courseCode', 'creditNum', 'listOfPrereqs', 'numPrereqs', 'classStanding', 'semOffered', 'attributes', 'description')



admin.site.register(Major, MajorAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(School, SchoolAdmin)