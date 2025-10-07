from pymongo import MongoClient
from meds import extract_medicines_from_image
from datetime import datetime
import ast


client = MongoClient("mongodb://localhost:27017/")

# selecting the ocr database
db = client["admin"]

users_collection = db["meds"]

def get_available_users():
    try:
        users = users_collection.distinct("Name")
        return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

def select_user():
    users = get_available_users()
    
    if not users:
        print("No users found in database. Let's create a new user.")
        user_name = input("Enter user name: ").strip()
        user_age = input("Enter user age: ").strip()
        user_city = input("Enter user city: ").strip()
        
        # Create new user entry
        new_user = {
            'Name': user_name,
            'Age': int(user_age) if user_age.isdigit() else user_age,
            'City': user_city,
            'medicines': [],
            'created_at': datetime.now()
        }
        
        try:
            users_collection.insert_one(new_user)
            print(f"New user '{user_name}' created successfully!")
            return user_name
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    print("\nAvailable users:")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user}")
    
    print(f"{len(users) + 1}. Create new user")
    
    while True:
        try:
            choice = input(f"\nSelect user (1-{len(users) + 1}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(users):
                selected_user = users[choice_num - 1]
                print(f"Selected user: {selected_user}")
                return selected_user
            elif choice_num == len(users) + 1:
                # Create new user
                user_name = input("Enter user name: ").strip()
                user_age = input("Enter user age: ").strip()
                user_city = input("Enter user city: ").strip()
                
                new_user = {
                    'Name': user_name,
                    'Age': int(user_age) if user_age.isdigit() else user_age,
                    'City': user_city,
                    'medicines': [],
                    'created_at': datetime.now()
                }
                
                try:
                    users_collection.insert_one(new_user)
                    print(f"New user '{user_name}' created successfully!")
                    return user_name
                except Exception as e:
                    print(f"Error creating user: {e}")
                    return None
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def save_medicines_to_user(user_name, medicines_text, image_path):
    """Save extracted medicines to the selected user's record"""
    try:
        # Try to parse the medicines text as a Python list
        try:
            medicines_list = ast.literal_eval(medicines_text)
            if not isinstance(medicines_list, list):
                medicines_list = [medicines_text]
        except (ValueError, SyntaxError):
            # If parsing fails, treat as a single medicine or split by lines
            medicines_list = [medicines_text.strip()]
        
        # Create medicine entry with timestamp and source
        medicine_entry = {
            'medicines': medicines_list,
            'extracted_from': image_path,
            'added_at': datetime.now(),
            'raw_extraction': medicines_text
        }
        
        # Update user's record to add medicines
        result = users_collection.update_one(
            {'Name': user_name},
            {'$push': {'medicines': medicine_entry}}
        )
        
        if result.modified_count > 0:
            print(f"Successfully saved medicines to user '{user_name}':")
            for med in medicines_list:
                print(f"  - {med}")
            return True
        else:
            print(f"Failed to save medicines. User '{user_name}' might not exist.")
            return False
            
    except Exception as e:
        print(f"Error saving medicines: {e}")
        return False

# main function that extracts the meds and saves to db
def process_medicine_extraction(image_path):
    print(f"Extracting medicines from image: {image_path}")
    
    # Extract medicines from image
    medicines = extract_medicines_from_image(image_path)
    
    if not medicines:
        print("No medicines found in the image.")
        return
    
    print(f"\nExtracted medicines: {medicines}")
    
    # Ask user to confirm the extraction
    confirm = input("\nDo you want to save these medicines? (y/n): ").strip().lower()
    if confirm != 'y' and confirm != 'yes':
        print("Medicine extraction cancelled.")
        return
    
    # Select user to save medicines against
    selected_user = select_user()
    
    if selected_user:
        # Save medicines to the selected user
        success = save_medicines_to_user(selected_user, medicines, image_path)
        if success:
            print(f"\nMedicines successfully saved for user: {selected_user}")
        else:
            print("Failed to save medicines to database.")
    else:
        print("No user selected. Medicines not saved.")

# Example usage
if __name__ == "__main__":
    # You can call this function with an image path
    print("Starting medicine extraction process...")
    process_medicine_extraction("test-docs/test3.png")
    print("Medicine extraction process completed.")