# DataGuardian

DataGuardian is an open-source Python library for automated data quality profiling, validation and drift detection.

## Features

- Dataset profiling
- Missing value analysis
- Duplicate detection
- Data quality scoring
- YAML data contracts
- Dataset validation
- Drift detection
- HTML reports
- JSON reports
- CLI integration
- CI/CD ready

## Installation

pip install -e .

## Quick Start

from dataguardian import profile

report = profile("customers.csv")

## Roadmap

### MVP

- CSV & Parquet support
- Profiling
- Quality report
- YAML contracts
- Dataset validation
- GitHub Actions

## License

MIT
