# Local RAG Pipeline with Llama 3

## Project Overview

This project implements a complete Retrieval-Augmented Generation (RAG) pipeline using local resources, including the Llama 3 language model. The system processes PDF documents, performs semantic search, and generates context-aware responses to user queries.

## Key Features

- PDF text extraction and preprocessing
- Text embedding generation using SentenceTransformers
- Semantic search functionality
- Local deployment of Llama 3 language model
- Context-augmented prompt engineering
- Efficient query processing and response generation

## Technologies Used

- Python
- PyTorch
- Hugging Face Transformers
- SentenceTransformers
- PyMuPDF (fitz)
- NVIDIA CUDA (for GPU acceleration)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/local-rag-pipeline.git
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Download the Llama 3 model weights (requires Hugging Face access token).

## Usage

1. Place your PDF document in the project directory.
2. Run the preprocessing script to extract and embed text:
   ```
   python preprocess.py
   ```
3. Start the RAG pipeline:
   ```
   python rag_pipeline.py
   ```
4. Enter your queries and receive context-aware responses.

## Performance

- Processes a 1200-page textbook in under [X] minutes
- Generates responses in [Y] seconds on average
- Supports [Z] concurrent users on a single GPU

## Future Improvements

- Implement advanced PDF extraction techniques
- Experiment with different embedding models
- Add support for multi-modal inputs (text, images, tables)
- Develop an evaluation framework for response quality
- Optimize for larger datasets using vector databases

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
