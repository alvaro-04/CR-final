import json
import csv
import sys
import os

def json_to_csv(json_file_path, csv_file_path=None):
    """
    Convert a JSON file to a CSV file with a 'conversations' column
    
    Args:
        json_file_path (str): Path to the input JSON file
        csv_file_path (str, optional): Path to the output CSV file. 
                                      If None, uses same name as JSON with .csv extension
    """
    # Set default CSV file path if not provided
    if csv_file_path is None:
        csv_file_path = os.path.splitext(json_file_path)[0] + '.csv'
    
    try:
        # Load JSON data
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        
        print(f"Loaded JSON data from: {json_file_path}")
        print(f"Data type: {type(data)}")
        
        # Handle different JSON structures
        conversations_list = []
        
        if isinstance(data, list):
            # If JSON is a list directly
            conversations_list = data
            print(f"Found {len(conversations_list)} conversations in list format")
            
        elif isinstance(data, dict):
            # If JSON is a dictionary with conversations in a specific key
            possible_keys = ['conversations', 'data', 'messages', 'chats', 'dialogs']
            
            for key in possible_keys:
                if key in data:
                    if isinstance(data[key], list):
                        conversations_list = data[key]
                        print(f"Found {len(conversations_list)} conversations in key: '{key}'")
                        break
            
            # If no recognized key found, try to use the entire dict
            if not conversations_list:
                print("No recognized conversation key found. Creating single conversation from entire dictionary.")
                conversations_list = [data]
        
        else:
            raise ValueError(f"Unsupported JSON structure. Expected list or dict, got {type(data)}")
        
        # Write to CSV
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            
            # Write header
            writer.writerow(['conversations'])
            
            # Write each conversation
            for conv in conversations_list:
                # Convert conversation to string
                if isinstance(conv, (dict, list)):
                    # Pretty print for readability
                    conv_str = json.dumps(conv, ensure_ascii=False, indent=None)
                else:
                    conv_str = str(conv)
                
                writer.writerow([conv_str])
        
        print(f"Successfully converted to CSV: {csv_file_path}")
        print(f"Total conversations written: {len(conversations_list)}")
        
        # Show sample of first conversation
        if conversations_list:
            print("\nFirst conversation sample:")
            sample = json.dumps(conversations_list[0] if isinstance(conversations_list[0], (dict, list)) else conversations_list[0], 
                              ensure_ascii=False, indent=2)
            print(sample[:500] + "..." if len(sample) > 500 else sample)
        
        return csv_file_path
        
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {json_file_path}")
        print(f"Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    """
    Main function to handle command line arguments
    """
    # Check if JSON file path is provided
    if len(sys.argv) < 2:
        print("Usage: python json_to_csv.py <json_file_path> [csv_file_path]")
        print("Example: python json_to_csv.py ./dataset.json ./output.csv")
        print("Example: python json_to_csv.py ./dataset.json")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    
    # Get optional CSV file path
    csv_file_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Convert JSON to CSV
    json_to_csv(json_file_path, csv_file_path)

if __name__ == "__main__":
    main()