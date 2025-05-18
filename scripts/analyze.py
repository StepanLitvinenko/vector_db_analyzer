#!/usr/bin/env python3
import argparse
from analyzer.core import CodeAnalyzer


def main():
    parser = argparse.ArgumentParser(description='Universal C++ Code Analyzer')
    parser.add_argument('project_path', help='Path to C++ project directory')
    parser.add_argument('--rebuild', action='store_true',
                        help='Force rebuild the knowledge base')

    args = parser.parse_args()

    analyzer = CodeAnalyzer(args.project_path)
    if args.rebuild or not analyzer.vector_db.is_persisted():
        analyzer.analyze_project()

    print("Analysis completed successfully!")


if __name__ == "__main__":
    main()