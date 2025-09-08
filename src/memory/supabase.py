#!/usr/bin/env python3

"""
AUTHOR: Dan Njuguna
DATE: 2025-09-07

DESCRIPTION:
    This module defines the Supabase memory manager for the application.
    It provides functionality to store and retrieve user conversation history.
"""

from supabase import create_client, Client
from models.supabase import MessageRecord
from utils.config import settings
from loguru._logger import Logger
from utils.types import Sender
from datetime import datetime
from typing import List
import asyncio
import logging
import uuid


class SupabaseMemoryManager:
    """
    This class implements the memory management instance using supabase to
    ensure chats are persisted and saved for future reuse or context maintenance.
    """
    def __init__(
        self,
        logger: Logger | logging.Logger
    ):
        self.logger = logger
        self._client = self._create_client()

    def _create_client(self) -> Client:
        """
        Create a Supabase client instance.
        """
        try:
            self.logger.info("Creating Supabase client")
            
            supabase_url = settings.get("supabase_url", "")
            supabase_key = settings.get("supabase_key", "")
            
            if not supabase_url or not supabase_key:
                raise ValueError("Missing Supabase URL or API key in configuration")
            
            # Create client with minimal configuration to avoid version conflicts
            client: Client = create_client(supabase_url, supabase_key)
            
            self.logger.info("Supabase client created successfully")
            assert client is not None, "Supabase client creation failed"
            return client

        except Exception as e:
            self.logger.error(f"Error creating Supabase client: {e}")
            raise

    def ensure_uuid(self, value: str) -> str:
        try:
            return str(uuid.UUID(value))
        except (ValueError, TypeError):
            return str(uuid.uuid4())
    
    async def add_message_record(
        self,
        message: MessageRecord
    ) -> MessageRecord:
        """
        This method adds a message record to the Supabase database.
        """
        try:
            self.logger.info(f"Adding message record for user {message.user_id}")

            # Ensure UUIDs for user_id and chat_id
            user_id = self.ensure_uuid(message.user_id)
            chat_id = self.ensure_uuid(message.chat_id)

            # Convert message to dict for Supabase - use string IDs directly
            message_data = {
                "user_id": user_id,
                "chat_id": chat_id,
                "sender": message.sender.value,
                "message": message.message,
                "meta": message.meta or {},
                "timestamp": message.timestamp.isoformat()
            }
            
            # Insert into messages table
            result = await asyncio.to_thread(
                lambda: self._client.table("messages").insert(message_data).execute()
            )
            
            if result.data:
                self.logger.info(f"Message record added successfully: {result.data[0]['id']}")
                return message
            else:
                raise Exception("No data returned from insert operation")
                
        except Exception as e:
            self.logger.error(f"Error adding message record: {e}")
            raise

    async def get_conversation_history(
        self,
        user_id: str,
        chat_id: str,
        query: str = "",
        limit: int = 3
    ) -> List[MessageRecord]:
        """
        Retrieve conversation history for a user and optionally a specific chat.
        Filters and prioritizes messages based on relevance to the query.
        """
        try:
            self.logger.info(f"Retrieving conversation history for user {user_id} and chat {chat_id}")

            # Ensure uuid
            chat_id = self.ensure_uuid(chat_id)
            user_id = self.ensure_uuid(user_id)

            self.logger.debug(f"UUIDs after ensure_uuid - user_id: {user_id}, chat_id: {chat_id}")

            query_builder = self._client.table("messages").select("*").eq("user_id", user_id).eq("chat_id", chat_id)

            result = await asyncio.to_thread(
                lambda: query_builder.order("timestamp", desc=False).limit(limit * 2).execute()
            )

            if result.data:
                self.logger.debug(f"Retrieved data: {result.data}")
                messages = []
                for record in result.data:
                    message = MessageRecord(
                        user_id=str(record["user_id"]),
                        chat_id=str(record.get("chat_id", "")),
                        sender=Sender(record["sender"]),
                        message=record["message"],
                        meta=record.get("meta", {}),
                        timestamp=datetime.fromisoformat(record["timestamp"].replace('Z', '+00:00'))
                    )
                    messages.append(message)

                # Filter messages based on relevance to the query
                if query:
                    messages = sorted(
                        messages,
                        key=lambda msg: self._calculate_relevance(msg.message, query),
                        reverse=True
                    )

                # Limit the number of messages returned
                messages = messages[:limit]

                self.logger.info(f"Retrieved {len(messages)} relevant messages")
                return messages
            else:
                self.logger.debug("No data returned from query")
                return []

        except Exception as e:
            self.logger.error(f"Error retrieving conversation history: {e}")
            return []

    def _calculate_relevance(self, message: str, query: str) -> float:
        """
        Calculate the relevance of a message to the query.
        This is a placeholder for a more sophisticated relevance algorithm.
        """
        return query.lower() in message.lower()

    async def clear_conversation_history(
        self,
        user_id: str,
        chat_id: str
    ) -> bool:
        """
        Clear conversation history for a user and optionally a specific chat.
        """
        try:
            self.logger.info(f"Clearing conversation history for user {user_id}")

            query = self._client.table("messages").delete().eq("user_id", user_id).contains("meta", {"chat_id": chat_id})

            result = await asyncio.to_thread(lambda: query.execute())
            if hasattr(result, "error"):
                self.logger.error(f"Error clearing conversation history: {getattr(result, "error")}")
                return False
            self.logger.info(f"{result.count} messages deleted")

            self.logger.info(f"Cleared conversation history successfully")
            return True
                
        except Exception as e:
            self.logger.error(f"Error clearing conversation history: {e}")
            return False