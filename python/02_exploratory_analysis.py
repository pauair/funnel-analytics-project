# %% [markdown]
# ## ============================================================================
# 
# ## E-COMMERCE FUNNEL ANALYTICS PROJECT
# ## NOTEBOOK: 02_EXPLORATORY_ANALYSIS
# 
# ### PURPOSE:
# ### Explore user, session, product, category, price, and time behavior before
# ### building the session-level funnel analysis.
# 
# ## ============================================================================

# %% [markdown]
# ## Analysis objectives
# 
# 1. Load the cleaned event-level dataset.
# 2. Review baseline users, sessions, products, and categories.
# 3. Compare event volumes across the main event types.
# 4. Review price and session activity distributions.
# 5. Analyze event volume by date and hour.
# 6. Identify the most active categories and products.

# %%
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")
pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", "{:.2f}".format)

plt.rcParams.update({
    "font.family": "Tahoma",
    "axes.titlesize": 14,
    "axes.labelsize": 10,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8
})

def format_chart(ax):
    ax.grid(
        axis="both",
        color="#E5E7EB",
        linewidth=0.8,
        alpha=0.8
    )

    sns.despine(
        ax=ax,
        top=True,
        right=True
    )
    return ax

general_color = "#6670A3"

# %% [markdown]
# ## Load cleaned event data
# 
# The exploratory analysis uses the cleaned event-level dataset created during
# data preparation. The raw source file remains unchanged.

# %%
events = pd.read_csv("../data/processed/events_clean.csv", parse_dates=["event_time", "event_date"])

print(f"Cleaned file: ../data/processed/events_clean.csv")
print(f"Rows loaded: {len(events)}")
events.head()

# %% [markdown]
# ## Baseline KPIs
# 
# I will review the main dimensions of the dataset before analyzing individual
# event types or funnel stages.

# %%
baseline_kpis = pd.DataFrame({
    "metric": [
        "Event records",
        "Unique users",
        "Unique sessions",
        "Unique products",
        "Unique category codes",
        "Average price",
        "Median price"
    ],
    "value": [
        len(events),
        events["user_id"].nunique(),
        events["user_session"].nunique(),
        events["product_id"].nunique(),
        events["category_code"].nunique(),
        events["price"].mean(),
        events["price"].median()
    ]
})

baseline_kpis

# %% [markdown]
# ## Event volume by type
# 
# The event distribution provides the first view of the shopping journey.
# These are event counts, not unique users or sessions.

# %%
event_order = ["view", "cart", "purchase"]
event_counts = (
    events["event_type"]
    .value_counts()
    .reindex(event_order)
    .rename_axis("event_type")
    .reset_index(name="event_count")
)
event_counts["event_percentage"] = event_counts["event_count"] / len(events) * 100
event_counts

# %%
custom_palette = {
    "view": "#8E97AC",
    "cart": "#FFC400",
    "purchase": "#6CB54D"
}

fig, ax = plt.subplots(figsize=(7, 4))

sns.barplot(
    data=event_counts,
    x="event_type",
    y="event_count",
    order=event_order,
    hue="event_type",
    hue_order=event_order,
    palette=custom_palette,
    legend=False,
    ax=ax
)

ax.set_title(
    "Event volume by event type",
    pad=20
)

ax.set_xlabel(
    "Event type",
    labelpad=15
)

ax.set_ylabel(
    "Number of events",
    labelpad=15
)

fig.tight_layout(pad=2)

format_chart(ax)
ax.grid(axis="x", visible=False)

plt.show()

# %%


# %% [markdown]
# ## Price distribution
# 
# I will review the price distribution to identify the typical price range and
# potentially extreme values that may affect comparisons.

# %%
price_summary = events["price"].describe(
    percentiles=[0.25, 0.50,0.75, 0.90, 0.99]
)
price_summary

# %%
price_bins = [0, 25, 50, 100, 250, 500, 1000, float("inf")]

price_labels = ["0–25", "25–50", "50–100", "100–250", "250–500", "500–1,000", "1,000+"]

events["price_band"] = pd.cut(
    events["price"],
    bins=price_bins,
    labels=price_labels,
    right=False
)

price_band_counts = (
    events["price_band"]
    .value_counts(sort=False)
    .rename_axis("price_band")
    .reset_index(name="event_count")
)

fig, ax = plt.subplots(figsize=(9, 4))
sns.barplot(
    data=price_band_counts,
    x="price_band",
    y ="event_count",
    color=general_color,
    ax=ax
)

ax.set_title(
    "Product price distribution",
    pad=20
)

ax.set_xlabel(
    "Price",
    labelpad=15
)

ax.set_ylabel(
    "Event count",
    labelpad=15
)

format_chart(ax)
ax.grid(axis="x", visible=False)

plt.show()

# %% [markdown]
# ## Session activity
# 
# I will review how many events are associated with each session. This prepares
# the analysis for the session-level funnel without calculating conversion
# metrics yet.

# %%
session_activity = (
    events.groupby(["user_id", "user_session"], as_index=False)
    .agg(
        user_id=("user_id", "first"),
        event_count=("event_type", "size"),
        unique_event_types=("event_type", "nunique"),
        session_start=("event_time", "min"),
        session_end=("event_time", "max")
    )
)
session_activity["duration_minutes"] = (
    session_activity["session_end"] - session_activity["session_start"]
).dt.total_seconds() / 60

session_activity[["event_count", "unique_event_types", "duration_minutes"]].describe()

# %%
session_bins = [ 0, 1, 2, 3, 5, 10, 20, 50, float("inf")]

session_labels = [
    "1 event",
    "2 events",
    "3 events",
    "4–5 events",
    "6–10 events",
    "11–20 events",
    "21–50 events",
    "51+ events"
]

session_activity["event_band"] = pd.cut(
    session_activity["event_count"],
    bins=session_bins,
    labels=session_labels,
    right=True,
    include_lowest=True
)

session_event_bands = (
    session_activity["event_band"]
    .value_counts(sort=False)
    .rename_axis("event_band")
    .reset_index(name="session_count")
)

fig, ax = plt.subplots(figsize=(9, 4))

sns.barplot(
    data=session_event_bands,
    x="event_band",
    y="session_count",
    color=general_color,
    ax=ax
)

ax.set_title(
    "Sessions by Number of Events",
    pad=20
)

ax.set_xlabel(
    "Events per session",
    labelpad=15
)

ax.set_ylabel(
    "Number of sessions",
    labelpad=15
)

format_chart(ax)
ax.grid(axis="x", visible=False)

plt.show()

# %% [markdown]
# ## Event volume by date and hour
# 
# I will analyze when users are most active on the platform. The timestamps are
# already represented in UTC.

# %%
daily_events = (
    events.groupby("event_date", as_index=False)
    .size()
    .rename(columns={"size": "event_count"})
)

daily_events.head()

# %%
fig, ax = plt.subplots(figsize=(9, 4))

sns.lineplot(
    data=daily_events, 
    x="event_date", 
    y="event_count",
    color=general_color,
    linewidth=1.5,
    ax=ax)

ax.set_title(
    "Daily event volume", 
    pad=20)

ax.set_xlabel(
    "Date", 
    labelpad=15)

ax.set_ylabel(
    "Number of events", 
    labelpad=15)

format_chart(ax)
ax.grid(axis="x", visible=False)

plt.show()

# %%
hourly_events = (
    events.groupby("event_hour", as_index=False)
    .size()
    .rename(columns={"size": "event_count"})
)

fig, ax = plt.subplots(figsize=(9, 4))
sns.barplot(
    data=hourly_events, 
    x="event_hour", 
    y="event_count", 
    color=general_color,
    ax=ax)

ax.set_title(
    "Event volume by hour (UTC)",
    pad=20)

ax.set_xlabel(
    "Hour of day (UTC)", 
    labelpad=15)

ax.set_ylabel(
    "Number of events", 
    labelpad=15)

format_chart(ax)
ax.grid(axis="x", visible=False)

plt.show()

# %% [markdown]
# ## Category and product activity
# 
# I will identify the categories and products with the highest observed event
# volume. These results will support the later business-question analysis.

# %%
category_summary = (
    events.groupby("category_level_1", as_index=False)
    .agg(
        event_count=("event_type", "size"),
        view_count=("event_type", lambda values: (values == "view").sum()),
        cart_count=("event_type", lambda values: (values == "cart").sum()),
        purchase_count=("event_type", lambda values: (values == "purchase").sum())
    )
    .sort_values("event_count", ascending=False)
)

category_summary.head(15)

# %%
top_categories = (
    category_summary[category_summary["category_level_1"] != "Unknown"]
    .nlargest(10, "event_count")
    .sort_values("event_count")
)

fig, ax = plt.subplots(figsize=(9, 4))
sns.barplot(
    data=top_categories, 
    x="event_count", 
    y="category_level_1", 
    color=general_color,
    ax=ax)

ax.set_title(
    "Top categories by event volume", 
    pad=20)

ax.set_xlabel(
    "Number of events", 
    labelpad=15)

ax.set_ylabel(
    "Category level 1", 
    labelpad=15)

format_chart(ax)
ax.grid(axis="y", visible=False)

plt.show()

# %%
product_summary = (
    events.groupby("product_id", as_index=False)
    .agg(
        event_count=("event_type", "size"),
        view_count=("event_type", lambda values: (values == "view").sum()),
        cart_count=("event_type", lambda values: (values == "cart").sum()),
        purchase_count=("event_type", lambda values: (values == "purchase").sum()),
        average_price=("price", "mean")
    )
)

top_viewed_products = product_summary.nlargest(10, "view_count")
top_viewed_products


