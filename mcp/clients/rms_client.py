"""RMS API client for MCP server."""

import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import date, time
import logging

from config import Config
from models.reservation import (
    ReservationRequest, ReservationUpdate, ReservationCancel,
    AvailabilityRequest, ReservationDetails, AvailabilityResponse,
    ReservationConfirmation, AvailabilitySlot
)

logger = logging.getLogger(__name__)


class RMSAPIClient:
    """Client for communicating with RMS backend API."""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or Config.RMS_API_URL
        self.api_key = api_key or Config.RMS_API_KEY
        self.default_restaurant_id = Config.DEFAULT_RESTAURANT_ID
        self.default_organization_id = Config.DEFAULT_ORGANIZATION_ID
        
        # HTTP client with timeout and retry configuration
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _get_headers(self, restaurant_id: str = None) -> Dict[str, str]:
        """Get request headers with tenant context."""
        headers = {
            "Content-Type": "application/json",
            "X-Restaurant-ID": restaurant_id or self.default_restaurant_id,
            "X-Organization-ID": self.default_organization_id,
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def check_availability(self, request: AvailabilityRequest) -> AvailabilityResponse:
        """Check table availability for given date, time, and party size."""
        try:
            url = f"{self.base_url}/api/v1/public/reservations/{request.restaurant_id}/availability"
            params = {
                "date": request.date.isoformat(),
                "party_size": request.party_size
            }
            
            headers = self._get_headers(request.restaurant_id)
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Transform response to our model
            available_slots = []
            if "available_slots" in data:
                for slot in data["available_slots"]:
                    available_slots.append(AvailabilitySlot(
                        time=slot["time"],
                        available_tables=slot["available_tables"],
                        duration_minutes=120
                    ))
            
            return AvailabilityResponse(
                date=request.date.isoformat(),
                party_size=request.party_size,
                available_slots=available_slots,
                message=f"Found {len(available_slots)} available slots for {request.party_size} guests on {request.date}"
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error checking availability: {e}")
            return AvailabilityResponse(
                date=request.date.isoformat(),
                party_size=request.party_size,
                available_slots=[],
                message=f"Error checking availability: {e.response.status_code}"
            )
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return AvailabilityResponse(
                date=request.date.isoformat(),
                party_size=request.party_size,
                available_slots=[],
                message=f"Error checking availability: {str(e)}"
            )
    
    async def create_reservation(self, request: ReservationRequest) -> ReservationConfirmation:
        """Create a new reservation."""
        try:
            url = f"{self.base_url}/api/v1/public/reservations/{request.restaurant_id}/book"
            
            # Transform time object to string format
            time_str = request.time.strftime("%H:%M")
            
            payload = {
                "customer_name": request.customer_name,
                "customer_email": request.customer_email,
                "customer_phone": request.customer_phone,
                "reservation_date": request.date.isoformat(),
                "reservation_time": time_str,
                "party_size": request.party_size,
                "special_requests": request.special_requests or ""
            }
            
            headers = self._get_headers(request.restaurant_id)
            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            return ReservationConfirmation(
                reservation_id=data["reservation_id"],
                confirmation_number=data.get("confirmation_number", data["reservation_id"][:8].upper()),
                customer_name=data["customer_name"],
                date=data["reservation_date"],
                time=data["reservation_time"],
                party_size=data["party_size"],
                restaurant_name=data.get("restaurant_name", "Demo Restaurant"),
                status=data.get("status", "confirmed"),
                message=f"Reservation confirmed for {data['customer_name']} on {data['reservation_date']} at {data['reservation_time']}",
                special_requests=data.get("special_requests")
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating reservation: {e}")
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except:
                pass
            
            raise Exception(f"Failed to create reservation: {error_detail}")
        
        except Exception as e:
            logger.error(f"Error creating reservation: {e}")
            raise Exception(f"Failed to create reservation: {str(e)}")
    
    async def get_reservation(self, reservation_id: str, customer_email: str) -> ReservationDetails:
        """Get reservation details by ID."""
        try:
            # For public API, we'll use the restaurant ID from the reservation
            # In a real implementation, you might need to lookup the restaurant first
            url = f"{self.base_url}/api/v1/public/reservations/{self.default_restaurant_id}/{reservation_id}"
            
            headers = self._get_headers()
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Verify customer email matches
            if data["customer_email"].lower() != customer_email.lower():
                raise Exception("Email does not match reservation")
            
            return ReservationDetails(
                id=data["id"],
                customer_name=data["customer_name"],
                customer_email=data["customer_email"],
                customer_phone=data["customer_phone"],
                date=data["reservation_date"],
                time=data["reservation_time"],
                party_size=data["party_size"],
                status=data.get("status", "confirmed"),
                special_requests=data.get("special_requests"),
                created_at=data.get("created_at", ""),
                restaurant_name=data.get("restaurant_name", "Demo Restaurant"),
                table_number=data.get("table_number")
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting reservation: {e}")
            if e.response.status_code == 404:
                raise Exception("Reservation not found")
            raise Exception(f"Failed to get reservation: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Error getting reservation: {e}")
            raise Exception(f"Failed to get reservation: {str(e)}")
    
    async def update_reservation(self, request: ReservationUpdate) -> ReservationDetails:
        """Update an existing reservation."""
        try:
            url = f"{self.base_url}/api/v1/public/reservations/{self.default_restaurant_id}/{request.reservation_id}"
            
            # Build update payload
            payload = {}
            if request.date:
                payload["reservation_date"] = request.date.isoformat()
            if request.time:
                payload["reservation_time"] = request.time.strftime("%H:%M")
            if request.party_size:
                payload["party_size"] = request.party_size
            if request.special_requests is not None:
                payload["special_requests"] = request.special_requests
            
            headers = self._get_headers()
            response = await self.client.put(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            return ReservationDetails(
                id=data["id"],
                customer_name=data["customer_name"],
                customer_email=data["customer_email"],
                customer_phone=data["customer_phone"],
                date=data["reservation_date"],
                time=data["reservation_time"],
                party_size=data["party_size"],
                status=data.get("status", "confirmed"),
                special_requests=data.get("special_requests"),
                created_at=data.get("created_at", ""),
                restaurant_name=data.get("restaurant_name", "Demo Restaurant"),
                table_number=data.get("table_number")
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error updating reservation: {e}")
            raise Exception(f"Failed to update reservation: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Error updating reservation: {e}")
            raise Exception(f"Failed to update reservation: {str(e)}")
    
    async def cancel_reservation(self, request: ReservationCancel) -> Dict[str, Any]:
        """Cancel a reservation."""
        try:
            url = f"{self.base_url}/api/v1/public/reservations/{self.default_restaurant_id}/{request.reservation_id}"
            
            headers = self._get_headers()
            response = await self.client.delete(url, headers=headers)
            response.raise_for_status()
            
            return {
                "success": True,
                "message": f"Reservation {request.reservation_id} has been cancelled",
                "reservation_id": request.reservation_id,
                "reason": request.reason
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error cancelling reservation: {e}")
            raise Exception(f"Failed to cancel reservation: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Error cancelling reservation: {e}")
            raise Exception(f"Failed to cancel reservation: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check if RMS API is healthy."""
        try:
            url = f"{self.base_url}/health"
            response = await self.client.get(url, timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False