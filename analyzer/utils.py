import logging
import chardet

def configure_logger(config):
    """Configure logging system"""
    logging.basicConfig(
        level=config['level'],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config['log_file']),
            logging.StreamHandler()
        ]
    )

def detect_encoding(file_path):
    """Detect file encoding"""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def read_file_with_fallback(path):
    """Read file with encoding fallback"""
    try:
        encoding = detect_encoding(path)
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(path, 'r', encoding='cp1251') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read {path}: {str(e)}")