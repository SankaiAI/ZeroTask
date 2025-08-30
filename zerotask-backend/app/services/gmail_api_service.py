"""
Gmail API Service for ZeroTask - PRD Section 8 Implementation

This service provides Gmail API functionality for reading emails and creating drafts.
It integrates with the Gmail OAuth service to use authenticated credentials and follows
the local-first architecture with minimal data transmission.

Key Features:
- Read Gmail messages with filters and pagination
- Search for specific email content
- Create draft replies (no sending capability)
- Fetch email threads and metadata
- Local processing with evidence link generation
"""

import base64
import email
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import httpx
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session

from app.services.gmail_oauth_service import GmailOAuthService


class GmailApiService:
    """Gmail API service for email reading and draft creation - PRD Section 8"""
    
    @staticmethod
    async def get_authenticated_service(db: Session):
        """Get authenticated Gmail API service"""
        credentials = await GmailOAuthService.get_valid_credentials(db)
        
        if not credentials:
            raise ValueError("Gmail not authenticated. Please complete OAuth flow first.")
        
        try:
            service = build('gmail', 'v1', credentials=credentials)
            return service
        except Exception as e:
            raise ValueError(f"Failed to build Gmail service: {str(e)}")
    
    @staticmethod
    async def get_user_profile(db: Session) -> Dict[str, Any]:
        """
        Get Gmail user profile information
        
        Returns:
            User profile with email address and message counts
        """
        try:
            service = await GmailApiService.get_authenticated_service(db)
            
            profile = service.users().getProfile(userId='me').execute()
            
            return {
                "email_address": profile.get('emailAddress'),
                "messages_total": profile.get('messagesTotal', 0),
                "threads_total": profile.get('threadsTotal', 0),
                "history_id": profile.get('historyId')
            }
            
        except HttpError as e:
            raise ValueError(f"Gmail API error: {e}")
        except Exception as e:
            raise ValueError(f"Error getting user profile: {str(e)}")
    
    @staticmethod
    async def get_recent_messages(
        db: Session,
        max_results: int = 50,
        query: Optional[str] = None,
        label_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent Gmail messages with optional filtering
        
        Args:
            db: Database session
            max_results: Maximum number of messages to return
            query: Gmail search query (e.g., "is:unread", "in:inbox")
            label_ids: List of label IDs to filter by
            
        Returns:
            List of message metadata and content
        """
        try:
            service = await GmailApiService.get_authenticated_service(db)
            
            # Build query parameters
            list_params = {
                'userId': 'me',
                'maxResults': max_results,
                'includeSpamTrash': False
            }
            
            if query:
                list_params['q'] = query
            if label_ids:
                list_params['labelIds'] = label_ids
                
            # Get message list
            messages_result = service.users().messages().list(**list_params).execute()
            messages = messages_result.get('messages', [])
            
            # Fetch detailed information for each message
            detailed_messages = []
            for message in messages:
                try:
                    msg = service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    parsed_message = GmailApiService._parse_message(msg)
                    detailed_messages.append(parsed_message)
                    
                except HttpError as e:
                    print(f"Error fetching message {message['id']}: {e}")
                    continue
            
            return detailed_messages
            
        except HttpError as e:
            raise ValueError(f"Gmail API error: {e}")
        except Exception as e:
            raise ValueError(f"Error getting recent messages: {str(e)}")
    
    @staticmethod
    async def get_today_messages(db: Session, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Get today's Gmail messages - PRD requirement for daily brief
        
        Returns:
            List of today's messages with metadata
        """
        today = datetime.now().strftime('%Y/%m/%d')
        query = f"after:{today}"
        
        return await GmailApiService.get_recent_messages(
            db=db,
            max_results=max_results,
            query=query
        )
    
    @staticmethod
    async def get_important_threads(db: Session, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Get important email threads from recent days - PRD requirement
        
        Args:
            db: Database session
            days_back: Number of days to look back for threads
            
        Returns:
            List of important thread information
        """
        since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
        
        # Search for important indicators
        queries = [
            f"is:important after:{since_date}",
            f"is:starred after:{since_date}",
            f"from:me after:{since_date}",  # Sent emails often indicate importance
        ]
        
        all_threads = []
        
        for query in queries:
            try:
                messages = await GmailApiService.get_recent_messages(
                    db=db,
                    max_results=20,
                    query=query
                )
                
                # Group by thread ID to avoid duplicates
                for message in messages:
                    thread_id = message.get('thread_id')
                    if not any(t.get('thread_id') == thread_id for t in all_threads):
                        # Get full thread context
                        thread_info = await GmailApiService.get_thread(db, thread_id)
                        if thread_info:
                            all_threads.append(thread_info)
                            
            except Exception as e:
                print(f"Error getting threads for query '{query}': {e}")
                continue
        
        return all_threads[:50]  # Limit to avoid overwhelming
    
    @staticmethod
    async def get_thread(db: Session, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full Gmail thread with all messages
        
        Args:
            db: Database session
            thread_id: Gmail thread ID
            
        Returns:
            Thread information with all messages
        """
        try:
            service = await GmailApiService.get_authenticated_service(db)
            
            thread = service.users().threads().get(
                userId='me',
                id=thread_id,
                format='full'
            ).execute()
            
            messages = []
            for msg in thread.get('messages', []):
                parsed_message = GmailApiService._parse_message(msg)
                messages.append(parsed_message)
            
            if not messages:
                return None
            
            # Use first message for thread metadata
            first_message = messages[0]
            
            return {
                'thread_id': thread_id,
                'subject': first_message.get('subject'),
                'participants': GmailApiService._extract_participants(messages),
                'message_count': len(messages),
                'messages': messages,
                'last_message_date': messages[-1].get('date'),
                'snippet': thread.get('snippet', ''),
                'labels': first_message.get('labels', []),
                'web_link': f"https://mail.google.com/mail/u/0/#inbox/{thread_id}"
            }
            
        except HttpError as e:
            print(f"Error getting thread {thread_id}: {e}")
            return None
        except Exception as e:
            print(f"Error processing thread {thread_id}: {e}")
            return None
    
    @staticmethod
    def _parse_message(message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail message into structured format"""
        headers = {h['name'].lower(): h['value'] for h in message['payload'].get('headers', [])}
        
        # Extract message body
        body = GmailApiService._extract_message_body(message['payload'])
        
        return {
            'id': message['id'],
            'thread_id': message['threadId'],
            'subject': headers.get('subject', ''),
            'from': headers.get('from', ''),
            'to': headers.get('to', ''),
            'date': headers.get('date', ''),
            'body': body,
            'snippet': message.get('snippet', ''),
            'labels': message.get('labelIds', []),
            'internal_date': message.get('internalDate'),
            'web_link': f"https://mail.google.com/mail/u/0/#inbox/{message['id']}"
        }
    
    @staticmethod
    def _extract_message_body(payload: Dict[str, Any]) -> str:
        """Extract text body from Gmail message payload"""
        body = ""
        
        if 'parts' in payload:
            # Multi-part message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        data = part['body']['data']
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    # Fallback to HTML if no plain text
                    if 'data' in part['body']:
                        data = part['body']['data']
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            # Single part message
            if payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
            elif payload['mimeType'] == 'text/html' and 'data' in payload['body']:
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    @staticmethod
    def _extract_participants(messages: List[Dict[str, Any]]) -> List[str]:
        """Extract unique participants from thread messages"""
        participants = set()
        
        for msg in messages:
            if msg.get('from'):
                participants.add(msg['from'])
            if msg.get('to'):
                # Parse multiple recipients
                recipients = msg['to'].split(',')
                for recipient in recipients:
                    participants.add(recipient.strip())
        
        return list(participants)
    
    @staticmethod
    async def create_draft_reply(
        db: Session,
        message_id: str,
        draft_content: str,
        subject_prefix: str = "Re: "
    ) -> Dict[str, Any]:
        """
        Create a Gmail draft reply - PRD Section 8 requirement
        
        Args:
            db: Database session
            message_id: ID of message to reply to
            draft_content: Content of the draft reply
            subject_prefix: Prefix for reply subject
            
        Returns:
            Draft information including Gmail draft ID
        """
        try:
            service = await GmailApiService.get_authenticated_service(db)
            
            # Get original message for reply context
            original_msg = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            original_headers = {
                h['name'].lower(): h['value'] 
                for h in original_msg['payload'].get('headers', [])
            }
            
            # Build reply message
            reply_to = original_headers.get('reply-to', original_headers.get('from', ''))
            original_subject = original_headers.get('subject', '')
            
            # Ensure subject has Re: prefix
            if not original_subject.startswith('Re:'):
                reply_subject = f"{subject_prefix}{original_subject}"
            else:
                reply_subject = original_subject
            
            # Create MIME message
            message = MIMEText(draft_content)
            message['to'] = reply_to
            message['subject'] = reply_subject
            message['In-Reply-To'] = original_headers.get('message-id', '')
            message['References'] = original_headers.get('message-id', '')
            
            # Create draft
            draft_message = {
                'message': {
                    'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8'),
                    'threadId': original_msg['threadId']
                }
            }
            
            draft = service.users().drafts().create(
                userId='me',
                body=draft_message
            ).execute()
            
            return {
                'success': True,
                'draft_id': draft['id'],
                'message': 'Gmail draft created successfully',
                'thread_id': original_msg['threadId'],
                'subject': reply_subject,
                'recipient': reply_to,
                'gmail_link': f"https://mail.google.com/mail/u/0/#drafts/{draft['id']}"
            }
            
        except HttpError as e:
            return {
                'success': False,
                'message': f'Gmail API error: {e}',
                'error_code': e.resp.status if hasattr(e, 'resp') else None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating draft: {str(e)}'
            }
    
    @staticmethod
    async def search_emails(
        db: Session,
        query: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search Gmail messages with query
        
        Args:
            db: Database session
            query: Gmail search query syntax
            max_results: Maximum results to return
            
        Returns:
            List of matching messages
        """
        return await GmailApiService.get_recent_messages(
            db=db,
            max_results=max_results,
            query=query
        )
    
    @staticmethod
    async def get_labels(db: Session) -> List[Dict[str, Any]]:
        """
        Get Gmail labels for filtering
        
        Returns:
            List of available Gmail labels
        """
        try:
            service = await GmailApiService.get_authenticated_service(db)
            
            labels_result = service.users().labels().list(userId='me').execute()
            labels = labels_result.get('labels', [])
            
            return [
                {
                    'id': label['id'],
                    'name': label['name'],
                    'type': label.get('type', 'user'),
                    'messages_total': label.get('messagesTotal', 0),
                    'messages_unread': label.get('messagesUnread', 0)
                }
                for label in labels
            ]
            
        except HttpError as e:
            raise ValueError(f"Gmail API error: {e}")
        except Exception as e:
            raise ValueError(f"Error getting labels: {str(e)}")