# Esports IQ — Sports Shop Intelligence Dashboard

## Run
1. Install Python 3.10+.
2. Extract this ZIP and open a terminal in the folder.
3. Run `pip install -r requirements.txt`
4. Run `streamlit run app.py`
5. Upload an `.xlsx` or `.csv` file in the sidebar.

## What is implemented (80% starter build)
- Styled Streamlit dashboard with demo data
- Excel/CSV upload and header normalization for common names
- KPI cards: sales revenue, units sold, shops, stock alerts, estimated gross profit
- Shop revenue comparison and category mix charts
- Stock health/reorder status
- Top products by revenue
- Rule-based replenishment recommendations
- Shop/product table, filters and CSV export
- Downloadable Excel template

## Required input columns
- `shop_name`
- `product_name`
- `category`
- `units_sold`
- `unit_price`
- `stock_qty`

## Optional input columns
`city`, `state`, `brand`, `reorder_level`, `revenue`, `cost_price`, `date`, `supplier`, `channel`

When `revenue` is missing, it is calculated as units_sold × unit_price. When `cost_price` is missing, gross-profit estimates will not be meaningful. Set reorder_level to a sensible value per product/shop to enable useful alerts.

## Remaining 20% for students
The project is intentionally designed as a student extension challenge. Suggested tasks:
1. Add date-range filtering and month-over-month sales trend.
2. Add demand forecasting (compare a baseline moving average with a model).
3. Add a product recommendation or cross-sell module.
4. Add supplier scorecards using delivery time, defect/return rate and purchase cost.
5. Add role-based access, shop-level data isolation and audit logs.
6. Add database persistence (SQLite/PostgreSQL) instead of file-only uploads.
7. Add automated tests, data validation, and deployment.

Students should select and document their chosen enhancements rather than assume these features already exist.

## Data and calculation caveats
Demo records are synthetic, not real store data. Gross profit estimate = revenue − units_sold × cost_price; it excludes operating costs, tax, discounts and returns unless those are already reflected in source values. Stock status uses stock_qty against reorder_level; configure reorder levels to suit lead time and demand. This is a prototype, not a live POS/ERP integration.
