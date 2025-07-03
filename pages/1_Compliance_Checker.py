if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")
        st.dataframe(df)

        if "Entity" in df.columns and "Compliant" in df.columns:
            compliance_rate = (df["Compliant"].str.lower() == "yes").mean() * 100
            st.metric("Compliance Rate", f"{compliance_rate:.1f}%")

            st.markdown("### 📌 Entity-by-Entity Compliance")
            for _, row in df.iterrows():
                entity = row["Entity"]
                compliant = str(row["Compliant"]).strip().lower() == "yes"
                status = "✅ Compliant" if compliant else "❌ Non-Compliant"
                st.markdown(f"- **{entity}**: {status}")
        else:
            st.warning("⚠️ Missing expected columns like `Entity` or `Compliant`")

    except Exception as e:
        st.error(f"⚠️ Error loading file: {e}")
