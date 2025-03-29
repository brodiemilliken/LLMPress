import torch
import sys

def check_gpu():
    """Verify GPU/CUDA availability and print detailed information."""
    print("\n=== GPU AVAILABILITY CHECK ===")
    
    # Basic availability
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    
    if not cuda_available:
        print("\nGPU SUPPORT IS DISABLED!")
        print("Possible reasons:")
        print("1. NVIDIA drivers not installed or outdated")
        print("2. CUDA toolkit not installed or incompatible")
        print("3. PyTorch built without CUDA support")
        print("4. Docker NVIDIA runtime not properly configured")
        print("\nTry running: 'nvidia-smi' on your host to check driver status")
        return False
    
    # Detailed information
    device_count = torch.cuda.device_count()
    print(f"GPU Count: {device_count}")
    
    for i in range(device_count):
        print(f"\nGPU #{i}:")
        print(f"  Name: {torch.cuda.get_device_name(i)}")
        print(f"  Compute Capability: {torch.cuda.get_device_capability(i)}")
        
        # Memory info
        mem_info = torch.cuda.mem_get_info(i)
        free_memory = mem_info[0] / (1024 ** 3)
        total_memory = mem_info[1] / (1024 ** 3)
        print(f"  Memory: {free_memory:.2f}GB free / {total_memory:.2f}GB total")
    
    print("\nGPU SUPPORT IS ENABLED AND WORKING CORRECTLY")
    return True

if __name__ == "__main__":
    success = check_gpu()
    if not success and len(sys.argv) > 1 and sys.argv[1] == "--strict":
        sys.exit(1)  # Exit with error code if strict mode