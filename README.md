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
This process is implemented using the **ADF ingestion_pipeline**.
Key Features:
1. Data in the Raw Zone is organized using the yyyy/mm/dd/region/<file_name> directory structure to enable efficient data discovery and management.
2. Successful and failed ingestion events are logged in a JSON file.
3. Supports restart-from-failure mechanism.
4. Supports backfilling.

<img width="1355" height="744" alt="Screenshot 2026-01-11 113056" src="https://github.com/user-attachments/assets/0690cbf6-66fb-4c03-ab28-b4c424c28d0e" />
<img width="820" height="629" alt="Screenshot 2026-01-11 143359" src="https://github.com/user-attachments/assets/378898a4-8210-448d-9ae1-aede56775d87" />
<img width="1194" height="375" alt="Screenshot 2026-01-11 143537" src="https://github.com/user-attachments/assets/5ca25166-3cac-4a07-ba3f-2cd9825dbd79" />

### Setting Up Delta Tables (Pre-requisites)
This step prepares all required Delta tables **before** processing any Raw Zone data.  
The setup is implemented using the following **Databricks Notebooks**:

- `UnifiedSalesDeltaTableSetup`
- `ExtendedSalesDeltaTableSetup`
- `QuarantinedSalesDeltaTableSetup`

#### UnifiedSalesDeltaTable
The **UnifiedSalesDeltaTable** is the primary Delta table and serves as the **single source of truth** for sales data.  
It contains **clean, validated, and analytics-ready** records that are safe for downstream consumption.

##### Maintaing Data Quality in UnifiedSalesDeltaTable
- `Schema Enforcment`
- `NOT NULL & CHECK CONSTRAINT`

##### Optimizations on UnifiedSalesDeltaTable
- `optimizeWrite` & `autoCompact` to automatically manage small files.
- `partition by (SaleDate, Region)` to improve performance on date and region-based analytical queries


### Processing Raw Zone Data 
This process is implemented using **Databricks Notebooks**:

- `NorthProcessing`
- `SouthProcessing`
- `WestProcessing`

Each notebook processes sales data for its respective region.
#### Notebook Workflow
1. **Read Source Data**
   - Read the region-specific sales CSV file from the Raw Zone.

2. **Standardize Schema**
   - Rename columns to match the target schema.
   - Cast columns to appropriate data types.
   - Add required metadata columns.
   - Ensure alignment with the **UnifiedSalesDeltaTable** schema.

3. **Data Quality (DQ) Checks**
   Validate records for:
   - Missing or null values
   - Empty string values
   - Invalid numeric values (e.g., `Price <= 0`)

4. **Split Records Based on Quality**
   - **Good Records**: Pass all DQ checks
   - **Bad Records**: Fail one or more DQ checks

5. **Deduplicate Good Records**
   - Remove duplicates by retaining only the **latest record**
   - Use a ranking window function for deduplication

6. **Detect Schema Drift & Unexpected Data**
   - Identify additional unexpected columns in good records
   - Separate these columns from expected columns

7. **Load Data into Target Tables**
   - **MERGE** good records with expetcted columns into **UnifiedSalesDeltaTable**
     - Merge keys: `SaleID`, `SaleDate`, `Region`
   - **Append** unexpetcted columns of good records to **ExtendedSalesDeltaTable**
   - **Append** bad records to **QuarantinedSalesDeltaTable**

### Orchestrating the processing notebooks
This process is implemented using the **ADF processing_pipeline**.
Key Features:
1. Orchestrated in a way that North, South & West data are paralley processed, drastically minimizing overall processing pipeline execution time
1. Successful and failed processing events are logged in a JSON file.
2. Supports restart-from-failure mechanism.










