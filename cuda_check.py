import torch

# 1. Basic check
print(f"CUDA available: {torch.cuda.is_available()}")

# 2. Get device count and names
if torch.cuda.is_available():
    device_count = torch.cuda.device_count()
    print(f"Number of GPUs: {device_count}")
    
    for i in range(device_count):
        print(f"Device {i}: {torch.cuda.get_device_name(i)}")
        print(f" - Memory: {torch.cuda.get_device_properties(i).total_memory / 1e9:.2f} GB")