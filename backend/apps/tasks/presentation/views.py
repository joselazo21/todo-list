"""
DRF Views for Task presentation layer
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import logging

from ..application.use_cases import (
    CreateTaskUseCase, UpdateTaskUseCase, GetTaskUseCase, ListTasksUseCase,
    DeleteTaskUseCase, BulkCompleteTasksUseCase, GetTaskStatisticsUseCase,
    GetUserProductivityUseCase, GetTaskSuggestionsUseCase, AutoPrioritizeTasksUseCase
)
from ..domain.services import TaskDomainService
from ..infrastructure.repositories import DjangoTaskRepository
from .serializers import (
    CreateTaskSerializer, UpdateTaskSerializer, TaskSerializer,
    TaskFilterSerializer, BulkCompleteTasksSerializer, TaskStatisticsSerializer,
    ProductivitySerializer, TaskSuggestionSerializer, BulkCompleteResponseSerializer
)

logger = logging.getLogger(__name__)


class TaskListCreateView(APIView):
    """List tasks with filtering or create a new task"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, description='Filter by status'),
            OpenApiParameter('priority', OpenApiTypes.STR, description='Filter by priority'),
            OpenApiParameter('overdue_only', OpenApiTypes.BOOL, description='Show only overdue tasks'),
            OpenApiParameter('search_term', OpenApiTypes.STR, description='Search in title/description'),
        ],
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request):
        """List tasks with filtering"""
        try:
            # Initialize dependencies
            repository = DjangoTaskRepository()
            use_case = ListTasksUseCase(repository)
            
            # Validate and convert query parameters
            filter_serializer = TaskFilterSerializer(data=request.query_params)
            filter_serializer.is_valid(raise_exception=True)
            
            filter_dto = filter_serializer.to_dto(str(request.user.id))
            
            # Execute use case
            task_dtos = use_case.execute(filter_dto)
            
            # Serialize response
            serializer = TaskSerializer(task_dtos, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}")
            return Response(
                {'error': 'Unable to fetch tasks'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        request=CreateTaskSerializer,
        responses={201: TaskSerializer}
    )
    def post(self, request):
        """Create a new task"""
        try:
            # Initialize dependencies
            repository = DjangoTaskRepository()
            use_case = CreateTaskUseCase(repository)
            
            # Validate input
            serializer = CreateTaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            create_dto = serializer.to_dto(str(request.user.id))
            
            # Execute use case
            task_dto = use_case.execute(create_dto)
            
            # Serialize response
            response_serializer = TaskSerializer(task_dto)
            logger.info(f"Task created: {task_dto.title} for user {request.user.id}")
            
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            return Response(
                {'error': 'Unable to create task'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskDetailView(APIView):
    """Retrieve, update or delete a specific task"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(responses={200: TaskSerializer})
    def get(self, request, task_id):
        """Retrieve a specific task"""
        try:
            repository = DjangoTaskRepository()
            use_case = GetTaskUseCase(repository)
            
            task_dto = use_case.execute(task_id, str(request.user.id))
            
            if not task_dto:
                return Response(
                    {'error': 'Task not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = TaskSerializer(task_dto)
            return Response(serializer.data)
            
        except PermissionError:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"Error retrieving task {task_id}: {str(e)}")
            return Response(
                {'error': 'Unable to fetch task'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        request=UpdateTaskSerializer,
        responses={200: TaskSerializer}
    )
    def put(self, request, task_id):
        """Update a specific task"""
        try:
            repository = DjangoTaskRepository()
            use_case = UpdateTaskUseCase(repository)
            
            # Debug logging
            logger.info(f"PUT request data for task {task_id}: {request.data}")
            
            # Validate input
            serializer = UpdateTaskSerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Validation errors for task {task_id}: {serializer.errors}")
                return Response(
                    {'error': 'Validation failed', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            update_dto = serializer.to_dto(task_id)
            
            # Check authorization - task must belong to current user
            existing_task = repository.find_by_id(task_id)
            if not existing_task:
                return Response(
                    {'error': 'Task not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if existing_task.user_id != str(request.user.id):
                return Response(
                    {'error': 'Access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Execute use case
            task_dto = use_case.execute(update_dto)
            
            # Serialize response
            response_serializer = TaskSerializer(task_dto)
            logger.info(f"Task updated: {task_id}")
            
            return Response(response_serializer.data)
            
        except ValueError as e:
            logger.error(f"ValueError updating task {task_id}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionError:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            return Response(
                {'error': 'Unable to update task'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(responses={204: None})
    def delete(self, request, task_id):
        """Delete a specific task"""
        try:
            repository = DjangoTaskRepository()
            use_case = DeleteTaskUseCase(repository)
            
            success = use_case.execute(task_id, str(request.user.id))
            
            if success:
                logger.info(f"Task deleted: {task_id}")
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': 'Task not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionError:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            return Response(
                {'error': 'Unable to delete task'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    request=BulkCompleteTasksSerializer,
    responses={200: BulkCompleteResponseSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_complete_tasks(request):
    """Mark multiple tasks as completed"""
    try:
        # Initialize dependencies
        repository = DjangoTaskRepository()
        domain_service = TaskDomainService(repository)
        use_case = BulkCompleteTasksUseCase(repository, domain_service)
        
        # Validate input
        serializer = BulkCompleteTasksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        bulk_dto = serializer.to_dto(str(request.user.id))
        
        # Execute use case
        result = use_case.execute(bulk_dto)
        
        logger.info(f"Bulk completed {result['updated_count']} tasks for user {request.user.id}")
        
        # Serialize response
        response_serializer = BulkCompleteResponseSerializer(result)
        return Response(response_serializer.data)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error in bulk complete: {str(e)}")
        return Response(
            {'error': 'Unable to complete tasks'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(responses={200: TaskStatisticsSerializer})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_statistics(request):
    """Get task statistics for the authenticated user"""
    try:
        repository = DjangoTaskRepository()
        use_case = GetTaskStatisticsUseCase(repository)
        
        stats_dto = use_case.execute(str(request.user.id))
        
        serializer = TaskStatisticsSerializer(stats_dto)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting task statistics: {str(e)}")
        return Response(
            {'error': 'Unable to fetch statistics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    parameters=[
        OpenApiParameter('days', OpenApiTypes.INT, description='Number of days for productivity calculation'),
    ],
    responses={200: ProductivitySerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_productivity(request):
    """Get user productivity metrics"""
    try:
        repository = DjangoTaskRepository()
        domain_service = TaskDomainService(repository)
        use_case = GetUserProductivityUseCase(repository, domain_service)
        
        days = int(request.query_params.get('days', 30))
        productivity_dto = use_case.execute(str(request.user.id), days)
        
        serializer = ProductivitySerializer(productivity_dto)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting productivity metrics: {str(e)}")
        return Response(
            {'error': 'Unable to fetch productivity metrics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(responses={200: TaskSuggestionSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_suggestions(request, task_id):
    """Get improvement suggestions for a specific task"""
    try:
        repository = DjangoTaskRepository()
        domain_service = TaskDomainService(repository)
        use_case = GetTaskSuggestionsUseCase(repository, domain_service)
        
        suggestions_dto = use_case.execute(task_id, str(request.user.id))
        
        serializer = TaskSuggestionSerializer(suggestions_dto, many=True)
        return Response(serializer.data)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except PermissionError:
        return Response(
            {'error': 'Access denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    except Exception as e:
        logger.error(f"Error getting task suggestions: {str(e)}")
        return Response(
            {'error': 'Unable to fetch suggestions'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(responses={200: TaskSerializer(many=True)})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_prioritize_tasks(request):
    """Automatically prioritize user's tasks based on deadlines"""
    try:
        repository = DjangoTaskRepository()
        domain_service = TaskDomainService(repository)
        use_case = AutoPrioritizeTasksUseCase(repository, domain_service)
        
        updated_tasks_dto = use_case.execute(str(request.user.id))
        
        serializer = TaskSerializer(updated_tasks_dto, many=True)
        logger.info(f"Auto-prioritized {len(updated_tasks_dto)} tasks for user {request.user.id}")
        
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error auto-prioritizing tasks: {str(e)}")
        return Response(
            {'error': 'Unable to auto-prioritize tasks'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )