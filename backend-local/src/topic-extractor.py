import pandas as pd
from bertopic import BERTopic
from sklearn.datasets import fetch_20newsgroups

print("Loading 20 Newsgroups dataset...")
newsgroups_data = fetch_20newsgroups(subset='all', remove=('headers', 'footers', 'quotes'))
docs = newsgroups_data['data']      # type: ignore
print(f"Loaded {len(docs)} documents.")

print("Initializing BERTopic model...")
topic_model = BERTopic(verbose=True)

print("Fitting BERTopic model to documents (this may take a few minutes)...")
topics, probs = topic_model.fit_transform(docs)
print("Topic modeling complete!")

print("\n--- Topic Information ---")
topic_info = topic_model.get_topic_info()
print(topic_info.head(10))

# --- MODIFIED PART FOR ROBUSTNESS ---
# Filter out the outlier topic (-1)
# And then sort by count to find the most frequent *actual* topic  
non_outlier_topics = topic_info[topic_info['Topic'] != -1]

if not non_outlier_topics.empty:
    # Get the most frequent topic among non-outliers
    # This will be the first row after filtering and sorting by Count (descending by default)
    most_frequent_topic_id = non_outlier_topics.iloc[0]['Topic']
    most_frequent_topic_name = non_outlier_topics.iloc[0]['Name']
    most_frequent_topic_count = non_outlier_topics.iloc[0]['Count']


    print(f"\n--- Most Frequent Actual Topic ({most_frequent_topic_name}, Count: {most_frequent_topic_count}) ---")
    print(topic_model.get_topic(most_frequent_topic_id))

    # --- Information for a Specific Document (using the new logic) ---
    sample_doc_index = 100
    sample_doc = docs[sample_doc_index]
    assigned_topic = topics[sample_doc_index]
    topic_probability = probs[sample_doc_index]     # type: ignore

    print(f"\n--- Information for Sample Document (Index {sample_doc_index}) ---")
    print(f"Document snippet: \"{sample_doc[:200]}...\"")
    print(f"Assigned Topic ID: {assigned_topic}")
    # Safely get topic name, handling if assigned_topic is -1
    assigned_topic_name = topic_model.get_topic_info(topic=assigned_topic)['Name'].iloc[0] if assigned_topic != -1 else "Outlier Topic"
    print(f"Topic Name: {assigned_topic_name}")
    print(f"Probability: {topic_probability:.4f}")

    # Visualizations will still work normally as they handle -1 topics correctly
    print("\n--- Generating Intertopic Distance Map (interactive plot) ---")
    fig1 = topic_model.visualize_topics()

    print("\n--- Generating Topic Word Scores Bar Chart (interactive plot) ---")
    fig2 = topic_model.visualize_barchart(top_n_topics=10)
    
    fig1.write_html("intertopic_distance_map.html")
    fig2.write_html("topic_word_scores.html")
    
else:
    print("\nNo actual topics (other than outliers) were detected by BERTopic.")
    print("This might happen if:")
    print("  - Your documents are very diverse with no strong clusters.")
    print("  - The 'min_topic_size' parameter in BERTopic is too high for your dataset.")
    print("  - There simply aren't distinct topics in your data.")
    print("Consider adjusting BERTopic parameters like 'min_topic_size', 'n_neighbors' (in UMAP), or providing a different embedding model.")

print("\nDemo complete. Check your browser/Jupyter output for interactive visualizations.")
