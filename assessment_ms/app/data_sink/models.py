from django.db import models


from data_source.models_abstract import AbstractMoodleUser

class MoodleUser(AbstractMoodleUser):
    ignore_activity = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f'{self.id} - {self.username}'

