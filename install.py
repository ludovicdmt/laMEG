"""
This module automates the installation and setup process for MATLAB and SPM (Statistical Parametric Mapping)
on a Linux system. It includes functions to install Python packages, download and install the MATLAB runtime,
install the SPM software, and configure the necessary environment variables for the system.
"""

import glob
import os
import site
import subprocess
import sys
import importlib
import zipfile


def install_package():
    """
    Installs the current directory as a pip package.
    This function assumes the directory contains a setup.py file.
    """
    subprocess.check_call([sys.executable, "-m", "pip", "install", "."])


def install_spm():
    """
    Installs the SPM standalone package from a combined CTF file,
    assumes that the SPM standalone package is present in a subdirectory relative to this script.
    """
    spm_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spm')

    # Change to the directory containing the spm package standalone
    if not os.path.exists(os.path.join(spm_dir, 'spm_standalone', 'spm_standalone.ctf')):
        os.chdir(os.path.join(spm_dir, 'spm_standalone'))
        # Combine file parts into ctf file and remove parts
        subprocess.check_call(['bysp', 'c', 'spm_standalone.ctf'])
        files = glob.glob(os.path.join(spm_dir, 'spm_standalone', 'spm_standalone.ctf.*.part'))
        for file in files:
            os.remove(file)

    # Change to the directory containing the spm package
    os.chdir(spm_dir)
    # Install the spm package
    subprocess.check_call([sys.executable, "setup.py", "install"])
    # Change back to the original directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))


def download_matlab_runtime(url, save_path):
    """
    Downloads the MATLAB runtime from a specified URL to a specified path,
    ensuring the directory structure is created if it does not exist.
    """

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if not os.path.exists(save_path):
        # Download the file using wget
        subprocess.check_call(['wget', '-c', url, '-O', save_path])


def extract_matlab_runtime(zip_path, extract_to):
    """
    Extracts the MATLAB runtime from a zip file to a specified directory,
    sets executable permissions where necessary.
    """

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Create target directory if it doesn't exist
        os.makedirs(extract_to, exist_ok=True)

        # Extract files one at a time
        for file_info in zip_ref.infolist():
            extracted_file_path = os.path.join(extract_to, file_info.filename)

            # Extract the file
            zip_ref.extract(file_info, extract_to)

            # Check if the file needs executable permissions
            if file_info.filename.endswith('.sh') or file_info.filename.endswith(
                    'install') or 'bin' in file_info.filename:
                # Ensure the file is there and set executable permission
                if os.path.isfile(extracted_file_path):
                    os.chmod(extracted_file_path, os.stat(extracted_file_path).st_mode | 0o755)

    return extract_to


def install_matlab_runtime(install_dir):
    """
    Runs the MATLAB runtime installer script in silent mode with predetermined settings,
    ensuring all necessary files are properly installed.
    """

    install_script = os.path.join(install_dir, 'install')
    destination_dir = os.path.join(install_dir, 'MATLAB_Runtime')

    # Ensure the install script has execute permissions
    if not os.path.exists(install_script):
        raise FileNotFoundError(f"The install script was not found in {install_dir}")

    # Run the installation command with the destination folder
    subprocess.check_call(
        [
            install_script,
            '-mode',
            'silent',
            '-agreeToLicense',
            'yes',
            '-destinationFolder',
            destination_dir])
    return destination_dir


def create_activate_script(matlab_runtime_path, conda_env_path):
    """
    Creates a script to set environment variables necessary for MATLAB to function correctly,
    to be activated with the Conda environment.
    """

    activate_script_dir = os.path.join(conda_env_path, "etc", "conda", "activate.d")
    os.makedirs(activate_script_dir, exist_ok=True)
    activate_script_path = os.path.join(activate_script_dir, "env_vars.sh")
    with open(activate_script_path, "w") as f:
        f.write(f'export MATLAB_RUNTIME_DIR="{matlab_runtime_path}"\n')
        f.write(
            'export LD_LIBRARY_PATH="${MATLAB_RUNTIME_DIR}/v96/runtime/glnxa64:'
            '${MATLAB_RUNTIME_DIR}/v96/bin/glnxa64:'
            '${MATLAB_RUNTIME_DIR}/v96/sys/os/glnxa64:'
            '$LD_LIBRARY_PATH"\n'
        )
        f.write('export XAPPLRESDIR="${MATLAB_RUNTIME_DIR}/v96/X11/app-defaults"\n')


def create_deactivate_script(conda_env_path):
    """
    Creates a script to unset environment variables when the Conda environment is deactivated.
    """

    deactivate_script_dir = os.path.join(conda_env_path, "etc", "conda", "deactivate.d")
    os.makedirs(deactivate_script_dir, exist_ok=True)
    deactivate_script_path = os.path.join(deactivate_script_dir, "env_vars.sh")
    with open(deactivate_script_path, "w") as f:
        f.write('unset MATLAB_RUNTIME_DIR\n')
        f.write('unset LD_LIBRARY_PATH\n')
        f.write('unset XAPPLRESDIR\n')


def get_installed_package_dir(package_name):
    """
    Searches for an installed package within site-packages directories and returns its path.
    Raises an exception if the package is not found.
    """

    site_packages = site.getsitepackages()
    for site_package in site_packages:
        potential_path = os.path.join(site_package, package_name)
        if os.path.isdir(potential_path):
            return potential_path
    raise Exception(f"Package {package_name} not found in site-packages directories: {site_packages}")



def main():
    """
    Main function to orchestrate the setup process.
    Handles installation, setup, and cleanup of necessary components.
    """

    # Install the package first
    install_package()

    # Force Python to recognize new packages
    importlib.invalidate_caches()

    # Install standalone SPM
    install_spm()

    # Attempt to locate the installed package directory
    package_dir = get_installed_package_dir('lameg')

    matlab_runtime_zip = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'MATLAB_Runtime_R2019a_Update_9_glnxa64.zip')
    matlab_download_url = (
        'https://ssd.mathworks.com/supportfiles/downloads/R2019a/Release/9/'
        'deployment_files/installer/complete/glnxa64/'
        'MATLAB_Runtime_R2019a_Update_9_glnxa64.zip'
    )

    # Download MATLAB Runtime
    download_matlab_runtime(matlab_download_url, matlab_runtime_zip)
    matlab_runtime_extract_dir = os.path.join(package_dir, 'matlab_runtime')

    conda_env_path = os.path.dirname(os.path.dirname(sys.executable))

    # Extract MATLAB Runtime
    extracted_path = extract_matlab_runtime(matlab_runtime_zip, matlab_runtime_extract_dir)

    # Install MATLAB Runtime
    matlab_runtime_path = install_matlab_runtime(extracted_path)

    # Set environment variables in Conda environment scripts
    create_activate_script(matlab_runtime_path, conda_env_path)
    create_deactivate_script(conda_env_path)

    os.remove(matlab_runtime_zip)


if __name__ == "__main__":
    main()
