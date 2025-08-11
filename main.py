import sys
import json
import argparse
from get_deps import Deps
from openai import OpenAI
from pprint import pprint
from ldai.client import AIConfig, ModelConfig, LDMessage, ProviderConfig, Context, LDAIConfigTracker
from ldai.tracker import TokenUsage

# Automatically picks up OPENAI_API_KEY from env
client = OpenAI()

def get_ai_config(payload: dict) -> tuple[AIConfig, LDAIConfigTracker]:
    aiclient = Deps().get_launchdarkly_ai()
    context = Context.builder('cockroachdb').kind('database').name('cockroachdb').build()
    fallback_value = AIConfig(
        enabled=True,
        model=ModelConfig(
            name="gpt-4o-mini",
            parameters={"temperature": 0.8},
        ),
        messages=[LDMessage(role="system", content="")],
        provider=ProviderConfig(name="my-default-provider"),
    )
    return aiclient.config('evaluate-database-changes', context, fallback_value, { 
        'schema': payload.get('schema', []),
        'schema_diff': payload.get('schema_diff', []),
        'sql_queries': payload.get('sql_queries', []),
        'queries_diff': payload.get('queries_diff', [])
    })

def get_openai_recommendation(payload: dict) -> str:
    config, tracker = get_ai_config(payload)
    # print("config:")
    # pprint(config)
    messages = [] if config.messages is None else config.messages
    # print([message.to_dict() for message in messages])
    response = tracker.track_openai_metrics(
        lambda:
            client.chat.completions.create(
                model=config.model.name,
                messages=[message.to_dict() for message in messages],
            )
    )
    ldclient = Deps().get_launchdarkly()
    ldclient.flush()
    
    return response.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description='Analyze database changes')
    parser.add_argument('--input-file', required=True, help='Path to input JSON file')
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r') as f:
            input_data = f.read()
            # print("🔍 Reading from file:", args.input_file) # TODO: remove debug print
            # print("🔍 Input Data:")                         # TODO: remove debug print
            # print(input_data)                               # TODO: remove debug print
        
        # First parse the outer JSON structure
        payload = json.loads(input_data)
        if (payload.get('queries_diff') is None or len(payload.get('queries_diff')) == 0) and (payload.get('schema_diff') is None or len(payload.get('schema_diff')) == 0):
            print("There are no changes to the database, so this PR will not affect the database.")
            return
        
        # Parse any string values that are actually JSON
        for key in ['sql_queries', 'queries_diff', 'schema', 'schema_diff']:
            if key in payload and isinstance(payload[key], str):
                try:
                    # Try to parse the string as JSON
                    payload[key] = json.loads(payload[key])
                except json.JSONDecodeError:
                    # If it's not valid JSON, keep it as a string
                    pass

        # print("\n🔍 Parsed Payload:")                      # TODO: remove debug print
        # print(json.dumps(payload, indent=2))               # TODO: remove debug print

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse input JSON: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Input file not found: {args.input_file}")
        sys.exit(1)

    recommendations = get_openai_recommendation(payload)
    print("\n📌 LD-DBAi Recommendations:\n")
    print(recommendations)

if __name__ == "__main__":
    main()

