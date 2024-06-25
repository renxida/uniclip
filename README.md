# Uniclip

Uniclip is a clipboard synchronization tool that allows you to share clipboard content across multiple devices within a group. It provides an easy way to keep your clipboard in sync across different machines, making it perfect for users who frequently work with multiple computers or collaborate in teams.

Current version: 0.1.1

## Features

- Cross-device clipboard synchronization
- Group-based sharing for team collaboration
- Support for both headless and GUI environments
- Easy to install and use
- Secure communication between clients and server

## Installation

You can install Uniclip using pip:

```bash
pip install uniclip
```

## Usage

### Client Mode

To run Uniclip in client mode:

```bash
uniclip client --group <your_group_id> --server <server_address>
```

Optional arguments:
- `--headless`: Force headless mode for the client

Example:
```bash
uniclip client --group myteam --server http://uniclip-server.example.com:2547
```

### Server Mode

To run Uniclip in server mode:

```bash
uniclip server
```

### Install as a Service

To install Uniclip as a systemd service:

For client:
```bash
uniclip install
```

For server (requires root privileges):
```bash
sudo uniclip server install
```

## Configuration

Uniclip uses a configuration file located at `~/.config/uniclip/config.yaml`. You can set default values for the group ID, server address, and headless mode in this file.

Example configuration:

```yaml
group_id: myteam
server_address: http://uniclip-server.example.com:2547
headless: false
```

## Development

To set up the development environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/renxida/uniclip.git
   cd uniclip
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

4. Run tests (assuming you have a `tests` directory with test files):
   ```bash
   python -m unittest discover tests
   ```

## Continuous Integration and Deployment

This project uses GitHub Actions for continuous integration and deployment. We follow semantic versioning (SemVer) for version numbers.

### Creating a New Release

To create a new release:

1. Go to the "Actions" tab in your GitHub repository.
2. Select the "Release" workflow.
3. Click "Run workflow".
4. Choose the type of release:
   - `patch`: for backwards-compatible bug fixes
   - `minor`: for new backwards-compatible features
   - `major`: for changes that break backward compatibility
5. Click "Run workflow".

This will automatically:
- Determine the next version number based on the current version and the type of release
- Update the version number in `uniclip/__init__.py`
- Create a new commit with the version change
- Push the commit to the repository
- Create a new tag with the version number
- Create a new GitHub release
- Update the version number in this README

The publish workflow will then automatically trigger, building and publishing the new version to PyPI.

Note: Only maintainers with the necessary permissions can trigger this workflow and publish releases.

### Automatic Publishing

When a new release is created (either manually or through the Release workflow), the Publish workflow automatically builds the package and publishes it to PyPI using the Trusted Publisher mechanism.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape Uniclip
- Inspired by the need for seamless clipboard sharing in multi-device environments

## Support

If you encounter any problems or have any questions, please [open an issue](https://github.com/renxida/uniclip/issues) on GitHub.