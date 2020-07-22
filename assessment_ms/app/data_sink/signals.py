from django.db.models.signals import post_init
from django.dispatch import receiver
from data_source.models_abstract import AbstractMoodle

from pprint import PrettyPrinter

sender_list = []
mdlabstrclasses = AbstractMoodle.__subclasses__()
for mdlabstrclass in mdlabstrclasses:
    for mdlsrcclass in mdlabstrclass.__subclasses__():
        if mdlsrcclass._meta.app_label != __package__:
            sender_list.append(mdlsrcclass)

print("The following Moodle data_source models are signalling new instances:")
pp =  PrettyPrinter()
pp.pprint(sender_list)

@receiver(post_init)
def update_data_sink(sender, instance, **kwargs):
    if sender in sender_list:
        mdlsink_list = [item for item in sender.__bases__[0].__subclasses__() if item != sender]
        if not mdlsink_list:
            raise Exception("No sink class for Moodle data_source class ", sender)
        elif len(mdlsink_list) > 1:
            raise Exception("Ambiguous: More than one sink class for Moodle data_source class ", sender)
        else:
            mdlsink = mdlsink_list[0]
            fields = sender._meta.get_fields()
        try:
            obj = mdlsink.objects.get(pk=instance.pk)
        except mdlsink.DoesNotExist:
            obj = mdlsink()
            for field in fields:
                field_name = field.name
                value = getattr(instance, field_name)
                setattr(obj, field_name, value)
            obj.save()
        else:
            # update is not necessary in cases like logstore_standard_log where only new rows are expected
            updated_fields = []
            for field in fields:
                field_name = field.name
                value = getattr(instance, field_name)
                if getattr(obj, field_name) != value:
                    setattr(obj, field_name, value)
                    updated_fields.append(field_name)
            if updated_fields:
                obj.save(update_fields=updated_fields)


