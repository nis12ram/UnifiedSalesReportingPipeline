# UnifiedSalesReportingPipeline - An End-to-End Azure Data Engineering Project that solves real world problem

## Project Overview
UnifiedSalesReporting is an Azure-based data engineering solution designed to automate the ingestion, transformation, and reporting of daily sales data from multiple regional branches (North, South, and West). The project addresses the business challenge of consolidating heterogeneous regional sales files into a single, reliable, and analytics-ready data source.

The UnifiedSalesReporting pipeline is built using:
1. **Azure Data Factory (Orchestration)**: *Modular and reusable pipelines with detailed centralized logging*, *historical backfilling*, *and fault-tolerant orchestration using retry and restart-from-failure mechanisms*.
2. **Azure Databricks (Processing)**: *Parameterized notebooks*, *centralized data governance using unity catalog*, *metadata enrichment for processed data*, *robust data quality checks with quarantine support*, *and data rescue support for schema drift and unexpected data*.
3. **Azure Data Lake Storage Gen2 (Layered Storage)**: *Layered landing, raw, processed, and metadata zones to manage the data lifecycle, quality, and governance*.
4. **Delta Lake (Sink)**: *ACID-compliant unified storage optimized with optimized writes, auto-compaction, and partitioning to ensure reliable, scalable, and consistent analytics*.

It solves issues of inconsistent file schemas, data quality (e.g., negative revenue, missing product information), and differing regional formats by applying robust data engineering practices throughout the workflow.

## Architecture
The pipeline uses a lakehouse architecture. 

At the end of each business day, regional branches upload their sales data to the *landing* container in ADLS Gen2, organized by region. An **ADF ingestion pipeline** is then triggered, which moves the raw files as-is into the *raw* container in ADLS Gen2, organized by year, month, day, and region. The ingestion pipeline also logs the success or failure of ingestion for each regional file.

Once all ingestions succeed, the **ADF processing pipeline** is triggered. This pipeline launches **Databricks jobs** and simultaneously logs processing success or failure.

**Databricks jobs** reads regional sales data from the *raw* container, then clean, normalize, and enrich the data with metadata (Region, ProcessingTime, SourcePath). Data quality checks are performed, and records are separated into good and bad records.
* Good records are written to:
    * UnifiedSalesDeltaTable (main columns)
    * ExtendedSalesDeltaTable (additional columns)
* Bad records are written to QuarantinedSalesDeltaTable

The **UnifiedSalesDeltaTable** enforces strict data quality through **NOT NULL** and **CHECK** constraints, with **Schema Enforcement** ensuring only valid and well-structured data is written. It is optimized using **optimizeWrite** and **autoCompact**, and provides fast query performance by being **partitioned by (SaleDate, Region)**.





