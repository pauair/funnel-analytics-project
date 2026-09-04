# %% [markdown]
# ## ============================================================================
# 
# ## E-COMMERCE FUNNEL ANALYTICS PROJECT
# ## NOTEBOOK: 00_DATA_QUALITY
# 
# ### PURPOSE:
# ### Assess the quality and consistency of the source e-commerce event data
# ### before preparing the dataset and calculating funnel metrics.
# 
# ## ============================================================================

# %% [markdown]
# ## Analysis objectives
# 
# 1. Load and preview the source event dataset.
# 2. Review the dataset structure and column data types.
# 3. Check missing and blank values.
# 4. Validate event type values.
# 5. Check for duplicated rows.
# 6. Validate the event timestamp range.

# %%
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", "{:.2f}".format)

# %% [markdown]
# ## Preview source data
# 
# The source file contains event-level records. Each row represents an
# interaction made by a user during an e-commerce session.

# %%
events = pd.read_csv("../data/events.csv")
events.head()

# %% [markdown]
# ## Count total source records
# 
# I will first confirm the total number of event records and columns available
# for the analysis.

# %%
rows, columns = events.shape

print(f"Total source records: {rows}")
print(f"Total columns: {columns}")

# %% [markdown]
# ## Review source columns
# 
# The available fields describe the event timestamp, event type, product,
# category, brand, price, user, and session.

# %%
print(list(events.columns))

# %% [markdown]
# ## Review data types and non-null values
# 
# `info()` helps identify the current data type of each field and the number
# of non-null values. 
# The timestamp will be converted to a datetime field
# during the data preparation stage.

# %%
events.info()

# %% [markdown]
# ## NULL and blank value validation
# 
# I will quantify missing values before deciding how each field should be
# treated. Missing category or brand information may be retained as
# `Unknown`, while missing session identifiers require special attention for
# session-level funnel metrics.

# %%
missing_values = events.isna().sum().to_frame("missing_values")
missing_values["missing_percentage"] = (
    missing_values["missing_values"] / len(events) * 100
)

missing_values.sort_values("missing_values", ascending=False)

# %% [markdown]
# ## Check event type values
# 
# The funnel is expected to contain three event types: product views, cart
# actions, and purchases. I will validate the values and their proportions.

# %%
event_counts = events["event_type"].value_counts(dropna=False).to_frame("event_count")
event_counts["event_percentage"] = event_counts["event_count"] / len(events) * 100
event_counts

# %% [markdown]
# ## Check fully duplicated rows
# 
# I will count fully duplicated records. I will not remove them in this
# notebook because the cleaning decision belongs in the data preparation
# stage and should be documented there.

# %%
fully_duplicated_rows = events.duplicated().sum()
print(f"Fully duplicated rows: {fully_duplicated_rows:}")

events[events.duplicated(keep=False)].head(6)

# %% [markdown]
# ## Check dataset date range
# 
# The timestamp is currently stored as text. I will parse it as UTC and check
# for invalid values and the period covered by the source data.

# %%
event_time_parsed = pd.to_datetime(
    events["event_time"],
    utc=True,
    errors="coerce"
)

invalid_timestamp_count = event_time_parsed.isna().sum()

print(f"Invalid timestamps: {invalid_timestamp_count:}")
print(f"Earliest event: {event_time_parsed.min()}")
print(f"Latest event: {event_time_parsed.max()}")

# %%



