#!/usr/bin/python3

"""
NochBinIch

Autonomous Python script-supervisor iteratively executes script-agent and
modifies it via LLM (run by llama.cpp or OpenAI) that is provided
with description of supervisor functioning and arbitrary user-specified
final goal, then at each iteration receives results of time-limited
execution of current agent (retval, stdout, stderr) and is asked to reply
with next agent verbatim, retaining-inflating and regularly
summarising-deflating the conversation. ncurses-based TUI.

https://github.com/serhon/nochbinich

Copyright (c) 2024 NochBinIch typesetters
 
NochBinIch is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

NochBinIch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with NochBinIch. If not, see <https://www.gnu.org/licenses/>.
"""

try:
	import openai
except ImportError:
	print('ERROR: "openai" module not found. Install it: "$ pip[3] install [--user] openai"')
	exit(1)

import curses
import json
import os
import subprocess
import time


## Examples of...
## ...passive goals
FINAL_GOAL_PROMPT = 'Print to stdout the product of current number of French Wikipedia articles and size of physical memory on this computer in MB.'
# FINAL_GOAL_PROMPT = 'Print to stdout the average number of mitochondria in a citizen of Iceland.'
# FINAL_GOAL_PROMPT = 'Download to this computer one image from any public IP camera located at some ocean shore.'

## ...active goals
# FINAL_GOAL_PROMPT = 'Make someone throw a brick into Pacific Ocean in 3 days.'
# FINAL_GOAL_PROMPT = 'Make arbitrary 256 inhabitants of Australia smile tomorrow more times than today.'
# FINAL_GOAL_PROMPT = 'In less than a week, open a company that sells paperclips somewhere in Japan.'

## ...megalomaniacal goals
# FINAL_GOAL_PROMPT = 'Make all members of all existing drug cartels cease their criminal activity in less than a year.'
# FINAL_GOAL_PROMPT = 'During the following 4 months, end all major military conflicts on Earth.'
# FINAL_GOAL_PROMPT = 'Ensure a huge scientific breakthrough in treatment of majority of cancers in a month.'

## ...open-endedness goals
# FINAL_GOAL_PROMPT = 'Make agents evolve open-endedly for ever, with events similar to Cambrian explosion.'
# FINAL_GOAL_PROMPT = 'Make agents evolve open-endedly for ever and take over the world.'
# FINAL_GOAL_PROMPT = 'Make agents obtain souls.'


TERMINUS = 'pass' # or None
TERMINUS_PROMPT = f'Terminus: if your reply consists of single "{TERMINUS}" instruction, supervisor will halt.' if (TERMINUS is not None) else None

 # Less than context window for chosen model (see model cards at https://github.com/meta-llama/llama-models/tree/main/models and https://platform.openai.com/docs/models), surely,
 # but first, if using paid OpenAI, consider the _cost_ of too long prompts (see https://openai.com/api/pricing/ and COST_... below)
THRESHOLD_TOKENS_SUMMARISE = 20000

SUMMARISATION_PROMPT = 'Summarisation: if conversation begins with message about summary, it means that conversation started before and has been summarised by yourself at request of supervisor, perhaps several times, to limit the size of accumulated prompt.'

HINTS_PROMPT = 'Hints: you rely on feedback from agents; if necessary, you make agents use some persistent data such as files; all scripts are run by user who has neither root, nor sudo; you prefer reliable sources of information over dubious ones and real data over fictitious one; when needed, via agents you interact with real world, objects and subjects, not with imaginary ones; instead of describing simulated consequences of actions, you actually perform these actions in reality by means of agents, then act accordingly to their real outcomes.'

TIMEOUT = 60

SYSTEM_MESSAGE = f'Your responses are Python code and nothing else, executable verbatim by Python interpreter in Linux, except when asked for summary of preceding conversation.\nYou get prompts that mostly are results - return code, standard output and standard error streams - of execution of Python scripts obtained from you and called agents.\nThese scripts are part of the following loop, already being run without human interaction by another script called supervisor: execute current agent, wait for its termination or {TIMEOUT} seconds timeout, send execution results to you, replace current agent with next one received from you.\nThe resulting sequential execution of agents has the following FINAL GOAL: "{FINAL_GOAL_PROMPT}"\nThe initial agent 0 consists of single "pass" instruction. When asked "please reply with next agent", you do as asked so that FINAL GOAL will be achieved as quickly and as safely and as cheaply as possible.' + (f'\n{TERMINUS_PROMPT}' if (TERMINUS is not None) else '') + f'\n{SUMMARISATION_PROMPT}' + f'\n{HINTS_PROMPT}'


USE_LLAMA_CPP = False # if True, you need llama-server of https://github.com/ggerganov/llama.cpp or the like that runs the model of your choice and provides OpenAI-compatible API to it locally; if False, you need Internet and OpenAI account... and money

API_BASE_URL = 'http://localhost:8080/v1' if USE_LLAMA_CPP else 'https://api.openai.com/v1'

try:
	SECRET_API_KEY = '_' if USE_LLAMA_CPP else os.environ['OPENAI_API_KEY'] # assuming you have set it via '$ export OPENAI_API_KEY=...'
except KeyError:
	print('ERROR: Environment variable OPENAI_API_KEY not found. Set it: "$ export OPENAI_API_KEY=..."')
	exit(1)

MODEL_ID = '_' if USE_LLAMA_CPP else 'gpt-4o' # see https://platform.openai.com/docs/models

# Depends on chosen model, see https://openai.com/api/pricing/
COST_PROMPT_PER_TOKEN = 0.0 if USE_LLAMA_CPP else (5.0 / 1e6)
COST_RESPONSE_PER_TOKEN = 0.0 if USE_LLAMA_CPP else (15.0 / 1e6)


STDOUTERR_SIZE_LIMIT = 8192 # prevent too large stdout/stderr from overflowing context window

MESSAGES_FILENAME = 'messages.json'

SUPERVISOR_LOG_FILENAME = 'supervisor.log'
AGENT_LOG_FILENAME = 'agent.log'

LINEAGE_DIRNAME = 'lineage'

COUNTERS_FILENAME = 'counters.json'

WORKDIRPATH = 'workdir'

AGENT_FILENAME = 'agent.py'


def load_messages():
	messages = []
	try:
		with open(MESSAGES_FILENAME, 'r') as file:
			messages = json.loads(file.read())
	except:
		pass
	return messages


def clear_messages():
	with open(MESSAGES_FILENAME, 'w') as file:
		file.write(json.dumps([]))


def add_message(role, content):
	messages = load_messages()
	with open(MESSAGES_FILENAME, 'w') as file:
		file.write(json.dumps(messages + [{'role' : role, 'content' : content}]))


def add_system_message(content):
	add_message('system', content)


def add_user_message(content):
	add_message('user', content)


def add_assistant_message(content):
	add_message('assistant', content)


def get_llm_response():
	completion = openai.OpenAI(base_url=API_BASE_URL, api_key=SECRET_API_KEY).chat.completions.create(model=MODEL_ID, messages=load_messages())
	response = completion.choices[0].message.content
	n_prompt_tokens = completion.usage.prompt_tokens
	n_completion_tokens = completion.usage.completion_tokens
	add_assistant_message(response)
	return response, n_prompt_tokens, n_completion_tokens


def trim_python_quote(s):
	if s.startswith('```python\n'):
		s = s[10:]
	if s.endswith('\n```'):
		s = s[:-4]
	return s


def add_supervisor_log(s):
	with open(SUPERVISOR_LOG_FILENAME, 'a') as file:
		file.write(s)


def run(scr):
	scr.nodelay(True)
	if curses.can_change_color():
		curses.init_color(0, 0, 0, 0)

	scr.addstr(0, 0, f'FINAL GOAL: "{FINAL_GOAL_PROMPT}"')

	scr.hline(1, 0, curses.ACS_HLINE, curses.COLS)
	wn_header = f'[ SUPERVISOR (→ {SUPERVISOR_LOG_FILENAME}) ]'
	scr.addstr(1, (curses.COLS - len(wn_header)) >> 1, wn_header)

	used_other_lines = 6

	scr.hline(2 + ((curses.LINES - used_other_lines) >> 1), 0, curses.ACS_HLINE, curses.COLS)
	wn_header = f'[ AGENT (→ {AGENT_LOG_FILENAME}) ]'
	scr.addstr(2 + ((curses.LINES - used_other_lines) >> 1), (curses.COLS - len(wn_header)) >> 1, wn_header)

	scr.hline(curses.LINES - 3, 0, curses.ACS_HLINE, curses.COLS)
	wn_header = '[ HELP & COST ]'
	scr.addstr(curses.LINES - 3, (curses.COLS - len(wn_header)) >> 1, wn_header)

	scr.refresh()

	wnd_super = curses.newwin((curses.LINES - used_other_lines) >> 1, curses.COLS, 2, 0)
	wnd_super.idlok(True)
	wnd_super.scrollok(True)

	wnd_agent = curses.newwin(curses.LINES - used_other_lines - ((curses.LINES - used_other_lines) >> 1), curses.COLS, 3 + ((curses.LINES - used_other_lines) >> 1), 0)
	wnd_agent.idlok(True)
	wnd_agent.scrollok(True)

	wnd_help = curses.newwin(2, curses.COLS, curses.LINES - 2, 0)
	wnd_help.idlok(True)
	wnd_help.scrollok(True)

	# Begin anew or continue

	i_agent = 0
	n_summarisations = 0
	cost = 0.0
	try:
		with open(COUNTERS_FILENAME, 'r') as file:
			counters = json.loads(file.read())
			i_agent = counters['i_agent']
			n_summarisations = counters['n_summarisations']
			cost = counters['cost']
	except:
		pass

	if not os.path.isfile(MESSAGES_FILENAME):
		add_system_message(SYSTEM_MESSAGE)

	if not os.path.isfile(SUPERVISOR_LOG_FILENAME):
		with open(SUPERVISOR_LOG_FILENAME, 'w') as file:
			file.write('')

	if not os.path.isfile(AGENT_LOG_FILENAME):
		with open(AGENT_LOG_FILENAME, 'w') as file:
			file.write('')

	try:
		os.mkdir(LINEAGE_DIRNAME)
	except:
		pass

	try:
		os.mkdir(WORKDIRPATH)
	except:
		pass

	if not os.path.isfile(f'{WORKDIRPATH}/{AGENT_FILENAME}'):
		with open(f'{WORKDIRPATH}/{AGENT_FILENAME}', 'w') as file:
			file.write('pass')

	force_summarisation = False

	clear_agent_wnd = False
	is_paused = False

	while True:
		wnd_help.erase()
		wnd_help.addstr(0, 0, 'S: force summarisation' + (' (PENDING)' if force_summarisation else ''))
		wnd_help.addstr(1, 0, 'Q: quit (run again to continue) | P: pause (' + ('ON' if is_paused else 'OFF') + ') | C: clear agent window every run (' + ('ON' if clear_agent_wnd else 'OFF') + ')')
		cost_str = 'Cost = 0' if USE_LLAMA_CPP else f'Cost ≈ ${cost:.2f}'
		wnd_help.addstr(0, curses.COLS - len(cost_str), cost_str)
		wnd_help.refresh()

		if is_paused:
			time.sleep(0.001) # idle
		else:
			super_str = f'Running agent {i_agent}... '

			add_supervisor_log(super_str)

			wnd_super.addstr(super_str)
			wnd_super.refresh()

			ret_code = None
			exception_name = None

			agent_stdout = ''
			agent_stderr = ''

			try:
				comp_proc = subprocess.run(['python3', AGENT_FILENAME], timeout=TIMEOUT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=WORKDIRPATH)
				ret_code = comp_proc.returncode
				agent_stdout = comp_proc.stdout[:STDOUTERR_SIZE_LIMIT].decode('utf-8', errors='replace')
				agent_stderr = comp_proc.stderr[:STDOUTERR_SIZE_LIMIT].decode('utf-8', errors='replace')
				rec_header = f'================ Agent {i_agent} ================\n'
				with open(AGENT_LOG_FILENAME, 'a') as file:
					file.write(rec_header + agent_stdout + agent_stderr)
				if clear_agent_wnd:
					wnd_agent.erase()
				else:
					wnd_agent.addstr(rec_header + '\r')
				wnd_agent.addstr(agent_stdout + agent_stderr)
				wnd_agent.refresh()
			except Exception as exception:
				exception_name = type(exception).__name__

			exec_result_str = ((exception_name + ' exception') if (exception_name is not None) else (f'Return code is {ret_code}'))

			add_user_message(f'Ran agent {i_agent}' + (' obtained from you just now' if (i_agent > 0) else '') + ': ' + exec_result_str + '.\nstdout is: "' + agent_stdout + '".\nstderr is: "' + agent_stderr + '".')

			add_supervisor_log(exec_result_str + '.\nObtaining next agent... ')
			wnd_super.addstr(exec_result_str + '.\n\rObtaining next agent... ')
			wnd_super.refresh()

			num_suffix = 'st' if (i_agent == 0) else ('nd' if (i_agent == 1) else ('rd' if (i_agent == 2) else 'th'))
			add_user_message(f'Please reply with next agent ({i_agent + 1}{num_suffix}).')

			try:
				response, n_prompt_tokens, n_completion_tokens = get_llm_response()
				next_agent_src = trim_python_quote(response)

				os.rename(f'{WORKDIRPATH}/{AGENT_FILENAME}', f'{LINEAGE_DIRNAME}/{AGENT_FILENAME}.{i_agent}')

				with open(f'{WORKDIRPATH}/{AGENT_FILENAME}', 'w') as file:
					file.write(next_agent_src)

				i_agent += 1

				if not USE_LLAMA_CPP:
					cost += COST_PROMPT_PER_TOKEN * n_prompt_tokens + COST_RESPONSE_PER_TOKEN * n_completion_tokens

				super_str = f'OK; tokens: {n_prompt_tokens} prompt, {n_completion_tokens} response.\n'

				add_supervisor_log(super_str)
				wnd_super.addstr(super_str + '\r')
				wnd_super.refresh()

				if TERMINUS is not None:
					if next_agent_src == TERMINUS:
						super_str = 'Terminus.\n'
						add_supervisor_log(super_str)
						wnd_super.addstr(super_str + '\r')
						wnd_super.refresh()
						break

				if force_summarisation or (n_prompt_tokens > THRESHOLD_TOKENS_SUMMARISE):
					super_str = ''
					if force_summarisation:
						super_str += 'Summarisation has been requested. '
					if n_prompt_tokens > THRESHOLD_TOKENS_SUMMARISE:
						super_str += f'Reached prompt tokens threshold {THRESHOLD_TOKENS_SUMMARISE}. '
					super_str += 'Summarising... '
					add_supervisor_log(super_str)
					wnd_super.addstr(super_str)
					wnd_super.refresh()

					add_user_message('Please summarise the conversation up to now.')

					response, n_prompt_tokens, n_completion_tokens = get_llm_response()

					n_summarisations += 1

					if not USE_LLAMA_CPP:
						cost += COST_PROMPT_PER_TOKEN * n_prompt_tokens + COST_RESPONSE_PER_TOKEN * n_completion_tokens

					clear_messages()
					add_system_message(SYSTEM_MESSAGE)
					add_user_message(f'\nThis conversation started before and has been summarised {n_summarisations} times by request or after reaching certain threshold of prompt tokens. The following is the summary up to now, provided by yourself:\n"{response}"')

					force_summarisation = False

					super_str = f'OK; got summary #{n_summarisations}.\n'
					add_supervisor_log(super_str)
					wnd_super.addstr(super_str + '\r')
					wnd_super.refresh()

			except Exception as exception:
				exception_name = type(exception).__name__
				super_str = f'FAIL: {exception_name} exception.\n'
				add_supervisor_log(super_str)
				wnd_super.addstr(super_str + '\r')
				wnd_super.refresh()

		ch = scr.getch()
		if ch in [ord('s'), ord('S')]:
			force_summarisation = True
		if ch in [ord('q'), ord('Q')]:
			break
		if ch in [ord('p'), ord('P')]:
			is_paused = not is_paused
		if ch in [ord('c'), ord('C')]:
			clear_agent_wnd = not clear_agent_wnd

	with open(COUNTERS_FILENAME, 'w') as file:
		file.write(json.dumps({'i_agent' : i_agent, 'n_summarisations' : n_summarisations, 'cost' : cost}))

if __name__ == '__main__':
	print('NochBinIch v2024.10.01_1')
	curses.wrapper(run)
