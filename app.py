import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.impute import SimpleImputer
import joblib

st.set_page_config(page_title="Best Patient Clustering", layout="wide")
st.title("🩺 Patient Clustering (Best Algorithm Automatically Selected)")

uploaded_file = st.file_uploader("Upload your patient dataset (CSV)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("📊 Dataset Preview")
    st.write(df.head())

    df_encoded = pd.get_dummies(df, drop_first=True)
    imputer = SimpleImputer(strategy="mean")
    X_imputed = imputer.fit_transform(df_encoded)
    X_scaled = StandardScaler().fit_transform(X_imputed)

    results = {}

    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans_labels = kmeans.fit_predict(X_scaled)
    results["KMeans"] = {
        "labels": kmeans_labels,
        "silhouette": silhouette_score(X_scaled, kmeans_labels) if len(set(kmeans_labels)) > 1 else -1
    }

    hier = AgglomerativeClustering(n_clusters=3, linkage="ward")
    hier_labels = hier.fit_predict(X_scaled)
    results["Hierarchical"] = {
        "labels": hier_labels,
        "silhouette": silhouette_score(X_scaled, hier_labels) if len(set(hier_labels)) > 1 else -1
    }

    db = DBSCAN(eps=0.5, min_samples=5)
    db_labels = db.fit_predict(X_scaled)
    results["DBSCAN"] = {
        "labels": db_labels,
        "silhouette": silhouette_score(X_scaled, db_labels) if len(set(db_labels)) > 1 and -1 not in db_labels else -1
    }

    best_algo = max(results, key=lambda x: results[x]["silhouette"])
    best_labels = results[best_algo]["labels"]

    st.success(f"✅ Best clustering method selected: **{best_algo}**")
    st.write(f"Silhouette Score: **{results[best_algo]['silhouette']:.3f}**")

    df["Cluster"] = best_labels
    st.subheader("🧩 Clustered Data (Best Method)")
    st.write(df.head())

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=best_labels, palette="Set2", s=60)
    plt.title(f"{best_algo} Clustering (PCA Projection)")
    st.pyplot(plt)

    if best_algo == "Hierarchical":
        st.subheader("📉 Dendrogram (Truncated)")
        Z = linkage(X_scaled, method="ward")
        plt.figure(figsize=(10, 4))
        dendrogram(Z, truncate_mode="level", p=5, no_labels=True)
        plt.title("Hierarchical Clustering Dendrogram (Truncated)")
        st.pyplot(plt)

    st.subheader("⬇️ Download Clustered Dataset")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "clustered_patients.csv", "text/csv")

    joblib.dump(df, "clustered_patients.joblib")