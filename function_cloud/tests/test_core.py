"""
Tests for the Function Cloud (FC) library core functionality.
"""

import pytest
from unittest.mock import patch, MagicMock

from function_cloud import FC
from function_cloud.config import FCConfig
from function_cloud.dependency_analyzer import DependencyAnalyzer
from function_cloud.deployer import FCDeployer


def test_fc_configure():
    """Test FC.configure method."""
    # Reset config
    FCConfig.token = None
    
    # Configure
    FC.configure(token="test_token", memory=2048, timeout=120)
    
    # Check configuration
    assert FCConfig.token == "test_token"
    assert FCConfig.memory == 2048
    assert FCConfig.timeout == 120


@patch.object(DependencyAnalyzer, 'analyze_imports', return_value=set(['requests']))
@patch.object(DependencyAnalyzer, 'enhance_with_llm', return_value={"packages": ["requests"]})
@patch.object(FCDeployer, 'create_modal_function')
@patch.object(FCDeployer, 'deploy_function', return_value="https://example.com/function")
def test_fc_function_decorator(mock_deploy, mock_create, mock_enhance, mock_analyze):
    """Test FC.function decorator."""
    # Reset config
    FCConfig.token = "test_token"
    
    # Define a function
    @FC.function
    def test_func(x, y):
        return x + y
    
    # Call the function to trigger deployment
    result = test_func(1, 2)
    
    # Check result
    assert result == 3
    
    # Check that the deployment functions were called
    mock_analyze.assert_called_once()
    mock_enhance.assert_called_once()
    mock_create.assert_called_once()
    mock_deploy.assert_called_once()
    
    # Check URL
    assert test_func.get_url() == "https://example.com/function"


@patch.object(DependencyAnalyzer, 'analyze_imports', return_value=set(['requests']))
@patch.object(DependencyAnalyzer, 'enhance_with_llm', return_value={"packages": ["requests"]})
@patch.object(FCDeployer, 'create_modal_function')
@patch.object(FCDeployer, 'deploy_function', return_value="https://example.com/method")
def test_fc_method_decorator(mock_deploy, mock_create, mock_enhance, mock_analyze):
    """Test FC.method decorator."""
    # Reset config
    FCConfig.token = "test_token"
    
    # Define a class with a method
    class TestClass:
        def __init__(self):
            self.value = 0
            
        @FC.method
        def increment(self, amount):
            self.value += amount
            return self.value
    
    # Create an instance
    obj = TestClass()
    
    # Call the method to trigger deployment
    result = obj.increment(5)
    
    # Check result
    assert result == 5
    assert obj.value == 5
    
    # Check that the deployment functions were called
    mock_analyze.assert_called_once()
    mock_enhance.assert_called_once()
    mock_create.assert_called_once()
    mock_deploy.assert_called_once()
    
    # Check URL
    assert obj.increment.get_url() == "https://example.com/method"


@patch.object(DependencyAnalyzer, 'analyze_imports', return_value=set(['requests']))
@patch.object(DependencyAnalyzer, 'enhance_with_llm', return_value={"packages": ["requests"]})
@patch.object(FCDeployer, 'create_modal_function')
@patch.object(FCDeployer, 'deploy_function', return_value="https://example.com/endpoint")
def test_fc_endpoint_decorator(mock_deploy, mock_create, mock_enhance, mock_analyze):
    """Test FC.endpoint decorator."""
    # Reset config
    FCConfig.token = "test_token"
    
    # Define an endpoint
    @FC.endpoint(methods=["GET", "POST"])
    def test_endpoint(name):
        return {"message": f"Hello, {name}!"}
    
    # Call the endpoint to trigger deployment
    result = test_endpoint("World")
    
    # Check result
    assert result == {"message": "Hello, World!"}
    
    # Check that the deployment functions were called
    mock_analyze.assert_called_once()
    mock_enhance.assert_called_once()
    mock_create.assert_called_once()
    mock_deploy.assert_called_once()
    
    # Check URL
    assert test_endpoint.get_url() == "https://example.com/endpoint"
    
    # Check endpoint attributes
    assert hasattr(test_endpoint, "_fc_endpoint")
    assert test_endpoint._fc_endpoint is True
    assert hasattr(test_endpoint, "_fc_endpoint_methods")
    assert test_endpoint._fc_endpoint_methods == ["GET", "POST"]
