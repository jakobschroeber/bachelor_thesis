from .models_abstract import AbstractMoodleUser, AbstractMoodleCourse, AbstractMoodleContext, AbstractMoodleRole, \
    AbstractMoodleRoleAssignments
from django.db import models


# Source tables for administration and / or assessment

class User(AbstractMoodleUser):
    class Meta:
        managed = False
        db_table = "mdl_user"


class Course(AbstractMoodleCourse):
    class Meta:
        managed = False
        db_table = 'mdl_course'


class Context(AbstractMoodleContext):
    class Meta:
        managed = False
        db_table = 'mdl_context'


class Role(AbstractMoodleRole):
    class Meta:
        managed = False
        db_table = 'mdl_role'


class RoleAssignments(AbstractMoodleRoleAssignments):
    class Meta:
        managed = False
        db_table = 'mdl_role_assignments'


# Source tables for assessment only

class UserPreferences(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=1333)

    class Meta:
        managed = False
        db_table = 'mdl_user_preferences'
        unique_together = (('userid', 'name'),)


class LogstoreStandardLog(models.Model):
    id = models.BigIntegerField(primary_key=True)
    eventname = models.CharField(max_length=255)
    component = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    objecttable = models.CharField(max_length=50, blank=True, null=True)
    objectid = models.BigIntegerField(blank=True, null=True)
    crud = models.CharField(max_length=1)
    edulevel = models.IntegerField()
    contextid = models.BigIntegerField()
    contextlevel = models.BigIntegerField()
    contextinstanceid = models.BigIntegerField()
    userid = models.BigIntegerField()
    courseid = models.BigIntegerField(blank=True, null=True)
    relateduserid = models.BigIntegerField(blank=True, null=True)
    anonymous = models.IntegerField()
    other = models.TextField(blank=True, null=True)
    timecreated = models.BigIntegerField()
    origin = models.CharField(max_length=10, blank=True, null=True)
    ip = models.CharField(max_length=45, blank=True, null=True)
    realuserid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_logstore_standard_log'


class Assign(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField()
    introformat = models.SmallIntegerField()
    alwaysshowdescription = models.IntegerField()
    nosubmissions = models.IntegerField()
    submissiondrafts = models.IntegerField()
    sendnotifications = models.IntegerField()
    sendlatenotifications = models.IntegerField()
    duedate = models.BigIntegerField()
    allowsubmissionsfromdate = models.BigIntegerField()
    grade = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    requiresubmissionstatement = models.IntegerField()
    completionsubmit = models.IntegerField()
    cutoffdate = models.BigIntegerField()
    gradingduedate = models.BigIntegerField()
    teamsubmission = models.IntegerField()
    requireallteammemberssubmit = models.IntegerField()
    teamsubmissiongroupingid = models.BigIntegerField()
    blindmarking = models.IntegerField()
    hidegrader = models.IntegerField()
    revealidentities = models.IntegerField()
    attemptreopenmethod = models.CharField(max_length=10)
    maxattempts = models.IntegerField()
    markingworkflow = models.IntegerField()
    markingallocation = models.IntegerField()
    sendstudentnotifications = models.IntegerField()
    preventsubmissionnotingroup = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assign'


class AssignSubmission(models.Model):
    id = models.BigIntegerField(primary_key=True)
    assignment = models.BigIntegerField()
    userid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    status = models.CharField(max_length=10, blank=True, null=True)
    groupid = models.BigIntegerField()
    attemptnumber = models.BigIntegerField()
    latest = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_assign_submission'
        unique_together = (('assignment', 'userid', 'groupid', 'attemptnumber'),)


class CourseModules(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.BigIntegerField()
    module = models.BigIntegerField()
    instance = models.BigIntegerField()
    section = models.BigIntegerField()
    idnumber = models.CharField(max_length=100, blank=True, null=True)
    added = models.BigIntegerField()
    score = models.SmallIntegerField()
    indent = models.IntegerField()
    visible = models.IntegerField()
    visibleoncoursepage = models.IntegerField()
    visibleold = models.IntegerField()
    groupmode = models.SmallIntegerField()
    groupingid = models.BigIntegerField()
    completion = models.IntegerField()
    completiongradeitemnumber = models.BigIntegerField(blank=True, null=True)
    completionview = models.IntegerField()
    completionexpected = models.BigIntegerField()
    showdescription = models.IntegerField()
    availability = models.TextField(blank=True, null=True)
    deletioninprogress = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_course_modules'


class TagInstance(models.Model):
    id = models.BigIntegerField(primary_key=True)
    tagid = models.BigIntegerField()
    component = models.CharField(max_length=100)
    itemtype = models.CharField(max_length=100)
    itemid = models.BigIntegerField()
    contextid = models.BigIntegerField(blank=True, null=True)
    tiuserid = models.BigIntegerField()
    ordering = models.BigIntegerField(blank=True, null=True)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_tag_instance'
        unique_together = (('component', 'itemtype', 'itemid', 'contextid', 'tiuserid', 'tagid'),)


class Comments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    contextid = models.BigIntegerField()
    component = models.CharField(max_length=255, blank=True, null=True)
    commentarea = models.CharField(max_length=255)
    itemid = models.BigIntegerField()
    content = models.TextField()
    format = models.IntegerField()
    userid = models.BigIntegerField()
    timecreated = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_comments'


class ForumPosts(models.Model):
    id = models.BigIntegerField(primary_key=True)
    discussion = models.BigIntegerField()
    parent = models.BigIntegerField()
    userid = models.BigIntegerField()
    created = models.BigIntegerField()
    modified = models.BigIntegerField()
    mailed = models.IntegerField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    messageformat = models.IntegerField()
    messagetrust = models.IntegerField()
    attachment = models.CharField(max_length=100)
    totalscore = models.SmallIntegerField()
    mailnow = models.BigIntegerField()
    deleted = models.IntegerField()
    privatereplyto = models.BigIntegerField()
    wordcount = models.BigIntegerField(blank=True, null=True)
    charcount = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mdl_forum_posts'