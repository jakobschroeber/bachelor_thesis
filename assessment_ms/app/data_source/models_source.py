from .models_abstract import AbstractMoodleUser, AbstractMoodleUserPreferences, AbstractMoodleLogstoreStandardLog, \
    AbstractMoodleAssign, AbstractMoodleAssignSubmission, AbstractMoodleCourseModules, AbstractMoodleTagInstance, \
    AbstractMoodleComments, AbstractMoodleForumPosts


class SourceMoodleUser(AbstractMoodleUser):
    class Meta:
        managed = False
        db_table = "m_user"


class SourceMoodleUserPreferences(AbstractMoodleUserPreferences):
    class Meta:
        managed = False
        db_table = "m_user_preferences"


class SourceMoodleLogstoreStandardLog(AbstractMoodleLogstoreStandardLog):
    class Meta:
        managed = False
        db_table = "m_logstore_standard_log"


class SourceMoodleAssignSubmission(AbstractMoodleAssignSubmission):
    class Meta:
        managed = False
        db_table = "m_assign_submission"


class SourceMoodleAssign(AbstractMoodleAssign):
    class Meta:
        managed = False
        db_table = "m_assign"


class SourceMoodleCourseModules(AbstractMoodleCourseModules):
    class Meta:
        managed = False
        db_table = "m_course_modules"


class SourceMoodleTagInstance(AbstractMoodleTagInstance):
    class Meta:
        managed = False
        db_table = "m_tag_instance"


class SourceMoodleComments(AbstractMoodleComments):
    class Meta:
        managed = False
        db_table = "m_comments"


class SourceMoodleComments(AbstractMoodleForumPosts):
    class Meta:
        managed = False
        db_table = "m_forum_posts"