# LLMPress

A tool for compressing text using LLM predictability patterns.

## Overview

LLMPress uses the predictive power of language models to compress text more efficiently than traditional compression algorithms. By encoding highly predictable tokens as simple rank values and using variable-length encoding for other tokens, LLMPress can achieve competitive compression ratios for natural language text.

## Features

- **Compression**: Compress text files using the GPT-2 model, reducing their size while maintaining the integrity of the original content.
- **Decompression**: Reconstruct the original text from compressed files using saved ranks, ensuring that the decompressed text matches the original.
- **Utility Functions**: Includes various utility functions for token encoding, bit conversion, and other necessary operations to support compression and decompression.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Compression

```bash
python src/compressor.py your_text_file.txt --output compressed.bin
```

### Decompression

```bash
python src/decompressor.py compressed.bin --output decompressed.txt
```

### Validation

```bash
python src/validator.py --compressed compressed.bin --decompressed decompressed.txt --original your_text_file.txt
```

## How it Works

1. **Token Prediction**: For each position in the text, the model predicts the most likely next tokens.
2. **Rank-Based Encoding**: If the actual next token is among the top predictions, we encode just its rank (0-63).
3. **Explicit Encoding**: If the token is not predictable, we encode its full ID or ASCII value.
4. **Variable-Length Format**: Explicit tokens use a variable-length encoding to minimize space.

## Troubleshooting

### Tokenizers Installation Issues

If you see errors related to building/installing the tokenizers package:

1. Try installing a pre-built wheel:
   ```
   python -m pip install https://download.pytorch.org/whl/cpu/tokenizers-0.13.3-cp39-cp39-win_amd64.whl
   ```
   (Replace cp39 with your Python version and win_amd64 with your platform)

2. If that fails, the system will use a minimal tokenizer implementation as a fallback.

## Testing

Unit tests for the compression and decompression functionalities can be found in the `tests/test_compression.py` file. To run the tests, use:

```
pytest tests/test_compression.py
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.