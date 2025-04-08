# DoliaAI - Intelligent Computer Control System

DoliaAI is an advanced AI system capable of controlling and interacting with your computer through natural language commands. It uses computer vision and machine learning to understand screen states and execute complex actions. This open-source project aims to create an AI assistant that can see, think, and act like a human when controlling a computer.

## ⚠️ Beta Status

**DoliaAI is currently in beta development.** While we're excited to share this project with the community, please be aware that:

- The system may encounter unexpected errors or bugs
- Performance may vary depending on your system configuration
- Some features may not work as expected or may be incomplete
- Regular updates and fixes are being implemented

We encourage users to report any issues they encounter to help improve the system. Your feedback is valuable to us!

## Vision & Inspiration

DoliaAI was inspired by the vision of creating an AI that can truly understand and interact with a computer like a human would. The project combines cutting-edge AI technologies with practical computer control to create a system that can:

- **See**: Continuously capture and analyze screen content using computer vision
- **Think**: Process information and make intelligent decisions using Gemini API
- **Act**: Execute precise computer control actions based on visual feedback
- **Learn**: Improve over time by learning from successes and failures

This project is completely **FREE and OPEN SOURCE**, built by the community for the community.

## Core Features

- **Natural Language Control**: Control your computer using simple English commands
- **Visual Feedback Loop**: Real-time screen analysis and state tracking
- **Intelligent Error Handling**: Automatic error detection and recovery
- **Learning Capabilities**: System learns from successful and failed actions
- **Multi-Step Reasoning**: Complex task planning and execution
- **Continuous Visual Feedback**: Real-time screen state analysis
- **Adaptive Problem Solving**: Tries multiple approaches when initial attempts fail

## How It Works

DoliaAI operates through a continuous loop of observation, analysis, and action:

1. **Capture**: Takes screenshots of the current screen state
2. **Analyze**: Sends images to Gemini API for intelligent analysis
3. **Plan**: Creates a detailed action plan based on the analysis
4. **Execute**: Performs precise computer control actions
5. **Verify**: Checks if the action was successful
6. **Learn**: Updates its knowledge base based on results

For example, when asked to "open YouTube", DoliaAI will:
1. Look for available browsers on the system
2. Open the most suitable browser
3. Navigate to the address bar
4. Type "youtube.com" and press Enter
5. Verify the page loaded correctly
6. Learn from the experience for future tasks

## Advanced Capabilities

- **Bypass Link Shorteners**: Automatically navigate through shortened URLs
- **Smart Application Management**: Find and launch applications intelligently
- **Contextual Understanding**: Maintain awareness of the current task context
- **Error Recovery**: Try alternative approaches when initial attempts fail
- **Continuous Learning**: Improve performance over time through experience

## Known Issues

As a beta release, DoliaAI may encounter the following issues:

- **Screen Recognition Limitations**: May not correctly identify all UI elements in certain applications
- **Timing Sensitivity**: Some actions may fail due to system response time variations
- **API Rate Limits**: Gemini API has usage limits that may affect performance
- **Application Compatibility**: Some applications may not respond as expected to automated controls
- **Resource Usage**: High CPU/GPU usage during continuous screen analysis

We're actively working to address these issues in future updates.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Nahvine/DoliaAI.git
cd DoliaAI
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Gemini API key:
- Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Add it to your environment variables or config file

## Usage

1. Start the AI system:
```bash
python main.py
```

2. Basic Commands:
- "Open Chrome"
- "Open Notepad and type Hello World"
- "Save this file to Documents"
- "Click the Start button"
- "Close all windows"
- "Bypass this link shortener"

3. Advanced Features:
- Multi-step task execution
- Automatic error recovery
- Learning from user interactions
- Visual state analysis

## Configuration

The system can be configured through `config.json`:
- API settings
- Timeout values
- Logging preferences
- Application paths

## Error Handling

DoliaAI includes intelligent error handling for:
- Path not found errors
- Permission issues
- Application not responding
- System resource constraints

## Future Development

We're actively working on:
- **Voice Control**: Add voice command capabilities
- **Plugin System**: Allow AI to learn specialized knowledge for different applications
- **Auto-Healing**: Automatically fix scripts when errors occur
- **Enhanced Security**: Implement sandboxing for safer operations
- **Performance Optimization**: Improve response times and efficiency

## Contributing

Contributions are welcome! We're looking for:
- Developers to improve the codebase
- Testers to find bugs and edge cases
- Documentation writers to improve guides
- Ideas for new features and capabilities

Please feel free to submit a Pull Request or open an Issue with your ideas.

## Project Creators

- **Lead Developer**: [@Nahvine](https://github.com/Nahvine) - Vision and initial implementation
- **Community Contributors**: Join us in making DoliaAI even better!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API for AI capabilities
- Python community for excellent libraries
- Contributors and testers
- Open source community for inspiration and tools
