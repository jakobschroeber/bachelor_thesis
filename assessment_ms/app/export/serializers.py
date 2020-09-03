from rest_framework.serializers import ModelSerializer, CharField

from assessment.models.constructs import ConstructResult, ConstructIndicatorResult


class ConstructIndicatorResultSerializer(ModelSerializer):
    measure_id = CharField(source='indicator.id', read_only=True)
    measure_name = CharField(source='indicator.name', read_only=True)
    measure_DIFA_id = CharField(source='indicator.DIFA_reference_id', read_only=True)
    description = CharField(source='indicator.description', read_only=True)
    result = CharField(source='value', read_only=True)

    class Meta:
        model = ConstructIndicatorResult
        fields = [
            'measure_id',
            'measure_name',
            'measure_DIFA_id',
            'description',
            'result'
        ]


class ConstructResultSerializer(ModelSerializer):
    userid              = CharField(source='user.id', read_only=True)
    courseid            = CharField(source='course.id', read_only=True)
    constructid         = CharField(source='assessment.construct.id', read_only=True)
    construct_name      = CharField(source='assessment.construct.name', read_only=True)
    analysis_timestamp  = CharField(source='assessment.time_created', read_only=True)
    description         = CharField(source='assessment.construct.description', read_only=True)
    result              = CharField(source='value', read_only=True)
    measures            = ConstructIndicatorResultSerializer(many=True, read_only=True)

    class Meta:
        model = ConstructResult
        fields = [
            'userid',
            'courseid',
            'constructid',
            'construct_name',
            'analysis_timestamp',
            'description',
            'result',
            'measures'
        ]
