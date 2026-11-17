from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        project = self.get_object()

        project.status = 'COMPLETED'
        project.save()

        return Response({
            'message': 'Project approved successfully.',
            'project_id': project.id,
            'status': project.status
        })
