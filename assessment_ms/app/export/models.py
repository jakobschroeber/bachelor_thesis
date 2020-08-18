import uuid
from cassandra.cqlengine import columns
from django_cassandra_engine.models import DjangoCassandraModel


class AssessmentResult(DjangoCassandraModel):
    id              = columns.UUID(primary_key=True, default=uuid.uuid4)
    construct_id    = columns.Integer(index=True)
    indicator_id    = columns.Integer(index=True)
    course_id       = columns.Integer(index=True)
    user_id         = columns.Integer(index=True)
    value           = columns.Integer()
    time_created    = columns.DateTime()

# def export_results():
#     from assessment.models.indicators import IndicatorResult
#     from .models import AssessmentResult
#     from cassandra.cqlengine.query import BatchQuery
#
#     export_qs = IndicatorResult.objects.filter(exported=False).values(
#         'indicator_id', 'course_id', 'user_id', 'value', 'time_created')
#     with BatchQuery() as b:
#         for result in export_qs:
#             AssessmentResult.batch(b).using('cassandra').create(**result)
#     # for result in export_qs:
#     #     AssessmentResult.objects.create(**result)
#     export_qs.update(exported=True)
