Contributing to QKD Simulation Platform
======================================

Thank you for your interest in contributing to the QKD Simulation Platform! This guide will help you get started with contributing to the project.

Getting Started
--------------

Before contributing, please:

1. **Read the Documentation**: Familiarize yourself with the project structure and goals
2. **Check Existing Issues**: Look for existing issues or discussions about your contribution
3. **Follow the Code of Conduct**: Ensure your contributions align with our community standards
4. **Set Up Development Environment**: Follow the installation guide for developers

Development Setup
----------------

Prerequisites
~~~~~~~~~~~~

- **Python 3.8+** with pip
- **Node.js 14+** with npm
- **Git** for version control
- **Code editor** (VS Code, PyCharm, etc.)
- **Testing framework** (pytest for Python, Jest for JavaScript)

Fork and Clone
~~~~~~~~~~~~~

1. **Fork the repository** on GitHub
2. **Clone your fork**:

   .. code-block:: bash

      git clone https://github.com/your-username/qkd-simulation-platform.git
      cd qkd-simulation-platform

3. **Add upstream remote**:

   .. code-block:: bash

      git remote add upstream https://github.com/original-owner/qkd-simulation-platform.git

Development Environment
~~~~~~~~~~~~~~~~~~~~~~

1. **Set up Python environment**:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      pip install -r requirements.txt
      pip install -r requirements-dev.txt  # Development dependencies

2. **Set up frontend environment**:

   .. code-block:: bash

      cd frontend
      npm install
      cd ..

3. **Install pre-commit hooks**:

   .. code-block:: bash

      pre-commit install

Project Structure
----------------

Understanding the codebase structure is essential for effective contributions:

.. code-block:: text

   cow_qkd_repo/
   ├── api.py                    # FastAPI application entry point
   ├── main.py                   # Main simulation functions and utilities
   ├── requirements.txt          # Python dependencies
   ├── requirements-dev.txt      # Development dependencies
   ├── simulation/               # Core simulation package
   │   ├── __init__.py
   │   ├── Network.py           # Network management and multi-node simulation
   │   ├── Hardware.py          # Optical component models
   │   ├── Sender.py            # Protocol sender implementations
   │   ├── Receiver.py          # Protocol receiver implementations
   │   └── ...
   ├── frontend/                # React frontend application
   │   ├── package.json
   │   ├── src/
   │   │   ├── components/      # React components
   │   │   │   ├── QKDForm.js
   │   │   │   ├── QKDNetwork.js
   │   │   │   └── Results.js
   │   │   └── ...
   │   └── ...
   ├── docs/                    # Documentation
   │   ├── requirements.txt
   │   └── source/
   │       ├── conf.py
   │       ├── index.rst
   │       └── ...
   ├── tests/                   # Test suite
   │   ├── test_network.py
   │   ├── test_hardware.py
   │   ├── test_protocols.py
   │   └── ...
   └── examples/                # Example scripts and tutorials
       ├── basic_simulation.py
       ├── protocol_comparison.py
       └── ...

Core Components
~~~~~~~~~~~~~~

**Backend (Python)**:
- `simulation/`: Core simulation logic
- `api.py`: REST API endpoints
- `main.py`: Utility functions and analysis tools

**Frontend (React)**:
- `frontend/src/components/`: React components
- `frontend/src/App.js`: Main application
- `frontend/public/`: Static assets

**Documentation**:
- `docs/source/`: Sphinx documentation source
- `docs/requirements.txt`: Documentation dependencies

**Testing**:
- `tests/`: Unit and integration tests
- `requirements-dev.txt`: Development dependencies

Development Workflow
-------------------

Branch Strategy
~~~~~~~~~~~~~~

We use a feature branch workflow:

1. **Main branch**: Stable, production-ready code
2. **Develop branch**: Integration branch for features
3. **Feature branches**: Individual features and fixes
4. **Release branches**: Preparation for releases

Creating a Feature Branch
~~~~~~~~~~~~~~~~~~~~~~~~

1. **Update your local main branch**:

   .. code-block:: bash

      git checkout main
      git pull upstream main

2. **Create a feature branch**:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

3. **Make your changes** and commit them:

   .. code-block:: bash

      git add .
      git commit -m "Add feature: brief description"

4. **Push to your fork**:

   .. code-block:: bash

      git push origin feature/your-feature-name

5. **Create a pull request** on GitHub

Commit Guidelines
~~~~~~~~~~~~~~~~

Follow conventional commit format:

.. code-block:: text

   type(scope): description

   [optional body]

   [optional footer]

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
- `feat(protocols): add new QKD protocol implementation`
- `fix(network): resolve node connection issue`
- `docs(api): update API documentation`
- `test(hardware): add detector model tests`

Code Style
----------

Python Style Guide
~~~~~~~~~~~~~~~~~

Follow PEP 8 with these additions:

**Imports**:
.. code-block:: python

   # Standard library imports
   import math
   import random
   from typing import List, Tuple, Optional

   # Third-party imports
   import numpy as np
   from fastapi import FastAPI

   # Local imports
   from simulation.Network import Network
   from simulation.Hardware import LightSource

**Naming Conventions**:
- **Classes**: PascalCase (e.g., `SinglePhotonDetector`)
- **Functions/Methods**: snake_case (e.g., `generate_photon_count`)
- **Variables**: snake_case (e.g., `avg_photon_number`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_PHOTON_NUMBER`)

**Documentation**:
- Use docstrings for all public functions and classes
- Follow Google docstring format
- Include type hints for function parameters and return values

**Example**:
.. code-block:: python

   def calculate_qber(alice_key: List[int], bob_key: List[int], 
                     dr: float = 0.10, seed: Optional[int] = None) -> Tuple[float, int]:
       """Calculate the Quantum Bit Error Rate (QBER) using a random sample.
       
       Args:
           alice_key: Alice's sifted key bits
           bob_key: Bob's sifted key bits
           dr: Disclose rate for QBER estimation (0-1)
           seed: Random seed for reproducible results
           
       Returns:
           Tuple of (qber, num_errors)
           
       Raises:
           ValueError: If keys have different lengths
       """
       if len(alice_key) != len(bob_key):
           raise ValueError("Sifted keys must be of the same length")
       
       # Implementation...
       return qber, num_errors
```

JavaScript/React Style Guide
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Follow Airbnb JavaScript Style Guide with React-specific additions:

**Component Structure**:
.. code-block:: javascript

   import React, { useState, useEffect } from 'react';
   import PropTypes from 'prop-types';
   import { Box, Button } from '@mui/material';

   const QKDForm = ({ params, onChange }) => {
     const [localParams, setLocalParams] = useState(params);

     const handleChange = (e) => {
       const { name, value, type } = e.target;
       const newValue = type === 'number' ? Number(value) : value;
       const newParams = { ...localParams, [name]: newValue };
       
       setLocalParams(newParams);
       onChange(newParams);
     };

     return (
       <Box component="form" onSubmit={(e) => e.preventDefault()}>
         {/* Component JSX */}
       </Box>
     );
   };

   QKDForm.propTypes = {
     params: PropTypes.object.isRequired,
     onChange: PropTypes.func.isRequired,
   };

   export default QKDForm;
```

**Naming Conventions**:
- **Components**: PascalCase (e.g., `QKDForm`)
- **Functions**: camelCase (e.g., `handleChange`)
- **Variables**: camelCase (e.g., `localParams`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_NODES`)

Testing
-------

Test Structure
~~~~~~~~~~~~~

**Unit Tests**:
- Test individual functions and classes
- Mock external dependencies
- Test edge cases and error conditions
- Aim for high code coverage

**Integration Tests**:
- Test component interactions
- Test API endpoints
- Test end-to-end workflows
- Test realistic scenarios

**Test Organization**:
.. code-block:: text

   tests/
   ├── unit/
   │   ├── test_network.py
   │   ├── test_hardware.py
   │   ├── test_protocols.py
   │   └── ...
   ├── integration/
   │   ├── test_api.py
   │   ├── test_simulation.py
   │   └── ...
   ├── frontend/
   │   ├── QKDForm.test.js
   │   ├── QKDNetwork.test.js
   │   └── ...
   └── conftest.py
```

Running Tests
~~~~~~~~~~~~

**Python Tests**:
.. code-block:: bash

   # Run all tests
   pytest

   # Run specific test file
   pytest tests/test_network.py

   # Run with coverage
   pytest --cov=simulation

   # Run with verbose output
   pytest -v

**Frontend Tests**:
.. code-block:: bash

   cd frontend
   npm test

   # Run with coverage
   npm test -- --coverage

   # Run specific test
   npm test -- QKDForm.test.js
```

Writing Tests
~~~~~~~~~~~~

**Python Test Example**:
.. code-block:: python

   import pytest
   from simulation.Network import Network, Node
   from simulation.Hardware import LightSource

   class TestNetwork:
       def setup_method(self):
           """Set up test fixtures."""
           self.network = Network()
           self.node1 = self.network.add_node('Alice')
           self.node2 = self.network.add_node('Bob')

       def test_add_node(self):
           """Test adding nodes to network."""
           assert len(self.network.nodes) == 2
           assert 'Alice' in self.network.nodes
           assert 'Bob' in self.network.nodes

       def test_connect_nodes(self):
           """Test connecting nodes with channel."""
           self.network.connect_nodes('Alice', 'Bob', distance_km=20)
           assert 'Bob' in self.node1.connected_links
           assert 'Alice' in self.node2.connected_links

       def test_invalid_node_connection(self):
           """Test error handling for invalid connections."""
           with pytest.raises(ValueError):
               self.network.connect_nodes('Alice', 'Charlie', distance_km=20)
```

**JavaScript Test Example**:
.. code-block:: javascript

   import React from 'react';
   import { render, screen, fireEvent } from '@testing-library/react';
   import QKDForm from '../QKDForm';

   describe('QKDForm', () => {
     const mockOnChange = jest.fn();
     const defaultParams = {
       protocol: 'dps',
       cow_monitor_pulse_ratio: 0.1,
     };

     beforeEach(() => {
       mockOnChange.mockClear();
     });

     it('renders protocol selection', () => {
       render(<QKDForm params={defaultParams} onChange={mockOnChange} />);
       
       expect(screen.getByLabelText(/protocol/i)).toBeInTheDocument();
     });

     it('calls onChange when protocol changes', () => {
       render(<QKDForm params={defaultParams} onChange={mockOnChange} />);
       
       const protocolSelect = screen.getByLabelText(/protocol/i);
       fireEvent.change(protocolSelect, { target: { value: 'cow' } });
       
       expect(mockOnChange).toHaveBeenCalledWith({
         ...defaultParams,
         protocol: 'cow',
       });
     });
   });
```

Documentation
-------------

Documentation Standards
~~~~~~~~~~~~~~~~~~~~~~

**Code Documentation**:
- Document all public APIs
- Include usage examples
- Explain complex algorithms
- Provide parameter descriptions

**User Documentation**:
- Write clear, concise instructions
- Include screenshots and diagrams
- Provide troubleshooting guides
- Keep documentation up-to-date

**API Documentation**:
- Document all endpoints
- Include request/response examples
- Explain error codes
- Provide authentication details

Writing Documentation
~~~~~~~~~~~~~~~~~~~~

**Sphinx Documentation**:
.. code-block:: rst

   .. function:: calculate_qber(alice_key, bob_key, dr=0.10, seed=None)

      Calculate the Quantum Bit Error Rate (QBER) using a random sample.

      :param list alice_key: Alice's sifted key bits
      :param list bob_key: Bob's sifted key bits
      :param float dr: Disclose rate for QBER estimation (0-1)
      :param int seed: Random seed for reproducible results
      :return: Tuple of (qber, num_errors)
      :rtype: tuple
      :raises ValueError: If keys have different lengths

      **Example**:

      .. code-block:: python

         alice_key = [0, 1, 0, 1, 0]
         bob_key = [0, 1, 0, 0, 0]
         qber, errors = calculate_qber(alice_key, bob_key)
         print(f"QBER: {qber:.3f}, Errors: {errors}")
```

**README Updates**:
- Update README.md for significant changes
- Include installation instructions
- Provide usage examples
- List dependencies and requirements

Pull Request Process
-------------------

Creating a Pull Request
~~~~~~~~~~~~~~~~~~~~~~

1. **Ensure your code is ready**:
   - All tests pass
   - Code follows style guidelines
   - Documentation is updated
   - No sensitive information is included

2. **Create the pull request**:
   - Use a descriptive title
   - Fill out the PR template
   - Link related issues
   - Add appropriate labels

3. **PR Template**:
   .. code-block:: markdown

      ## Description
      Brief description of the changes

      ## Type of Change
      - [ ] Bug fix
      - [ ] New feature
      - [ ] Documentation update
      - [ ] Performance improvement
      - [ ] Refactoring

      ## Testing
      - [ ] Unit tests pass
      - [ ] Integration tests pass
      - [ ] Manual testing completed

      ## Checklist
      - [ ] Code follows style guidelines
      - [ ] Documentation is updated
      - [ ] Tests are added/updated
      - [ ] No breaking changes

4. **Respond to feedback**:
   - Address review comments
   - Make requested changes
   - Update PR as needed
   - Be responsive to maintainers

Review Process
~~~~~~~~~~~~~

**Code Review Checklist**:
- [ ] Code follows style guidelines
- [ ] Tests are comprehensive
- [ ] Documentation is updated
- [ ] No security issues
- [ ] Performance is acceptable
- [ ] Error handling is appropriate
- [ ] No breaking changes (unless intended)

**Review Guidelines**:
- Be constructive and respectful
- Focus on code quality and correctness
- Suggest improvements when possible
- Approve when criteria are met

Areas for Contribution
----------------------

New Features
~~~~~~~~~~~

**Protocol Implementations**:
- Implement new QKD protocols
- Add protocol-specific parameters
- Create protocol comparison tools
- Develop protocol optimization algorithms

**Hardware Models**:
- Add new optical component models
- Improve existing component accuracy
- Add realistic noise models
- Implement hardware calibration tools

**Network Features**:
- Add new network topologies
- Implement routing algorithms
- Add network optimization tools
- Create network visualization features

**Analysis Tools**:
- Add statistical analysis tools
- Implement performance optimization
- Create security analysis tools
- Add data export/import features

Bug Fixes
~~~~~~~~~

**Common Issues**:
- Simulation accuracy problems
- Performance bottlenecks
- User interface bugs
- Documentation errors
- Test failures

**Reporting Bugs**:
- Use the issue template
- Provide detailed reproduction steps
- Include error messages and logs
- Describe expected vs. actual behavior

Documentation
~~~~~~~~~~~~

**User Documentation**:
- Improve user guides
- Add tutorials and examples
- Create troubleshooting guides
- Update API documentation

**Developer Documentation**:
- Improve code documentation
- Add architecture diagrams
- Create development guides
- Update contribution guidelines

**Research Documentation**:
- Document protocol implementations
- Add mathematical derivations
- Create validation studies
- Document performance analysis

Testing
~~~~~~~

**Test Coverage**:
- Add missing unit tests
- Improve integration tests
- Add performance tests
- Create automated testing

**Test Infrastructure**:
- Improve test frameworks
- Add continuous integration
- Create test data generators
- Implement test reporting

Community Guidelines
-------------------

Code of Conduct
~~~~~~~~~~~~~~~

**Our Standards**:
- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative and constructive
- Focus on what is best for the community

**Unacceptable Behavior**:
- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Other conduct inappropriate for a professional environment

Communication
~~~~~~~~~~~~~

**GitHub Issues**:
- Use issue templates
- Be clear and specific
- Provide context and examples
- Respond to maintainer questions

**Discussion Forum**:
- Be respectful and constructive
- Help other community members
- Share knowledge and experiences
- Follow forum guidelines

**Pull Requests**:
- Be responsive to feedback
- Explain your changes clearly
- Help with testing and review
- Follow contribution guidelines

Getting Help
-----------

**For Contributors**:
- Read the documentation thoroughly
- Check existing issues and discussions
- Ask questions in the discussion forum
- Contact maintainers for guidance

**For Maintainers**:
- Be responsive to community questions
- Provide clear feedback on contributions
- Help new contributors get started
- Maintain project quality and standards

**Resources**:
- Project documentation
- GitHub discussions
- Issue tracker
- Mailing list (if available)

Recognition
----------

**Contributor Recognition**:
- Contributors are listed in CONTRIBUTORS.md
- Significant contributions are acknowledged in releases
- Contributors may be invited to join the maintainer team
- Community recognition for valuable contributions

**Types of Contributions**:
- Code contributions
- Documentation improvements
- Bug reports and fixes
- Feature suggestions
- Community support
- Testing and validation

Thank you for contributing to the QKD Simulation Platform! Your contributions help make this project better for everyone in the quantum communication community. 