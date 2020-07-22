from django.db import models

class AbstractMoodle(models.Model):
    class Meta:
        abstract = True


class AbstractMoodleUser(AbstractMoodle):
    id          = models.BigIntegerField(primary_key=True)
    username    = models.CharField(max_length=100)

    class Meta:
        abstract = True


class AbstractMoodleUserPreferences(AbstractMoodle):
    id      = models.BigIntegerField(primary_key=True)
    userid  = models.BigIntegerField()
    name    = models.CharField(max_length=255)
    value   = models.CharField(max_length=1333)

    class Meta:
        abstract = True


class AbstractMoodleLogstoreStandardLog(AbstractMoodle):
    id          = models.BigIntegerField(primary_key=True)
    eventname   = models.CharField(max_length=255)
    component   = models.CharField(max_length=100)
    action      = models.CharField(max_length=100)
    target      = models.CharField(max_length=100)
    objecttable = models.CharField(max_length=50)
    contextid   = models.BigIntegerField()
    userid      = models.BigIntegerField()
    courseid    = models.BigIntegerField()
    timecreated = models.BigIntegerField()

    class Meta:
        abstract = True


class AbstractMoodleAssign(AbstractMoodle):
    id              = models.BigIntegerField(primary_key=True)
    course          = models.BigIntegerField()
    duedate         = models.BigIntegerField()

    class Meta:
        abstract = True


class AbstractMoodleAssignSubmission(AbstractMoodle):
    id              = models.BigIntegerField(primary_key=True)
    assignment      = models.BigIntegerField()
    userid          = models.BigIntegerField()
    timecreated     = models.BigIntegerField()
    timemodified    = models.BigIntegerField()
    status          = models.CharField(max_length=10)
    attemptnumber   = models.CharField(max_length=255)

    class Meta:
        abstract = True


class AbstractMoodleCourseModules(AbstractMoodle):
    id              = models.BigIntegerField(primary_key=True)
    course          = models.BigIntegerField()
    instance        = models.BigIntegerField()
    added           = models.BigIntegerField()

    class Meta:
        abstract = True


class AbstractMoodleTagInstance(AbstractMoodle):
    id              = models.BigIntegerField(primary_key=True)
    tagid           = models.BigIntegerField()
    itemid          = models.BigIntegerField()
    contextid       = models.BigIntegerField()

    class Meta:
        abstract = True


class AbstractMoodleComments(AbstractMoodle):
    id              = models.BigIntegerField(primary_key=True)
    userid          = models.BigIntegerField()

    class Meta:
        abstract = True


class AbstractMoodleForumPosts(AbstractMoodle):
    id              = models.BigIntegerField(primary_key=True)
    userid          = models.BigIntegerField()
    created         = models.BigIntegerField()
    wordcount       = models.BigIntegerField()

    class Meta:
        abstract = True