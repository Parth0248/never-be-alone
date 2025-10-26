"""Calendar & Reminder Agent - Creates and manages calendar events and reminders."""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import re
from .base_agent import BaseAgent


class CalendarAgent(BaseAgent):
    """Agent that creates calendar events and reminders."""

    def __init__(self):
        super().__init__(
            name="calendar_agent",
            description="Creates calendar events, reminders, and manages scheduling"
        )
        self.reminders = []  # In-memory storage (would use database in production)

    async def handle_task(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calendar and reminder tasks.

        Args:
            action: Action to perform (create_reminder, create_event, list_reminders)
            params: Parameters for the action

        Returns:
            Task result
        """
        if action == "create_reminder":
            return await self._create_reminder(params)
        elif action == "create_event":
            return await self._create_event(params)
        elif action == "list_reminders":
            return await self._list_reminders(params)
        elif action == "delete_reminder":
            return await self._delete_reminder(params)
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "message": "Action not supported"
            }

    async def _create_reminder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a reminder from parameters.

        Args:
            params: Dict containing:
                - text: Reminder text
                - time: Time reference (e.g., "tomorrow", "3pm")
                - action: Optional action to perform
                - person: Optional person related to reminder

        Returns:
            Reminder creation result
        """
        text = params.get("text", "")
        time_ref = params.get("time")

        # Parse time reference
        reminder_time = self._parse_time_reference(time_ref)

        # Create reminder object
        reminder = {
            "id": len(self.reminders) + 1,
            "text": text,
            "time": reminder_time,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "params": params
        }

        self.reminders.append(reminder)

        # In production, would integrate with:
        # - Google Calendar API
        # - Apple Calendar
        # - Notion
        # - Todoist
        # etc.

        return {
            "success": True,
            "result": {
                "reminder_id": reminder["id"],
                "reminder": reminder,
                "formatted_time": reminder_time.strftime("%Y-%m-%d %H:%M") if isinstance(reminder_time, datetime) else reminder_time
            },
            "message": f"Reminder created for {reminder_time}"
        }

    async def _create_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a calendar event.

        Args:
            params: Dict containing:
                - title: Event title
                - start_time: Start time
                - end_time: End time
                - location: Optional location
                - attendees: Optional list of attendees

        Returns:
            Event creation result
        """
        title = params.get("title", params.get("text", "Untitled Event"))
        start_time = self._parse_time_reference(params.get("start_time"))
        end_time = params.get("end_time")

        if not end_time and isinstance(start_time, datetime):
            end_time = start_time + timedelta(hours=1)  # Default 1-hour event
        else:
            end_time = self._parse_time_reference(end_time)

        event = {
            "id": f"event_{len(self.reminders) + 1}",
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "location": params.get("location"),
            "attendees": params.get("attendees", []),
            "created_at": datetime.now().isoformat()
        }

        # In production, integrate with Google Calendar API
        # service = build('calendar', 'v3', credentials=credentials)
        # event = service.events().insert(calendarId='primary', body=event).execute()

        return {
            "success": True,
            "result": {
                "event_id": event["id"],
                "event": event
            },
            "message": f"Event '{title}' created for {start_time}"
        }

    async def _list_reminders(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List active reminders.

        Args:
            params: Optional filters (status, date_range)

        Returns:
            List of reminders
        """
        status_filter = params.get("status", "active")

        filtered_reminders = [
            r for r in self.reminders
            if r.get("status") == status_filter
        ]

        return {
            "success": True,
            "result": {
                "reminders": filtered_reminders,
                "count": len(filtered_reminders)
            },
            "message": f"Found {len(filtered_reminders)} reminders"
        }

    async def _delete_reminder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a reminder.

        Args:
            params: Dict containing reminder_id

        Returns:
            Deletion result
        """
        reminder_id = params.get("reminder_id")

        for reminder in self.reminders:
            if reminder.get("id") == reminder_id:
                reminder["status"] = "deleted"
                return {
                    "success": True,
                    "result": {"reminder_id": reminder_id},
                    "message": "Reminder deleted"
                }

        return {
            "success": False,
            "error": "Reminder not found",
            "message": f"No reminder found with id {reminder_id}"
        }

    def _parse_time_reference(self, time_ref: Any) -> datetime:
        """Parse a time reference into a datetime object.

        Args:
            time_ref: Time reference (string like "tomorrow", "3pm", or datetime)

        Returns:
            datetime object
        """
        if isinstance(time_ref, datetime):
            return time_ref

        if not time_ref or not isinstance(time_ref, str):
            return datetime.now() + timedelta(hours=1)  # Default to 1 hour from now

        time_ref = time_ref.lower().strip()
        now = datetime.now()

        # Handle relative time references
        if time_ref == "now":
            return now
        elif time_ref == "today":
            return now.replace(hour=18, minute=0, second=0, microsecond=0)  # Default to 6pm
        elif time_ref == "tomorrow":
            return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)  # 9am tomorrow
        elif time_ref == "tonight":
            return now.replace(hour=20, minute=0, second=0, microsecond=0)  # 8pm
        elif time_ref == "next week":
            return (now + timedelta(weeks=1)).replace(hour=9, minute=0, second=0, microsecond=0)

        # Handle day names
        days_of_week = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }

        for day_name, day_num in days_of_week.items():
            if day_name in time_ref:
                days_ahead = day_num - now.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                return (now + timedelta(days=days_ahead)).replace(hour=9, minute=0, second=0, microsecond=0)

        # Handle time patterns like "3pm", "15:00"
        time_pattern = r'(\d{1,2}):?(\d{2})?\s*(am|pm)?'
        match = re.search(time_pattern, time_ref)

        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            am_pm = match.group(3)

            if am_pm:
                if am_pm == "pm" and hour < 12:
                    hour += 12
                elif am_pm == "am" and hour == 12:
                    hour = 0

            # Determine if time should be today or tomorrow
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if target_time < now:
                target_time += timedelta(days=1)

            return target_time

        # Handle relative time like "in 2 hours", "in 30 minutes"
        relative_pattern = r'in\s+(\d+)\s+(minute|hour|day|week)s?'
        match = re.search(relative_pattern, time_ref)

        if match:
            amount = int(match.group(1))
            unit = match.group(2)

            if unit == "minute":
                return now + timedelta(minutes=amount)
            elif unit == "hour":
                return now + timedelta(hours=amount)
            elif unit == "day":
                return now + timedelta(days=amount)
            elif unit == "week":
                return now + timedelta(weeks=amount)

        # Default: 1 hour from now
        return now + timedelta(hours=1)

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities."""
        return {
            "name": self.name,
            "description": self.description,
            "actions": [
                {
                    "name": "create_reminder",
                    "description": "Create a reminder for a specific time",
                    "params": ["text", "time", "action", "person"]
                },
                {
                    "name": "create_event",
                    "description": "Create a calendar event",
                    "params": ["title", "start_time", "end_time", "location", "attendees"]
                },
                {
                    "name": "list_reminders",
                    "description": "List active reminders",
                    "params": ["status", "date_range"]
                },
                {
                    "name": "delete_reminder",
                    "description": "Delete a reminder",
                    "params": ["reminder_id"]
                }
            ],
            "integrations": [
                "Google Calendar (planned)",
                "Apple Calendar (planned)",
                "Notion (planned)",
                "Todoist (planned)"
            ]
        }
