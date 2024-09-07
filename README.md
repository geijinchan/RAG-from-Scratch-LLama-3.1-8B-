# RAG Pipeline from Scratch with Llama 3.1 8B

## Project Overview

This project implements a complete Retrieval-Augmented Generation (RAG) pipeline using local resources, including the Llama 3.1 8B language model. The system processes PDF documents we used[this pdf](https://pressbooks.oer.hawaii.edu/humannutrition2/open/download?type=pdf), performs semantic search, and generates context-aware responses to user queries about nutrition.

## Key Features

- PDF text extraction and preprocessing
- Text embedding generation using SentenceTransformers
- Semantic search functionality
- Local deployment of Llama 3.1 8B language model
- Context-augmented prompt engineering
- Efficient query processing and response generation

## Technologies Used

- Python
- PyTorch
- Hugging Face Transformers
- SentenceTransformers
- PyMuPDF (fitz)
- NVIDIA CUDA (for GPU acceleration)

## Prerequisites

- NVIDIA GPU with at least 8GB VRAM
- [CUDA toolkit installed](https://developer.nvidia.com/cuda-toolkit-archive)
- Python 3.8+
- [Hugging Face account with access to Llama 3.1 8B model](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/geijinchan/RAG-from-Scratch-LLama-3.1-8B-.git
   cd RAG-from-Scratch-LLama-3.1-8B-
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Download the Llama 3.1 8B model weights (requires Hugging Face access token).

## Usage

1. Place your PDF document (e.g., nutrition textbook) in the project directory.
2. Run the Jupyter notebook to process the PDF, create embeddings, and set up the RAG pipeline.
3. Use the provided functions to ask questions about nutrition and receive context-aware responses.

## Example Queries

- "What are the macronutrients, and what roles do they play in the human body?"
- "How do vitamins and minerals differ in their roles and importance for health?"
- "Describe the process of digestion and absorption of nutrients in the human body."

## Performance

- Processes a 1200-page nutrition textbook
- Generates responses using a locally deployed 8B parameter language model
- Supports semantic search and context-aware answer generation

## Future Improvements

- Implement advanced PDF extraction techniques
- Experiment with different embedding models
- Add support for multi-modal inputs (text, images, tables)
- Develop an evaluation framework for response quality
- Optimize for larger datasets using vector databases

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Hugging Face for providing access to the Llama 3.1 8B model
- The authors of the nutrition textbook used in this project
