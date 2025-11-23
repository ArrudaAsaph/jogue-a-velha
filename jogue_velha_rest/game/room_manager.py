class RoomManager:
    _instance = None
    _rooms = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RoomManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._rooms = {}
            self._initialized = True

    def find_one(self, query):
        """
        Find a room by query (compatible with MongoDB API)
        Args:
            query: dict with roomId key
        Returns:
            Room data or None
        """
        room_id = query.get('roomId')
        return self._rooms.get(room_id)

    def update_one(self, query, update):
        """
        Update a room (compatible with MongoDB API)
        Args:
            query: dict with roomId key
            update: dict with $set key containing fields to update
        """
        room_id = query.get('roomId')
        if room_id in self._rooms:
            set_data = update.get('$set', {})
            self._rooms[room_id].update(set_data)

    def insert_one(self, document):
        """
        Insert a new room
        Args:
            document: dict with room data
        """
        room_id = document.get('roomId')
        if room_id:
            self._rooms[room_id] = document

    def delete_one(self, query):
        """
        Delete a room
        Args:
            query: dict with roomId key
        """
        room_id = query.get('roomId')
        if room_id in self._rooms:
            del self._rooms[room_id]

    def clear_all(self):
        """Clear all rooms (useful for testing)"""
        self._rooms.clear()

# Global instance
room_manager = RoomManager()
