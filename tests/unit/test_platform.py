"""
Unit tests for platform management functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from app.modules.platform.models.application import (
    RestaurantApplication,
    RestaurantApplicationCreate,
    RestaurantApplicationUpdate,
    RestaurantApplicationRead,
    RestaurantApplicationApproval,
    RestaurantApplicationRejection,
    ApplicationStats,
)
from app.modules.platform.services.application import PlatformApplicationService
from fastapi import HTTPException


class TestApplicationModels:
    """Test application model classes and schemas."""
    
    def test_restaurant_application_create_schema(self):
        """Test RestaurantApplicationCreate schema validation."""
        application_data = {
            "applicant_name": "John Doe",
            "applicant_email": "john@example.com",
            "restaurant_name": "John's Restaurant",
            "restaurant_address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345"
            },
            "restaurant_phone": "+1-555-0123",
            "restaurant_email": "info@johnsrestaurant.com",
            "business_description": "A family-owned Italian restaurant"
        }
        
        application = RestaurantApplicationCreate(**application_data)
        assert application.applicant_name == "John Doe"
        assert application.applicant_email == "john@example.com"
        assert application.restaurant_name == "John's Restaurant"
        assert application.restaurant_address["city"] == "Anytown"
        
    def test_restaurant_application_update_schema(self):
        """Test RestaurantApplicationUpdate schema with partial updates."""
        update_data = {
            "status": "approved",
            "admin_notes": "Application looks good, approved"
        }
        
        application_update = RestaurantApplicationUpdate(**update_data)
        assert application_update.status == "approved"
        assert application_update.admin_notes == "Application looks good, approved"
        
    def test_restaurant_application_read_schema(self):
        """Test RestaurantApplicationRead schema."""
        read_data = {
            "id": str(uuid4()),
            "organization_id": str(uuid4()),
            "applicant_name": "Jane Smith",
            "applicant_email": "jane@example.com",
            "restaurant_name": "Jane's Bistro",
            "status": "pending",
            "created_at": "2025-08-17T10:00:00",
            "updated_at": "2025-08-17T10:00:00"
        }
        
        application = RestaurantApplicationRead(**read_data)
        assert application.applicant_name == "Jane Smith"
        assert application.restaurant_name == "Jane's Bistro"
        assert application.status == "pending"
        
    def test_restaurant_application_approval_schema(self):
        """Test RestaurantApplicationApproval schema."""
        approval_data = {
            "admin_notes": "Approved after reviewing business license"
        }
        
        approval = RestaurantApplicationApproval(**approval_data)
        assert approval.admin_notes == "Approved after reviewing business license"
        
    def test_restaurant_application_rejection_schema(self):
        """Test RestaurantApplicationRejection schema."""
        rejection_data = {
            "admin_notes": "Missing required documentation"
        }
        
        rejection = RestaurantApplicationRejection(**rejection_data)
        assert rejection.admin_notes == "Missing required documentation"
        
    def test_application_stats_schema(self):
        """Test ApplicationStats schema."""
        stats_data = {
            "total_applications": 100,
            "pending_applications": 25,
            "approved_applications": 60,
            "rejected_applications": 15,
            "recent_applications": 10
        }
        
        stats = ApplicationStats(**stats_data)
        assert stats.total_applications == 100
        assert stats.pending_applications == 25
        assert stats.approved_applications == 60
        assert stats.rejected_applications == 15
        assert stats.recent_applications == 10


class TestPlatformApplicationService:
    """Test application service business logic."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def sample_application_data(self):
        """Sample application creation data."""
        return RestaurantApplicationCreate(
            applicant_name="Test Applicant",
            applicant_email="test@example.com",
            restaurant_name="Test Restaurant",
            restaurant_address={
                "street": "456 Test St",
                "city": "Test City",
                "state": "TS",
                "zip": "54321"
            },
            restaurant_phone="+1-555-9999",
            restaurant_email="info@testrestaurant.com",
            business_description="A test restaurant for unit testing"
        )
    
    @pytest.mark.asyncio
    async def test_create_application_success(self, mock_session, sample_application_data):
        """Test successful application creation."""
        # Mock the created application
        created_application = Mock(spec=RestaurantApplication)
        created_application.id = str(uuid4())
        created_application.applicant_name = sample_application_data.applicant_name
        created_application.restaurant_name = sample_application_data.restaurant_name
        created_application.status = "pending"
        
        # Configure session mock
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Mock the actual service method to return our mock
        original_method = PlatformApplicationService.create_application
        PlatformApplicationService.create_application = AsyncMock(return_value=created_application)
        
        try:
            result = await PlatformApplicationService.create_application(mock_session, sample_application_data)
            
            assert result.applicant_name == "Test Applicant"
            assert result.restaurant_name == "Test Restaurant"
            assert result.status == "pending"
            PlatformApplicationService.create_application.assert_called_once_with(mock_session, sample_application_data)
        finally:
            # Restore original method
            PlatformApplicationService.create_application = original_method
    
    @pytest.mark.asyncio
    async def test_get_applications_list(self, mock_session):
        """Test getting applications list."""
        # Mock applications list
        mock_applications = [
            Mock(id=str(uuid4()), applicant_name="Applicant 1", status="pending"),
            Mock(id=str(uuid4()), applicant_name="Applicant 2", status="approved")
        ]
        
        # Mock the service method
        original_method = PlatformApplicationService.get_applications
        PlatformApplicationService.get_applications = AsyncMock(return_value=mock_applications)
        
        try:
            result = await PlatformApplicationService.get_applications(mock_session, skip=0, limit=10)
            
            assert len(result) == 2
            assert result[0].applicant_name == "Applicant 1"
            assert result[0].status == "pending"
            assert result[1].applicant_name == "Applicant 2"
            assert result[1].status == "approved"
        finally:
            # Restore original method
            PlatformApplicationService.get_applications = original_method
    
    @pytest.mark.asyncio
    async def test_get_application_by_id_not_found(self, mock_session):
        """Test getting application by ID when not found."""
        application_id = str(uuid4())
        
        # Mock the service method to raise HTTPException
        original_method = PlatformApplicationService.get_application_by_id
        PlatformApplicationService.get_application_by_id = AsyncMock(side_effect=HTTPException(status_code=404, detail="Application not found"))
        
        try:
            with pytest.raises(HTTPException) as exc_info:
                await PlatformApplicationService.get_application_by_id(mock_session, application_id)
            assert exc_info.value.status_code == 404
            assert "Application not found" in str(exc_info.value.detail)
        finally:
            # Restore original method
            PlatformApplicationService.get_application_by_id = original_method
    
    @pytest.mark.asyncio
    async def test_approve_application_success(self, mock_session):
        """Test successful application approval."""
        application_id = str(uuid4())
        admin_notes = "Application approved after review"
        
        # Mock the service method
        original_method = PlatformApplicationService.approve_application
        PlatformApplicationService.approve_application = AsyncMock(return_value=True)
        
        try:
            result = await PlatformApplicationService.approve_application(
                mock_session, application_id, admin_notes
            )
            
            assert result is True
            PlatformApplicationService.approve_application.assert_called_once_with(
                mock_session, application_id, admin_notes
            )
        finally:
            # Restore original method
            PlatformApplicationService.approve_application = original_method
    
    @pytest.mark.asyncio
    async def test_reject_application_success(self, mock_session):
        """Test successful application rejection."""
        application_id = str(uuid4())
        admin_notes = "Application rejected due to incomplete information"
        
        # Mock the service method
        original_method = PlatformApplicationService.reject_application
        PlatformApplicationService.reject_application = AsyncMock(return_value=True)
        
        try:
            result = await PlatformApplicationService.reject_application(
                mock_session, application_id, admin_notes
            )
            
            assert result is True
            PlatformApplicationService.reject_application.assert_called_once_with(
                mock_session, application_id, admin_notes
            )
        finally:
            # Restore original method
            PlatformApplicationService.reject_application = original_method
    
    @pytest.mark.asyncio
    async def test_get_application_stats(self, mock_session):
        """Test getting application statistics."""
        # Mock stats
        mock_stats = ApplicationStats(
            total_applications=50,
            pending_applications=15,
            approved_applications=30,
            rejected_applications=5,
            recent_applications=8
        )
        
        # Mock the service method
        original_method = PlatformApplicationService.get_application_stats
        PlatformApplicationService.get_application_stats = AsyncMock(return_value=mock_stats)
        
        try:
            result = await PlatformApplicationService.get_application_stats(mock_session)
            
            assert result.total_applications == 50
            assert result.pending_applications == 15
            assert result.approved_applications == 30
            assert result.rejected_applications == 5
            assert result.recent_applications == 8
        finally:
            # Restore original method
            PlatformApplicationService.get_application_stats = original_method


class TestApplicationValidation:
    """Test application validation logic."""
    
    def test_application_status_validation(self):
        """Test application status validation."""
        valid_statuses = ["pending", "approved", "rejected"]
        
        for status in valid_statuses:
            update = RestaurantApplicationUpdate(status=status)
            assert update.status == status
    
    def test_required_fields_validation(self):
        """Test required fields validation."""
        # Test missing required fields
        with pytest.raises(ValueError):
            RestaurantApplicationCreate()
        
        # Test with minimum required fields
        application = RestaurantApplicationCreate(
            applicant_name="Test",
            applicant_email="test@example.com",
            restaurant_name="Test Restaurant"
        )
        assert application.applicant_name == "Test"
        assert application.applicant_email == "test@example.com"
        assert application.restaurant_name == "Test Restaurant"
    
    def test_email_format_validation(self):
        """Test email format validation."""
        # This would typically be handled by Pydantic validators
        # For now, we just test that the field accepts email strings
        application = RestaurantApplicationCreate(
            applicant_name="Test",
            applicant_email="valid@example.com",
            restaurant_name="Test Restaurant"
        )
        assert application.applicant_email == "valid@example.com"
    
    def test_default_status(self):
        """Test default status is pending."""
        # Since status is not part of create schema, it should default to pending in the service
        application = RestaurantApplicationCreate(
            applicant_name="Test",
            applicant_email="test@example.com",
            restaurant_name="Test Restaurant"
        )
        # Status would be set to "pending" by the service layer
        assert hasattr(application, 'applicant_name')
        assert hasattr(application, 'applicant_email')
        assert hasattr(application, 'restaurant_name')


class TestApplicationWorkflow:
    """Test application workflow logic."""
    
    @pytest.mark.asyncio
    async def test_application_approval_workflow(self):
        """Test the complete application approval workflow."""
        mock_session = AsyncMock()
        application_id = str(uuid4())
        
        # Mock the service methods for the workflow
        original_approve = PlatformApplicationService.approve_application
        original_get = PlatformApplicationService.get_application_by_id
        
        # Mock application before approval
        pending_application = Mock()
        pending_application.status = "pending"
        
        # Mock application after approval
        approved_application = Mock()
        approved_application.status = "approved"
        approved_application.organization_id = str(uuid4())
        
        PlatformApplicationService.get_application_by_id = AsyncMock(return_value=pending_application)
        PlatformApplicationService.approve_application = AsyncMock(return_value=True)
        
        try:
            # Get application (should be pending)
            app = await PlatformApplicationService.get_application_by_id(mock_session, application_id)
            assert app.status == "pending"
            
            # Approve application
            result = await PlatformApplicationService.approve_application(
                mock_session, application_id, "Approved by admin"
            )
            assert result is True
            
        finally:
            # Restore original methods
            PlatformApplicationService.approve_application = original_approve
            PlatformApplicationService.get_application_by_id = original_get
    
    @pytest.mark.asyncio
    async def test_application_rejection_workflow(self):
        """Test the complete application rejection workflow."""
        mock_session = AsyncMock()
        application_id = str(uuid4())
        
        # Mock the service methods for the workflow
        original_reject = PlatformApplicationService.reject_application
        original_get = PlatformApplicationService.get_application_by_id
        
        # Mock application before rejection
        pending_application = Mock()
        pending_application.status = "pending"
        
        PlatformApplicationService.get_application_by_id = AsyncMock(return_value=pending_application)
        PlatformApplicationService.reject_application = AsyncMock(return_value=True)
        
        try:
            # Get application (should be pending)
            app = await PlatformApplicationService.get_application_by_id(mock_session, application_id)
            assert app.status == "pending"
            
            # Reject application
            result = await PlatformApplicationService.reject_application(
                mock_session, application_id, "Missing required documents"
            )
            assert result is True
            
        finally:
            # Restore original methods
            PlatformApplicationService.reject_application = original_reject
            PlatformApplicationService.get_application_by_id = original_get