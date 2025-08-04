"""Mock Database for API Contract Testing.

This module provides database mocking functionality for testing the gateway service.
Uses SQLite in-memory database to simulate PostgreSQL.
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class MockDatabase:
    """Mock database that simulates PostgreSQL behavior using SQLite."""
    
    def __init__(self):
        """Initialize in-memory SQLite database."""
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._insert_test_data()
    
    def _create_tables(self):
        """Create database tables."""
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                join_date DATE NOT NULL DEFAULT CURRENT_DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Face entries table
        cursor.execute("""
            CREATE TABLE face_entries (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                embedding BLOB NOT NULL,
                quality TEXT NOT NULL CHECK (quality IN ('high', 'medium', 'low')),
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Auth sessions table
        cursor.execute("""
            CREATE TABLE auth_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX idx_face_entries_user_id ON face_entries(user_id)")
        cursor.execute("CREATE INDEX idx_auth_sessions_token ON auth_sessions(token)")
        
        self.conn.commit()
    
    def _insert_test_data(self):
        """Insert test data for API testing."""
        cursor = self.conn.cursor()
        
        # Test users
        test_users = [
            ("test-user-1", "testuser", "Test User", "test@example.com"),
            ("test-user-2", "demo", "Demo User", "demo@example.com"),
            ("test-user-3", "admin", "Admin User", "admin@example.com"),
        ]
        
        for user_id, username, full_name, email in test_users:
            cursor.execute("""
                INSERT INTO users (id, username, full_name, email)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, full_name, email))
        
        # Test face entries
        cursor.execute("""
            INSERT INTO face_entries (id, user_id, embedding, quality)
            VALUES (?, ?, ?, ?)
        """, ("face-1", "test-user-1", b"mock-embedding-testuser", "high"))
        
        cursor.execute("""
            INSERT INTO face_entries (id, user_id, embedding, quality)
            VALUES (?, ?, ?, ?)
        """, ("face-2", "test-user-2", b"mock-embedding-demo", "medium"))
        
        self.conn.commit()
    
    def get_connection_string(self) -> str:
        """Get PostgreSQL-style connection string pointing to mock database.
        
        In real implementation, this would start a mock PostgreSQL server.
        For simplicity, we'll return SQLite connection info.
        """
        return ":memory:"
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Execute a query and return results."""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        if query.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        else:
            self.conn.commit()
            return []
    
    def close(self):
        """Close the database connection."""
        self.conn.close()


# Global mock database instance for tests
_mock_db_instance = None


def get_mock_database() -> MockDatabase:
    """Get singleton mock database instance."""
    global _mock_db_instance
    if _mock_db_instance is None:
        _mock_db_instance = MockDatabase()
    return _mock_db_instance


def reset_mock_database():
    """Reset the mock database (create new instance)."""
    global _mock_db_instance
    if _mock_db_instance:
        _mock_db_instance.close()
    _mock_db_instance = MockDatabase()
    return _mock_db_instance
