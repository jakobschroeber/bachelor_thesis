from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ConstructResultSerializer
from assessment.models.constructs import Construct, ConstructAssessment, ConstructResult


class ConstructResultsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        qs = ConstructResult.objects.none()
        for construct in Construct.objects.all():
            try:
                latest = ConstructAssessment.objects.filter(construct=construct).latest('time_created')
            except ConstructAssessment.DoesNotExist:
                raise Exception(f'Construct with id {constructid} does not have results')

            qs |= ConstructResult.objects.filter(assessment=latest).select_related('assessment').prefetch_related('measures')

        serializer = ConstructResultSerializer(qs, many=True)

        return Response(serializer.data)


# prepared for REST request
# def get_latest_assessment(constructid):
#     try:
#         construct = Construct.objects.get(id=constructid)
#     except Construct.DoesNotExist:
#         raise Exception(f'Construct with id {constructid} does not exist')
#
#     construct_assessments = ConstructAssessment.objects.filter(construct=construct)
#     if not (construct_assessments):
#         raise Exception(f'Construct with id {constructid} does not have any assessments yet')
#
#     latest_assessment = construct_assessments.latest('time_created')
#
#     return latest_assessment