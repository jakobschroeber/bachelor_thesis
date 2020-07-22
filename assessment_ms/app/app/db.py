# adapted from https://docs.djangoproject.com/en/2.2/topics/db/multi-db/

class Router:
    """
    A router to control all database operations on models in the
    applications listed in route_app_labels.
    """
    route_app_labels = {'data_source',}

    def db_for_read(self, model, **hints):
        """
        db to use to read models listed in in apps route_app_labels.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'moodle'
        return None

    def db_for_write(self, model, **hints):
        """
        db to use to write models listed in in apps route_app_labels.
        Beware that save() and delete() are not supposed to happen
        """
        if model._meta.app_label in self.route_app_labels:
            raise Exception("No writing to Moodle DB allowed.")
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if models listed in in apps route_app_labels
        are involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure models listed in in apps route_app_labels are not migrated.
        """
        if app_label in self.route_app_labels:
            return False
        return None