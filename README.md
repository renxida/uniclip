# Uniclip

Uniclip is a clipboard synchronization tool that allows you to share clipboard content across multiple devices within a group. It provides an easy way to keep your clipboard in sync across different machines, making it perfect for users who frequently work with multiple computers or collaborate in teams.

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
   git clone https://github.com/yourusername/uniclip.git
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape Uniclip
- Inspired by the need for seamless clipboard sharing in multi-device environments

## Support

If you encounter any problems or have any questions, please [open an issue](https://github.com/yourusername/uniclip/issues) on GitHub.