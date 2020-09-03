from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ConstructResultSerializer
from assessment.models.constructs import Construct, ConstructAssessment, ConstructResult


class ConstructResultsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        qs = ConstructResult.objects.none()
        for construct in Construct.objects.all():
            latest = ConstructAssessment.objects.filter(construct=construct).latest('time_created')
            qs |= ConstructResult.objects.filter(assessment=latest).select_related('assessment').prefetch_related('measures')

        serializer = ConstructResultSerializer(qs, many=True)

        return Response(serializer.data)

        # idea: remove Assessment foreign key from ConstructIndicatorResult, replace by ConstructResult foreign key
        # problem: we don't have ConstructResult foreign key when saving indicator results, need to change save_result
        #
        # combined foreign key (assessment, user, course)