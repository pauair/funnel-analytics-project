# %% [markdown]
# ## ============================================================================
# 
# ## E-COMMERCE FUNNEL ANALYTICS PROJECT
# ## NOTEBOOK: 04_BUSINESS_QUESTIONS
# 
# ### PURPOSE:
# ### This notebook translates the funnel results into product, category, price,
# ### and session insights.
# 
# ## ============================================================================

# %% [markdown]
# ## Analysis objectives
# 
# This notebook answers four business questions:
# 
# 1. Which products have high visibility but weak purchase activity?
# 2. Which categories show stronger or weaker conversion?
# 3. How does price relate to event-level conversion?
# 4. Do more engaged sessions have stronger funnel outcomes?
# 
# Product, category, and price metrics are event-based. Session metrics use the session-level table created in the funnel analysis notebook.

# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from IPython.display import display

sns.set_theme(style='whitegrid')
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:.2f}'.format)

plt.rcParams.update({
    'font.family': 'Tahoma',
    'axes.titlesize': 14,
    'axes.labelsize': 10,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8
})

general_color = '#6670A3'
highlight_color = '#6CB54D'
warning_color = '#FFC400'
grid_color = '#E5E7EB'

def format_chart(ax):
    ax.grid(
        axis='both', 
        color=grid_color, 
        linewidth=0.8, 
        alpha=0.8)
    sns.despine(
        ax=ax, 
        top=True, 
        right=True)
    return ax

def add_event_rates(summary):
    summary['view_to_cart_rate'] = (
        summary['cart_count']
        .div(summary['view_count'])
        .mul(100)
        .where(summary['view_count'] > 0)
    )
    summary['view_to_purchase_rate'] = (
        summary['purchase_count']
        .div(summary['view_count'])
        .mul(100)
        .where(summary['view_count'] > 0)
    )
    return summary

# %% [markdown]
# ## Load the analytical datasets
# 
# I will use the cleaned event-level dataset for product, category, and price
# questions. I will use the session-level export for session engagement metrics.

# %%
events = pd.read_csv(
    '../data/processed/events_clean.csv',
    parse_dates=['event_time', 'event_date']
)

session_funnel = pd.read_csv(
    '../data/processed/tableau_funnel_sessions.csv',
    parse_dates=['session_start_date']
)

print(f'Cleaned event rows loaded: {len(events)}')
print(f'Session-level rows loaded: {len(session_funnel)}')

# %% [markdown]
# ### QUESTION 1: 
# ## Which products have high visibility but weak purchase activity?
# 
# A product with many views and few purchases may represent an opportunity for
# further investigation. Possible explanations include pricing, availability,
# product relevance, or friction on the product detail page.

# %%
product_summary = (
    events.groupby('product_id', as_index=False)
    .agg(
        event_count=('event_type', 'size'),
        view_count=('event_type', lambda values: (values == 'view').sum()),
        cart_count=('event_type', lambda values: (values == 'cart').sum()),
        purchase_count=('event_type', lambda values: (values == 'purchase').sum()),
        average_price=('price', 'mean'),
        category_code=('category_code', 'first'),
        brand=('brand', 'first')
    )
)

product_summary = add_event_rates(product_summary)
high_visibility_threshold = product_summary['view_count'].quantile(0.90)

product_opportunities = (
    product_summary[product_summary['view_count'] >= high_visibility_threshold]
    .sort_values(['view_to_purchase_rate', 'view_count'], ascending=[True, False])
    .head(10)
)

print('High-visibility products with the lowest view-to-purchase rates:')
display(product_opportunities[[
    'product_id', 'view_count', 'cart_count', 'purchase_count',
    'view_to_cart_rate', 'view_to_purchase_rate', 'average_price',
    'category_code', 'brand'
]])

# %%
top_viewed_products = (
    product_summary
    .nlargest(10, "view_count")
    .sort_values("view_count")
)

product_order = (
    top_viewed_products
    .sort_values("view_count", ascending=False)["product_id"]
    .tolist()
)

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(
    data=top_viewed_products,
    x='product_id',
    y='view_count',
    color=general_color,
    order=product_order,
    ax=ax
)
ax.set_title(
    'Top 10 products by view volume', 
    pad=20)
ax.set_xlabel(
    'Product ID', 
    labelpad=15)
ax.set_ylabel(
    'Number of views', 
    labelpad=15)

format_chart(ax)
ax.grid(axis="x", visible=False)

plt.show()

# %% [markdown]
# ### QUESTION 2: 
# ## Which categories show stronger or weaker conversion?
# 
# I will compare categories using a minimum view threshold. This avoids ranking
# categories with very few observations and focuses the comparison on categories
# with enough activity to be directionally useful.

# %%
category_summary = (
    events.groupby('category_level_1', as_index=False)
    .agg(
        event_count=('event_type', 'size'),
        view_count=('event_type', lambda values: (values == 'view').sum()),
        cart_count=('event_type', lambda values: (values == 'cart').sum()),
        purchase_count=('event_type', lambda values: (values == 'purchase').sum()),
        average_price=('price', 'mean')
    )
)

category_summary = add_event_rates(category_summary)
category_comparison = (
    category_summary[
        (category_summary['category_level_1'] != 'Unknown')
        & (category_summary['view_count'] >= 1_000)
    ]
    .sort_values('view_to_purchase_rate', ascending=False)
)

print('Category comparison using categories with at least 1000 views:')
display(category_comparison)

# %%
top_categories = category_comparison.nlargest(10, 'view_count').sort_values('view_count')

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(
    data=top_categories,
    x='view_count',
    y='category_level_1',
    color=general_color,
    ax=ax
)
ax.set_title(
    'Top categories by view volume', 
    pad=20)

ax.set_xlabel(
    'Number of views', 
    labelpad=15)

ax.set_ylabel(
    'Category', 
    labelpad=15)

format_chart(ax)
ax.grid(axis="y", visible=False)

plt.show()

# %% [markdown]
# ### QUESTION 3: 
# ## How does price relate to event-level conversion?
# 
# Price bands make the distribution easier to compare than a raw price
# histogram. These rates are based on event counts, so they should be used as
# directional indicators rather than customer-level conversion rates.

# %%
price_bins = [0, 25, 50, 100, 250, 500, 1_000, np.inf]
price_labels = ['0–25', '25–50', '50–100', '100–250', '250–500', '500–1,000', '1,000+']

events['price_band'] = pd.cut(
    events['price'],
    bins=price_bins,
    labels=price_labels,
    right=False
)

price_summary = (
    events.groupby('price_band', observed=False, as_index=False)
    .agg(
        event_count=('event_type', 'size'),
        view_count=('event_type', lambda values: (values == 'view').sum()),
        cart_count=('event_type', lambda values: (values == 'cart').sum()),
        purchase_count=('event_type', lambda values: (values == 'purchase').sum())
    )
)

price_summary = add_event_rates(price_summary)
display(price_summary)

# %%
fig, ax = plt.subplots(figsize=(8, 4))

sns.barplot(
    data=price_summary,
    x='price_band',
    y='view_to_purchase_rate',
    color=highlight_color,
    ax=ax
)

ax.set_title(
    'View-to-purchase rate by price band', 
    pad=20)

ax.set_xlabel(
    'Price band', 
    labelpad=15)

ax.set_ylabel(
    'View-to-purchase rate (%)', 
    labelpad=15)

format_chart(ax)
ax.grid(axis='x', visible=False)

plt.show()

# %% [markdown]
# ### QUESTION 4: 
# ## Do more engaged sessions have stronger funnel outcomes?
# 
# I will group sessions by the number of recorded events and compare the share
# of sessions that completed the chronological funnel. This helps distinguish
# simple traffic volume from deeper engagement.

# %%
session_funnel['event_band'] = pd.cut(
    session_funnel['event_count'],
    bins=[0, 1, 2, 3, 5, 10, np.inf],
    labels=['1', '2', '3', '4–5', '6–10', '11+'],
    right=True
)

session_engagement = (
    session_funnel.groupby('event_band', observed=False, as_index=False)
    .agg(
        session_count=('user_session', 'size'),
        view_sessions=('has_view', 'sum'),
        ordered_purchase_sessions=('valid_funnel_order', 'sum')
    )
)

session_engagement['ordered_purchase_rate'] = (
    session_engagement['ordered_purchase_sessions']
    .div(session_engagement['view_sessions'])
    .mul(100)
    .where(session_engagement['view_sessions'] > 0)
)

display(session_engagement)

# %%
fig, ax = plt.subplots(figsize=(8, 4))

sns.barplot(
    data=session_engagement,
    x='event_band',
    y='ordered_purchase_rate',
    color=highlight_color,
    ax=ax
)

ax.set_title(
    'Chronological purchase rate by session activity', 
    pad=20)
ax.set_xlabel(
    'Events per session', 
    labelpad=15)
ax.set_ylabel(
    'Purchase rate after view (%)', 
    labelpad=15)

format_chart(ax)
ax.grid(axis='x', visible=False)

plt.show()

# %% [markdown]
# ### Business summary
# 
# The results are descriptive and should be used to prioritize further investigation. High-visibility products with low purchase rates may require review of pricing, availability, relevance, and product-page experience. Category and price comparisons should be interpreted with their event-based definitions and minimum-volume thresholds in mind. Additional analysis would be needed to test whether the observed differences are statistically meaningful.


