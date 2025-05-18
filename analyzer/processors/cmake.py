import logging
import re
from pathlib import Path
from langchain.schema import Document
from ..utils import read_file_with_fallback


class CMakeProcessor:
    def __init__(self, config):
        self.config = config['cmake']
        self.general_config = config['general']

    def process(self, project_root):
        """Process CMake files"""
        cmake_files = self._find_cmake_files(project_root)
        return self._analyze_cmake(cmake_files)

    def _find_cmake_files(self, project_root):
        """Find all CMake-related files"""
        cmake_files = {}

        for path in Path(project_root).rglob('*'):
            if path.is_file() and (path.name == "CMakeLists.txt" or path.suffix == ".cmake"):
                try:
                    content = read_file_with_fallback(path)
                    cmake_files[path] = content
                except Exception as e:
                    logging.error(f"Error reading CMake file {path}: {str(e)}")

        return cmake_files

    def _analyze_cmake(self, files):
        """Analyze CMake files and create documents"""
        docs = []

        for path, content in files.items():
            try:
                analysis = self._parse_cmake(content)
                docs.append(Document(
                    page_content=self._format_analysis(analysis),
                    metadata={
                        "source": str(path),
                        "type": "cmake",
                        "language": "cmake"
                    }
                ))
            except Exception as e:
                logging.error(f"Error analyzing {path}: {str(e)}")

        return docs

    def _parse_cmake(self, content):
        """Parse CMake content and extract important information"""
        analysis = {
            'targets': self._find_targets(content),
            'dependencies': self._find_dependencies(content),
            'variables': self._find_variables(content),
            'options': self._find_options(content)
        }

        if self.config['enable_optimization_checks']:
            analysis['optimizations'] = self._find_optimizations(content)

        return analysis

    def _find_targets(self, content):
        return re.findall(
            r'add_(executable|library)\s*\(\s*(\w+)',
            content
        )

    def _find_dependencies(self, content):
        deps = re.findall(
            r'target_link_libraries\s*\(\s*(\w+)\s+([^)]+)',
            content
        )
        return {target: libs.split() for target, libs in deps}

    def _find_variables(self, content):
        return re.findall(r'set\s*\(\s*(\w+)\s+([^)]+)', content)

    def _find_options(self, content):
        return re.findall(r'option\s*\(\s*(\w+)\s+"([^"]+)"', content)

    def _find_optimizations(self, content):
        optimizations = []
        if re.search(r'CMAKE_BUILD_TYPE\s+.*Release', content):
            optimizations.append('Release build')
        if re.search(r'IPO\s+ON', content):
            optimizations.append('Interprocedural Optimization')
        return optimizations

    def _format_analysis(self, analysis):
        """Format analysis results into readable text"""
        parts = []
        if analysis['targets']:
            parts.append("Targets:")
            for target_type, name in analysis['targets']:
                parts.append(f"- {name} ({target_type})")

        if analysis['dependencies']:
            parts.append("\nDependencies:")
            for target, libs in analysis['dependencies'].items():
                parts.append(f"- {target}: {', '.join(libs)}")

        return "\n".join(parts)