"""
DRF Views for User presentation layer
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import logging

from ..application.use_cases import (
    CreateUserUseCase, UpdateUserUseCase, GetUserUseCase, GetUserByEmailUseCase,
    ListUsersUseCase, DeleteUserUseCase, ChangePasswordUseCase, VerifyEmailUseCase,
    UnlockAccountUseCase, GetUserStatisticsUseCase, GetSecurityRecommendationsUseCase,
    UnlockExpiredAccountsUseCase
)
from ..domain.services import UserDomainService
from ..infrastructure.repositories import DjangoUserRepository
from .serializers import (
    CreateUserSerializer, UpdateUserSerializer, UserSerializer,
    UserFilterSerializer, ChangePasswordSerializer, EmailVerificationSerializer,
    UserStatisticsSerializer, SecurityRecommendationSerializer
)

logger = logging.getLogger(__name__)


class UserListCreateView(APIView):
    """List users with filtering or create a new user"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, description='Filter by status'),
            OpenApiParameter('is_email_verified', OpenApiTypes.BOOL, description='Filter by email verification'),
            OpenApiParameter('is_locked', OpenApiTypes.BOOL, description='Filter by account lock status'),
            OpenApiParameter('search_term', OpenApiTypes.STR, description='Search in name/email'),
        ],
        responses={200: UserSerializer(many=True)}
    )
    def get(self, request):
        """List users with filtering"""
        try:
            # Initialize dependencies
            repository = DjangoUserRepository()
            use_case = ListUsersUseCase(repository)
            
            # Validate and convert query parameters
            filter_serializer = UserFilterSerializer(data=request.query_params)
            filter_serializer.is_valid(raise_exception=True)
            
            filter_dto = filter_serializer.to_dto()
            
            # Execute use case
            user_dtos = use_case.execute(filter_dto)
            
            # Serialize response
            serializer = UserSerializer(user_dtos, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return Response(
                {'error': 'Unable to fetch users'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        request=CreateUserSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request):
        """Create a new user"""
        try:
            # Initialize dependencies
            repository = DjangoUserRepository()
            domain_service = UserDomainService(repository)
            use_case = CreateUserUseCase(repository, domain_service)
            
            # Validate input
            serializer = CreateUserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            create_dto = serializer.to_dto()
            
            # Execute use case
            user_dto = use_case.execute(create_dto)
            
            # Serialize response
            response_serializer = UserSerializer(user_dto)
            logger.info(f"User created: {user_dto.name} ({user_dto.email})")
            
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return Response(
                {'error': 'Unable to create user'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserDetailView(APIView):
    """Retrieve, update or delete a specific user"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(responses={200: UserSerializer})
    def get(self, request, user_id):
        """Retrieve a specific user"""
        try:
            repository = DjangoUserRepository()
            use_case = GetUserUseCase(repository)
            
            user_dto = use_case.execute(user_id)
            
            if not user_dto:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check permissions - users can only see their own data unless admin
            if str(request.user.id) != user_id and not request.user.is_staff:
                return Response(
                    {'error': 'Access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = UserSerializer(user_dto)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {str(e)}")
            return Response(
                {'error': 'Unable to fetch user'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        request=UpdateUserSerializer,
        responses={200: UserSerializer}
    )
    def put(self, request, user_id):
        """Update a specific user"""
        try:
            # Check permissions - users can only update their own data unless admin
            if str(request.user.id) != user_id and not request.user.is_staff:
                return Response(
                    {'error': 'Access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            repository = DjangoUserRepository()
            use_case = UpdateUserUseCase(repository)
            
            # Validate input
            serializer = UpdateUserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            update_dto = serializer.to_dto(user_id)
            
            # Execute use case
            user_dto = use_case.execute(update_dto)
            
            # Serialize response
            response_serializer = UserSerializer(user_dto)
            logger.info(f"User updated: {user_id}")
            
            return Response(response_serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            return Response(
                {'error': 'Unable to update user'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(responses={204: None})
    def delete(self, request, user_id):
        """Delete a specific user"""
        try:
            # Only admins can delete users
            if not request.user.is_staff:
                return Response(
                    {'error': 'Access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            repository = DjangoUserRepository()
            use_case = DeleteUserUseCase(repository)
            
            success = use_case.execute(user_id)
            
            if success:
                logger.info(f"User deleted: {user_id}")
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            return Response(
                {'error': 'Unable to delete user'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    request=ChangePasswordSerializer,
    responses={200: UserSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request, user_id):
    """Change user password"""
    try:
        # Check permissions - users can only change their own password
        if str(request.user.id) != user_id:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Initialize dependencies
        repository = DjangoUserRepository()
        domain_service = UserDomainService(repository)
        use_case = ChangePasswordUseCase(repository, domain_service)
        
        # Validate input
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        change_dto = serializer.to_dto(user_id)
        
        # Execute use case
        user_dto = use_case.execute(change_dto)
        
        logger.info(f"Password changed for user: {user_id}")
        
        # Serialize response
        response_serializer = UserSerializer(user_dto)
        return Response(response_serializer.data)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error changing password for user {user_id}: {str(e)}")
        return Response(
            {'error': 'Unable to change password'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    request=EmailVerificationSerializer,
    responses={200: UserSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_email(request, user_id):
    """Verify user email"""
    try:
        # Check permissions - users can only verify their own email
        if str(request.user.id) != user_id:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Initialize dependencies
        repository = DjangoUserRepository()
        domain_service = UserDomainService(repository)
        use_case = VerifyEmailUseCase(repository, domain_service)
        
        # Validate input
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        verify_dto = serializer.to_dto(user_id)
        
        # Execute use case
        user_dto = use_case.execute(verify_dto)
        
        logger.info(f"Email verified for user: {user_id}")
        
        # Serialize response
        response_serializer = UserSerializer(user_dto)
        return Response(response_serializer.data)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error verifying email for user {user_id}: {str(e)}")
        return Response(
            {'error': 'Unable to verify email'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(responses={200: UserSerializer})
@api_view(['POST'])
@permission_classes([IsAdminUser])
def unlock_account(request, user_id):
    """Unlock user account (admin only)"""
    try:
        repository = DjangoUserRepository()
        use_case = UnlockAccountUseCase(repository)
        
        user_dto = use_case.execute(user_id)
        
        logger.info(f"Account unlocked for user: {user_id}")
        
        serializer = UserSerializer(user_dto)
        return Response(serializer.data)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error unlocking account for user {user_id}: {str(e)}")
        return Response(
            {'error': 'Unable to unlock account'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(responses={200: UserStatisticsSerializer})
@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_statistics(request):
    """Get user statistics (admin only)"""
    try:
        repository = DjangoUserRepository()
        use_case = GetUserStatisticsUseCase(repository)
        
        stats_dto = use_case.execute()
        
        serializer = UserStatisticsSerializer(stats_dto)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting user statistics: {str(e)}")
        return Response(
            {'error': 'Unable to fetch statistics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(responses={200: SecurityRecommendationSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def security_recommendations(request, user_id):
    """Get security recommendations for user"""
    try:
        # Check permissions - users can only see their own recommendations
        if str(request.user.id) != user_id and not request.user.is_staff:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        repository = DjangoUserRepository()
        domain_service = UserDomainService(repository)
        use_case = GetSecurityRecommendationsUseCase(repository, domain_service)
        
        recommendations_dto = use_case.execute(user_id)
        
        serializer = SecurityRecommendationSerializer(recommendations_dto, many=True)
        return Response(serializer.data)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error getting security recommendations: {str(e)}")
        return Response(
            {'error': 'Unable to fetch recommendations'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )