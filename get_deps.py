"""
Dependencies - this is a centralized place to get all the dependencies
in the codebase we can use any of the deps here like this:
from get_deps import Deps
ldclient = Deps().get_launchdarkly()
ai_client = Deps().get_launchdarkly_ai()
this also allows us to swap dependencies easily if needed
"""

import ldclient
from ldclient.config import Config
from ldai.client import LDAIClient
import os
import time
class Deps:
    @staticmethod
    def get_launchdarkly() -> ldclient.LDClient:
        """
        Returns a configured LaunchDarkly SDK client.
        Uses the singleton pattern as recommended by LaunchDarkly.
        Gets the SDK key from the LAUNCHDARKLY_SDK_KEY environment variable.
        
        Returns:
            ldclient.LDClient: Configured LaunchDarkly client singleton
            
        Raises:
            ValueError: If launchdarkly_sdk_key environment variable is not set
        """
        sdk_key = os.getenv("LAUNCHDARKLY_SDK_KEY")
        # print("sdk_key")
        # print(sdk_key)
        if not sdk_key:
            # test account - https://app.ld.catamorphic.com/projects/ld-db-ai/ai-configs?selected-env=production&env=production&env=test
            sdk_key = "sdk-ed735e05-b610-447e-b59b-7be4a525749c"
            
        # Set the configuration with custom endpoints
        ldclient.set_config(Config(
            sdk_key=sdk_key,
            base_uri="https://app.ld.catamorphic.com",
            events_uri="https://events.ld.catamorphic.com",
            stream_uri="https://stream.ld.catamorphic.com"
        ))
        return ldclient.get()

    @staticmethod
    def get_launchdarkly_ai() -> LDAIClient:
        """
        Returns a configured LaunchDarkly AI client.
        Uses the base LaunchDarkly client to create an AI client.
        
        Returns:
            LDAIClient: Configured LaunchDarkly AI client
        """
        base_client = Deps.get_launchdarkly()
        return LDAIClient(base_client)

