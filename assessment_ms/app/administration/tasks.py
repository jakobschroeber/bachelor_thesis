from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.db import transaction

from data_source.models_abstract import AbstractMoodle


source_class_list = []
mdlabstrclasses = AbstractMoodle.__subclasses__()
for mdlabstrclass in mdlabstrclasses:
    for mdlsrcclass in mdlabstrclass.__subclasses__():
        if mdlsrcclass._meta.app_label != __package__:
            source_class_list.append(mdlsrcclass)


@shared_task
def update_administration_data():
    print(f'Starting update of administration data ... The following data_source models are updated: {source_class_list}')
    with transaction.atomic(using='default'):
        with transaction.atomic(using='moodle'):
            for source_class in source_class_list:
                source_class_instances = source_class.objects.all()
                sink_class_list = [item for item in source_class.__bases__[0].__subclasses__() if item != source_class]
                if not sink_class_list:
                    raise Exception("No administration model found for data_source model ", source_class)
                elif len(sink_class_list) > 1:
                    raise Exception("Ambiguous: More than one administration model for data_source model ", source_class)
                else:
                    sink_class = sink_class_list[0]
                    sink_class_instances = sink_class.objects.all()
                    fields = source_class._meta.get_fields()
                # deleting instances
                source_class_instances_list = list(source_class_instances.values_list('id', flat=True))
                delete_list = list(sink_class_instances.exclude(pk__in=source_class_instances_list).values_list('id', flat=True))
                if (delete_list):
                    sink_class_instances.filter(pk__in=delete_list).delete()
                    print(f'app administration, model {source_class.__name__}: deleted rows with id in {delete_list}')
                # creating/updating instances
                for instance in source_class_instances:
                    try:
                        obj = sink_class_instances.get(pk=instance.pk)
                    except sink_class.DoesNotExist:
                        obj = sink_class()
                        for field in fields:
                            field_name = field.name
                            value = getattr(instance, field_name)
                            setattr(obj, field_name, value)
                        obj.save()
                    else:
                        updated_fields = []
                        for field in fields:
                            field_name = field.name
                            value = getattr(instance, field_name)
                            if getattr(obj, field_name) != value:
                                setattr(obj, field_name, value)
                                updated_fields.append(field_name)
                        if updated_fields:
                            obj.save(update_fields=updated_fields)
                if (source_class_instances_list):
                    print(f'Processing administration data of model {source_class.__name__}: created/updated rows with id in {source_class_instances_list}')
        print(f'Completed  update of administration data')