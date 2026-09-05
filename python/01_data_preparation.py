# %% [markdown]
# ## ============================================================================
# 
# ## E-COMMERCE FUNNEL ANALYTICS PROJECT
# ## NOTEBOOK: 01_DATA_PREPARATION
# 
# ### PURPOSE:
# ### Clean the source event data and create analysis-ready fields for
# ### exploratory analysis and session-level funnel metrics.
# 
# ## ============================================================================

# %% [markdown]
# ## Preparation objectives
# 
# 1. Load the source event dataset.
# 2. Create a working copy without changing the raw file.
# 3. Remove fully duplicated records.
# 4. Convert event timestamps to UTC datetime values.
# 5. Standardize missing category and brand values.
# 6. Create category hierarchy fields.
# 7. Remove records without a session identifier from the funnel dataset.
# 8. Export the cleaned event-level dataset.

# %%
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", "{:.2f}".format)

# %% [markdown]
# ## Load source data
# 
# The raw file is kept unchanged. All preparation steps will be applied to a
# separate working DataFrame.

# %%
events_raw = pd.read_csv("../data/events.csv")
events = events_raw.copy()

print(f"Source file: {"../data/events.csv"}")
print(f"Source rows: {len(events_raw)}")

# %% [markdown]
# ## Remove fully duplicated records
# 
# The data-quality review identified fully duplicated rows. I will remove
# exact duplicates while keeping the first occurrence of each record.
# 
# This step does not remove repeated users or repeated products. Those
# repetitions represent normal e-commerce behavior.

# %%
rows_before_deduplication = len(events)

events = events.drop_duplicates().copy()

duplicates_removed = rows_before_deduplication - len(events)
print(f"Fully duplicated rows removed: {duplicates_removed:}")
print(f"Rows after deduplication: {len(events)}")

# %% [markdown]
# ## Parse event timestamps
# 
# The source timestamp is stored as text. I will convert it to a UTC datetime
# field so that the data can be sorted and grouped by date and hour.

# %%
events["event_time"] = pd.to_datetime(
    events["event_time"],
    utc=True,
    errors="coerce"
)

events["event_date"] = events["event_time"].dt.date
events["event_hour"] = events["event_time"].dt.hour

print(f"Invalid timestamps after conversion: {events['event_time'].isna().sum()}")
events[["event_time", "event_date", "event_hour"]].head()

# %% [markdown]
# ## Standardize missing category and brand values
# 
# Missing category and brand values will be retained as `Unknown`. Removing
# these records would discard valid views, cart actions, or purchases from
# the funnel analysis.

# %%
for column in ["category_code", "brand"]:
    events[column] = events[column].fillna("Unknown").astype("string").str.strip()
    events.loc[events[column].eq(""), column] = "Unknown"

print("Missing values:")
print(events[["category_code", "brand"]].isna().sum())

print("\nBlank values:")
print(events[["category_code", "brand"]].eq("").sum())

# %% [markdown]
# ## Create category hierarchy fields
# 
# The `category_code` field contains category levels separated by periods. I
# will split it into separate fields to support category-level analysis.

# %%
category_levels = events["category_code"].str.split(".", n=2, expand=True)

events["category_level_1"] = category_levels[0].fillna("Unknown")
events["category_level_2"] = category_levels[1].fillna("Unknown")
events["category_level_3"] = category_levels[2].fillna("Unknown")

events[["category_code", "category_level_1", "category_level_2", "category_level_3"]].head()

# %% [markdown]
# ## Handle missing session identifiers
# 
# The funnel will be calculated at session level. Records without a
# `user_session` value cannot be assigned to a reliable session, so they will
# be excluded from the analysis-ready funnel dataset.

# %%
missing_sessions = events["user_session"].isna().sum()
events = events.dropna(subset=["user_session"]).copy()

print(f"Rows without a session identifier removed: {missing_sessions:}")
print(f"Analysis-ready rows: {len(events)}")

# %% [markdown]
# ## Validate the analysis-ready dataset
# 
# I will confirm the final dimensions, event values, missing sessions, and
# duplicate rows before exporting the cleaned file.

# %%
print(f"Final rows: {len(events):}")
print(f"Final columns: {len(events.columns)}")
print(f"Duplicate rows remaining: {events.duplicated().sum()}")
print(f"Missing sessions remaining: {events['user_session'].isna().sum()}")

print("\nEvent counts:")
print(events["event_type"].value_counts(dropna=False))

# %% [markdown]
# ## Export cleaned data
# 
# The cleaned event-level dataset will be saved under `data/processed`. The
# raw source file remains unchanged.

# %%
events.to_csv("../data/processed/events_clean.csv", index=False)

print(f"Cleaned dataset saved to: {"../data/processed/events_clean.csv"}")


