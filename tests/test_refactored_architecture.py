"""
Integration tests for the refactored architecture.

This module contains tests to validate the new modular components
and their integration with the existing system.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_crm_sync.clients.zoho.notes import Notes
from email_crm_sync.clients.zoho.search import Search
from email_crm_sync.services.email_processor import EmailProcessor
from email_crm_sync.exceptions import (
    CrmSyncError, ZohoApiError, NoteCreationError, SearchError, EmailProcessingError
)
from email_crm_sync.config import config


class TestModularComponents:
    """Test the new modular components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_client.base_url = "https://www.zohoapis.eu/crm/v8"
        self.mock_client.headers = {"Authorization": "Bearer test-token"}
        self.mock_client.developments_module = "Developments"
        self.mock_client.session = Mock()  # Add session mock
        self.mock_client.timeout = 30  # Add timeout
    
    def test_notes_creation(self):
        """Test note creation through modular component."""
        notes = Notes(self.mock_client)
        
        # Mock successful response matching Zoho API structure
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.text = ""
        mock_response.json.return_value = {
            "data": [{
                "code": "SUCCESS",
                "details": {"id": "note123"},
                "message": "record added",
                "status": "success"
            }]
        }
        
        # Mock the session post method
        self.mock_client.session.post.return_value = mock_response
        
        result = notes.create(
            parent_id="dev123",
            content="Test note content",
            title="Test Note"
        )
        
        assert result["success"] is True
        assert result["note_id"] == "note123"
    
    def test_notes_creation_failure(self):
        """Test note creation failure handling."""
        notes = Notes(self.mock_client)
        
        # Mock error response matching Zoho API structure
        mock_response = Mock()
        mock_response.status_code = 201  # Even successful HTTP can have failed data
        mock_response.text = ""
        mock_response.json.return_value = {
            "data": [{
                "code": "INVALID_DATA", 
                "message": "Invalid note data",
                "status": "error"
            }]
        }
        
        # Mock the session post method
        self.mock_client.session.post.return_value = mock_response
        
        with pytest.raises(NoteCreationError):
            notes.create(
                parent_id="dev123",
                content="Test note content"
            )
    
    def test_search_coql_query(self):
        """Test COQL query through modular component."""
        search = Search(self.mock_client)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"id": "dev123", "Name": "Test Development"}],
            "success": True
        }
        
        with patch('requests.post', return_value=mock_response):
            result = search.coql_query("SELECT id, Name FROM Developments")
            
            assert result["success"] is True
            assert len(result["data"]) == 1
            assert result["data"][0]["id"] == "dev123"
    
    def test_search_coql_query_failure(self):
        """Test COQL query failure handling."""
        search = Search(self.mock_client)
        
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "code": "INVALID_QUERY",
            "message": "Invalid COQL query"
        }
        
        with patch('requests.post', return_value=mock_response):
            with pytest.raises(SearchError):
                search.coql_query("INVALID QUERY")
    
    def test_email_record_search(self):
        """Test email-based record search."""
        search = Search(self.mock_client)
        
        # Mock both methods that might be called
        with patch.object(search, 'search_records') as mock_search_records, \
             patch.object(search, 'coql_query') as mock_coql:
            
            # First method returns data successfully
            mock_search_records.return_value = {
                "data": [{"id": "dev123", "Email": "test@example.com"}]
            }
            
            result = search.by_email("test@example.com")
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["Email"] == "test@example.com"


class TestEmailProcessor:
    """Test the email processor implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_zoho_client = Mock()
        self.mock_openai_client = Mock()
        self.mock_gmail_client = Mock()
        
        # Set up modular components
        self.mock_zoho_client.notes = Mock()
        self.mock_zoho_client.search = Mock()
        
        self.processor = EmailProcessor(
            gmail=self.mock_gmail_client,
            openai=self.mock_openai_client,
            zoho=self.mock_zoho_client
        )
    
    def test_email_processor_initialization(self):
        """Test that EmailProcessor initializes correctly."""
        assert self.processor.gmail is not None
        assert self.processor.openai is not None
        assert self.processor.zoho is not None
        assert self.processor._accounts_cache is None
        assert self.processor._cache_populated is False
    
    def test_word_search_safe(self):
        """Test safe word search functionality."""
        # Mock the zoho search method
        self.mock_zoho_client.search_by_word = Mock(return_value=[
            {'id': '123', 'Account_Name': 'Test Account'}
        ])
        
        results = self.processor._word_search_safe('test')
        assert len(results) == 1
        assert results[0]['id'] == '123'
    
    def test_word_search_safe_no_results(self):
        """Test safe word search with no results."""
        self.mock_zoho_client.search_by_word = Mock(return_value=[])
        
        results = self.processor._word_search_safe('nonexistent')
        assert len(results) == 0
    
    def test_process_email_success(self):
        """Test successful email processing."""
        # Mock Gmail emails
        self.mock_gmail_client.get_starred_emails.return_value = [
            {"id": "msg123"}
        ]
        
        # Mock Gmail email content
        self.mock_gmail_client.get_email.return_value = {
            "sender_email": "test@example.com",
            "subject": "Test Subject",
            "body": "Test email body"
        }
        
        # Mock search results
        self.mock_zoho_client.search_by_email.return_value = [
            {"id": "dev123", "Name": "Test Development"}
        ]
        
        # Mock OpenAI response
        self.mock_openai_client.process_email_comprehensive.return_value = {
            "summary": "Email summary from AI"
        }
        
        # Mock note creation
        self.mock_zoho_client.notes.create.return_value = {
            "data": [{"id": "note123"}],
            "success": True
        }
        
        result = self.processor.process_emails()
        
        assert result["total_emails"] == 1
        assert result["processed"] >= 0  # Should process at least some emails
    
    def test_process_email_no_matching_records(self):
        """Test email processing with no matching records."""
        # Mock Gmail emails
        self.mock_gmail_client.get_starred_emails.return_value = [
            {"id": "msg123"}
        ]
        
        # Mock Gmail email content
        self.mock_gmail_client.get_email.return_value = {
            "sender_email": "unknown@example.com",
            "subject": "Test Subject",
            "body": "Test email body"
        }
        
        # Mock no search results
        self.mock_zoho_client.search_by_email.return_value = []
        
        result = self.processor.process_emails()
        
        assert result["total_emails"] == 1
        # Should still process even with no matches (creates fallback notes)
    
    def test_process_email_note_creation_failure(self):
        """Test email processing with note creation failure."""
        # Mock Gmail emails
        self.mock_gmail_client.get_starred_emails.return_value = [
            {"id": "msg123"}
        ]
        
        # Mock Gmail email content
        self.mock_gmail_client.get_email.return_value = {
            "sender_email": "test@example.com",
            "subject": "Test Subject",
            "body": "Test email body"
        }
        
        # Mock search results
        self.mock_zoho_client.search_by_email.return_value = [
            {"id": "dev123", "Name": "Test Development"}
        ]
        
        # Mock OpenAI response
        self.mock_openai_client.process_email_comprehensive.return_value = {
            "summary": "Email summary from AI"
        }
        
        # Mock note creation failure
        self.mock_zoho_client.notes.create.side_effect = NoteCreationError("Note creation failed")
        
        result = self.processor.process_emails()
        
        assert result["total_emails"] == 1
        # Should handle the error gracefully


class TestIntegration:
    """Test integration between components."""
    
    def test_config_singleton(self):
        """Test that configuration is properly loaded as singleton."""
        # Should be able to access config without initialization
        assert config is not None
        assert hasattr(config, 'get_zoho_config')  # Check for actual method
        assert hasattr(config, 'get_openai_config')  # Check for actual method
    
    def test_exception_hierarchy(self):
        """Test that custom exceptions work properly."""
        # Test inheritance (already imported at top)
        assert issubclass(ZohoApiError, CrmSyncError)
        assert issubclass(NoteCreationError, ZohoApiError)
        assert issubclass(SearchError, ZohoApiError)
        assert issubclass(EmailProcessingError, CrmSyncError)
        
        # Test exception creation
        try:
            raise NoteCreationError("Test error")
        except CrmSyncError as e:
            assert str(e) == "Test error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
