import os
import csv
import tkinter as tk
from tkinter import filedialog

def parse_can_data(file_path):
    # Generate output file path in the same directory as the input file
    output_file = os.path.splitext(file_path)[0] + ".csv"
    
    with open(file_path, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        csv_writer = csv.writer(outfile)
        # Add headers for timestamp, relative time, bus, full ID, priority, PGN, source address, destination address, data length, full data, and data bytes
        csv_writer.writerow(["Timestamp", "Relative_Time", "Bus", "Full_ID", "Priority", "PGN", "Source_Address", "Destination_Address", "Data_Length", "Full_Data"] + [f"Data_{i+1}" for i in range(8)])
        
        first_timestamp = None  # Variable to store the first timestamp
        
        for line in infile:
            # Check for valid CAN data format
            parts = line.strip().split()
            if len(parts) < 3 or '#' not in parts[2]:
                continue

            try:
                # Extract timestamp, bus, CAN ID, and data
                timestamp = float(parts[0][1:-1])  # Strip parentheses and convert to float
                if first_timestamp is None:
                    first_timestamp = timestamp  # Set the first timestamp
                relative_time = timestamp - first_timestamp  # Calculate relative time

                bus = parts[1]
                full_id, data = parts[2].split('#')
                full_id_int = int(full_id, 16)

                # Parse ID components
                priority = (full_id_int >> 26) & 0x07
                pdu_format = (full_id_int >> 16) & 0xFF
                pdu_specific = (full_id_int >> 8) & 0xFF

                # Determine PGN
                if pdu_format >= 0xF0:  # PDU2 format
                    pgn = (pdu_format << 8) | pdu_specific
                    destination_address = "N/A"
                else:  # PDU1 format
                    pgn = (pdu_format << 8)
                    destination_address = pdu_specific

                source_address = full_id_int & 0xFF
                data_length = len(data) // 2
                data_bytes = [data[i:i+2] for i in range(0, len(data), 2)]
                data_bytes = (data_bytes + [""] * 8)[:8]

                # Write to CSV
                csv_writer.writerow([
                    timestamp, relative_time, bus, full_id, priority, f"0x{pgn:04X}", source_address, destination_address, data_length, data
                ] + data_bytes)
            except Exception as e:
                print(f"Error processing line: {line}. Error: {e}")

    print(f"File saved to {output_file}")
    return output_file

def main():
    # Setup Tkinter root
    root = tk.Tk()
    root.withdraw()

    # Open file dialog to select .log or .txt file
    file_path = filedialog.askopenfilename(
        title="Select a CAN Log File",
        filetypes=[("Log and Text Files", "*.log;*.txt"), ("All Files", "*.*")]
    )
    
    if not file_path:
        print("No file selected.")
        return

    # Parse and save CAN data
    csv_path = parse_can_data(file_path)

    # Open the directory containing the CSV in file explorer
    os.startfile(os.path.dirname(csv_path))

if __name__ == "__main__":
    main()
