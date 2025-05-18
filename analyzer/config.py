import configparser
import os
from pathlib import Path

DEFAULT_CONFIG = """
[general]
model = deepseek-coder:6.7b
db_path = .code_rag
chunk_size = 2000
chunk_overlap = 200
max_file_size = 100000

[cpp]
extensions = .cpp, .hpp, .h, .cxx, .cc
ignore_dirs = build, cmake-build, third_party, tests
ignore_files = CMakeLists.txt, *.cmake

[cmake]
analyze_cmake = true
enable_optimization_checks = true

[logging]
level = INFO
log_file = code_analyzer.log
"""


def load_config(project_root):
    config = configparser.ConfigParser()
    config.read_string(DEFAULT_CONFIG)

    project_config = Path(project_root) / ".ragconfig"
    if project_config.exists():
        config.read(project_config)

    return {
        'general': {
            'model': config.get('general', 'model'),
            'db_path': str(Path(project_root) / config.get('general', 'db_path')),
            'chunk_size': config.getint('general', 'chunk_size'),
            'chunk_overlap': config.getint('general', 'chunk_overlap'),
            'max_file_size': config.getint('general', 'max_file_size'),
            'max_batch_size': config.getint('general', 'max_batch_size', fallback=500)

        },
        'cpp': {
            'extensions': [e.strip() for e in config.get('cpp', 'extensions').split(',')],
            'ignore_dirs': [d.strip() for d in config.get('cpp', 'ignore_dirs').split(',')],
            'ignore_files': [f.strip() for f in config.get('cpp', 'ignore_files').split(',')]
        },
        'cmake': {
            'analyze_cmake': config.getboolean('cmake', 'analyze_cmake'),
            'enable_optimization_checks': config.getboolean('cmake', 'enable_optimization_checks')
        },
        'logging': {
            'level': config.get('logging', 'level'),
            'log_file': config.get('logging', 'log_file')
        }
    }