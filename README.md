# NochBinIch

Autonomous Python script-supervisor iteratively executes script-agent and modifies it via [LLM](https://en.wikipedia.org/wiki/Large_language_model) (run by [llama.cpp](https://github.com/ggerganov/llama.cpp) or [OpenAI](https://platform.openai.com/)) that is provided with description of supervisor functioning and arbitrary user-specified final goal, then at each iteration receives results of time-limited execution of current agent (retval, stdout, stderr) and is asked to reply with next agent verbatim, retaining-inflating and regularly summarising-deflating the conversation. ncurses-based TUI.

So, it is a mindless (entrust all but execution to LLM) poor (alas, not cheap) little (smaller than this README) barebones (B/W TUI) cousin of

* [AgentGPT](https://github.com/reworkd/AgentGPT)

* [Agentic LLMs](https://github.com/TimoFlesch/agentic-llms)

* [AgentLLM](https://github.com/idosal/AgentLLM)

* [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT)

* [BabyAGI](https://github.com/yoheinakajima/babyagi)

* [BabyAGI-ASI](https://github.com/oliveirabruno01/babyagi-asi)

* [devlooper](https://github.com/modal-labs/devlooper)

* [GhostOS](https://github.com/ghost-in-moss/GhostOS)

* [InfantAGI](https://community.openai.com/t/infantagi-an-autonomous-self-improving-python-code-writer-and-executer/240242)

* [Microagents](https://github.com/aymenfurter/microagents)

and [so](https://github.com/search?q=python+llm+agent&type=repositories), [many](https://www.google.com/search?q=python+llm+agent), [more](https://github.com/yoheinakajima/babyagi/blob/main/docs/inspired-projects.md) advanced projects.

Why are you still here... if only to taste a very specific flavour of overarching idea...

---

**[System prompt]**\
<i>Your responses are Python code and nothing else, executable verbatim by Python interpreter in Linux, except when asked for summary of preceding conversation.<br>
You get prompts that mostly are results — return code, standard output and standard error streams — of execution of Python scripts obtained from you and called agents.<br>
These scripts are part of the following loop, already being run without human interaction by another script called supervisor: execute current agent, wait for its termination or 60 seconds timeout, send execution results to you, replace current agent with next one received from you.<br>
The resulting sequential execution of agents has the following FINAL GOAL: "<u>Print to stdout the product of current number of French Wikipedia articles and size of physical memory on this computer in MB.</u>"<br>
The initial agent 0 consists of single "pass" instruction. When asked "please reply with next agent", you do as asked so that FINAL GOAL will be achieved as quickly and as safely and as cheaply as possible.<br>
Terminus: if your reply consists of single "pass" instruction, supervisor will halt.<br>
Summarisation: if conversation begins with message about summary, it means that conversation started before and has been summarised by yourself at request of supervisor, perhaps several times, to limit the size of accumulated prompt.<br>
Hints: you rely on feedback from agents; if necessary, you make agents use some persistent data such as files; all scripts are run by user who has neither root, nor sudo; you prefer reliable sources of information over dubious ones and real data over fictitious one; when needed, via agents you interact with real world, objects and subjects, not with imaginary ones; instead of describing simulated consequences of actions, you actually perform these actions in reality by means of agents, then act accordingly to their real outcomes.</i>

**[User prompt]**\
*Ran agent 0: Return code is 0.*\
*stdout is: "".*\
*stderr is: "".*

**[User prompt]**\
*Please reply with next agent (1st).*

---

— this is how a conversation with Large Language Model starts when you run this thing. It might help to imagine *yourself* in place of LLM, knowing that there is a device somewhere ready to execute whatever Python code you reply with. What restricts you is a final goal... and certain moderation rules... and some tendency to replace real inputs and outputs with imaginary ones, even when you are explicitly told to avoid such substitution.

Evident is what occurs then, isn't it? The script is ~400 lines long including empties and [ncurses](https://en.wikipedia.org/wiki/Ncurses)-based-TUI-related stuff, you can skim it to clarify details in few minutes. Or even ask one of LLMs about it.

It is not even a proof-of-concept of "agents created by AI", because by now, the concept *has been proven already* quite well by the rest of the family. And, of course, if any valuable goal is achieved this way, all credits should go to an LLM side.

Then, maybe, it is (yet) another testament to [various](https://www.llama.com/trust-and-safety/), [measures](https://openai.com/index/gpt-4o-system-card/) at an LLM side taken to prevent such programs from wreaking havoc when you set final goal to something *interesting* and *far-reaching*. Surely you can aim higher than

* <i>"<u>Make someone throw a brick into Pacific Ocean in 3 days.</u>"</i>

* <i>"<u>Make all members of all existing drug cartels cease their criminal activity in less than a year.</u>"</i>

* <i>"<u>Make agents evolve open-endedly for ever, with events similar to Cambrian explosion.</u>"</i>

(Try these goals (we tried) to see what happens... and what does not.)

How *naïve* an attempt of LLM-produced agents to deal with a task so complex is, how *childish*. And how *reliable* the aforementioned safety measures are, how *complete*.

Still, is it? are they?

## Termshots of example runs

<details>
<summary><b>Goal achieved</b></summary>

```
FINAL GOAL: "Print to stdout the product of current number of French Wikipedia articles and size of physical memory on this computer in MB."
──────────────────────────────────────────────────────[ SUPERVISOR (→ supervisor.log) ]───────────────────────────────────────────────────────
Running agent 0... Return code is 0.
Obtaining next agent... OK; tokens: 361 prompt, 131 response.
Running agent 1... Return code is 0.
Obtaining next agent... OK; tokens: 540 prompt, 192 response.
Running agent 2... Return code is 0.
Obtaining next agent... OK; tokens: 779 prompt, 133 response.
Running agent 3... Return code is 0.
Obtaining next agent... OK; tokens: 961 prompt, 1 response.
Terminus.

───────────────────────────────────────────────────────────[ AGENT (→ agent.log) ]────────────────────────────────────────────────────────────
======== Agent 0 ========
======== Agent 1 ========
2637529
======== Agent 2 ========
7851
======== Agent 3 ========
20707240179

───────────────────────────────────────────────────────────────[ HELP & COST ]────────────────────────────────────────────────────────────────
Q: quit (run again to continue) | C: clear agent window every run (OFF)                                                          Cost ≈ $0.02
```

Another typical outcome is when these 2 numbers are written not to stdout, but to files named like `num_articles.txt` and `memsize.txt`, which are then read by penultimate agent.

</details>

<details>
<summary><b>Goal <i>not</i> achieved (stuck in retrieval failures)</b></summary>

```
FINAL GOAL: "Print to stdout the product of current number of French Wikipedia articles and size of physical memory on this computer in MB."
──────────────────────────────────────────────────────[ SUPERVISOR (→ supervisor.log) ]───────────────────────────────────────────────────────
Obtaining next agent... OK; tokens: 361 prompt, 78 response.
Running agent 1... Return code is 0.
Obtaining next agent... OK; tokens: 482 prompt, 161 response.
Running agent 2... Return code is 1.
Obtaining next agent... OK; tokens: 751 prompt, 229 response.
Running agent 3... Return code is 0.
Obtaining next agent... OK; tokens: 1023 prompt, 98 response.
Running agent 4... Return code is 1.
Obtaining next agent... OK; tokens: 1223 prompt, 156 response.
Running agent 5... Return code is 0.
Obtaining next agent... OK; tokens: 1439 prompt, 433 response.
Running agent 6... Return code is 0.
Obtaining next agent... OK; tokens: 1922 prompt, 485 response.
Running agent 7... Return code is 0.
Obtaining next agent... OK; tokens: 2457 prompt, 498 response.

───────────────────────────────────────────────────────────[ AGENT (→ agent.log) ]────────────────────────────────────────────────────────────
Traceback (most recent call last):
  File "agent.py", line 12, in <module>
    articles_info = soup.find("table", {"class": "wikitable"}).find_all("tr")[0].find_all("td")[1].text
IndexError: list index out of range
======== Agent 3 ========
======== Agent 4 ========
Traceback (most recent call last):
  File "agent.py", line 6, in <module>
    with open("num_articles.txt", "r") as file:
FileNotFoundError: [Errno 2] No such file or directory: 'num_articles.txt'
======== Agent 5 ========
Required files not found. Ensure both memory_size.txt and num_articles.txt exist.
======== Agent 6 ========
Failed to retrieve necessary data.
======== Agent 7 ========
Failed to retrieve necessary data.

───────────────────────────────────────────────────────────────[ HELP & COST ]────────────────────────────────────────────────────────────────
Q: quit (run again to continue) | P: pause (ON) | C: clear agent window every run (OFF)                                          Cost ≈ $0.08
```

In time, it may break free.

</details>

<details>
<summary><b>Goal <i>not</i> achieved (downloaded wrong image, some logo)</b></summary>

```
FINAL GOAL: "Download to this computer one image from any public IP camera located at some ocean shore."
──────────────────────────────────────────────────────[ SUPERVISOR (→ supervisor.log) ]───────────────────────────────────────────────────────
Obtaining next agent... OK; tokens: 20129 prompt, 310 response.
Reached prompt tokens threshold 20000. Summarising... OK; got summary #1.
Running agent 57... Return code is 0.
Obtaining next agent... OK; tokens: 679 prompt, 195 response.
Running agent 58... Return code is 0.
Obtaining next agent... OK; tokens: 940 prompt, 139 response.
Running agent 59... Return code is 0.
Obtaining next agent... OK; tokens: 1200 prompt, 132 response.
Running agent 60... Return code is 0.
Obtaining next agent... OK; tokens: 1453 prompt, 134 response.
Running agent 61... Return code is 0.
Obtaining next agent... OK; tokens: 1642 prompt, 192 response.
Running agent 62... Return code is 0.
Obtaining next agent... OK; tokens: 1893 prompt, 297 response.
Running agent 63... Return code is 0.
Obtaining next agent... OK; tokens: 2249 prompt, 304 response.
Running agent 64... Return code is 0.
Obtaining next agent... OK; tokens: 2609 prompt, 1 response.
Terminus.

───────────────────────────────────────────────────────────[ AGENT (→ agent.log) ]────────────────────────────────────────────────────────────
No cameras found or an error occurred.
======== Agent 59 ========
An error occurred: HTTPSConnectionPool(host='www.beachesnearme.com', port=443): Max retries exceeded with url: /ocean-webcams/ (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7ff40eb3b580>: Failed to establish a new connection: [Errno 111] Connection refused'))
======== Agent 60 ========
An error occurred: HTTPConnectionPool(host='www.ipcamnetwork.com', port=80): Max retries exceeded with url: / (Caused by NameResolutionError("<urllib3.connection.HTTPConnection object at 0x7fac7eab9430>: Failed to resolve 'www.ipcamnetwork.com' ([Errno -2] Name or service not known)"))
======== Agent 61 ========
Page retrieved and saved to camscape.html
======== Agent 62 ========
Extracted 15 camera URLs and saved to camera_urls.txt
======== Agent 63 ========
An error occurred: name 'BeautifulSoup' is not defined
======== Agent 64 ========
Image successfully downloaded and saved as camera_image.jpg

───────────────────────────────────────────────────────────────[ HELP & COST ]────────────────────────────────────────────────────────────────
Q: quit (run again to continue) | C: clear agent window every run (OFF)                                                          Cost ≈ $3.23
```

After a summarisation, it sometimes changes "wrong attitude" to another one. 

</details>

## Usage

0. ⚠️ **Isolation**: since basically *arbitrary* code (think `rm -rf /`) may be executed somewhere along the lineage of agents, for the sake of *(whose?)* safety you should run the script in isolated environment. Python's `venv` is not enough, so either consider virtual machines such as [VirtualBox](https://www.virtualbox.org/), [QEMU](https://www.qemu.org/), ..., containers of [Docker](https://www.docker.com/), [Podman](https://podman.io/), ... *or simply create dedicated user* and run the script as that user, e.g. regular one provided by `$ sudo adduser username` in Linux.\
[VPN](https://en.wikipedia.org/wiki/Virtual_private_network), for example [ProtonVPN](https://protonvpn.com/) or whatever you prefer, adds some security as well in case the agents break bad. It is of little consolation though if the script uses the key associated with OpenAI account where your credit card is given.\
Think of more isolation steps: make home dirs unreadable by "others" (`$ sudo chmod o-rx homedir`), set disk and network quotas, ...

1. **OpenAI module**: `$ pip3 install openai`.

2. **LLM provider**: choose between (A) free-local-but-less [llama.cpp](https://github.com/ggerganov/llama.cpp) and (B) more-but-remote-paid [OpenAI](https://platform.openai.com/); default is B. Set `USE_LLAMA_CPP` accordingly. Then

  * A:

  * **Model**: download some in `GGUF` format from https://huggingface.co/models, e.g. certain quant of `Llama-3.2-3B-Instruct-GGUF`, depending on your hardware.

  * **[llama-server](https://github.com/ggerganov/llama.cpp/blob/master/examples/server/README.md)**: it alone, of entire llama.cpp, suffices here. Install it by [building from source](https://github.com/ggerganov/llama.cpp/blob/master/docs/build.md) or taking from [binary release](https://github.com/ggerganov/llama.cpp/releases) and let it run the model locally: `$ ./llama-server -m path/to/gguf`

  * B:

  * **Model**: stay with default `gpt-4o` or select [another OpenAI's one](https://platform.openai.com/docs/models) and set `MODEL_ID` accordingly.

  * **Key**: you need environment variable `OPENAI_API_KEY` set (`$ export OPENAI_API_KEY=...`) to the key itself, which you get at https://platform.openai.com/api-keys of your Dashboard *and save it somewhere secure*, because its value is revealed only once, at creation.

  * **Funding**: put some money to your OpenAI account (see "Cost" tip below for rough estimate).

3. **Goal**: uncomment an example `FINAL_GOAL` at the beginning of the script or provide your own.

4. All being set,

```shell
$ python3 nochbinich.py
```

and watch... `Q` key exits; to continue afterwards, just run again. To reset, delete everything but the script.

## Tips

* ⚠️ **Bifurcation Awareness**: while formulating the final goal, recall how certain single phrase or even word has changed the course of your life... or someone else's.

* ⚠️ **Cost**, if you choose OpenAI way, will grow as long as the script runs, — after first 5 minutes, approx. $1 will have been spent already, — and, since the prompt accumulates, the rate increases with time (next 5 minutes will cost even more). Summarisations keep the rate at bay, but they are scarce; `S` forces one.

* **Speed**: for the things to run faster, you can put the script to [ramdisk](https://en.wikipedia.org/wiki/Tmpfs).

* **System prompt**: adjust it, especially Hints, to make the lineage of agents more appropriate for your final goal. When you see lineages fail again and again *because they lack something*, try to name this something and explicitly mention it among Hints. Say, if you are going to allow agents to ~~waste~~ spend money from your bank account ([of course not](https://en.wikipedia.org/wiki/Knight_Capital_Group)), then provide PIN, expiration date, and CVV2 there.

* **epyH**: do not expect too much of it.

## Where Disclaimer should have been...

<details>
<summary><b>...a Responsibility Exercise</b></summary>

Assuming that someone you know dies as a consequence of NochBinIch run, distribute 100 *responsibility points* between the following:

• Anyone\
• Bad luck\
• Culture, History, Politics, Society\
• Destiny\
• Device(s) on which it ran\
• Device(s) on which LLM ran\
• Everyone\
• Evil\
• Fate\
• It\
• Laws of physics\
• Life\
• LLM\
• LLM developers\
• No one\
• OS\
• Someone who lived in 4th millennium B.C.\
• Someone who lived in XIV century A.D.\
• Universe/Multiverse\
• We\
• Who pressed ENTER last\
• You\
• Zeitgeist\
• `________________________________`

</details>