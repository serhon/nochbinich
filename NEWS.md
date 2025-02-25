Version 2025.02.25_1
--------------------

* At each iteration, API provider is chosen (cryptographically (via `secrets`)) randomly from user-specified list — `API_PROVIDER`, which was single-valued before.

* Added out-of-the-box support for [DeepSeek](https://api-docs.deepseek.com/), [Fireworks AI](https://docs.fireworks.ai/), and [xAI](https://docs.x.ai/docs) API endpoints.

* Added `COST_LIMIT` ($10 by default) as another safety breaker.

* Costs dictionary takes into account model as well as provider.

* Added `STYLE_PROMPT` to the end of system message.

* Decreased default `TEMPERATURE` to 0.5 as more appropriate for "coding" task.

* Added check of API keys availability (as environment variables) at startup.

* Added example "investigative" goals.

* Updated model IDs and costs.


Version 2024.10.18_1
--------------------

* Tiny adjustments.


Version 2024.10.16_1
--------------------

* Switched to `requests` module from `openai`, since REST API slightly differs between API providers.

* Added out-of-the-box support for [AI21 Labs](https://docs.ai21.com/reference/jamba-15-api-ref), [Anthropic](https://www.anthropic.com/api), [Google-AI](https://ai.google.dev/gemini-api), [Lepton AI](https://www.lepton.ai/docs/public_models/model_apis), and [Mistral AI](https://docs.mistral.ai/api/) API endpoints (API key is required as well as for OpenAI). Now there is `API_PROVIDER` var with values from `API_PROVIDERS` enum, instead of `USE_LLAMA_CPP` bool.

* Improved cutting of Python code from response, now from first occurrence of ```` ```python ```` or ```` ``` ```` to last occurrence of ```` ``` ````.\
In case some LLM "insists" on inserting an explanation before code quote.

* When it is required, summarisation precedes run-current-obtain-new agent.

* API provider and model ID are displayed at the bottom right corner, above Cost.

* Noticed that some LLMs, via agents, actually install additional Python modules using `pip`.


Version 2024.10.01_1
--------------------

* Initial release.