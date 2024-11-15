import argparse
import csv
import ctypes
import logging
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import NoReturn, Dict, List, Any, Optional
from contextlib import contextmanager
import shutil
from logging.handlers import RotatingFileHandler
from pynput.keyboard import Controller, Key

# Constants
VERSION = "0.5.2"
BENCHMARK_LOG = "benchmark.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 3
LOAD_WAIT_TIME = 40
CONSOLE_WAIT_TIME = 1
START_DELAY = 5
PROCESS_NAME = "csgo.exe"

logger = logging.getLogger("CLI")

@contextmanager
def timer_resolution_context():
    """Context manager for Windows timer resolution."""
    try:
        timer_resolution(True)
        yield
    finally:
        timer_resolution(False)

def aggregate(input_files: List[str], output_file: str) -> None:
    """
    Aggregate multiple CSV files into one.
    
    Args:
        input_files: List of input CSV file paths
        output_file: Path to output aggregated CSV file
    """
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8", newline='') as outfile:
            first_file = True
            for file in input_files:
                with open(file, encoding="utf-8") as infile:
                    content = infile.read()
                    if first_file:
                        outfile.write(content)
                        first_file = False
                    else:
                        # Skip header for subsequent files
                        outfile.write(''.join(content.splitlines(True)[1:]))
    except IOError as e:
        logger.error(f"Failed to aggregate files: {e}")
        raise

def app_latency(input_file: str, output_file: str) -> None:
    """
    Calculate application latency from CSV data.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file with latency data
    """
    try:
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        if not input_path.is_file():
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(input_path, encoding="utf-8", newline='') as infile:
            contents: List[Dict[str, str]] = list(csv.DictReader(infile))

        # Convert key names to lowercase
        contents = [{k.lower(): v for k, v in row.items()} for row in contents]

        with open(output_path, "w", encoding="utf-8", newline='') as outfile:
            outfile.write("MsPCLatency\n")

            for i in range(1, len(contents)):
                try:
                    ms_input_latency = (
                        float(contents[i]["msbetweenpresents"])
                        + float(contents[i]["msuntildisplayed"])
                        - float(contents[i - 1]["msinpresentapi"])
                    )
                    outfile.write(f"{ms_input_latency:.3f}\n")
                except (KeyError, ValueError) as e:
                    logger.warning(f"Skipping invalid data row {i}: {e}")

    except IOError as e:
        logger.error(f"Failed to process latency data: {e}")
        raise

def parse_config(config_path: str) -> Dict[str, str]:
    """
    Parse configuration file with error handling.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration key-value pairs
    """
    config: Dict[str, str] = {}
    
    try:
        config_path = Path(config_path).resolve()
        if not config_path.is_file():
            logger.error(f"Config file not found: {config_path}")
            return {}
            
        with open(config_path, encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line or line.startswith("//"):
                    continue

                try:
                    setting, value = [part.strip() for part in line.split("=", 1)]
                    if setting and value:
                        config[setting] = value
                except ValueError:
                    logger.warning(f"Invalid config line {line_num}: {line}")

    except IOError as e:
        logger.error(f"Failed to read config file: {e}")
        return {}

    return config

def timer_resolution(enabled: bool) -> int:
    """Set Windows timer resolution."""
    try:
        ntdll = ctypes.WinDLL("ntdll.dll")
        min_res, max_res, curr_res = ctypes.c_ulong(), ctypes.c_ulong(), ctypes.c_ulong()

        ntdll.NtQueryTimerResolution(
            ctypes.byref(min_res),
            ctypes.byref(max_res),
            ctypes.byref(curr_res),
        )

        return ntdll.NtSetTimerResolution(10000, int(enabled), ctypes.byref(curr_res))
    except Exception as e:
        logger.error(f"Failed to set timer resolution: {e}")
        return -1

def main() -> int:
    """Main program logic with improved error handling and security."""
    try:
        # Initialize logging with rotation
        logging.basicConfig(
            format="[%(name)s] %(levelname)s: %(message)s",
            level=logging.INFO,
            handlers=[
                logging.StreamHandler(),
                RotatingFileHandler(BENCHMARK_LOG, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT, encoding="utf-8")
            ]
        )

        # Check admin privileges first
        if not ctypes.windll.shell32.IsUserAnAdmin():
            logger.error("Administrator privileges required")
            return 1

        # Set working directory safely
        if getattr(sys, "frozen", False):
            os.chdir(Path(sys.executable).parent)
        elif __file__:
            os.chdir(Path(__file__).parent)

        # Load and validate configuration
        cfg = {
            "map": "1",
            "cache_trials": "1",
            "trials": "3",
            "skip_confirmation": "0",
            "output_path": str(Path("captures") / f"csgo-autobenchmark-{time.strftime('%d%m%y%H%M%S')}"),
        }

        windows_version_info = sys.getwindowsversion()
        presentmon = f"PresentMon-{'1.10.0' if windows_version_info.major >= 10 and windows_version_info.product_type != 3 else '1.6.0'}-x64.exe"
        presentmon_path = Path("bin/PresentMon") / presentmon
        
        if not presentmon_path.is_file():
            logger.error(f"PresentMon not found: {presentmon_path}")
            return 1

        map_options = {
            1: {"map": "de_dust2", "record_duration": "40"},
            2: {"map": "de_cache", "record_duration": "45"},
        }

        # Parse arguments
        parser = argparse.ArgumentParser(description=f"csgo-autobenchmark Version {VERSION}")
        parser.add_argument("--version", action="version", version=f"csgo-autobenchmark v{VERSION}")
        parser.add_argument("--map", type=int, metavar="<map choice>", help="1 for de_dust2, 2 for de_cache")
        parser.add_argument("--cache-trials", type=int, metavar="<amount>", help="number of trials to execute to build cache")
        parser.add_argument("--trials", type=int, metavar="<amount>", help="number of trials to benchmark")
        parser.add_argument("--skip-confirmation", action="store_const", const=1, help="skip start confirmation")
        parser.add_argument("--output-path", metavar="<path>", help="specify output folder for CSV logs")
        
        args = parser.parse_args()
        config_file = parse_config("config.txt")

        # Update configuration with higher precedence for CLI arguments
        for key in cfg:
            for src in (config_file, vars(args)):
                if src.get(key) is not None:
                    cfg[key] = str(src[key])

        # Validate configuration
        try:
            map_config = map_options[int(cfg["map"])]
            cs_map = map_config["map"]
            record_duration = int(map_config["record_duration"])
        except (KeyError, ValueError):
            logger.error("Invalid map specified")
            return 1

        if int(cfg["trials"]) <= 0 or int(cfg["cache_trials"]) < 0:
            logger.error("Invalid trials or cache trials specified")
            return 1

        # Create output directory
        output_path = Path(cfg["output_path"])
        try:
            output_path.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            logger.error(f"Output directory already exists: {output_path}")
            return 1

        # Calculate and display estimated time
        estimated_time_sec = 43 + (int(cfg["cache_trials"]) + int(cfg["trials"])) * (record_duration + 15)
        logger.info(f"Estimated time: {round(estimated_time_sec / 60)} minutes approx")
        
        for key, value in cfg.items():
            logger.info(f"{key}: {value}")

        if not int(cfg["skip_confirmation"]):
            input("Press enter to start benchmarking...")

        logger.info("Starting in 5 seconds (tab back into game)")
        time.sleep(START_DELAY)

        with timer_resolution_context():
            keyboard = Controller()

            # Open console
            keyboard.tap(Key.f5)
            time.sleep(CONSOLE_WAIT_TIME)

            # Load map
            keyboard.type(f"map {cs_map}\n")
            logger.info(f"Waiting for {cs_map} to load")
            time.sleep(LOAD_WAIT_TIME)

            keyboard.tap(Key.f5)
            time.sleep(CONSOLE_WAIT_TIME)

            # Load benchmark config
            keyboard.type("exec benchmark\n")
            time.sleep(CONSOLE_WAIT_TIME)

            # Run cache trials
            if int(cfg["cache_trials"]) > 0:
                for trial in range(1, int(cfg["cache_trials"]) + 1):
                    logger.info(f"Cache trial: {trial}/{cfg['cache_trials']}")
                    keyboard.type("benchmark\n")
                    time.sleep(record_duration + 15)

            # Run benchmark trials
            for trial in range(1, int(cfg["trials"]) + 1):
                logger.info(f"Recording trial: {trial}/{cfg['trials']}")
                keyboard.type("benchmark\n")

                trial_output = output_path / f"Trial-{trial}.csv"
                cmd = [
                    str(presentmon_path),
                    "-stop_existing_session",
                    "-no_top",
                    "-delay", "5",
                    "-timed", str(record_duration),
                    "-process_name", PROCESS_NAME,
                    "-output_file", str(trial_output)
                ]

                with subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                ) as process:
                    time.sleep(record_duration + 15)
                    process.kill()

                if not trial_output.exists():
                    logger.error("CSV log unsuccessful, this may be due to missing dependencies or Windows components")
                    return 1

            # Process results
            raw_csvs = [str(output_path / f"Trial-{trial}.csv") for trial in range(1, int(cfg["trials"]) + 1)]
            aggregate(raw_csvs, str(output_path / "Aggregated.csv"))
            app_latency(
                str(output_path / "Aggregated.csv"),
                str(output_path / "MsPCLatency.csv")
            )

            logger.info(f"Raw and aggregated CSVs located in: {output_path}")

        return 0

    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        logger.debug(traceback.format_exc())
        return 1

def entry_point() -> NoReturn:
    """Entry point with improved error handling and cleanup."""
    exit_code = 1
    try:
        exit_code = main()
    except KeyboardInterrupt:
        logger.info("Benchmark interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.debug(traceback.format_exc())
    finally:
        try:
            # Check if we need to keep console window open
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            process_array = (ctypes.c_uint * 1)()
            num_processes = kernel32.GetConsoleProcessList(process_array, 1)
            
            if num_processes < 3:
                input("Press enter to exit...")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        sys.exit(exit_code)

if __name__ == "__main__":
    entry_point()
