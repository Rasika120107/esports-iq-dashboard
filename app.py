import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import date

st.set_page_config(page_title="Esports IQ | Sports Retail Intelligence", page_icon="🏆", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:linear-gradient(135deg,#f5f7fc 0%,#edf2fa 52%,#f8f9fc 100%); }
.block-container { max-width:1500px; padding-top:1.2rem; padding-bottom:2.5rem; }
.hero { padding:28px 32px; border-radius:22px; color:#fff; background:linear-gradient(115deg,#111c3c 0%,#243d82 58%,#6557d9 100%); margin-bottom:20px; box-shadow:0 14px 35px #15234b20; }
.hero h1 { font-family:'Space Grotesk',sans-serif; font-size:2.25rem; font-weight:700; margin:0; letter-spacing:-1.2px; }
.hero p { color:#dce4ff; margin:8px 0 0 0; }
.eyebrow { color:#b9c7ff; font-size:.72rem; letter-spacing:2px; font-weight:700; text-transform:uppercase; margin-bottom:8px; }
.kpi { background:rgba(255,255,255,.95); border:1px solid #e1e7f3; border-radius:17px; padding:16px 18px; min-height:110px; box-shadow:0 6px 18px #15234b0a; }
.kpi-label { color:#65728e; font-size:.81rem; font-weight:600; }
.kpi-value { color:#182b5b; font-family:'Space Grotesk',sans-serif; font-size:1.8rem; font-weight:700; margin-top:6px; }
.kpi-note { color:#8993a8; font-size:.75rem; margin-top:2px; }
.section-title { font-family:'Space Grotesk',sans-serif; color:#1b2e5b; font-size:1.18rem; font-weight:700; margin:8px 0 2px; }
.section-sub { color:#7a849a; font-size:.84rem; margin-bottom:12px; }
div[data-testid="stDataFrame"] { border-radius:14px; overflow:hidden; }
div.stButton>button, div.stDownloadButton>button { border-radius:10px; font-weight:700; }
</style>
""", unsafe_allow_html=True)

ALIASES = {
 "shop_name":["shop_name","shop name","store","store_name","retailer"],
 "city":["city","town"],
 "state":["state","state/ut","region"],
 "product_name":["product_name","product name","item","item_name","product"],
 "category":["category","product_category","product category","sport"],
 "brand":["brand","manufacturer"],
 "units_sold":["units_sold","units sold","quantity_sold","quantity sold","sales_units"],
 "unit_price":["unit_price","unit price","price","selling_price"],
 "stock_qty":["stock_qty","stock qty","stock","inventory","inventory_qty","quantity_in_stock"],
 "reorder_level":["reorder_level","reorder level","minimum_stock"],
 "revenue":["revenue","sales_revenue","sales revenue","sales"],
 "cost_price":["cost_price","cost price","unit_cost"],
 "date":["date","sale_date","transaction_date"],
 "supplier":["supplier","vendor"],
 "channel":["channel","sales_channel"]
}
def normalize(df):
 df=df.copy()
 cols={str(c).strip().lower().replace("-","_"):c for c in df.columns}
 rename={}
 for target,opts in ALIASES.items():
  for opt in opts:
   k=opt.lower().replace("-","_")
   if k in cols: rename[cols[k]]=target; break
 return df.rename(columns=rename)

def sample_data():
 rows=[
 ["Ace Sports Hub","Pune","Maharashtra","Cricket Bat - Pro","Cricket","Vector","34",2499,42,12,84966,1650,"2026-09-05","ProSport Supply","Store"],
 ["Ace Sports Hub","Pune","Maharashtra","Leather Cricket Ball","Cricket","RedLine","120",299,180,40,35880,170,"2026-09-06","RedLine Wholesale","Store"],
 ["Metro Sports","Mumbai","Maharashtra","Football - Match","Football","Striker","56",1299,18,20,72744,820,"2026-09-08","PlayMore Distribution","Online"],
 ["Metro Sports","Mumbai","Maharashtra","Football Boots","Football","Striker","28",3499,9,12,97972,20,"2026-09-09","PlayMore Distribution","Store"],
 ["Champion Corner","Delhi","Delhi","Badminton Racket","Badminton","SmashPro","44",1899,32,10,83556,1120,"2026-09-10","Ace Imports","Store"],
 ["Champion Corner","Delhi","Delhi","Shuttlecock Tube","Badminton","SmashPro","95",399,72,24,37905,210,"2026-09-11","Ace Imports","Online"],
 ["Court & Field","Bengaluru","Karnataka","Tennis Racket","Tennis","CourtMax","18",4999,8,10,89982,3100,"2026-09-12","CourtMax India","Store"],
 ["Court & Field","Bengaluru","Karnataka","Yoga Mat","Fitness","FlexFit","63",899,54,15,56637,500,"2026-09-13","FlexFit Direct","Online"],
 ["Goal Getter","Hyderabad","Telangana","Basketball - Size 7","Basketball","HoopWorks","31",1599,22,12,49569,940,"2026-09-14","SportSource","Store"],
 ["Goal Getter","Hyderabad","Telangana","Resistance Bands","Fitness","FlexFit","80",499,14,20,39920,260,"2026-09-15","FlexFit Direct","Online"],
 ["PlayArena","Chennai","Tamil Nadu","Swimming Goggles","Swimming","AquaEdge","47",699,38,12,32853,340,"2026-09-16","AquaEdge Wholesale","Store"],
 ["PlayArena","Chennai","Tamil Nadu","Running Shoes","Running","PaceLab","22",4299,7,14,94578,790,"2026-09-17","PaceLab Distribution","Online"],
 ["Sports Lane","Jaipur","Rajasthan","Table Tennis Bat","Table Tennis","SpinKing","39",1099,27,10,42861,630,"2026-09-18","SpinKing Traders","Store"],
 ["Sports Lane","Jaipur","Rajasthan","Dumbbell Set 10kg","Fitness","IronCore","16",2199,5,8,35184,1350,"2026-09-19","IronCore India","Store"],
 ["Peak Performance","Kolkata","West Bengal","Cycling Helmet","Cycling","RoadSafe","25",1799,11,10,44975,900,"2026-09-20","RoadSafe Supply","Online"],
 ["Peak Performance","Kolkata","West Bengal","Cricket Bat - Youth","Cricket","Vector","41",1499,63,15,61459,900,"2026-09-21","ProSport Supply","Store"],
 ["Urban Athlete","Ahmedabad","Gujarat","Skipping Rope","Fitness","FlexFit","72",249,6,18,17928,300,"2026-09-22","FlexFit Direct","Online"],
 ["Urban Athlete","Ahmedabad","Gujarat","Volleyball","Volleyball","Striker","29",999,26,10,28971,590,"2026-09-23","PlayMore Distribution","Store"],
 ["NorthStar Sports","Lucknow","Uttar Pradesh","Badminton Shoes","Badminton","SmashPro","19",2799,4,10,53181,1500,"2026-09-24","Ace Imports","Online"],
 ["NorthStar Sports","Lucknow","Uttar Pradesh","Sports Water Bottle","Accessories","HydraGo","85",349,94,25,29665,100,"2026-09-25","General Sports Supply","Store"],
 ["Coastal Sports","Kochi","Kerala","Swimming Kickboard","Swimming","AquaEdge","21",799,16,8,16779,390,"2026-09-26","AquaEdge Wholesale","Store"],
 ["Coastal Sports","Kochi","Kerala","Gym Gloves","Fitness","IronCore","37",599,7,12,22163,260,"2026-09-27","IronCore India","Online"],
 ]
 cols=["shop_name","city","state","product_name","category","brand","units_sold","unit_price","stock_qty","reorder_level","revenue","cost_price","date","supplier","channel"]
 return pd.DataFrame(rows,columns=cols)

def prepare(raw):
 d=normalize(raw)
 required=["shop_name","product_name","category","units_sold","unit_price","stock_qty"]
 missing=[x for x in required if x not in d.columns]
 if missing: return None, "Missing required columns: "+", ".join(missing)
 for c in ["city","state","brand","reorder_level","revenue","cost_price","date","supplier","channel"]:
  if c not in d.columns: d[c]="Not specified"
 for c in ["units_sold","unit_price","stock_qty","reorder_level","revenue","cost_price"]:
  d[c]=pd.to_numeric(d[c],errors="coerce")
 d=d.dropna(subset=["units_sold","unit_price","stock_qty"]).copy()
 d=d[(d.units_sold>=0)&(d.unit_price>=0)&(d.stock_qty>=0)]
 d["revenue"]=d["revenue"].fillna(d["units_sold"]*d["unit_price"])
 d["cost_price"]=d["cost_price"].fillna(0)
 d["reorder_level"]=d["reorder_level"].fillna(0)
 d["gross_profit_est"]=d["revenue"]-d["units_sold"]*d["cost_price"]
 d["margin_pct"]=d.apply(lambda r: (r["gross_profit_est"]/r["revenue"]*100) if r["revenue"] else 0,axis=1)
 d["stock_status"]=d.apply(lambda r: "Reorder now" if r["stock_qty"]<=r["reorder_level"] else ("Low stock" if r["stock_qty"]<=r["reorder_level"]*1.5 and r["reorder_level"]>0 else "Healthy"),axis=1)
 d["stock_value_est"]=d["stock_qty"]*d["cost_price"]
 return d,None

def money(n):
 if abs(n)>=10000000: return f"₹{n/10000000:.2f} Cr"
 if abs(n)>=100000: return f"₹{n/100000:.2f} L"
 return f"₹{n:,.0f}"

def layout(fig,height=340):
 fig.update_layout(height=height,margin=dict(l=8,r=8,t=35,b=8),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="DM Sans",color="#4e5d7b"),legend_title_text="")
 fig.update_xaxes(showgrid=False,zeroline=False)
 fig.update_yaxes(gridcolor="#e8edf6",zeroline=False)
 return fig

st.markdown("""<div class="hero"><div class="eyebrow">SPORTS RETAIL • SMARTER OPERATIONS</div><h1>Esports IQ</h1><p>One intelligent view of sports shops, products, inventory, sales and business opportunities.</p></div>""",unsafe_allow_html=True)

with st.sidebar:
 st.markdown("## 🏆 Esports IQ controls")
 st.caption("Upload a shop inventory or sales workbook to replace the demo data.")
 uploaded=st.file_uploader("Upload Excel (.xlsx) or CSV",type=["xlsx","csv"])
 st.divider()
 st.markdown("### Required fields")
 st.code("shop_name\\nproduct_name\\ncategory\\nunits_sold\\nunit_price\\nstock_qty",language="text")
 st.caption("Optional: city, state, brand, reorder_level, revenue, cost_price, date, supplier, channel.")
 st.info("This prototype is a decision-support dashboard. Demo records are synthetic.")

if uploaded:
 try:
  raw=pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
  df,err=prepare(raw)
  if err: st.error(err); st.stop()
  if df.empty: st.error("No valid rows found. Check sales, price and stock columns."); st.stop()
  label=f"Uploaded: {uploaded.name}"
 except Exception as e:
  st.error(f"Could not read file: {e}"); st.stop()
else:
 df,_=prepare(sample_data())
 label="Illustrative demo dataset • not real shop records"

st.markdown(f"<div style='color:#73809a;font-size:.82rem;margin:0 0 10px 2px'>DATASET: <b>{label}</b> · {len(df):,} product/shop records</div>",unsafe_allow_html=True)

a,b,c,d,e=st.columns([1.2,1.1,1.1,1.1,1.1])
shop_opts=sorted(df.shop_name.astype(str).unique())
cat_opts=sorted(df.category.astype(str).unique())
state_opts=sorted(df.state.astype(str).unique())
brand_opts=sorted(df.brand.astype(str).unique())
sel_shop=a.multiselect("Sports shop",shop_opts,placeholder="All shops")
sel_cat=b.multiselect("Sport / category",cat_opts,placeholder="All categories")
sel_state=c.multiselect("State",state_opts,placeholder="All states")
sel_brand=d.multiselect("Brand",brand_opts,placeholder="All brands")
status_opts=["Reorder now","Low stock","Healthy"]
sel_status=e.multiselect("Stock status",status_opts,placeholder="All stock")
f=df.copy()
if sel_shop:f=f[f.shop_name.isin(sel_shop)]
if sel_cat:f=f[f.category.isin(sel_cat)]
if sel_state:f=f[f.state.isin(sel_state)]
if sel_brand:f=f[f.brand.isin(sel_brand)]
if sel_status:f=f[f.stock_status.isin(sel_status)]

revenue=f.revenue.sum()
units=f.units_sold.sum()
shops=f.shop_name.nunique()
low=int(f.stock_status.isin(["Reorder now","Low stock"]).sum())
profit=f.gross_profit_est.sum()
inventory_value=f.stock_value_est.sum()
kpis=[
("Sales revenue",money(revenue),"Based on uploaded revenue or units × price"),
("Units sold",f"{units:,.0f}","Total units in filtered records"),
("Active shops",f"{shops:,}","Unique shop names"),
("Stock alerts",f"{low:,}", "Rows needing inventory review"),
("Estimated gross profit",money(profit),"Only reliable when cost_price is supplied")
]
cols=st.columns(5)
for col,(lab,val,note) in zip(cols,kpis):
 col.markdown(f'<div class="kpi"><div class="kpi-label">{lab}</div><div class="kpi-value">{val}</div><div class="kpi-note">{note}</div></div>',unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>",unsafe_allow_html=True)
l,r=st.columns([1.25,1])
with l:
 st.markdown('<div class="section-title">Sales performance by shop</div><div class="section-sub">Compare revenue across the selected shops</div>',unsafe_allow_html=True)
 x=f.groupby("shop_name",as_index=False).revenue.sum().sort_values("revenue")
 fig=px.bar(x,x="revenue",y="shop_name",orientation="h",color="revenue",color_continuous_scale=["#b8c5ff","#5146c8"],labels={"revenue":"Revenue (₹)","shop_name":""})
 fig.update_coloraxes(showscale=False)
 st.plotly_chart(layout(fig,max(340,min(520,24*len(x)+100))),use_container_width=True)
with r:
 st.markdown('<div class="section-title">Category mix</div><div class="section-sub">Sales contribution by sport and product category</div>',unsafe_allow_html=True)
 x=f.groupby("category",as_index=False).revenue.sum().sort_values("revenue",ascending=False)
 fig=px.pie(x,names="category",values="revenue",hole=.6,color_discrete_sequence=["#5146c8","#8179e6","#3c9cba","#5ebd9a","#efb65e","#ec806b","#8c9fbd","#b6c4da"])
 fig.update_traces(textposition="inside",textinfo="percent")
 st.plotly_chart(layout(fig,360),use_container_width=True)

l,r=st.columns(2)
with l:
 st.markdown('<div class="section-title">Inventory health</div><div class="section-sub">Products at, near or above their configured reorder level</div>',unsafe_allow_html=True)
 x=f.groupby("stock_status",as_index=False).size()
 order=["Reorder now","Low stock","Healthy"]
 x["stock_status"]=pd.Categorical(x.stock_status,categories=order,ordered=True);x=x.sort_values("stock_status")
 fig=px.bar(x,x="stock_status",y="size",color="stock_status",color_discrete_map={"Reorder now":"#e56f69","Low stock":"#efb65e","Healthy":"#45aa88"},labels={"size":"Product/shop records","stock_status":""})
 fig.update_layout(showlegend=False)
 st.plotly_chart(layout(fig,340),use_container_width=True)
with r:
 st.markdown('<div class="section-title">What is selling?</div><div class="section-sub">Top products by revenue in the current selection</div>',unsafe_allow_html=True)
 x=f.groupby("product_name",as_index=False).agg(revenue=("revenue","sum"),units_sold=("units_sold","sum")).sort_values("revenue",ascending=False).head(10).sort_values("revenue")
 fig=px.bar(x,x="revenue",y="product_name",orientation="h",color="units_sold",color_continuous_scale=["#c4bfff","#4d43bf"],labels={"revenue":"Revenue (₹)","product_name":"","units_sold":"Units sold"})
 fig.update_layout(coloraxis_colorbar=dict(title="Units"))
 st.plotly_chart(layout(fig,350),use_container_width=True)

st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
st.markdown('<div class="section-title">IQ recommendations</div><div class="section-sub">Rule-based prompts generated from the selected data. Review them before making purchasing decisions.</div>',unsafe_allow_html=True)
c1,c2,c3=st.columns(3)
reorder=f[f.stock_status=="Reorder now"].sort_values("units_sold",ascending=False)
lowstock=f[f.stock_status=="Low stock"]
top=f.groupby("product_name").agg(revenue=("revenue","sum"),units=("units_sold","sum")).sort_values("revenue",ascending=False)
with c1:
 st.markdown("#### 🔴 Replenishment queue")
 if len(reorder):
  st.write(f"**{len(reorder)}** product/shop records are at or below their reorder level.")
  st.caption("Start with items that combine low stock and higher unit sales.")
 else: st.write("No records are currently at or below a configured reorder level.")
with c2:
 st.markdown("#### 🟠 Watch list")
 st.write(f"**{len(lowstock)}** product/shop records are approaching the reorder threshold.")
 st.caption("Review supplier lead times and expected demand before ordering.")
with c3:
 st.markdown("#### 🟣 Commercial insight")
 if len(top):
  st.write(f"Highest-revenue product in this selection: **{top.index[0]}**.")
  st.caption("Revenue is not profit. Use complete and accurate cost data to compare margins.")
 else: st.write("No product insights available for this filter.")

st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
st.markdown('<div class="section-title">Shop & product intelligence table</div><div class="section-sub">Inspect stock, sales, supplier, margin estimates and export the filtered records.</div>',unsafe_allow_html=True)
columns=["shop_name","city","state","product_name","category","brand","units_sold","unit_price","revenue","stock_qty","reorder_level","stock_status","cost_price","gross_profit_est","margin_pct","supplier","channel","date"]
view=f[[c for c in columns if c in f.columns]].sort_values(["stock_status","revenue"],ascending=[True,False])
st.dataframe(view,use_container_width=True,hide_index=True,height=360)
st.download_button("⬇️ Download filtered analysis (CSV)",data=view.to_csv(index=False).encode("utf-8-sig"),file_name="esports_iq_analysis.csv",mime="text/csv")

template=pd.DataFrame({
 "shop_name":["Ace Sports Hub","Metro Sports"],"city":["Pune","Mumbai"],"state":["Maharashtra","Maharashtra"],
 "product_name":["Cricket Bat - Pro","Football - Match"],"category":["Cricket","Football"],"brand":["Vector","Striker"],
 "units_sold":[34,56],"unit_price":[2499,1299],"stock_qty":[42,18],"reorder_level":[12,20],
 "revenue":[84966,72744],"cost_price":[1650,820],"date":["2026-09-05","2026-09-08"],
 "supplier":["ProSport Supply","PlayMore Distribution"],"channel":["Store","Online"]
})
buf=BytesIO()
with pd.ExcelWriter(buf,engine="openpyxl") as w:
 template.to_excel(w,index=False,sheet_name="Sports_Shop_Data")
st.download_button("⬇️ Download Excel input template",data=buf.getvalue(),file_name="esports_iq_template.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.caption("Demo records are synthetic. Gross profit, margin and inventory valuation are estimates and depend on the quality of supplied cost/revenue data. This prototype does not connect to live POS, supplier, payment or ecommerce systems.")
