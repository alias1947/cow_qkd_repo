Installation Guide
=================

This guide provides step-by-step instructions for installing and setting up the QKD Simulation Platform on your system.

System Requirements
------------------

Minimum Requirements
~~~~~~~~~~~~~~~~~~~

* **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
* **Python**: 3.8 or higher
* **Node.js**: 14.0 or higher (for frontend)
* **Memory**: 4 GB RAM
* **Storage**: 2 GB free disk space

Recommended Requirements
~~~~~~~~~~~~~~~~~~~~~~~

* **Operating System**: Windows 11, macOS 12+, or Ubuntu 20.04+
* **Python**: 3.9 or higher
* **Node.js**: 16.0 or higher
* **Memory**: 8 GB RAM
* **Storage**: 5 GB free disk space
* **Processor**: Multi-core CPU for faster simulations

Prerequisites
-------------

Python Installation
~~~~~~~~~~~~~~~~~~~

1. **Download Python**: Visit `python.org <https://www.python.org/downloads/>`_ and download the latest Python version
2. **Install Python**: Run the installer and ensure "Add Python to PATH" is checked
3. **Verify Installation**: Open a terminal/command prompt and run:

   .. code-block:: bash

      python --version
      pip --version

Node.js Installation
~~~~~~~~~~~~~~~~~~~~

1. **Download Node.js**: Visit `nodejs.org <https://nodejs.org/>`_ and download the LTS version
2. **Install Node.js**: Run the installer and follow the setup wizard
3. **Verify Installation**: Open a terminal/command prompt and run:

   .. code-block:: bash

      node --version
      npm --version

Git Installation
~~~~~~~~~~~~~~~~

1. **Download Git**: Visit `git-scm.com <https://git-scm.com/>`_ and download Git
2. **Install Git**: Run the installer with default settings
3. **Verify Installation**: Open a terminal/command prompt and run:

   .. code-block:: bash

      git --version

Installation Methods
-------------------

Method 1: Clone from Repository (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Clone the Repository**:

   .. code-block:: bash

      git clone https://github.com/your-username/qkd-simulation-platform.git
      cd qkd-simulation-platform

2. **Install Python Dependencies**:

   .. code-block:: bash

      pip install -r requirements.txt

3. **Install Frontend Dependencies**:

   .. code-block:: bash

      cd frontend
      npm install
      cd ..

Method 2: Download ZIP Archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Download**: Download the ZIP archive from the GitHub releases page
2. **Extract**: Extract the archive to your desired location
3. **Install Dependencies**: Follow steps 2-3 from Method 1

Method 3: Using pip (Backend Only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For users who only need the backend simulation engine:

.. code-block:: bash

   pip install qkd-simulation-platform

Platform-Specific Instructions
-----------------------------

Windows Installation
~~~~~~~~~~~~~~~~~~~~

1. **Install Python**:
   - Download Python from `python.org <https://www.python.org/downloads/>`_
   - Run installer as Administrator
   - Check "Add Python to PATH" and "Install for all users"

2. **Install Node.js**:
   - Download Node.js LTS from `nodejs.org <https://nodejs.org/>`_
   - Run installer with default settings

3. **Install Git**:
   - Download Git from `git-scm.com <https://git-scm.com/>`_
   - Use default settings during installation

4. **Clone and Install**:
   - Open Command Prompt or PowerShell as Administrator
   - Follow Method 1 installation steps

5. **Verify Installation**:
   - Open Command Prompt and run:

   .. code-block:: cmd

      python --version
      node --version
      git --version

macOS Installation
~~~~~~~~~~~~~~~~~~

1. **Install Homebrew** (if not already installed):

   .. code-block:: bash

      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. **Install Python**:

   .. code-block:: bash

      brew install python

3. **Install Node.js**:

   .. code-block:: bash

      brew install node

4. **Install Git**:

   .. code-block:: bash

      brew install git

5. **Clone and Install**:
   - Open Terminal
   - Follow Method 1 installation steps

6. **Verify Installation**:

   .. code-block:: bash

      python3 --version
      node --version
      git --version

Linux Installation (Ubuntu/Debian)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Update System**:

   .. code-block:: bash

      sudo apt update
      sudo apt upgrade

2. **Install Python**:

   .. code-block:: bash

      sudo apt install python3 python3-pip python3-venv

3. **Install Node.js**:

   .. code-block:: bash

      curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
      sudo apt-get install -y nodejs

4. **Install Git**:

   .. code-block:: bash

      sudo apt install git

5. **Clone and Install**:
   - Open Terminal
   - Follow Method 1 installation steps

6. **Verify Installation**:

   .. code-block:: bash

      python3 --version
      node --version
      git --version

Virtual Environment Setup (Recommended)
--------------------------------------

Using a virtual environment is recommended to avoid conflicts with system Python packages:

1. **Create Virtual Environment**:

   .. code-block:: bash

      python -m venv qkd_env

2. **Activate Virtual Environment**:

   **Windows**:
   .. code-block:: cmd

      qkd_env\Scripts\activate

   **macOS/Linux**:
   .. code-block:: bash

      source qkd_env/bin/activate

3. **Install Dependencies**:

   .. code-block:: bash

      pip install -r requirements.txt

4. **Deactivate** (when done):

   .. code-block:: bash

      deactivate

Docker Installation (Alternative)
--------------------------------

For users who prefer containerized deployment:

1. **Install Docker**: Follow instructions at `docker.com <https://docs.docker.com/get-docker/>`_

2. **Build and Run**:

   .. code-block:: bash

      # Build the Docker image
      docker build -t qkd-simulation-platform .

      # Run the container
      docker run -p 8000:8000 -p 3000:3000 qkd-simulation-platform

Verification
-----------

After installation, verify that everything is working correctly:

1. **Test Backend**:

   .. code-block:: bash

      # Start the backend server
      uvicorn api:app --reload

   - Open a web browser and navigate to `http://127.0.0.1:8000`
   - You should see the API welcome message

2. **Test Frontend**:

   .. code-block:: bash

      # In a new terminal, start the frontend
      cd frontend
      npm start

   - Open a web browser and navigate to `http://localhost:3000`
   - You should see the QKD Simulation Platform interface

3. **Run a Test Simulation**:

   - In the frontend, select a protocol (e.g., DPS-QKD)
   - Configure a simple two-node network
   - Run a simulation and verify results are displayed

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

**Python not found**:
   - Ensure Python is added to PATH
   - Try using `python3` instead of `python`

**pip not found**:
   - Install pip: `python -m ensurepip --upgrade`
   - Or use: `python -m pip install -r requirements.txt`

**Node.js/npm not found**:
   - Reinstall Node.js and ensure it's added to PATH
   - Try using `nodejs` instead of `node` on some Linux systems

**Permission Errors**:
   - Use `sudo` on Linux/macOS for system-wide installation
   - Run Command Prompt as Administrator on Windows
   - Use virtual environments to avoid permission issues

**Port Already in Use**:
   - Kill processes using ports 8000 or 3000
   - Use different ports: `uvicorn api:app --reload --port 8001`

**Frontend Build Errors**:
   - Clear npm cache: `npm cache clean --force`
   - Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

**Backend Import Errors**:
   - Ensure you're in the correct directory
   - Check that all dependencies are installed
   - Verify Python path includes the project directory

Getting Help
-----------

If you encounter issues during installation:

1. **Check the FAQ**: Common questions and solutions
2. **Search Issues**: Look for similar problems in the GitHub issues
3. **Create an Issue**: Report bugs or request help on GitHub
4. **Community Support**: Join the discussion forum or mailing list

Next Steps
----------

After successful installation:

1. **Quick Start**: Follow the :doc:`quick-start` tutorial
2. **User Guide**: Learn about all features in the :doc:`user-guide`
3. **Examples**: Explore practical examples in the :doc:`examples` section
4. **API Reference**: Study the complete API documentation 