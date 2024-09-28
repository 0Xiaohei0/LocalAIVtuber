from enum import Enum, auto


class EventType(Enum):
    """
    Enum for all the allowed event types in the system.
    """
    INTERRUPT = auto()  # Triggered when you want interrupt the entire pipeline.

class EventManager:
    def __init__(self):
        # Dictionary to store events and their subscribers
        self._events = {}

    def subscribe(self, event_name: EventType, callback):
        """
        Subscribe a callback function to a named event.
        
        Parameters:
        event_name (str): The name of the event to subscribe to.
        callback (callable): The function to call when the event is triggered.
        """
        if event_name not in self._events:
            self._events[event_name] = []
        self._events[event_name].append(callback)

    def unsubscribe(self, event_name: EventType, callback):
        """
        Unsubscribe a callback function from a named event.
        
        Parameters:
        event_name (str): The name of the event to unsubscribe from.
        callback (callable): The function to remove from the subscription list.
        """
        if event_name in self._events:
            if callback in self._events[event_name]:
                self._events[event_name].remove(callback)

            # Clean up the event if no more subscribers exist
            if not self._events[event_name]:
                del self._events[event_name]

    def trigger(self, event_name, *args, **kwargs):
        """
        Trigger a named event, calling all subscribed functions.
        
        Parameters:
        event_name (str): The name of the event to trigger.
        *args, **kwargs: Arguments to pass to the subscribed callback functions.
        """
        if event_name in self._events:
            for callback in self._events[event_name]:
                callback(*args, **kwargs)

event_manager = EventManager()


# # Subscribe functions to the 'user_registered' event
# event_manager.subscribe('user_registered', on_user_registered)
# event_manager.subscribe('user_registered', send_welcome_email)

# # Trigger the event, which will call both subscribed functions
# event_manager.trigger('user_registered', username='JohnDoe')

# Output:
# User registered: JohnDoe
# Sending welcome email to JohnDoe
