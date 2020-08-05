from data_source.models_abstract import AbstractMoodleUser, AbstractMoodleCourse, AbstractMoodleContext, \
    AbstractMoodleRole, AbstractMoodleRoleAssignments

from django.db import models
from django.db import connection


class User(AbstractMoodleUser):
    ignore_activity = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f'{self.id} - {self.username}'


class Course(AbstractMoodleCourse):
    ignore_activity = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f'{self.id} - {self.shortname}'

    def get_users_for_assessment(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT u.id as 'userid' \
                            FROM administration_course c, administration_user u, \
                                administration_context cxt, administration_roleassignments ra \
                            WHERE ra.userid = u.id AND ra.contextid = cxt.id AND \
                                cxt.instanceid = c.id AND cxt.contextlevel = 50 AND \
                                ra.ignore_activity = 0 AND c.id = %s", [self.id])
            user_list = [row[0] for row in cursor.fetchall()]
        return user_list


class Context(AbstractMoodleContext):
    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f'{self.id}'


class Role(AbstractMoodleRole):
    ignore_activity = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f'{self.id} - {self.shortname}'


class RoleAssignments(AbstractMoodleRoleAssignments):
    ignore_activity = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f'{self.id}'
