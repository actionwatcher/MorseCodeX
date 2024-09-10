
def update_version_win(version_file_path, current_version):
    # Read the content of the version.txt file
    with open(version_file_path, 'r') as version_file:
        version_content = version_file.readlines()

    # Flag to check if a version update happened
    version_updated = False

    # Define the patterns we are looking for
    patterns = [
        "StringStruct('ProductVersion',",
        "StringStruct('Assembly Version',",
        "StringStruct('FileVersion',"
    ]

    # Iterate through each line and check for the specific patterns
    for i, line in enumerate(version_content):
        for pattern in patterns:
            if pattern in line:
                # Find the first occurrence of the version string between single quotes after the pattern
                start_idx = line.find("'", line.find(pattern)+len(pattern))  # Find the first single quote after the pattern
                end_idx = line.find("'", start_idx + 1)  # Find the second single quote after the start quote
                version_string = line[start_idx + 1:end_idx]  # Extract version between quotes
                # Compare the extracted version with the current version
                if version_string != current_version:
                    # Substitute only the version part between the quotes
                    new_line = line[:start_idx + 1] + current_version + line[end_idx:]
                    version_content[i] = new_line
                    version_updated = True
                    print(f"Updated line to: {new_line.strip()}")

    # Write the modified content back to the version.txt file if any update occurred
    if version_updated:
        with open(version_file_path, 'w') as version_file:
            version_file.writelines(version_content)
        print(f"Version updated to {current_version} in {version_file_path}.")
    else:
        print(f"No changes made, version already matches.")
    

def update_version_mac(spec_file_path, current_version):
    # Read the content of the .spec file
    with open(spec_file_path, 'r') as spec_file:
        spec_content = spec_file.readlines()

    # Flag to check if a version update happened
    version_updated = False

    # Iterate through each line and check for 'CFBundleShortVersionString'
    for i, line in enumerate(spec_content):
        if 'CFBundleShortVersionString' in line:
            print(f"Found 'CFBundleShortVersionString' in line: {line.strip()}")

            # Find the part after ':' and extract the version
            if ':' in line:
                # Split by ':' and extract the part after it
                key, version = line.split(':', 1)
                version = version.strip().strip("'\"")  # Clean up any whitespace and quotes

                # Compare with the current version
                if version != current_version:
                    print(f"Version mismatch found: {version} (file) != {current_version} (current)")
                    
                    # Replace the version in the line
                    new_line = f"{key}: '{current_version}'\n"
                    spec_content[i] = new_line
                    version_updated = True
                    print(f"Updated line to: {new_line.strip()}")
                else:
                    print(f"Version matches: {version} == {current_version}")

    # Write the modified content back to the .spec file if any update occurred
    if version_updated:
        with open(spec_file_path, 'w') as spec_file:
            spec_file.writelines(spec_content)
        print(f"Version updated to {current_version} in {spec_file_path}.")
    else:
        print(f"No changes made, version already matches.")


def update_version():
    with open('current_version.ver') as file:
        current_version = file.readline()
    update_version_win( 'version.txt', current_version)
    update_version_mac( 'MorseCodeX_mac.spec', current_version)

if __name__ == '__main__':
    update_version()
