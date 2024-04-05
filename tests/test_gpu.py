import pytest
from pydantic import ValidationError

from rapidswarm.models.gpu import GPU


def test_gpu_creation():
    gpu = GPU(
        id="gpu-1",
        model="NVIDIA GeForce RTX 3090",
        memory_size=24576,
    )
    assert gpu.id == "gpu-1"
    assert gpu.model == "NVIDIA GeForce RTX 3090"
    assert gpu.memory_size == 24576


def test_gpu_missing_id():
    with pytest.raises(ValidationError) as exc_info:
        GPU(model="NVIDIA GeForce RTX 3090", memory_size=24576)
    assert "id" in str(exc_info.value)


def test_gpu_missing_model():
    with pytest.raises(ValidationError) as exc_info:
        GPU(id="gpu-1", memory_size=24576)
    assert "model" in str(exc_info.value)


def test_gpu_missing_memory_size():
    gpu = GPU(id="gpu-1", model="NVIDIA GeForce RTX 3090")
    assert gpu.id == "gpu-1"
    assert gpu.model == "NVIDIA GeForce RTX 3090"
    assert gpu.memory_size is None  # Ensure memory_size is None when not provided


def test_gpu_invalid_memory_size():
    with pytest.raises(ValueError) as exc_info:
        GPU(id="gpu-1", model="NVIDIA GeForce RTX 3090", memory_size=-1)
    assert "memory_size must be a positive integer" in str(exc_info.value)


def test_gpu_string_representation():
    gpu = GPU(
        id="gpu-1",
        model="NVIDIA GeForce RTX 3090",
        memory_size=24576,
    )
    assert str(gpu) == "id='gpu-1' model='NVIDIA GeForce RTX 3090' memory_size=24576"
