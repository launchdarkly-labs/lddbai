import json
from get_deps import Deps
from openai import OpenAI
from ldai.client import AIConfig, ModelConfig, LDMessage, ProviderConfig, Context, LDAIConfigTracker
from ldai.tracker import TokenUsage

# Automatically picks up OPENAI_API_KEY from env
client = OpenAI()

def get_ai_config_full_evaluation(payload: dict) -> tuple[AIConfig, LDAIConfigTracker]:
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
        'schema': get_relevant_schema(payload.get('schema', []), payload.get('schema_diff', [])),
        'schema_diff': payload.get('schema_diff', []),
        'sql_queries': get_relevant_queries(payload.get('sql_queries', []), payload.get('queries_diff', [])),
        'queries_diff': payload.get('queries_diff', [])
    })

def get_relevant_schema(schema: dict, schema_diff: list) -> dict:
    """
    Use LaunchDarkly AI to determine which parts of the full schema are relevant
    for database change evaluation, based on the schema changes.
    """
    if not schema or not schema_diff:
        return schema
        
    # Create AI config with both schema and schema_diff context
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
    config, tracker = aiclient.config('get-relevant-schema', context, fallback_value, { 
        'schema': schema,
        'schema_diff': schema_diff,
    })
    
    if not config.enabled:
        return schema
    
    messages = [] if config.messages is None else config.messages
    
    # The messages and prompts are handled by LaunchDarkly AI configuration
    # Data context is provided through the config parameters
    
    response = tracker.track_openai_metrics(
        lambda: client.chat.completions.create(
            model=config.model.name,
            messages=[message.to_dict() for message in messages],
            **config.model.parameters
        )
    )
    
    # Flush LaunchDarkly client
    ldclient = Deps().get_launchdarkly()
    ldclient.flush()
    
    try:
        # Try to parse the response as JSON, fallback to original schema if parsing fails
        response_content = response.choices[0].message.content
        return json.loads(response_content)
    except (json.JSONDecodeError, KeyError, IndexError):
        # If AI response can't be parsed, return original schema
        return schema

def get_relevant_queries(queries: list, queries_diff: list) -> list:
    """
    Use LaunchDarkly AI to determine which parts of the full queries are relevant
    for database change evaluation, based on the query changes.
    """
    if not queries or not queries_diff:
        return queries
        
    # Create AI config with both queries and queries_diff context
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
    config, tracker = aiclient.config('get-relevant-queries', context, fallback_value, { 
        'sql_queries': queries,
        'queries_diff': queries_diff,
    })
    
    if not config.enabled:
        return queries
    
    messages = [] if config.messages is None else config.messages
    
    # The messages and prompts are handled by LaunchDarkly AI configuration
    # Data context is provided through the config parameters
    
    response = tracker.track_openai_metrics(
        lambda: client.chat.completions.create(
            model=config.model.name,
            messages=[message.to_dict() for message in messages],
            **config.model.parameters
        )
    )
    
    # Flush LaunchDarkly client
    ldclient = Deps().get_launchdarkly()
    ldclient.flush()
    
    try:
        # Try to parse the response as JSON, fallback to original queries if parsing fails
        response_content = response.choices[0].message.content
        return json.loads(response_content)
    except (json.JSONDecodeError, KeyError, IndexError):
        # If AI response can't be parsed, return original queries
        return queries
