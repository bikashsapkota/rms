"""Reservation management tools for MCP."""

from typing import Dict, Any
from datetime import datetime, date, time
import logging

from tools.base import ReservationTool
from models.common import ToolResponse
from models.reservation import (
    AvailabilityRequest, ReservationRequest, ReservationUpdate, 
    ReservationCancel, ReservationDetails
)

logger = logging.getLogger(__name__)


class CheckAvailabilityTool(ReservationTool):
    """Tool for checking table availability."""
    
    def __init__(self, rms_client):
        super().__init__(
            name="check_availability",
            description="Check table availability for a specific date, time, and party size",
            rms_client=rms_client
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResponse:
        """Execute availability check."""
        required_fields = ["restaurant_id", "date", "party_size"]
        
        if not self.validate_arguments(arguments, required_fields):
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error="Missing required fields: restaurant_id, date, party_size"
            )
        
        try:
            # Parse date and time
            date_obj = datetime.strptime(arguments["date"], "%Y-%m-%d").date()
            
            # For availability checks, we always set time to None to get all available slots
            # The user can see all options and choose their preferred time
            time_obj = None
            
            # Create availability request
            request = AvailabilityRequest(
                restaurant_id=arguments["restaurant_id"],
                date=date_obj,
                time=time_obj,
                party_size=int(arguments["party_size"])
            )
            
            # Check availability via RMS API
            response = await self.rms_client.check_availability(request)
            
            # Format result for user
            if response.available_slots:
                slot_details = []
                requested_time = arguments.get("time")
                for slot in response.available_slots:
                    # Highlight the requested time if it matches
                    if requested_time and slot.time == requested_time + ":00":
                        slot_details.append(f"- {slot.time} ({slot.available_tables} tables available) ⭐ REQUESTED TIME")
                    else:
                        slot_details.append(f"- {slot.time} ({slot.available_tables} tables available)")
                
                details = f"\nAvailable times:\n" + "\n".join(slot_details)
            else:
                details = "No available slots found."
            
            message = self.format_success_message("check_availability", details)
            
            return ToolResponse(
                tool_name=self.name,
                success=True,
                result={
                    "available": len(response.available_slots) > 0,
                    "date": response.date,
                    "party_size": response.party_size,
                    "available_slots": [
                        {
                            "time": slot.time,
                            "available_tables": slot.available_tables,
                            "duration_minutes": slot.duration_minutes
                        }
                        for slot in response.available_slots
                    ],
                    "message": message
                }
            )
            
        except ValueError as e:
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error=f"Invalid date or time format: {str(e)}"
            )
        except Exception as e:
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error=self.format_error_message(str(e))
            )


class CreateReservationTool(ReservationTool):
    """Tool for creating new reservations."""
    
    def __init__(self, rms_client):
        super().__init__(
            name="create_reservation",
            description="Create a new reservation",
            rms_client=rms_client
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResponse:
        """Execute reservation creation."""
        required_fields = [
            "restaurant_id", "customer_name", "customer_email", 
            "customer_phone", "date", "time", "party_size"
        ]
        
        if not self.validate_arguments(arguments, required_fields):
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error="Missing required fields: restaurant_id, customer_name, customer_email, customer_phone, date, time, party_size"
            )
        
        try:
            # Parse date and time
            date_obj = datetime.strptime(arguments["date"], "%Y-%m-%d").date()
            
            # Handle both HH:MM and HH:MM:SS time formats
            time_str = arguments["time"]
            if time_str.count(":") == 2:  # HH:MM:SS format
                time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
            else:  # HH:MM format
                time_obj = datetime.strptime(time_str, "%H:%M").time()
            
            # Create reservation request
            request = ReservationRequest(
                restaurant_id=arguments["restaurant_id"],
                customer_name=arguments["customer_name"],
                customer_email=arguments["customer_email"],
                customer_phone=arguments["customer_phone"],
                date=date_obj,
                time=time_obj,
                party_size=int(arguments["party_size"]),
                special_requests=arguments.get("special_requests")
            )
            
            # Create reservation via RMS API
            confirmation = await self.rms_client.create_reservation(request)
            
            # Format success message
            details = f"Confirmation: {confirmation.confirmation_number}\nDate: {confirmation.date}\nTime: {confirmation.time}\nParty size: {confirmation.party_size}"
            if confirmation.special_requests:
                details += f"\nSpecial requests: {confirmation.special_requests}"
            
            message = self.format_success_message("create_reservation", details)
            
            return ToolResponse(
                tool_name=self.name,
                success=True,
                result={
                    "reservation_id": confirmation.reservation_id,
                    "confirmation_number": confirmation.confirmation_number,
                    "customer_name": confirmation.customer_name,
                    "date": confirmation.date,
                    "time": confirmation.time,
                    "party_size": confirmation.party_size,
                    "restaurant_name": confirmation.restaurant_name,
                    "status": confirmation.status,
                    "message": message,
                    "special_requests": confirmation.special_requests
                }
            )
            
        except ValueError as e:
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error=f"Invalid date or time format: {str(e)}"
            )
        except Exception as e:
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error=self.format_error_message(str(e))
            )


class GetReservationTool(ReservationTool):
    """Tool for retrieving reservation details."""
    
    def __init__(self, rms_client):
        super().__init__(
            name="get_reservation",
            description="Retrieve reservation details by ID",
            rms_client=rms_client
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResponse:
        """Execute reservation retrieval."""
        required_fields = ["reservation_id", "customer_email"]
        
        if not self.validate_arguments(arguments, required_fields):
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error="Missing required fields: reservation_id, customer_email"
            )
        
        try:
            # Get reservation details via RMS API
            details = await self.rms_client.get_reservation(
                arguments["reservation_id"],
                arguments["customer_email"]
            )
            
            # Format details message
            details_msg = f"Customer: {details.customer_name}\nDate: {details.date}\nTime: {details.time}\nParty size: {details.party_size}\nStatus: {details.status}"
            if details.special_requests:
                details_msg += f"\nSpecial requests: {details.special_requests}"
            if details.table_number:
                details_msg += f"\nTable: {details.table_number}"
            
            message = self.format_success_message("get_reservation", details_msg)
            
            return ToolResponse(
                tool_name=self.name,
                success=True,
                result={
                    "id": details.id,
                    "customer_name": details.customer_name,
                    "customer_email": details.customer_email,
                    "customer_phone": details.customer_phone,
                    "date": details.date,
                    "time": details.time,
                    "party_size": details.party_size,
                    "status": details.status,
                    "special_requests": details.special_requests,
                    "created_at": details.created_at,
                    "restaurant_name": details.restaurant_name,
                    "table_number": details.table_number,
                    "message": message
                }
            )
            
        except Exception as e:
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error=self.format_error_message(str(e))
            )


class UpdateReservationTool(ReservationTool):
    """Tool for updating existing reservations."""
    
    def __init__(self, rms_client):
        super().__init__(
            name="update_reservation",
            description="Update an existing reservation",
            rms_client=rms_client
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResponse:
        """Execute reservation update."""
        required_fields = ["reservation_id", "customer_email"]
        
        if not self.validate_arguments(arguments, required_fields):
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error="Missing required fields: reservation_id, customer_email"
            )
        
        try:
            # Parse optional date and time if provided
            date_obj = None
            time_obj = None
            
            if arguments.get("date"):
                date_obj = datetime.strptime(arguments["date"], "%Y-%m-%d").date()
            
            if arguments.get("time"):
                time_obj = datetime.strptime(arguments["time"], "%H:%M").time()
            
            # Create update request
            request = ReservationUpdate(
                reservation_id=arguments["reservation_id"],
                customer_email=arguments["customer_email"],
                date=date_obj,
                time=time_obj,
                party_size=arguments.get("party_size"),
                special_requests=arguments.get("special_requests")
            )
            
            # Update reservation via RMS API
            details = await self.rms_client.update_reservation(request)
            
            # Format update message
            changes = []
            if date_obj:
                changes.append(f"Date: {details.date}")
            if time_obj:
                changes.append(f"Time: {details.time}")
            if arguments.get("party_size"):
                changes.append(f"Party size: {details.party_size}")
            if arguments.get("special_requests") is not None:
                changes.append(f"Special requests: {details.special_requests}")
            
            changes_msg = "\nUpdated: " + ", ".join(changes) if changes else ""
            message = self.format_success_message("update_reservation", changes_msg)
            
            return ToolResponse(
                tool_name=self.name,
                success=True,
                result={
                    "id": details.id,
                    "customer_name": details.customer_name,
                    "date": details.date,
                    "time": details.time,
                    "party_size": details.party_size,
                    "status": details.status,
                    "special_requests": details.special_requests,
                    "message": message
                }
            )
            
        except ValueError as e:
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error=f"Invalid date or time format: {str(e)}"
            )
        except Exception as e:
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error=self.format_error_message(str(e))
            )


class CancelReservationTool(ReservationTool):
    """Tool for canceling reservations."""
    
    def __init__(self, rms_client):
        super().__init__(
            name="cancel_reservation",
            description="Cancel a reservation",
            rms_client=rms_client
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResponse:
        """Execute reservation cancellation."""
        required_fields = ["reservation_id", "customer_email"]
        
        if not self.validate_arguments(arguments, required_fields):
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error="Missing required fields: reservation_id, customer_email"
            )
        
        try:
            # Create cancellation request
            request = ReservationCancel(
                reservation_id=arguments["reservation_id"],
                customer_email=arguments["customer_email"],
                reason=arguments.get("reason")
            )
            
            # Cancel reservation via RMS API
            result = await self.rms_client.cancel_reservation(request)
            
            # Format cancellation message
            details = f"Reservation {result['reservation_id']} has been cancelled."
            if result.get("reason"):
                details += f"\nReason: {result['reason']}"
            
            message = self.format_success_message("cancel_reservation", details)
            
            return ToolResponse(
                tool_name=self.name,
                success=True,
                result={
                    "success": result["success"],
                    "reservation_id": result["reservation_id"],
                    "reason": result.get("reason"),
                    "message": message
                }
            )
            
        except Exception as e:
            return ToolResponse(
                tool_name=self.name,
                success=False,
                result=None,
                error=self.format_error_message(str(e))
            )