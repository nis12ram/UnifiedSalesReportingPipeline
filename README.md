# UnifiedSalesReportingPipeline - An End-to-End Azure Data Engineering Project that solves real world problem

## Project Overview
UnifiedSalesReporting is an Azure-based data engineering solution designed to automate the ingestion, transformation, and reporting of daily sales data from multiple regional branches (North, South, and West). The project addresses the business challenge of consolidating heterogeneous regional sales files into a single, reliable, and analytics-ready data source.

The UnifiedSalesReporting pipeline is built using:
1. **Azure Data Factory**: *Modular and reusable pipelines with detailed centralized logging*, *historical backfilling*, *and fault-tolerant orchestration using retry and restart-from-failure mechanisms*.
2. **Azure Databricks**: *Parameterized notebooks*, *metadata enrichment for processed data*, *robust data quality checks with quarantine handling*,*and data rescue support for schema drift and unexpected data*.
3. **Azure Data Lake Storage Gen2**: *Layered Landing–Raw–Processed zones to manage data lifecycle, quality, and governance*.
4. **Delta Lake**: *ACID-compliant unified storage ensuring reliable, scalable, and consistent analytics*.

It solves issues of inconsistent file schemas, data quality (e.g., negative revenue, missing product information), and differing regional formats by applying robust data engineering practices throughout the workflow.





