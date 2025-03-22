#!/usr/bin/env python
"""
Setup script for LLMPress that handles dependencies intelligently
to avoid Rust compilation issues with tokenizers.
"""

import os
import sys
import subprocess
import argparse
import platform
import shutil

def run_command(cmd, description=None, exit_on_error=True):
    """Run a shell command and handle errors"""
    if description:
        print(f"\n{description}...")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        if exit_on_error:
            print("Exiting due to error.")
            sys.exit(1)
        return False
    print(result.stdout)
    return True

def install_prebuilt_tokenizers(python_executable="python"):
    """Install tokenizers from a pre-built wheel to avoid Rust compilation"""
    os_name = platform.system().lower()
    arch = platform.machine().lower()
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    
    # First try using PyTorch's index which has compatible wheels
    pytorch_command = f"{python_executable} -m pip install tokenizers==0.13.3 --extra-index-url https://download.pytorch.org/whl/cu118"
    success = run_command(pytorch_command, "Installing tokenizers from PyTorch's index", exit_on_error=False)
    if success:
        return True
    
    # Map OS and architecture to wheel names for direct installation
    if os_name == "windows":
        if arch == "amd64" or arch == "x86_64":
            arch_tag = "win_amd64"
        else:
            arch_tag = "win32"
    elif os_name == "darwin":  # macOS
        if arch == "arm64":
            arch_tag = "macosx_11_0_arm64"
        else:
            arch_tag = "macosx_10_9_x86_64"
    else:  # Linux and others
        if arch == "x86_64":
            arch_tag = "manylinux2014_x86_64"
        elif arch == "aarch64":
            arch_tag = "manylinux2014_aarch64"
        else:
            print(f"Unsupported architecture: {arch}. Will try pip's default wheel selection.")
            arch_tag = None

    # Try to find and install a pre-built wheel directly
    if arch_tag:
        wheel_name = f"tokenizers-0.13.3-cp{py_version}-cp{py_version}-{arch_tag}.whl"
        direct_url = f"https://files.pythonhosted.org/packages/76/01/6f4a6b52ef244daeaf18ac8608c62ddea187ddff9ce0449223fb7a855447/{wheel_name}"
        command = f"{python_executable} -m pip install {direct_url}"
        success = run_command(command, f"Installing tokenizers wheel directly for {os_name}/{arch}", exit_on_error=False)
        if success:
            return True

    # Try installing with no-build-isolation (may avoid some Rust issues)
    print("Direct wheel not found. Trying with --no-build-isolation...")
    command = f"{python_executable} -m pip install tokenizers==0.13.3 --no-build-isolation"
    success = run_command(command, "Installing tokenizers with --no-build-isolation", exit_on_error=False)
    if success:
        return True
    
    # Final fallback - install dependencies via requirements.txt
    print("Attempting to install via requirements.txt...")
    command = f"{python_executable} -m pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu118"
    return run_command(command, "Installing dependencies from requirements.txt", exit_on_error=False)

def check_rust_installed():
    """Check if Rust is installed and working"""
    rustc_check = subprocess.run("rustc --version", shell=True, capture_output=True, text=True)
    cargo_check = subprocess.run("cargo --version", shell=True, capture_output=True, text=True)
    
    if rustc_check.returncode == 0 and cargo_check.returncode == 0:
        print(f"Rust is installed: {rustc_check.stdout.strip()}")
        return True
    return False

def verify_models_dir():
    """Ensure the models directory exists for fallback tokenizers"""
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "gpt2_minimal_tokenizer")
    os.makedirs(models_dir, exist_ok=True)
    return models_dir

def setup_environment(args):
    """Set up the entire environment for LLMPress"""
    python_executable = args.python_executable
    
    # Create virtual environment if specified
    if args.create_venv:
        venv_path = args.venv_path or "llmpress_env"
        run_command(f"{python_executable} -m venv {venv_path}", f"Creating virtual environment at {venv_path}")
        
        # Update python_executable to use the venv
        if platform.system().lower() == "windows":
            python_executable = f"{venv_path}\\Scripts\\python"
        else:
            python_executable = f"{venv_path}/bin/python"
    
    # Upgrade pip first
    run_command(f"{python_executable} -m pip install --upgrade pip", "Upgrading pip", exit_on_error=False)
    
    # Check if Rust is available
    if not check_rust_installed() and args.try_install_rust:
        print("Rust is not installed. Attempting to install it...")
        if platform.system().lower() == "windows":
            # Download and run rustup-init.exe on Windows
            run_command("curl -sSf -o rustup-init.exe https://win.rustup.rs && rustup-init.exe -y", 
                       "Installing Rust", exit_on_error=False)
        else:
            # Use rustup-init script on Unix-based systems
            run_command("curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y", 
                       "Installing Rust", exit_on_error=False)
    
    # Ensure models directory exists
    models_dir = verify_models_dir()
    
    # Install tokenizers first (special handling)
    install_success = install_prebuilt_tokenizers(python_executable)
    if not install_success:
        print("Warning: Could not install tokenizers. Will use fallback minimal tokenizer.")
    
    # Install remaining dependencies
    if not args.skip_dependencies:
        core_deps = [
            "torch",
            "transformers",
            "numpy",
            "tqdm"
        ]
        deps_str = " ".join(core_deps)
        run_command(f"{python_executable} -m pip install {deps_str}", "Installing core dependencies")
    
    print("\n✓ Environment setup complete! You can now use LLMPress.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set up environment for LLMPress")
    parser.add_argument("--create-venv", action="store_true", help="Create a new virtual environment")
    parser.add_argument("--venv-path", help="Path for the new virtual environment (default: llmpress_env)")
    parser.add_argument("--python-executable", default="python", help="Python executable to use")
    parser.add_argument("--try-install-rust", action="store_true", help="Try to install Rust if not available")
    parser.add_argument("--skip-dependencies", action="store_true", help="Skip installing dependencies if only fixing tokenizers")
    args = parser.parse_args()
    
    setup_environment(args)
