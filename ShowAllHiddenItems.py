import os
import re
directories = ['C:\\Program Files (x86)\\Steam\\steamapps\\common\\Halo Infinite\\package\\pc\\en-US', 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Halo Infinite\\package\\pc\\common']

# Provided by codeape on stack overflow: https://stackoverflow.com/questions/1035340/reading-binary-file-and-looping-over-each-byte
def bytes_from_file(filename, chunksize=8192):
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                for b in chunk:
                    yield b
            else:
                break

for directory in directories:
    for filename in os.listdir(directory):
        if filename == 'gamecms.cms':
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                print ('Scanning for flags in ' + filepath)
                file_bytes = list(bytes_from_file(filepath))
                quote_byte_found = False
                
                num_patterns_found = 0
                skip_to_index = -1
                
                for index, byte in enumerate(file_bytes):
                    if index < skip_to_index:
                        quote_byte_found = False
                        continue
                    elif quote_byte_found and byte == 1 and file_bytes[index + 1] == 0x52: # The character immediately following the 0x01 should be an "R" (0x52).
                        # If we found the quote byte in our previous run and \x01 in this run.
                        file_bytes[index] = 0
                        num_patterns_found += 1
                        #print('Found desired pattern in ' + filepath + ' at index ' + str(index))
                        
                    elif byte == 34: # If the byte we found is a double-quote.
                        #print('found quote byte at ' + str(index))
                        quote_byte_found = True
                        
                    elif byte == 0x89 and file_bytes[index + 1] == 0x50 and file_bytes[index + 2] == 0x4E and file_bytes[index + 3] == 0x47:
                        quote_byte_found = False
                        # We've found a PNG. Skip to the end so we don't accidentally corrupt it.
                        iteration_index = index
                        while iteration_index < len(file_bytes) - 8:
                            # If we reach the end of the PNG, we set our skip point to it.
                            if file_bytes[iteration_index] == 0x49 and file_bytes[iteration_index + 1] == 0x45 and file_bytes[iteration_index + 2] == 0x4E and file_bytes[iteration_index + 3] == 0x44 \
                            and file_bytes[iteration_index + 4] == 0xAE and file_bytes[iteration_index + 5] == 0x42 and file_bytes[iteration_index + 6] == 0x60 and file_bytes[iteration_index + 7] == 0x82:
                                skip_to_index = iteration_index + 8
                                break
                            iteration_index += 1

                    else: # If we didn't find the correct byte sequence, reset our flag.
                        quote_byte_found = False 

                if num_patterns_found >= 1:
                    print ('Found ' + str(num_patterns_found) + ' flags to edit in ' + filepath + ', Updating...')
                    with open(filepath, 'wb') as file:
                        file.write(bytes(file_bytes))
                    print ('File updated')
