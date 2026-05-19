import os
import streamlit as st
import pandas as pd
import requests
import random
import plotly.graph_objects as go
from pytrends.request import TrendReq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from database import init_db, save_report, get_reports
from openai import OpenAI
from risk import generate_risk_analysis
import risk
from roadmap import generate_roadmap
from database import delete_report
import json

init_db()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="AI Business Navigator",
    page_icon="logo.png",   #favicon
    layout="wide"
)

# ---------------- API ----------------

def get_trend_score(keyword):
    try:
        py = TrendReq(hl='en-IN')
        py.build_payload([keyword], timeframe='today 3-m')
        data = py.interest_over_time()
        if not data.empty:
            return int(data[keyword].mean())
    except:
        pass
    return random.randint(50, 80)

def get_price(query):
    try:
        r = requests.get(f"https://dummyjson.com/products/search?q={query}", timeout=5)
        data = r.json()
        if "products" in data and len(data["products"]) > 0:
            return data["products"][0]["price"]
    except Exception as e:
        print("Price API Error:", e)

    return 500

# ---------------- AI ----------------

def fallback_ai(idea, trend):
    return f"""
### 🔹 SWOT Analysis

**Strength:**
- Growing demand ({trend})

**Weakness:**
- Initial investment required

**Opportunity:**
- Expanding market

**Threat:**
- High competition


### 🔹 Target Audience
- Young digital users interested in {idea}


### 🔹 Marketing Strategy
- Social media marketing (Instagram, reels)
- Influencer collaborations
- Content-based branding


### 🔹 90-Day Plan

**Month 1:**
- Market research
- Competitor analysis

**Month 2:**
- Business setup
- Product/service preparation

**Month 3:**
- Launch campaign
- Scale marketing efforts
"""

def generate_ai_plan(idea, budget, exp, trend):

            prompt = f"""
            Return ONLY valid JSON like this:

            {{
            "swot": {{
                "Strength": "...",
                "Weakness": "...",
                "Opportunity": "...",
                "Threat": "..."
            }},
            "audience": "...",
            "marketing": ["...", "..."],
            "plan": {{
                "Month 1": "...",
                "Month 2": "...",
                "Month 3": "..."
            }}
            }}

            Idea: {idea}
            Budget: ₹{budget}
            Experience: {exp}
            Trend: {trend}
            """

            try:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )

                return res.choices[0].message.content

            except Exception as e:
                print("OpenAI Error:", e)

                # 🔥 FALLBACK AI
                return fallback_ai(idea, trend)
    
# ---------------- LOGIC ----------------

def business_model(idea, budget, exp, trend):

    idea = idea.lower()

    # -------- E-COMMERCE / PRODUCT --------
    if any(word in idea for word in ["clothing", "tshirt", "fashion", "brand"]):
        return {
            "model": "Print on Demand"
        }

    # -------- FOOD / CAFE --------
    elif any(word in idea for word in ["food", "cafe", "restaurant", "bakery"]):
        if budget >= 50000:
            return {
                "model": "Cloud Kitchen"
            }
        else:
            return {
                "Home-based Food Service"
            }

    # -------- RESELLING --------
    elif budget < 20000 or exp == "Beginner":
        return {
            "model": "Reselling"
        }

    # -------- TREND BASED --------
    elif trend > 70:
        return {
            "model": "D2C Brand"
        }

    # -------- DEFAULT --------
    return {
        "model": "Service-Based Business"
    }

def risk_score(budget, trend):
    score = 20
    if budget < 20000:
        score += 30
    if trend < 40:
        score += 30
    return min(score, 100)

def health_score(risk):
    return 100 - risk

# ---------------- PDF ----------------

def generate_pdf(data):
    file = "report.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("AI Business Report", styles['Title']))
    content.append(Spacer(1, 10))

    for k, v in data.items():
        content.append(Paragraph(f"{k}: {v}", styles["Normal"]))

    doc.build(content)
    return file

# ---------------- CSS ----------------

st.markdown("""
<style>

/* Smooth UI */
* {
    transition: all 0.2s ease-in-out;
}

/* -------- CARD -------- */
.card {
    padding:15px;
    border-radius:10px;
    border:1px solid rgba(128,128,128,0.2);
    text-align:center;
    background: inherit;
    color: inherit;
}

/* Hover */
.card:hover {
    transform: translateY(-8px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

/* -------- HEADER -------- */
.header {
    text-align:center;
    padding:20px;
    border-radius:10px;
    margin-bottom:20px;
    background: inherit;
    color: inherit;
}

/* -------- SIDEBAR -------- */
.sidebar-box {
    padding:20px;
    border-radius:10px;
    background: inherit;
    color: inherit;
}

/* -------- BADGES -------- */
.green {
    background:#22c55e;
    color:white;
    padding:5px 10px;
    border-radius:5px;
}

.yellow {
    background:#facc15;
    color:black;
    padding:5px 10px;
    border-radius:5px;
}

/* -------- BUTTON -------- */
div.stButton > button {
    background-color: #4f46e5;
    color: white;
    border-radius: 8px;
}

div.stButton > button:hover {
    background-color: #4338ca;
    transform: scale(1.05);
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.card ul {
    text-align:left;
    padding-left:15px;
}
.card h4 {
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.markdown("""
<div class="header">
<h1> AI-Based Business Launch Navigator</h1>
<p>Smart Decisions for First-Time Entrepreneurs</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1,3])

# ---------------- INPUT ----------------

with left:
    st.markdown('<div class="sidebar-box">', unsafe_allow_html=True)

    budget = st.number_input("Budget (₹)", value=100000)
    exp = st.selectbox("Experience", ["Beginner","Intermediate","Expert"])
    idea = st.text_input("Business Idea")

    run = st.button("Generate AI Plan")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- OUTPUT ----------------

with right:

    if run and idea:

        with st.spinner("Analyzing & generating AI insights..."):

            trend = get_trend_score(idea)
            price = get_price(idea)

            model = business_model(idea, budget, exp, trend)
            risk = risk_score(budget, trend)

            risk_analysis_raw = generate_risk_analysis(idea, budget, trend, risk)

            # 🔥 Convert to structured format
            sections = {
                    "Where": [],
                    "Why": [],
                    "Solution": []
                }

            current = None

            for line in risk_analysis_raw.split("\n"):
                    line = line.strip()

                    if "Where" in line:
                        current = "Where"
                    elif "Why" in line:
                        current = "Why"
                    elif "Solution" in line:
                        current = "Solution"
                    elif line.startswith("-") and current:
                        sections[current].append(line.replace("-", "").strip())
            health = health_score(risk)

            revenue = [price*i for i in [50,100,150,200]]
            cost = [price*i for i in [30,60,90,120]]

            @st.cache_data
            def cached_ai(idea, budget, exp, trend):
                return generate_ai_plan(idea, budget, exp, trend)

            # ai_output = cached_ai(idea, budget, exp, trend)
            ai_output_raw = cached_ai(idea, budget, exp, trend)

        # 🔥 Ensure dictionary format
        if isinstance(ai_output_raw, dict):
            ai_output = ai_output_raw

        else:
            try:
                import json
                ai_output = json.loads(ai_output_raw)
            except:
                # fallback to structured data
                ai_output = {
                    "swot": {
                        "Strength": f"Growing demand ({trend})",
                        "Weakness": "Initial investment required",
                        "Opportunity": "Expanding market",
                        "Threat": "Competition"
                    },
                    "audience": f"People interested in {idea}",
                    "marketing": [
                        "Social media marketing",
                        "Influencer promotion",
                        "Content branding"
                    ],
                    "plan": {
                        "Month 1": "Research & validation",
                        "Month 2": "Setup & product",
                        "Month 3": "Launch & marketing"
                    }
                }

            save_report(
                idea,
                budget,
                exp,
                model["model"],   # 🔥 ONLY STRING
                trend,
                risk,
                health
            )

        # -------- METRICS --------
        c1, c2, c3, c4 = st.columns(4)

        c1.markdown(f'<div class="card"><b>Business Model</b><br>{model["model"]}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="card"><b>Health</b><br><span class="green">{health}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="card"><b>Risk</b><br><span class="yellow">{risk}</span></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="card"><b>Startup Cost</b><br>₹{price*100:,}</div>', unsafe_allow_html=True)

        # -------- TABS --------
        tabs = st.tabs([
            "Overview","Financial","Risk",
            "AI Strategy","Roadmap","Export","History"
        ])

        # -------- OVERVIEW --------
        with tabs[0]:
            col1, col2 = st.columns(2)

            # fig = go.Figure()

            # fig.add_trace(go.Scatter(
            #     x=[1,2,3,4],
            #     y=cost,
            #     name="Cost",
            #     mode='lines+markers',
            #     hovertemplate="Month: %{x}<br>Cost: ₹%{y}<extra></extra>"
            # ))

            # fig.add_trace(go.Scatter(
            #     x=[1,2,3,4],
            #     y=revenue,
            #     name="Revenue",
            #     mode='lines+markers',
            #     hovertemplate="Month: %{x}<br>Revenue: ₹%{y}<extra></extra>"
            # ))

            # fig.update_layout(
            #     title="Break-Even Analysis",
            #     xaxis_title="Months",
            #     yaxis_title="Amount (₹)",
            #     legend_title="Legend"
            # )

            months = ["Month 1","Month 2","Month 3","Month 4"]

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=months,
                y=cost,
                name="Cost",
                mode='lines+markers',
                hovertemplate="<b>%{x}</b><br>Cost: ₹%{y:,}<extra></extra>"
            ))

            fig.add_trace(go.Scatter(
                x=months,
                y=revenue,
                name="Revenue",
                mode='lines+markers',
                hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,}<extra></extra>"
            ))

            fig.update_layout(
                title="Break-Even Analysis",
                xaxis_title="Months",
                yaxis_title="Amount (₹)",
                hovermode="x unified"   # 🔥 CRITICAL FIX
            )
            col1.plotly_chart(fig, use_container_width=True)

            fig2 = go.Figure()

            # fig2.add_trace(go.Scatter(
            #     x=[1,2,3,4],
            #     y=revenue,
            #     fill='tozeroy',
            #     name="Revenue Growth",
            #     hovertemplate="Revenue: ₹%{y}<extra></extra>"
            # ))

            # fig2.update_layout(
            #     title="Profit Projection",
            #     xaxis_title="Months",
            #     yaxis_title="Revenue (₹)"
            # )

            fig2.add_trace(go.Scatter(
                x=months,
                y=revenue,
                fill='tozeroy',
                name="Revenue Growth",
                hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,}<extra></extra>"
            ))

            fig2.update_layout(
                title="Profit Projection",
                xaxis_title="Months",
                yaxis_title="Revenue (₹)",
                hovermode="x unified"
            )
            col2.plotly_chart(fig2, use_container_width=True)

        # -------- FINANCIAL --------
        with tabs[1]:
            st.write(f"Projected Revenue: ₹{revenue[-1]}")

            st.subheader("📊 Revenue vs Cost Analysis")

            # bar chart with hover details
            fig_bar = go.Figure()

            # fig_bar.add_trace(go.Bar(
            #     x=["Month 1","Month 2","Month 3","Month 4"],
            #     y=revenue,
            #     name="Revenue",
            #     # hovertemplate="Revenue: ₹%{y}<extra></extra>"
            # ))

            # fig_bar.add_trace(go.Bar(
            #     x=["Month 1","Month 2","Month 3","Month 4"],
            #     y=cost,
            #     name="Cost"
            # ))

            # fig_bar.update_layout(
            #     title="Monthly Revenue vs Cost",
            #     xaxis_title="Months",
            #     yaxis_title="Amount (₹)",
            #     barmode='group'
            # )

            fig_bar.add_trace(go.Bar(
                x=months,
                y=revenue,
                name="Revenue",
                hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,}<extra></extra>"
            ))

            fig_bar.add_trace(go.Bar(
                x=months,
                y=cost,
                name="Cost",
                hovertemplate="<b>%{x}</b><br>Cost: ₹%{y:,}<extra></extra>"
            ))

            fig_bar.update_layout(
                title="Monthly Revenue vs Cost",
                xaxis_title="Months",
                yaxis_title="Amount (₹)",
                hovermode="x unified"
            )

            st.plotly_chart(fig_bar, use_container_width=True)

            # Calculate profit
            profit = [r - c for r, c in zip(revenue, cost)]

            st.subheader("📈 Profit Growth")

            fig_profit = go.Figure()

            # fig_profit.add_trace(go.Scatter(
            #     x=["Month 1","Month 2","Month 3","Month 4"],
            #     y=profit,
            #     mode='lines+markers',
            #     name="Profit"
            # ))

            # fig_profit.update_layout(
            #     title="Profit Over Time",
            #     xaxis_title="Months",
            #     yaxis_title="Profit (₹)"
            # )

            fig_profit.add_trace(go.Scatter(
                x=months,
                y=profit,
                mode='lines+markers',
                name="Profit",
                hovertemplate="<b>%{x}</b><br>Profit: ₹%{y:,}<extra></extra>"
            ))

            fig_profit.update_layout(
                title="Profit Over Time",
                xaxis_title="Months",
                yaxis_title="Profit (₹)",
                hovermode="x unified"
            )

            st.plotly_chart(fig_profit, use_container_width=True)

            # Break-Event Point

            st.subheader("⚖️ Break-Even Analysis")

            months = ["Month 1","Month 2","Month 3","Month 4"]

            # Find break-even point
            break_even_month = None
            for i in range(len(revenue)):
                if revenue[i] >= cost[i]:
                    break_even_month = months[i]
                    break

            fig_be = go.Figure()

            # cost line
            fig_be.add_trace(go.Scatter(
                x=months,
                y=cost,
                mode='lines+markers',
                name="Cost",
                hovertemplate="<b>%{x}</b><br>Cost: ₹%{y:,}<extra></extra>"
            ))
            # revenue line
            fig_be.add_trace(go.Scatter(
                x=months,
                y=revenue,
                mode='lines+markers',
                name="Revenue",
                hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,}<extra></extra>"
            ))

            fig_be.update_layout(
                title="Break-Even Point Analysis",
                xaxis_title="Months",
                yaxis_title="Amount (₹)",
                hovermode="x unified"
            )

            # Highlight break-even point
            if break_even_month:
                idx = months.index(break_even_month)

                fig_be.add_trace(go.Scatter(
                    x=[months[idx]],
                    y=[revenue[idx]],
                    mode='markers+text',
                    text=["Break-Even"],
                    textposition="top center",
                    marker=dict(size=12),
                    name="Break-Even Point"
                ))

            # fig_be.update_layout(
            #     title="Break-Even Point Analysis",
            #     xaxis_title="Months",
            #     yaxis_title="Amount (₹)"
            # )

            st.plotly_chart(fig_be, use_container_width=True)

            # Show message
            if break_even_month:
                st.success(f"✅ Break-even achieved in {break_even_month}")
            else:
                st.warning("⚠️ Break-even not achieved in 4 months")

        # -------- RISK --------
        with tabs[2]:
            
            st.subheader("⚠️ Risk Distribution")

            labels = ["Risk", "Safe"]
            values = [risk, 100 - risk]

            # fig_pie = go.Figure(data=[go.Pie(
            #     labels=labels,
            #     values=values,
            #     hole=0.4
            # )])
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                hovertemplate="%{label}: %{value}%<extra></extra>"
            )])

            fig_pie.update_layout(
                title="Business Risk Analysis"
            )

            st.plotly_chart(fig_pie, use_container_width=True)

            # st.markdown("### 📊 Risk Insights & Solution")

            st.markdown("## 📊 Risk Insights")

            col1, col2, col3 = st.columns(3)

            # WHERE
            col1.markdown(f"""
            <div class="card">
            <h4>⚠️ Where Risk</h4>
            <ul>
            {''.join(f"<li>{i}</li>" for i in sections["Where"])}
            </ul>
            </div>
            """, unsafe_allow_html=True)

            # WHY
            col2.markdown(f"""
            <div class="card">
            <h4>❓ Why Risk</h4>
            <ul>
            {''.join(f"<li>{i}</li>" for i in sections["Why"])}
            </ul>
            </div>
            """, unsafe_allow_html=True)

            # SOLUTION
            col3.markdown(f"""
            <div class="card">
            <h4>✅ Solution</h4>
            <ul>
            {''.join(f"<li>{i}</li>" for i in sections["Solution"])}
            </ul>
            </div>
            """, unsafe_allow_html=True)

            # risk_analysis = generate_risk_analysis(idea, budget, trend, risk)

            # st.markdown(risk_analysis)

        # -------- AI --------
        with tabs[3]:

            st.markdown("## 🤖 AI Business Strategy")

            # -------- SWOT --------
            st.markdown("### 📊 SWOT Analysis")

            col1, col2, col3, col4 = st.columns(4)

            col1.markdown(f"""
            <div class="card">
            <b>Strength</b><br>{ai_output['swot']['Strength']}
            </div>
            """, unsafe_allow_html=True)

            col2.markdown(f"""
            <div class="card">
            <b>Weakness</b><br>{ai_output['swot']['Weakness']}
            </div>
            """, unsafe_allow_html=True)

            col3.markdown(f"""
            <div class="card">
            <b>Opportunity</b><br>{ai_output['swot']['Opportunity']}
            </div>
            """, unsafe_allow_html=True)

            col4.markdown(f"""
            <div class="card">
            <b>Threat</b><br>{ai_output['swot']['Threat']}
            </div>
            """, unsafe_allow_html=True)

            # -------- Audience --------
            st.markdown("### 🎯 Target Audience")
            st.markdown(f"<div class='card'>{ai_output['audience']}</div>", unsafe_allow_html=True)

            # -------- Marketing --------
            st.markdown("### 📢 Marketing Strategy")
            for m in ai_output["marketing"]:
                st.markdown(f"<div class='card'>✔ {m}</div>", unsafe_allow_html=True)

            # -------- Plan --------
            st.markdown("### 📅 90-Day Roadmap")
            for k, v in ai_output["plan"].items():
                st.markdown(f"<div class='card'><b>{k}</b><br>{v}</div>", unsafe_allow_html=True)

        # -------- ROADMAP --------
        with tabs[4]:

            st.markdown("## 🚀 AI Business Roadmap")

            roadmap = generate_roadmap(idea, budget)

            cols = st.columns(3)

            months = list(roadmap.keys())

            for i in range(len(months)):
                m = months[i]
                data = roadmap[m]

                cols[i].markdown(f"""
                <div style="
                    background:inherit;
                    color:inherit;
                    padding:15px;
                    border-radius:10px;
                    border:1px solid #ddd;
                ">
                <h4>{m}</h4>

                <b>Platform:</b> {data['platform']}<br><br>
                <b>Action:</b> {data['action']}<br><br>
                <b>How:</b> {data['how']}

                </div>
                """, unsafe_allow_html=True)

        # -------- EXPORT --------
        with tabs[5]:

            data = {
                "Idea": idea,
                "Model": model["model"],
                "Health": health,
                "Risk": risk,
                "AI Plan": json.dumps(ai_output, indent=2)
            }

            file = generate_pdf(data)

            with open(file, "rb") as f:
                st.download_button(
                    label="📄 Download PDF",
                    data=f,
                    file_name="business_report.pdf",
                    mime="application/pdf"
                )
        # -------- HISTORY --------
        
        with tabs[6]:
                st.subheader("📜 Previous Reports")

                reports = get_reports()

                if reports:
                    for r in reports:

                        col1, col2 = st.columns([5,1])

                        with col1:
                            st.markdown(f"""
                            **Idea:** {r[1]}  
                            Budget: ₹{r[2]}  
                            Model: {r[4]}  
                            Health: {r[7]}  
                            """)

                        with col2:
                            if st.button("❌ Delete", key=f"del_{r[0]}"):
                                delete_report(r[0])
                                st.success("Deleted successfully")
                                st.rerun()

                        st.markdown("---")
                else:
                    st.info("No reports yet")