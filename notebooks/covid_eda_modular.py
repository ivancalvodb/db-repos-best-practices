# Databricks notebook source
# MAGIC %md
# MAGIC ### View the latest COVID-19 hospitalization data
# MAGIC #### Setup 

# COMMAND ----------

# MAGIC %load_ext autoreload
# MAGIC %autoreload 2

# COMMAND ----------

# MAGIC %md
# MAGIC #### Get and Transform data

# COMMAND ----------

data_path = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/hospitalizations/covid-hospitalizations.csv'
print(f'Data path: {data_path}')

# COMMAND ----------

from libraries.transforms import *
import pandas as pd

df = pd.read_csv(data_path)
df = filter_country(df, country='DZA')
df = pivot_and_clean(df, fillna=0)  
df = clean_spark_cols(df)
df = index_to_col(df, colname='date')
# Convert from Pandas to a pyspark sql DataFrame.
df = spark.createDataFrame(df)

display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Save to Delta Lake
# MAGIC The current schema has spaces in the column names, which are incompatible with Delta Lake.  To save our data as a table, we'll replace the spaces with underscores.  We also need to add the date index as its own column or it won't be available to others who might query this table.

# COMMAND ----------

# This was added by me, fix on prod

import pyspark.sql.functions as F

df = df.withColumn("date", F.to_timestamp("date", "yyyy-MM-dd"))

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC #### Set the catalog and schema in Unity catalog before writting the table

# COMMAND ----------

CATALOG = "team_tuanis_catalog"
SCHEMA = "dev_schema"

spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

# COMMAND ----------

# Write to Delta Lake
df.write.mode('overwrite').option('overwriteSchema',True).saveAsTable('covid_stats')
