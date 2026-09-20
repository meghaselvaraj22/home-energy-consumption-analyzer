import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Home Energy Consumption Analyzer",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Home Energy Consumption Analyzer")
st.write("Monitor, analyze and optimize your household electricity consumption.")

st.divider()

if "appliances" not in st.session_state:
    st.session_state.appliances = []


# -----------------------------
# TN DOMESTIC ESTIMATED BILL
# -----------------------------

def calculate_tn_bill(units):

    slabs = [
        (100, 0.00),
        (400, 4.70),
        (500, 6.30),
        (600, 8.40),
        (800, 9.45),
        (1000, 10.50),
        (float("inf"), 11.55)
    ]

    remaining = units
    previous_limit = 0
    total_charge = 0

    for limit, rate in slabs:

        slab_units = min(
            max(remaining, 0),
            limit - previous_limit
        )

        total_charge += slab_units * rate
        remaining -= slab_units

        previous_limit = limit

        if remaining <= 0:
            break

    return total_charge


# -----------------------------
# ADD APPLIANCE
# -----------------------------

st.subheader("🔌 Add Appliance")

col1, col2 = st.columns(2)

with col1:

    appliance = st.text_input(
        "Appliance Name",
        placeholder="Example: Fan"
    )

    power = st.number_input(
        "Power Rating (Watts)",
        min_value=0.0,
        step=1.0
    )

with col2:

    hours = st.number_input(
        "Usage per Day (Hours)",
        min_value=0.0,
        max_value=24.0,
        step=0.5
    )

    quantity = st.number_input(
        "Quantity",
        min_value=1,
        step=1
    )


if st.button("➕ Add Appliance"):

    if appliance.strip() == "":
        st.warning("Please enter an appliance name.")

    elif power <= 0:
        st.warning("Please enter a valid power rating.")

    elif hours <= 0:
        st.warning("Please enter daily usage hours.")

    else:

        daily_energy = (
            power * hours * quantity
        ) / 1000

        monthly_energy = daily_energy * 30

        st.session_state.appliances.append({
            "Appliance": appliance,
            "Power (W)": power,
            "Hours/Day": hours,
            "Quantity": quantity,
            "Daily Energy (kWh)": daily_energy,
            "Monthly Energy (kWh)": monthly_energy
        })

        st.success(
            f"{appliance} added successfully!"
        )


st.divider()


# -----------------------------
# ANALYSIS
# -----------------------------

if st.session_state.appliances:

    df = pd.DataFrame(
        st.session_state.appliances
    )

    total_appliances = len(df)

    total_daily = df[
        "Daily Energy (kWh)"
    ].sum()

    total_monthly = df[
        "Monthly Energy (kWh)"
    ].sum()


    # -------------------------
    # TN BILL
    # -------------------------

    estimated_bill = calculate_tn_bill(
        total_monthly
    )

    yearly_bill = estimated_bill * 6


    # -------------------------
    # DASHBOARD
    # -------------------------

    st.subheader("📊 Energy Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🔌 Appliances",
            total_appliances
        )

    with col2:
        st.metric(
            "⚡ Daily Energy",
            f"{total_daily:.2f} kWh"
        )

    with col3:
        st.metric(
            "📅 Monthly Energy",
            f"{total_monthly:.2f} kWh"
        )

    with col4:
        st.metric(
            "💰 Est. Bill",
            f"₹ {estimated_bill:,.2f}"
        )


    st.divider()


    # -------------------------
    # BILL INFORMATION
    # -------------------------

    st.subheader("💰 Tamil Nadu Domestic Bill Estimate")

    st.info(
        "This is an estimated energy-charge calculation "
        "using the displayed domestic slab rates. "
        "Actual EB bills may differ."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Estimated Energy Charge",
            f"₹ {estimated_bill:,.2f}"
        )

    with col2:

        st.metric(
            "Approx. Annual Energy Charge",
            f"₹ {yearly_bill:,.2f}"
        )


    st.divider()


    # -------------------------
    # APPLIANCE TABLE
    # -------------------------

    st.subheader("📋 Appliance Details")

    st.dataframe(
        df.round(2),
        use_container_width=True
    )


    st.divider()


    # -------------------------
    # CHARTS
    # -------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📈 Monthly Consumption")

        bar_data = df.set_index(
            "Appliance"
        )["Monthly Energy (kWh)"]

        st.bar_chart(bar_data)


    with col2:

        st.subheader("🥧 Energy Consumption Share")

        pie_fig = px.pie(
            df,
            names="Appliance",
            values="Monthly Energy (kWh)",
            hole=0.35
        )

        pie_fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        st.plotly_chart(
            pie_fig,
            use_container_width=True
        )


    st.divider()


    # -------------------------
    # HIGHEST CONSUMER
    # -------------------------

    highest = df.loc[
        df["Monthly Energy (kWh)"].idxmax()
    ]

    st.subheader(
        "🔴 Highest Energy Consumer"
    )

    st.warning(
        f"**{highest['Appliance']}** consumes the most energy: "
        f"**{highest['Monthly Energy (kWh)']:.2f} kWh/month**."
    )


    # -------------------------
    # EFFICIENCY STATUS
    # -------------------------

    st.subheader(
        "🏠 Home Energy Status"
    )

    if total_monthly <= 100:
        status = "🟢 Low Consumption"

    elif total_monthly <= 400:
        status = "🟡 Moderate Consumption"

    else:
        status = "🔴 High Consumption"

    st.info(
        f"Current status: **{status}**"
    )


    # -------------------------
    # WHAT-IF ANALYSIS
    # -------------------------

    st.divider()

    st.subheader(
        "💡 What-if Energy Saving Analysis"
    )

    appliance_names = df[
        "Appliance"
    ].tolist()

    selected = st.selectbox(
        "Select an appliance",
        appliance_names
    )

    selected_row = df[
        df["Appliance"] == selected
    ].iloc[0]

    current_hours = float(
        selected_row["Hours/Day"]
    )

    appliance_power = float(
        selected_row["Power (W)"]
    )

    appliance_quantity = int(
        selected_row["Quantity"]
    )

    new_hours = st.slider(
        "Reduce usage to (hours/day)",
        min_value=0.0,
        max_value=current_hours,
        value=max(
            0.0,
            current_hours - 1
        ),
        step=0.5
    )

    current_monthly = (
        appliance_power
        * current_hours
        * appliance_quantity
        * 30
    ) / 1000

    new_monthly = (
        appliance_power
        * new_hours
        * appliance_quantity
        * 30
    ) / 1000

    energy_saved = (
        current_monthly - new_monthly
    )

    new_total_monthly = (
        total_monthly - energy_saved
    )

    new_estimated_bill = calculate_tn_bill(
        new_total_monthly
    )

    money_saved = (
        estimated_bill - new_estimated_bill
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "⚡ Energy Saved",
            f"{energy_saved:.2f} kWh/month"
        )

    with col2:

        st.metric(
            "💰 Bill Saving",
            f"₹ {money_saved:,.2f}/billing cycle"
        )

    with col3:

        st.metric(
            "📉 New Estimated Bill",
            f"₹ {new_estimated_bill:,.2f}"
        )


    if money_saved > 0:

        st.success(
            f"Reducing **{selected}** usage from "
            f"{current_hours:.1f} → {new_hours:.1f} hours/day "
            f"could reduce the estimated energy charge."
        )

# -------------------------
    # DOWNLOAD REPORT
    # -------------------------

    st.divider()

    st.subheader("📥 Download Energy Report")

    report_df = df.copy()

    report_df["Daily Energy (kWh)"] = report_df[
        "Daily Energy (kWh)"
    ].round(2)

    report_df["Monthly Energy (kWh)"] = report_df[
        "Monthly Energy (kWh)"
    ].round(2)

    csv_data = report_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="📥 Download CSV Report",
        data=csv_data,
        file_name="home_energy_report.csv",
        mime="text/csv"
    )
    # -------------------------
    # REMOVE APPLIANCE
    # -------------------------

    st.divider()

    st.subheader(
        "🗑️ Manage Appliances"
    )

    selected_remove = st.selectbox(
        "Select appliance to remove",
        appliance_names,
        key="remove_appliance"
    )

    if st.button(
        "Remove Selected Appliance"
    ):

        index = appliance_names.index(
            selected_remove
        )

        st.session_state.appliances.pop(
            index
        )

        st.success(
            f"{selected_remove} removed successfully!"
        )

        st.rerun()


    if st.button(
        "🗑️ Clear All Appliances"
    ):

        st.session_state.appliances = []

        st.rerun()


else:

    st.info(
        "Add appliances above to start analyzing "
        "your home energy consumption."
    )