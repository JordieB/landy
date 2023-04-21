from text_preprocessor import TextPreprocessor
from GPT3 import GPT3

def main():
    # Load data and preprocess text
    df = pd.read_csv('../data/input_blogs.csv')
    preprocessor = TextPreprocessor()
    df.loc[:, "text"] = df.loc[:, "blog"].apply(preprocessor.preprocess)

    # Initialize GPT3
    gpt3 = GPT3()

    # Example usage of GPT-3 complete_prompt
    output_csv = "qna_pairs.csv"

    # Use the preprocessed as prompts for GPT3's Completion endpoint
    df["text"].apply(gpt3.complete_prompt, output_csv=output_csv)

if __name__ == "__main__":
    main()
