import sys
# Move to the project directory to access main file
sys.path.append("src/")
print(sys.path)
from src.main import main

main()