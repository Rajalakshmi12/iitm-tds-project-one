import sqlite3
import os

def get_full_path(file_path: str):
    
    print(file_path)
    project_root = os.getcwd()  # Project root folder

    if os.path.isabs(file_path):
        # If it's an absolute path, make sure it's within the project root directory
        return os.path.join(project_root, file_path.lstrip('/'))  # lstrip removes the leading "/"
    else:
        return os.path.join(project_root, file_path)
    
def calculate_gold_ticket_sales():
    # Config directory for storing files
    path = "/data/ticket-sales.db"
    output_path = "/data/ticket-sales-gold.txt"
    DB_PATH = get_full_path(path)
    OUTPUT_FILE = get_full_path(output_path)

    try:
        # Connect to SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Query to calculate total sales for 'Gold' ticket type
        cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
        total_sales = cursor.fetchone()[0] or 0  # Default to 0 if no sales

        # Write the total sales to the output file
        with open(OUTPUT_FILE, "w") as file:
            file.write(str(total_sales))

        print(f"Total sales for 'Gold' tickets: {total_sales}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        conn.close()

# Call the function
calculate_gold_ticket_sales()
