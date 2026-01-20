# UnifiedSalesReportingPipeline - An End-to-End Azure Lakehouse Project for Reliable, Scalable Multi-Region Sales Reporting (***PROJECT 2***)

<img width="1345" height="819" alt="Screenshot 2026-01-13 224132" src="https://github.com/user-attachments/assets/b10f87ca-fa7b-4341-844e-377c2f243c7b" />

## Project Overview
**UnifiedSalesReporting is an Azure-based data engineering solution designed to automate the ingestion, transformation, and reporting of daily sales data from multiple regional branches (North, South, and West). The project addresses the business challenge of consolidating heterogeneous regional sales files into a single, reliable, and analytics-ready data source.**

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

## Layered Storage Overview
- `landing`: A container where branches drop their sales files.
- `raw`: A container where branch sales files are stored in a structured format to support data governance.
- `processed`: A container where transformed and processed data is stored as Delta tables.
- `metadata`: A container where centralized logging and operational metadata are maintained in JSON files.

## Full Breakdown
### 1️⃣ Dropping Daily Regional Sales Data into the Landing Zone
This process is simulated using a Python script (src/main.py) that automatically generates regional sales data (src/generate_realistic_sales_files.py) and then uploads it to the landing container (src/upload_to_adls.py). Each region has a different schema and data format, reflecting many real-world scenarios.

### 2️⃣ Ingesting Landing Zone Data into the Raw Zone
This process is implemented using the **ADF ingestion_pipeline**.
Key Features:
1. Data in the Raw Zone is organized using the yyyy/mm/dd/region/<file_name> directory structure to enable efficient data discovery and management.
2. Successful and failed ingestion events are logged in a JSON file.
3. Supports restart-from-failure mechanism.
4. Supports backfilling.

<img width="1355" height="744" alt="Screenshot 2026-01-11 113056" src="https://github.com/user-attachments/assets/0690cbf6-66fb-4c03-ab28-b4c424c28d0e" />
<img width="820" height="629" alt="Screenshot 2026-01-11 143359" src="https://github.com/user-attachments/assets/378898a4-8210-448d-9ae1-aede56775d87" />
<img width="1194" height="375" alt="Screenshot 2026-01-11 143537" src="https://github.com/user-attachments/assets/5ca25166-3cac-4a07-ba3f-2cd9825dbd79" />

### 3️⃣ Setting Up Delta Tables (Pre-requisites)
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


### 4️⃣ Processing Raw Zone Data 
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

### 5️⃣ Orchestrating the Processing Notebooks
This process is implemented using the **ADF processing_pipeline**.
Key Features:
1. The pipeline orchestrates the processing of North, South, and West data in parallel, significantly reducing overall execution time.
1. Successful and failed processing events are logged in a JSON file.
2. Supports restart-from-failure mechanism.

<img width="1426" height="661" alt="Screenshot 2026-01-11 211416" src="https://github.com/user-attachments/assets/53208026-0734-483c-9a39-fcd8b2eb11f9" />
<img width="1185" height="477" alt="Screenshot 2026-01-11 211600" src="https://github.com/user-attachments/assets/a729c973-c392-4f96-80a6-85d70fce8ce1" />
<img width="1109" height="440" alt="Screenshot 2026-01-11 211631" src="https://github.com/user-attachments/assets/484d97ff-467a-40bb-aa58-436063318fd7" />

### 6️⃣ Joining everything together
This process is implemented using the **ADF main_pipeline**.

<img width="1728" height="541" alt="Screenshot 2026-01-11 212911" src="https://github.com/user-attachments/assets/11a70383-05b9-480d-aa07-7098759c6ebb" />

## Problems Encountered and How They Were Solved
### Problem 1️⃣
*problem statement*: Due to the parallel orchestration of the North, South, and West processing notebooks, multiple notebooks sometimes attempt to write processed data to the Delta table simultaneously. This results in a **concurrent modification exception**

*solution*: To prevent concurrent modification exceptions from parallel notebook writes, the **UnifiedSalesDeltaTable** uses `partition-based write isolation` with an `exponential backoff retry strategy`, while the **ExtendedSalesDeltaTable** and **QuarantinedSalesDeltaTable** use `row-level concurrency` with an `exponential backoff retry strategy`.

For detailed solution -> https://www.linkedin.com/posts/nishant-choudhary-620292325_deltalake-deltatable-databricks-activity-7413619579626635265-Z8oS?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFIW0fgBT2zGDRtRxsSDdsT1rqXo-tSW3g8

### Problem 2️⃣
*problem statement*: How should bad records detected during data quality checks be handled: fail fast or quarantine?

*solution*: Since sales data originates from multiple branches with diverse formats, encountering bad records is expected. Failing fast would unnecessarily halt the pipeline, which is not the desired behavior. Instead, bad records are quarantined and kept separate from valid records, allowing the pipeline to continue while preserving invalid data for analysis and future pipeline improvements.

For detailed solution -> https://www.linkedin.com/posts/nishant-choudhary-620292325_dataengineering-bigdata-dataquality-activity-7410536022368956416-Xnfj?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFIW0fgBT2zGDRtRxsSDdsT1rqXo-tSW3g8

## How This Design Scales in Production
- New regions can be onboarded by adding configuration, not new pipelines
- Schema evolution is handled without breaking downstream consumers
- Processing is idempotent, enabling safe re-runs
- Delta Lake guarantees protect analytical workloads from partial or corrupt writes




