st.subheader("📊 Dashboard")

if not df.empty:

    # ---- KPIs ----
    total_scans = len(df)
    unique_barcodes = df['barcode'].nunique()
    duplicate_scans = len(df[df['remark'] == "Duplicate Scan"])
    new_items = len(df[df['remark'] == "New Item"])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Scans", total_scans)
    col2.metric("Unique Barcodes", unique_barcodes)
    col3.metric("Duplicate Scans", duplicate_scans)
    col4.metric("New Items", new_items)

    st.divider()

    # ---- USER ANALYSIS ----
    st.subheader("👤 Scans by User")

    user_counts = df['user'].value_counts().reset_index()
    user_counts.columns = ['User', 'Scans']

    st.bar_chart(user_counts.set_index('User'))

    # ---- TIME ANALYSIS ----
    st.subheader("📅 Scans Over Time")

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date

    time_counts = df.groupby('date').size()

    st.line_chart(time_counts)

else:
    st.info("No data available for dashboard yet.")