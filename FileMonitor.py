import time
import os
import re
import threading

class FileMonitor(threading.Thread):
  def __init__(self, file_path):
    threading.Thread.__init__(self)
    self.file_path = file_path
    self.last_modified = 0
    self.current_pattern = None
    self.output_file = None
    self.lock = threading.Lock()
    self.buffer = []

  def run(self):
    while True:
      with self.lock:
        # Get the last modified time of the file
        current_modified = os.path.getmtime(self.file_path)

        # Check if the file has been modified since the last check
        if current_modified > self.last_modified:
          # Read the file contents
          with open(self.file_path, 'r') as f:
            file_contents = f.read()

          # Find new patterns
          lines = file_contents.splitlines()
          i = 0
          while i < len(lines):
            line = lines[i]
            if line.startswith("BEGIN:"):
              # New pattern found
              new_pattern = line.split(":")[1].strip()
              output_file_name = new_pattern.replace(" ", "_") + ".txt"
              self.output_file = open(output_file_name, 'w')
              print(f"New pattern found: '{new_pattern}', writing to '{output_file_name}'")

              # Write the buffered contents to the new file
              for buffered_line in self.buffer:
                self.output_file.write(buffered_line + "\n")
              self.buffer = []

              # Write the current line to the new file
              self.output_file.write(line + "\n")

              # Keep reading until the next pattern
              i += 1
              while i < len(lines) and not lines[i].startswith("BEGIN"):
                self.output_file.write(lines[i] + "\n")
                i += 1

              # Close the output file
              self.output_file.close()

            else:
              # Buffer the line for the next pattern
              self.buffer.append(line)

            i += 1

          # Update the last modified time
          self.last_modified = current_modified

      # Wait for a short period before checking again
      time.sleep(1)

# Example usage
file_path = "log_runtime.txt"

# Create and start the FileMonitor thread
monitor_thread = FileMonitor(file_path)
monitor_thread.start()

# Keep the main thread running to prevent the program from exiting
while True:
  time.sleep(1)