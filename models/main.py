import pandas as pd
import ast  # to safely parse list strings

def extract_comment_data(
    sentiment_path="exploratory_data_analytics/sentiment_analysis/SA_res/comments_with_sentiment.csv",
    length_dist_path="intermediate_output/from_CLD_res/comment_length_distribution.csv",
    word_ranking_path="exploratory_data_analytics/representative_words/RW_res/complete_words_ranking.csv",
    topic_summary_path="exploratory_data_analytics/topic_modeling/TM_res/topic_summary.csv"
):
    # Load data
    sentiment_df = pd.read_csv(sentiment_path)
    length_df = pd.read_csv(length_dist_path)
    words_df = pd.read_csv(word_ranking_path)
    topic_df = pd.read_csv(topic_summary_path)

    # --- Sentiment Analysis ---
    def label_sentiment(s):
        s = s.lower()
        if '5' in s or '4' in s:
            return 'positive'
        elif '3' in s:
            return 'neutral'
        else:
            return 'negative'

    sentiment_labels = sentiment_df['sentiment'].map(label_sentiment)
    sentiment_counts = sentiment_labels.value_counts(normalize=True) * 100
    sentiment_dict = {
        'positive': round(sentiment_counts.get('positive', 0), 1),
        'neutral': round(sentiment_counts.get('neutral', 0), 1),
        'negative': round(sentiment_counts.get('negative', 0), 1),
    }

    # --- Average Comment Length ---
    total_words = (length_df["Length"] * length_df["Count"]).sum()
    total_comments = length_df["Count"].sum()
    avg_length = total_words / total_comments

    # --- Top Words ---
    top_words = words_df.sort_values("score", ascending=False).head(5)["word"].tolist()

    # --- Extract Topics ---
    # Keep the top N topics with the most comments
    top_topic_rows = topic_df[topic_df["Topic"] != -1].sort_values("Count", ascending=False).head(5)
    
    topics = []
    for row in top_topic_rows["Representation"]:
        try:
            words = ast.literal_eval(row)  # safely parse list of strings
            topics.append(", ".join(words[:3]))  # take top 3 words per topic
        except:
            continue

    return {
        "sentiment": sentiment_dict,
        "avg_length": avg_length,
        "top_words": top_words,
        "topics": topics
    }

def generate_gpt_prompt(comment_data):
    sentiment = comment_data["sentiment"]
    avg_length = comment_data["avg_length"]
    top_words = comment_data["top_words"]
    topics = comment_data["topics"]

    prompt = f"""
You are an AI assistant that creates a paragraph summary of YouTube video content based on viewer comment analysis.

Here is the extracted data from the comments section:
- Sentiment distribution: {sentiment['positive']}% positive, {sentiment['neutral']}% neutral, {sentiment['negative']}% negative.
- Average comment length: {avg_length:.1f} words per comment, indicating overall comment brevity or detail.
- Most frequent words across all comments: {", ".join(top_words)}.
- Dominant discussion topics extracted from clusters of related words: {", ".join(topics)}.

Using this data, generate a one-paragraph, insightful and human-like summary that describes what the audience is likely reacting to or discussing in the video. Highlight any strong emotional reactions, repeated discussion themes, or notable patterns. Make sure the summary reads as if written by a human analyst, not a template.

"""
    return prompt.strip()


def generate_template_based_summary(comment_data):
    sentiment = comment_data["sentiment"]
    avg_length = comment_data["avg_length"]
    top_words = comment_data["top_words"]
    topics = comment_data["topics"]

    summary = (
        f"The majority of the comments are positive ({sentiment['positive']}%), with some neutral "
        f"({sentiment['neutral']}%) and a few negative ones ({sentiment['negative']}%). "
        f"On average, each comment is about {avg_length:.1f} words long. "
        f"Common words include {', '.join(top_words[:3])}, suggesting recurring themes. "
        f"Topics like {', '.join(topics[:2])} are frequently mentioned by viewers."
    )
    return summary


def generate_refinement_prompt(raw_summary):
     return "Here is a draft summary based on YouTube comments about a video: \n" + raw_summary + "\nPlease rewrite this into a refined, fluent, and engaging paragraph that could appear in a report or presentation about the video. Make it sound professional yet natural, and ensure it highlights key emotional responses, discussion themes, and community interests reflected in the comment data." 

comment_dat = extract_comment_data()

print(generate_gpt_prompt(comment_dat))

raw_summary = generate_template_based_summary(comment_dat)
refinement_prompt = generate_refinement_prompt(raw_summary)

print(refinement_prompt)