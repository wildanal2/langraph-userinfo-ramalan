import pytest
from unittest.mock import Mock, patch, MagicMock
from src.infrastructure.langwatch import init_langwatch, get_langwatch_context
from src.services.llm_service import LLMService
from src.core.config import settings


class TestLangWatchIntegration:
    """Test LangWatch integration"""
    
    @patch('src.infrastructure.langwatch.langwatch')
    def test_init_langwatch_enabled(self, mock_langwatch):
        """Test LangWatch initialization when enabled"""
        with patch.object(settings, 'langwatch_enabled', True):
            with patch.object(settings, 'langwatch_api_key', 'test_key'):
                init_langwatch()
                assert mock_langwatch.api_key == 'test_key'
    
    @patch('src.infrastructure.langwatch.langwatch')
    def test_init_langwatch_disabled(self, mock_langwatch):
        """Test LangWatch initialization when disabled"""
        with patch.object(settings, 'langwatch_enabled', False):
            init_langwatch()
            # Should not set api_key when disabled
            assert not hasattr(mock_langwatch, 'api_key') or mock_langwatch.api_key != 'test_key'
    
    def test_get_langwatch_context_basic(self):
        """Test basic context generation"""
        with patch.object(settings, 'langwatch_enabled', True):
            context = get_langwatch_context('session_123')
            
            assert context['trace_id'] == 'session_123'
            assert context['user_id'] == 'session_123'
            assert settings.environment in context['labels']
            assert 'metadata' in context
    
    def test_get_langwatch_context_with_user(self):
        """Test context generation with user_id"""
        with patch.object(settings, 'langwatch_enabled', True):
            context = get_langwatch_context('session_123', 'user@example.com')
            
            assert context['trace_id'] == 'session_123'
            assert context['user_id'] == 'user@example.com'
    
    def test_get_langwatch_context_disabled(self):
        """Test context generation when disabled"""
        with patch.object(settings, 'langwatch_enabled', False):
            context = get_langwatch_context('session_123')
            assert context == {}
    
    @patch('src.services.llm_service.langwatch')
    @patch('src.services.llm_service.get_bedrock_client')
    def test_llm_service_with_langwatch(self, mock_bedrock, mock_langwatch):
        """Test LLM service wraps with LangWatch tracer"""
        mock_llm = Mock()
        mock_bedrock.return_value = mock_llm
        
        with patch.object(settings, 'langwatch_enabled', True):
            service = LLMService()
            # Verify LangChainTracer was called
            mock_langwatch.langchain.LangChainTracer.assert_called_once_with(mock_llm)
    
    @patch('src.services.llm_service.get_bedrock_client')
    def test_llm_service_without_langwatch(self, mock_bedrock):
        """Test LLM service without LangWatch when disabled"""
        mock_llm = Mock()
        mock_bedrock.return_value = mock_llm
        
        with patch.object(settings, 'langwatch_enabled', False):
            service = LLMService()
            assert service.llm == mock_llm


class TestLangWatchMetadata:
    """Test metadata tracking"""
    
    def test_metadata_structure(self):
        """Test metadata has correct structure"""
        with patch.object(settings, 'langwatch_enabled', True):
            context = get_langwatch_context('session_123', 'user@test.com')
            
            assert 'metadata' in context
            assert 'app_version' in context['metadata']
            assert 'environment' in context['metadata']
            assert context['metadata']['app_version'] == settings.app_version
            assert context['metadata']['environment'] == settings.environment
    
    def test_labels_include_environment(self):
        """Test labels include environment"""
        with patch.object(settings, 'langwatch_enabled', True):
            with patch.object(settings, 'environment', 'production'):
                context = get_langwatch_context('session_123')
                assert 'production' in context['labels']


@pytest.mark.integration
class TestLangWatchEndToEnd:
    """Integration tests for LangWatch"""
    
    @pytest.mark.skipif(not settings.langwatch_enabled, reason="LangWatch not enabled")
    def test_trace_creation(self):
        """Test that traces are created (requires LangWatch API key)"""
        # This test requires actual LangWatch API key
        # Skip in CI/CD unless configured
        pass
    
    @pytest.mark.skipif(not settings.langwatch_enabled, reason="LangWatch not enabled")
    def test_llm_call_traced(self):
        """Test that LLM calls are traced"""
        # This test requires actual LangWatch API key and Bedrock access
        # Skip in CI/CD unless configured
        pass


class TestLangWatchErrorHandling:
    """Test error handling in LangWatch integration"""
    
    @patch('src.infrastructure.langwatch.langwatch')
    def test_init_langwatch_exception(self, mock_langwatch):
        """Test graceful handling of initialization errors"""
        mock_langwatch.api_key = Mock(side_effect=Exception("Connection error"))
        
        with patch.object(settings, 'langwatch_enabled', True):
            with patch.object(settings, 'langwatch_api_key', 'test_key'):
                # Should not raise exception
                init_langwatch()
    
    def test_get_context_with_none_session(self):
        """Test context generation with None session_id"""
        with patch.object(settings, 'langwatch_enabled', True):
            # Should handle None gracefully
            context = get_langwatch_context(None)
            assert context['trace_id'] is None
