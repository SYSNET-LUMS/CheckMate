# Let's load the newly uploaded image (PGM file) and convert its content into a C-style header file

# Load the PGM file
pgm_image_path_uploaded = '/mnt/data/img.pgm'

# Read the PGM file content
with open(pgm_image_path_uploaded, 'rb') as pgm_file:
    pgm_data = pgm_file.read()

# Convert the binary content of the PGM file into hex format for a C-style array
pgm_data_hex = ', '.join([f"0x{byte:02x}" for byte in pgm_data])

# Create the C-style header content
header_content = f"unsigned char pgm_image_data[] = {{\n  {pgm_data_hex}\n}};"

# Save the new header file
output_header_path = '/mnt/data/pgm_image_header.h'

with open(output_header_path, 'w') as header_file:
    header_file.write(header_content)

# Provide the generated header file for download
output_header_path