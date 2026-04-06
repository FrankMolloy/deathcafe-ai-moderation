from moderation.services.moderation_engine import moderate_text
from moderation.services.manual_eval_cases import TEST_CASES


def run_tests():
    correct = 0

    for i, case in enumerate(TEST_CASES, 1):
        result = moderate_text(case["title"], case["body"])

        predicted = result["recommendation"]
        expected = case["expected"]

        match = predicted == expected

        print(f"\nTest {i}")
        print(f"Title: {case['title']}")
        print(f"Expected: {expected}")
        print(f"Predicted: {predicted}")
        print(f"Confidence: {result['confidence']}")
        print(f"Match: {'✅' if match else '❌'}")
        print(f"Explanation: {result['explanation']}")

        if match:
            correct += 1

    print("\n====================")
    print(f"Score: {correct}/{len(TEST_CASES)}")
    print("====================")


if __name__ == "__main__":
    run_tests()