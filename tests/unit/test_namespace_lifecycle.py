"""Unit tests for namespace lifecycle management."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from redroom.infrastructure.namespace_lifecycle import NamespaceLifecycle


@pytest.fixture
def mock_k8s_client():
    """Mock Kubernetes client."""
    with patch('redroom.infrastructure.namespace_lifecycle.config') as mock_config, \
         patch('redroom.infrastructure.namespace_lifecycle.client') as mock_client:
        
        # Mock config loading
        mock_config.load_kube_config.return_value = None
        
        # Mock API clients
        mock_v1 = MagicMock()
        mock_apps_v1 = MagicMock()
        mock_networking_v1 = MagicMock()
        
        mock_client.CoreV1Api.return_value = mock_v1
        mock_client.AppsV1Api.return_value = mock_apps_v1
        mock_client.NetworkingV1Api.return_value = mock_networking_v1
        
        yield {
            'v1': mock_v1,
            'apps_v1': mock_apps_v1,
            'networking_v1': mock_networking_v1
        }


def test_namespace_lifecycle_initialization(mock_k8s_client):
    """Test namespace lifecycle manager initializes correctly."""
    manager = NamespaceLifecycle()
    
    assert manager.v1 is not None
    assert manager.apps_v1 is not None
    assert manager.networking_v1 is not None


def test_create_shadow_namespace(mock_k8s_client):
    """Test shadow namespace creation."""
    manager = NamespaceLifecycle()
    
    # Mock successful namespace creation
    mock_k8s_client['v1'].create_namespace.return_value = Mock()
    
    # Mock deployment cloning
    mock_deployment = Mock()
    mock_deployment.metadata.labels = {"app": "test"}
    mock_deployment.spec = Mock()
    mock_k8s_client['apps_v1'].read_namespaced_deployment.return_value = mock_deployment
    mock_k8s_client['apps_v1'].create_namespaced_deployment.return_value = Mock()
    
    # Mock pod readiness
    mock_pod = Mock()
    mock_pod.status.phase = "Running"
    mock_pod.status.container_statuses = [Mock(ready=True)]
    mock_pods = Mock()
    mock_pods.items = [mock_pod]
    mock_k8s_client['v1'].list_namespaced_pod.return_value = mock_pods
    
    namespace = manager.create_shadow_namespace("demo-fintech")
    
    assert namespace.startswith("shadow-")
    assert len(namespace) == 15  # "shadow-" + 8 hex chars


def test_cleanup_namespace(mock_k8s_client):
    """Test namespace cleanup."""
    manager = NamespaceLifecycle()
    
    mock_k8s_client['v1'].delete_namespace.return_value = Mock()
    
    manager.cleanup_namespace("shadow-test123")
    
    mock_k8s_client['v1'].delete_namespace.assert_called_once()


def test_get_namespace_info(mock_k8s_client):
    """Test getting namespace information."""
    manager = NamespaceLifecycle()
    
    # Mock namespace
    mock_ns = Mock()
    mock_ns.metadata.name = "shadow-test123"
    mock_ns.metadata.labels = {"purpose": "exploit-testing"}
    mock_ns.metadata.annotations = {"ttl-seconds": "300"}
    mock_ns.status.phase = "Active"
    mock_k8s_client['v1'].read_namespace.return_value = mock_ns
    
    # Mock pods
    mock_pod = Mock()
    mock_pod.metadata.name = "test-pod"
    mock_pod.status.phase = "Running"
    mock_pod.status.container_statuses = [Mock(ready=True)]
    mock_pods = Mock()
    mock_pods.items = [mock_pod]
    mock_k8s_client['v1'].list_namespaced_pod.return_value = mock_pods
    
    info = manager.get_namespace_info("shadow-test123")
    
    assert info is not None
    assert info['name'] == "shadow-test123"
    assert info['status'] == "Active"
    assert info['pod_count'] == 1
