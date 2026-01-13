# CAN Bus-Off Attack Tool

A security testing tool that tests CAN node resilience by flooding the bus with high-frequency frames to attempt to trigger bus-off state.

## Overview

This tool sends CAN frames at maximum rate to a target CAN ID to test if the target node enters bus-off state. When a CAN node accumulates too many transmission errors, it enters bus-off state as a protective measure and stops transmitting.

### Purpose

- Test ECU resilience to high-frequency bus traffic
- Evaluate CAN controller error handling capabilities
- Assess bus-off protection mechanisms
- Security research and testing

## Requirements

### Hardware
- CAN-FD compatible interface (SocketCAN on Linux)
- Access to CAN bus

### Software
- **Python 3.9+**
- Linux system with SocketCAN support
- CAN interface configured

### Python Dependencies

```bash
pip install -r requirements.txt
```

Required package:
- `python-can` - CAN bus access library

## Installation

1. Clone or download this repository:
```bash
git clone <your-repo-url>
cd can-bus-off-attack
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure CAN interface:
```bash
sudo ip link set can0 type can bitrate 500000 dbitrate 2000000 fd on
sudo ip link set up can0
```

## Usage

### Basic Usage

```bash
python3 bus_off_attack.py
```

### Options

```bash
python3 bus_off_attack.py --channel can0 --target 0x123 --duration 10
```

Arguments:
- `--channel`: CAN interface name (default: `can0`)
- `--target`: Target CAN ID in hex (default: `0x123`)
- `--duration`: Attack duration in seconds (default: `10`)
- `-h, --help`: Show help message

### Examples

```bash
# Default settings (10 seconds, target 0x18E06289)
python3 bus_off_attack.py

# Custom target ID and duration
python3 bus_off_attack.py --target 0x123 --duration 30

# Different CAN interface
python3 bus_off_attack.py --channel can1 --target 0x456
```

## Output

The script provides real-time output showing:
- Configuration parameters
- Frame transmission statistics (every 10000 frames)
- Final summary with total frames sent and transmission rate

Example output:
```
============================================================
CAN Bus-Off Attack Test
============================================================
Channel: can0
Target ID: 0x123
Duration: 10 seconds
============================================================

Sending frames as fast as possible...
Press Ctrl+C to stop

Sent 10000 frames (23806 frames/sec)
Sent 20000 frames (23645 frames/sec)
...
============================================================
Total frames sent: 235439
Duration: 10.00 seconds
Average rate: 23547 frames/second
============================================================
```

## How Bus-Off Works

CAN nodes maintain error counters (transmit error counter, receive error counter). When a node's transmit error counter reaches 255, it enters bus-off state and stops transmitting. This is a protective mechanism to prevent a faulty node from disrupting the entire bus.

A bus-off attack attempts to cause errors by:
- Flooding the bus with high-frequency frames
- Potentially causing collisions or errors
- Triggering error counter increments
- Eventually causing the target to enter bus-off state

## Test Interpretation

### Successful Attack
If the target ECU enters bus-off state:
- The ECU stops responding to CAN messages
- Error counters reached threshold (255)
- Indicates vulnerability to high-frequency traffic

### Failed Attack
If the ECU remains operational:
- ECU's error handling successfully managed the traffic
- Error counters did not reach threshold
- Indicates robust error handling and recovery mechanisms

## Limitations

- This test uses valid CAN frames; actual bus-off typically requires errors (malformed frames, CRC errors, bit errors)
- SocketCAN hardware validates frames, so format errors may not be possible
- Results depend on CAN controller implementation and error handling
- Extended duration or multiple attack vectors may be needed

## Security Notice

This tool is for security testing and research purposes only. Use only on:
- Systems you own or have explicit permission to test
- Isolated lab environments
- For security research and validation

Unauthorized testing of vehicles or ECUs may violate laws and regulations.

## Technical Details

### CAN Configuration
- Transport: CAN-FD
- Frame format: Extended 29-bit IDs
- Bitrates: 500 kbps nominal, 2 Mbps data phase
- Payload: 64 bytes (CAN-FD maximum)

### Attack Method
The tool sends CAN-FD frames with maximum payload (64 bytes) to the target ID as rapidly as possible, attempting to:
1. Saturate the bus
2. Cause transmission errors
3. Increment error counters
4. Trigger bus-off state

## Contributing

Contributions welcome! Please ensure code follows PEP 8 style guidelines.

## License

MIT License

## Acknowledgments

- Based on CAN bus security testing methodology
- Uses the `python-can` library for CAN bus access
