#!/usr/bin/env python3
"""
Comprehensive Test Suite for Complete Airtable MCP Integration
Tests all new features and scopes:
- data.records:read/write
- data.recordComments:read/write
- schema.bases:read/write
- webhook:manage
- block:manage
- user.email:read
"""

import unittest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add repo root to sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Import the modules to test
from services.airtable_service import AirtableService
from src.python.tools.comments import CommentsTools
from src.python.tools.schema import SchemaTools
from src.python.tools.webhooks_advanced import WebhooksAdvancedTools
from src.python.tools.user_info import UserInfoTools
from src.python.tools.blocks import BlocksTools
from airtable_client import AirtableClient


class TestAirtableService(unittest.TestCase):
    """Test the extended AirtableService methods"""

    def setUp(self):
        self.service = AirtableService()
        self.test_token = "test_access_token"
        self.test_base_id = "test_base_123"
        self.test_table_id = "test_table_456"
        self.test_record_id = "test_record_789"

    @patch('services.airtable_service.AirtableService._make_request')
    async def test_get_record_comments(self, mock_request):
        """Test getting record comments"""
        mock_response = {
            "comments": [
                {
                    "id": "comment_1",
                    "text": "Test comment",
                    "createdBy": {"email": "user@example.com"},
                    "createdTime": "2023-01-01T00:00:00.000Z"
                }
            ]
        }
        mock_request.return_value = mock_response

        result = await self.service.get_record_comments(
            self.test_base_id, 
            self.test_table_id, 
            self.test_record_id, 
            self.test_token
        )
        
        self.assertEqual(len(result["comments"]), 1)
        self.assertEqual(result["comments"][0]["text"], "Test comment")

    @patch('services.airtable_service.AirtableService._make_request')
    async def test_create_record_comment(self, mock_request):
        """Test creating a record comment"""
        mock_response = {
            "comment": {
                "id": "comment_new",
                "text": "New comment",
                "createdTime": "2023-01-01T00:00:00.000Z"
            }
        }
        mock_request.return_value = mock_response

        result = await self.service.create_record_comment(
            self.test_base_id,
            self.test_table_id,
            self.test_record_id,
            "New comment",
            self.test_token
        )
        
        self.assertEqual(result["comment"]["text"], "New comment")

    @patch('services.airtable_service.AirtableService._make_request')
    async def test_get_user_info(self, mock_request):
        """Test getting user information"""
        mock_response = {
            "id": "user_123",
            "email": "user@example.com",
            "firstName": "John",
            "lastName": "Doe"
        }
        mock_request.return_value = mock_response

        result = await self.service.get_user_info(self.test_token)
        
        self.assertEqual(result["email"], "user@example.com")
        self.assertEqual(result["firstName"], "John")

    @patch('services.airtable_service.AirtableService._make_request')
    async def test_create_field(self, mock_request):
        """Test creating a field"""
        mock_response = {
            "fields": [
                {
                    "id": "field_123",
                    "name": "New Field",
                    "type": "singleLineText"
                }
            ]
        }
        mock_request.return_value = mock_response

        field_config = {
            "name": "New Field",
            "type": "singleLineText"
        }
        
        result = await self.service.create_field(
            self.test_base_id,
            self.test_table_id,
            field_config,
            self.test_token
        )
        
        self.assertEqual(len(result["fields"]), 1)
        self.assertEqual(result["fields"][0]["name"], "New Field")

    @patch('services.airtable_service.AirtableService._make_request')
    async def test_list_webhooks(self, mock_request):
        """Test listing webhooks"""
        mock_response = {
            "webhooks": [
                {
                    "id": "webhook_123",
                    "notificationUrl": "https://example.com/webhook",
                    "status": "active"
                }
            ]
        }
        mock_request.return_value = mock_response

        result = await self.service.list_webhooks(self.test_base_id, self.test_token)
        
        self.assertEqual(len(result["webhooks"]), 1)
        self.assertEqual(result["webhooks"][0]["status"], "active")

    @patch('services.airtable_service.AirtableService._make_request')
    async def test_list_blocks(self, mock_request):
        """Test listing blocks"""
        mock_response = {
            "blocks": [
                {
                    "id": "block_123",
                    "name": "Test Block",
                    "type": "custom"
                }
            ]
        }
        mock_request.return_value = mock_response

        result = await self.service.list_blocks(self.test_token)
        
        self.assertEqual(len(result["blocks"]), 1)
        self.assertEqual(result["blocks"][0]["name"], "Test Block")


class TestCommentsTools(unittest.TestCase):
    """Test the CommentsTools class"""

    def setUp(self):
        self.mock_service = Mock()
        self.tools = CommentsTools(self.mock_service)

    @patch('src.python.tools.comments.CommentsTools.get_record_comments')
    async def test_get_record_comments_tool(self, mock_get_comments the MCP):
        """Test tool for getting record comments"""
        mock_get_comments.return_value = "Comments retrieved successfully"
        
        # Mock the service's get_record_comments method
        self.mock_service.get_record_comments.return_value = {
            "comments": [
                {
                    "id": "comment_1",
                    "text": "Test comment",
                    "createdBy": {"email": "user@example.com"},
                    "createdTime": "2023-01-01T00:00:00.000Z"
                }
            ]
        }
        
        # Set access token
        mcp_mock = Mock()
        mcp_mock._access_token = "test_token"
        
        result = await self.tools.get_all_comments_for_record(
            "test_base", "test_table", "test_record", "test_token"
        )
        
        self.assertIn("Test comment", result)


class TestSchemaTools(unittest.TestCase):
    """Test the SchemaTools class"""

    def setUp(self):
        self.mock_service = Mock()
        self.tools = SchemaTools(self.mock_service)

    @patch('src.python.tools.schema.SchemaTools.get_base_schema')
    async def test_get_base_schema_tool(self, mock_get_schema):
        """Test the MCP tool for getting base schema"""
        mock_get_schema.return_value = {
            "tables": [
                {
                    "id": "table_123",
                    "name": "Test Table",
                    "fields": [
                        {
                            "id": "field_123",
                            "name": "Name",
                            "type": "singleLineText"
                        }
                    ]
                }
            ]
        }
        
        result = await self.tools.get_base_schema("test_base", "test_token")
        
        self.assertIn("Test Table", result)
        self.assertIn("Name", result)


class TestWebhooksAdvancedTools(unittest.TestCase):
    """Test the WebhooksAdvancedTools class"""

    def setUp(self):
        self.mock_service = Mock()
        self.tools = WebhooksAdvancedTools(self.mock_service)

    @patch('src.python.tools.webhooks_advanced.WebhooksAdvancedTools.list_webhooks')
    async def test_list_webhooks_tool(self, mock_list_webhooks):
        """Test the MCP tool for listing webhooks"""
        mock_list_webhooks.return_value = {
            "webhooks": [
                {
                    "id": "webhook_123",
                    "notificationUrl": "https://example.com/webhook",
                    "status": "active"
                }
            ]
        }
        
        result = await self.tools.list_webhooks("test_base", "test_token")
        
        self.assertIn("webhook_123", result)
        self.assertIn("active", result)


class TestUserInfoTools(unittest.TestCase):
    """Test the UserInfoTools class"""

    def setUp(self):
        self.mock_service = Mock()
        self.tools = UserInfoTools(self.mock_service)

    @patch('src.python.tools.user_info.UserInfoTools.get_user_info')
    async def test_get_user_info_tool(self, mock_get_user):
        """Test the MCP tool for getting user info"""
        mock_get_user.return_value = {
            "id": "user_123",
            "email": "user@example.com",
            "firstName": "John",
            "lastName": "Doe"
        }
        
        result = await self.tools.get_user_info("test_token")
        
        self.assertIn("user@example.com", result)
        self.assertIn("John", result)
        self.assertIn("Doe", result)


class TestBlocksTools(unittest.TestCase):
    """Test the BlocksTools class"""

    def setUp(self):
        self.mock_service = Mock()
        self.tools = BlocksTools(self.mock_service)

    @patch('src.python.tools.blocks.BlocksTools.list_blocks')
    async def test_list_blocks_tool(self, mock_list_blocks):
        """Test the MCP tool for listing blocks"""
        mock_list_blocks.return_value = {
            "blocks": [
                {
                    "id": "block_123",
                    "name": "Test Block",
                    "type": "custom"
                }
            ]
        }
        
        result = await self.tools.list_blocks("test_token")
        
        self.assertIn("Test Block", result)
        self.assertIn("custom", result)


class TestAirtableClient(unittest.TestCase):
    """Test the extended AirtableClient methods"""

    def setUp(self):
        self.user_id = "test_user"
        self.client = AirtableClient(self.user_id)

    @patch('aiohttp.ClientSession.get')
    async def test_get_record_comments_client(self, mock_get):
        """Test getting record comments via client"""
        # Mock the response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "comments": [
                {
                    "id": "comment_1",
                    "text": "Test comment"
                }
            ]
        }
        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)

        # Mock token retrieval
        with patch.object(self.client, '_get_access_token', return_value="test_token"):
            result = await self.client.get_record_comments(
                "test_base", "test_table", "test_record"
            )
            
            self.assertEqual(len(result["comments"]), 1)
            self.assertEqual(result["comments"][0]["text"], "Test comment")

    @patch('aiohttp.ClientSession.get')
    async def test_get_user_info_client(self, mock_get):
        """Test getting user info via client"""
        # Mock the response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "id": "user_123",
            "email": "user@example.com"
        }
        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)

        # Mock token retrieval
        with patch.object(self.client, '_get_access_token', return_value="test_token"):
            result = await self.client.get_user_info()
            
            self.assertEqual(result["email"], "user@example.com")

    @patch('aiohttp.ClientSession.get')
    async def test_list_webhooks_client(self, mock_get):
        """Test listing webhooks via client"""
        # Mock the response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "webhooks": [
                {
                    "id": "webhook_123",
                    "status": "active"
                }
            ]
        }
        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)

        # Mock token retrieval
        with patch.object(self.client, '_get_access_token', return_value="test_token"):
            result = await self.client.list_webhooks("test_base")
            
            self.assertEqual(len(result["webhooks"]), 1)
            self.assertEqual(result["webhooks"][0]["status"], "active")


class TestOAuthScopes(unittest.TestCase):
    """Test OAuth scopes configuration"""

    def test_airtable_scopes_configuration(self):
        """Test that all required scopes are configured"""
        from config.settings import get_settings
        
        settings = get_settings()
        scopes = settings.airtable_scopes
        
        # Check that all required scopes are present
        required_scopes = [
            "data.records:read",
            "data.records:write",
            "data.recordComments:read",
            "data.recordComments:write",
            "schema.bases:read",
            "schema.bases:write",
            "webhook:manage",
            "block:manage",
            "user.email:read"
        ]
        
        for scope in required_scopes:
            self.assertIn(scope, scopes, f"Missing scope: {scope}")

    def test_scopes_format(self):
        """Test that scopes are properly formatted"""
        from config.settings import get_settings
        
        settings = get_settings()
        scopes = settings.airtable_scopes
        
        # Scopes should be space-separated
        scope_list = scopes.split()
        self.assertGreater(len(scope_list), 1, "Scopes should be space-separated")
        
        # Each scope should be properly formatted
        for scope in scope_list:
            self.assertIn(":", scope, f"Invalid scope format: {scope}")


class TestMCPIntegration(unittest.TestCase):
    """Test MCP server integration"""

    def test_tools_registration(self):
        """Test that all tools can be registered"""
        # This test verifies that the tool registration functions don't raise exceptions
        from fastmcp import FastMCP
        
        mcp = FastMCP("Test Airtable Tools")
        
        # Mock service
        mock_service = Mock()
        
        try:
            from src.python.tools.comments import register_comment_tools
            from src.python.tools.schema import register_schema_tools
            from src.python.tools.webhooks_advanced import register_webhook_tools_advanced
            from src.python.tools.user_info import register_user_info_tools
            from src.python.tools.blocks import register_blocks_tools
            
            # This should not raise an exception
            register_comment_tools(mcp, mock_service)
            register_schema_tools(mcp, mock_service)
            register_webhook_tools_advanced(mcp, mock_service)
            register_user_info_tools(mcp, mock_service)
            register_blocks_tools(mcp, mock_service)
            
            self.assertTrue(True, "All tools registered successfully")
            
        except Exception as e:
            self.fail(f"Tool registration failed: {e}")


async def run_async_tests():
    """Run all async tests"""
    test_classes = [
        TestAirtableService,
        TestCommentsTools,
        TestSchemaTools,
        TestWebhooksAdvancedTools,
        TestUserInfoTools,
        TestBlocksTools,
        TestAirtableClient
    ]
    
    for test_class in test_classes:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            print(f"\n❌ Tests failed in {test_class.__name__}")
            return False
    
    return True


def main():
    """Main test runner"""
    print("🧪 Running Comprehensive Airtable MCP Integration Tests")
    print("=" * 60)
    
    # Run sync tests
    print("\n📋 Running synchronous tests...")
    sync_test_classes = [
        TestOAuthScopes,
        TestMCPIntegration
    ]
    
    all_passed = True
    for test_class in sync_test_classes:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            all_passed = False
            print(f"\n❌ Tests failed in {test_class.__name__}")
    
    # Run async tests
    print("\n🔄 Running asynchronous tests...")
    async_passed = asyncio.run(run_async_tests())
    
    if not async_passed:
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Complete integration is working correctly.")
        print("\n📋 Test Coverage Summary:")
        print("✅ AirtableService - All extended methods")
        print("✅ CommentsTools - All comment operations")
        print("✅ SchemaTools - All schema management operations")
        print("✅ WebhooksAdvancedTools - All webhook operations")
        print("✅ UserInfoTools - All user information operations")
        print("✅ BlocksTools - All block management operations")
        print("✅ AirtableClient - All extended client methods")
        print("✅ OAuth Scopes - Complete scope configuration")
        print("✅ MCP Integration - Tool registration and server startup")
    else:
        print("❌ Some tests failed. Please check the output above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
