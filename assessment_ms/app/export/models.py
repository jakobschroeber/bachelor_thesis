import uuid
from cassandra.cqlengine import columns
from django_cassandra_engine.models import DjangoCassandraModel


class IndicatorResultExport(DjangoCassandraModel):
    uuid            = columns.UUID(primary_key=True, default=uuid.uuid4)
    indicator_id    = columns.Integer(index=True)
    course_id       = columns.Integer(index=True)
    user_id         = columns.Integer(index=True)
    value           = columns.Float()
    time_created    = columns.DateTime()


class ConstructAssessmentExport(DjangoCassandraModel):
    uuid            = columns.UUID(primary_key=True, default=uuid.uuid4)
    construct_id    = columns.Integer(index=True)
    time_created    = columns.DateTime()


class ConstructResultExport(DjangoCassandraModel):
    uuid                    = columns.UUID(primary_key=True, default=uuid.uuid4)
    assessment_id           = columns.Integer(index=True)
    course_id               = columns.Integer(index=True)
    user_id                 = columns.Integer(index=True)
    value                   = columns.Float()
    time_created            = columns.DateTime()


class ConstructIndicatorResultExport(DjangoCassandraModel):
    uuid                        = columns.UUID(primary_key=True, default=uuid.uuid4)
    constructresult_id         = columns.Integer(index=True)
    indicator_id                = columns.Integer(index=True)
    course_id                   = columns.Integer(index=True)
    user_id                     = columns.Integer(index=True)
    value                       = columns.Float()
    time_created                = columns.DateTime()