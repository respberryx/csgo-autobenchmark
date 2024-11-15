# CSGO Autobenchmark

An automated benchmarking tool for Counter-Strike 2 (CS2) that measures system latency and performance metrics.

## Requirements

### System Requirements
- Windows 10/11
- Counter-Strike 2 installed on SSD (not recommended on HDD due to loading times)
- Administrator privileges
- Python 3.8 or higher

### CS2 Setup
1. Enable developer console in CS2 game settings
2. Bind console key to F5 (required)
3. Stable internet connection for map loading

## Installation Guide

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure CS2 Settings**
   - Copy `video.txt` to `C:\Program Files (x86)\Steam\Userdata\[YOUR_STEAM_ID]\730\local\cfg\`
   - Copy the `csgo` folder from this repository to `C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive` (required for benchmark scripts)

3. **Bind Console Key**
   - Launch CS2
   - Open console and enter: `bind F5 "toggleconsole"`

## Usage

1. **Preparation**
   - Launch CS2 and wait until you're in the main menu
   - Ensure the console is closed
   - Close any unnecessary background applications

2. **Running the Benchmark**
   ```bash
   python -m csgo_autobenchmark
   ```
   - Press Enter when ready to start benchmarking
   - You have 5 seconds to tab back into CS2
   - Do not interact with your PC during the benchmark

3. **Configuration (Optional)**
   Edit `config.txt` to customize:
   - Map selection (de_dust2 or de_cache)
   - Number of cache trials
   - Number of benchmark trials
   - Skip confirmation prompt
   - Custom output path

## Output Files

- `Trial-X.csv`: Raw data for each benchmark trial
- `Aggregated.csv`: Combined data from all trials
- `MsPCLatency.csv`: Processed system latency measurements
- `benchmark.log`: Detailed benchmark process log

## Command Line Arguments

```bash
python -m csgo_autobenchmark [options]

Options:
  --map <1|2>           Select map (1=de_dust2, 2=de_cache)
  --cache-trials <num>  Number of cache warmup trials
  --trials <num>        Number of benchmark trials
  --skip-confirmation   Skip start confirmation
  --output-path <path>  Custom output directory
```

## Troubleshooting

1. **PresentMon Not Found**
   - Ensure you have administrator privileges
   - Ensure that antivirus isn't blocking the executable

2. **CSV Log Unsuccessful**
   - Verify Windows Media Foundation (WMF) is installed
   - Run with administrator privileges

3. **Long Load Times**
   - Install CS2 on an SSD
   - Close background applications
   - Ensure stable internet connection

## Acknowledgments

- [PresentMon](https://github.com/GameTechDev/PresentMon) for performance monitoring
