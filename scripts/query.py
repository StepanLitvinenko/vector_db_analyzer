#!/usr/bin/env python3
import argparse
from analyzer.core import CodeAnalyzer


def main():
    parser = argparse.ArgumentParser(description='Query Code Knowledge Base')
    parser.add_argument('project_path', help='Path to project directory')




    parser.add_argument('query', help='Query to execute')

    args = parser.parse_args()

    analyzer = CodeAnalyzer(args.project_path)
    result = analyzer.query(args.query)

    print("\nAnalysis Result:")
    print(result['result'])


if __name__ == "__main__":
    main()