
import os

# Create directory structure
directories = [
    "elderly-voice-agent/frontend",
    "elderly-voice-agent/backend"
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    
print("Directory structure created successfully!")
