# vbase-py-samples

vBase Python Software Development Kit (SDK) Samples

-   Python 3.8+ support

---

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Introduction

vBase creates a global auditable record of when data was created, by whom, and how it has changed (collectively, “data provenance”). Data producers can prove the provenance of their data to any external party, increasing its value and marketability. Data consumers can ensure the integrity of historical data and any derivative calculations. The result is trustworthy information that can be put into production quickly without expensive and time-consuming trials.

vBase services do not require access to the data itself, assuring privacy. They also do not rely on centralized intermediaries, eliminating the technical, operating, and business risks of a trusted party controlling your data and its validation. vBase ensures data security and interoperability that is unattainable with legacy centralized systems. It does so by storing digital fingerprints of data, metadata, and revisions on secure public blockchains.

## Getting Started

The following samples illustrate common solutions built on top of the vBase SDK and services.

Please follow the [Quickstart](docs/quickstart.md) guide to configure your environment.

## Documentation writing hints
We use the MyST markdown format for our documentation. Here are some rules to make our documentation consistent and MyST-compatible:

1 - Please use the following format for a TOC links:
`[Item Name](docname.md#item-name)`

2 - Section header format:
`## Item Name <a href="#item-name" id="item-name"></a>`

3 - IDs should match the actual text
This won't work:
`## My Text <a href="#item-name" id="item-name"></a>`

This works: `## My Text <a href="#my-text" id="my-text"></a>`

MyST generates IDs based on the section text, so our IDs must match the generated ones. It's tedious, but necessary.
Every time when we change a caption for some section - we need to update the corresponding ID
