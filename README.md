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

## Full Breakdown
### Dropping Daily Regional Sales Data into the Landing Zone
This process is simulated using a Python script (src/main.py) that automatically generates regional sales data (src/generate_realistic_sales_files.py) and then uploads it to the landing container (src/upload_to_adls.py). Each region has a different schema and data format, reflecting many real-world scenarios.

### Ingesting Landing Zone Data into the Raw Zone
This step is implemented using the **ADF ingestion_pipeline**.
Key Features:
1. Data in the Raw Zone is organized using the yyyy/mm/dd/region/<file_name> directory structure to enable efficient data discovery and management.
2. Successful and failed ingestion events are logged in a JSON file.
3. Supports restart-from-failure mechanism.
4. Supports backfilling.

<img width="1355" height="744" alt="Screenshot 2026-01-11 113056" src="https://github.com/user-attachments/assets/0690cbf6-66fb-4c03-ab28-b4c424c28d0e" />

### Processing Landing Zone Data 
This step is implemented using **Databricks Notebooks** (Northprocessing, SouthProcessing, westprocessing).
**Notebook Working**:
reads specific region CSV sales file -> rename, cast, add metadata columns to adhere the schema of **UnifiedSalesDeltaTable** -> perform DQ checks (covering missing or null value, empty string value, invalid numeric value  like price <= 0) -> separate good & bad records based on DQ checks -> de-duplicating good records -> identify schema drift and unexpected data in good records & separate them -> MERGE good records to **UnifiedSalesDeltaTable** based on (SaleID, SaleDate and Region) -> Append unexpected data in good records to **ExtendedSalesDeltaTable** -> Append bad records to **QuarantinedSalesDeltaTable**









