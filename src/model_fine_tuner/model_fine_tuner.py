import openai

class ModelFineTuner:
    """A class for fine-tuning OpenAI models with provided question-answer pairs."""

    def __init__(self, model_id: str):
        """
        Initialize the ModelFineTuner with a specific model ID.

        :param model_id: The OpenAI model ID to be fine-tuned.
        """
        self.model_id = model_id

    @staticmethod
    def _prepare_training_data(question_answer_pairs):
        """
        Prepare the training data by combining question-answer pairs into single strings.

        :param question_answer_pairs: A list of tuples containing question and answer strings.
        :return: A list of strings with combined question and answer pairs.
        """
        return [f"{q} {a}" for q, a in question_answer_pairs]

    def fine_tune(self, question_answer_pairs, max_tokens=1024, n_epochs=10):
        """
        Fine-tune the model with the provided question-answer pairs.

        :param question_answer_pairs: A list of tuples containing question and answer strings.
        :param max_tokens: The maximum number of tokens for the fine-tuning task.
        :param n_epochs: The number of training epochs.
        :return: The fine-tuned model ID.
        """
        training_data = self._prepare_training_data(question_answer_pairs)

        fine_tuned_model = openai.FineTune.create(
            model=self.model_id,
            prompt=training_data,
            max_tokens=max_tokens,
            n_epochs=n_epochs
        )

        return fine_tuned_model.id

# Example usage:
if __name__ == "__main__":
    question_answer_pairs = [
        ("What is the capital of France?", "The capital of France is Paris."),
        ("What is the largest planet in our solar system?", "The largest planet in our solar system is Jupiter.")
    ]

    # model_fine_tuner = ModelFineTuner(model_id="gpt-3.5-turbo")
    # fine_tuned_model_id = model_fine_tuner.fine_tune(question_answer_pairs)
    # print(f"Fine-tuned model ID: {fine_tuned_model_id}")
